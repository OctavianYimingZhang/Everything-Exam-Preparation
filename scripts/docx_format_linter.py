#!/usr/bin/env python3
"""Validate Example Essay DOCX formatting, highlighting, and source maps."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from docx import Document  # type: ignore
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX  # type: ignore
    from docx.shared import Cm, Pt  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"python-docx is required: {exc}")

try:
    from example_essay_language_linter import lint_records as lint_language_records
    from example_essay_language_linter import load_docx_records
except Exception:  # pragma: no cover
    sys.path.append(str(Path(__file__).resolve().parent))
    try:
        from example_essay_language_linter import lint_records as lint_language_records
        from example_essay_language_linter import load_docx_records
    except Exception:  # pragma: no cover
        lint_language_records = None
        load_docx_records = None


AUTHOR_YEAR_RE = re.compile(r"\([A-Z][A-Za-z'’-]+(?:\s+et\s+al\.|\s+and\s+[A-Z][A-Za-z'’-]+)?(?:,\s*|\s+)(?:19|20)\d{2}[a-z]?\)")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
QUESTION_SUBTITLE_RE = re.compile(r"^\s*(explain|discuss|compare|evaluate|describe|how|why|what|to what extent)\b", re.I)
GREEN_SOURCE_TYPES = {"citation_original_source", "classic_experiment_source", "extra_reading_paper"}
PUBLIC_PREAMBLE_PATTERNS = [
    ("model_answer_built_from", re.compile(r"\bModel answer built from\b", re.I)),
    ("not_predicted_exam_question", re.compile(r"\bThis is not a predicted exam question\b", re.I)),
    ("exam_style_question", re.compile(r"\bExam[- ]style question\b", re.I)),
    ("decorative_question_label", re.compile(r"^\s*Question\s*:", re.I)),
    ("decorative_essay_topic_label", re.compile(r"^\s*Essay Topic\s*:", re.I)),
    ("standalone_example_essay_label", re.compile(r"^\s*Example\s+essay\s*:?\s*$", re.I)),
]
CM_TOL = 0.08
PT_TOL = 0.25


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def public_preamble_hits(text: str) -> list[str]:
    return [name for name, pattern in PUBLIC_PREAMBLE_PATTERNS if pattern.search(text)]


def source_was_read(source_run: dict[str, Any]) -> bool:
    return source_run.get("citation_original_read") is True or source_run.get("source_read") is True


def emu_to_cm(value) -> float:
    return float(value.cm)


def pt_value(value) -> float | None:
    if value is None:
        return None
    return float(value.pt)


def paragraph_spacing_pt(paragraph, attr: str) -> float:
    value = getattr(paragraph.paragraph_format, attr)
    if value is None and paragraph.style is not None:
        value = getattr(paragraph.style.paragraph_format, attr)
    numeric = pt_value(value)
    return 0.0 if numeric is None else numeric


def close(actual: float | None, expected: float, tol: float) -> bool:
    return actual is not None and abs(actual - expected) <= tol


def load_source_map(docx_path: Path, explicit_map: Path | None) -> dict[str, Any] | None:
    if explicit_map:
        return json.loads(explicit_map.read_text(encoding="utf-8"))
    candidate = docx_path.with_name(docx_path.stem.split("_")[0] + "_source_map.json")
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    candidate = docx_path.with_name(docx_path.stem + "_source_map.json")
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return None


def run_font_name(run) -> str | None:
    return run.font.name


def run_font_size_pt(run) -> float | None:
    return pt_value(run.font.size)


def paragraph_kind_from_map(source_map: dict[str, Any] | None, index: int, text: str = "") -> str:
    if not source_map:
        if index == 1:
            return "title"
        if index == 2 and QUESTION_SUBTITLE_RE.match(text):
            return "subtitle"
        return "body"
    paragraphs = source_map.get("paragraphs", [])
    if index - 1 < len(paragraphs):
        return paragraphs[index - 1].get("kind", "body")
    return "body"


def lint_docx(docx_path: Path, source_map_path: Path | None = None) -> dict[str, Any]:
    doc = Document(docx_path)
    source_map = load_source_map(docx_path, source_map_path)
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    section = doc.sections[0]
    format_checks = {
        "margins_2_5_cm": all(
            close(emu_to_cm(value), 2.5, CM_TOL)
            for value in [section.top_margin, section.bottom_margin, section.left_margin, section.right_margin]
        ),
        "arial": True,
        "line_spacing_1_5": True,
        "no_paragraph_spacing": True,
        "body_justified": True,
        "title_centered": True,
        "subtitles_left": True,
        "question_subtitle_plain": True,
        "no_empty_spacer_paragraphs": True,
        "no_public_preamble": True,
    }
    if not format_checks["margins_2_5_cm"]:
        failures.append({"type": "margins_not_2_5_cm"})

    total_body_words = 0
    yellow_words = 0
    green_words = 0
    paragraphs_missing_lecture_anchor = []
    green_runs_missing_citation = []
    green_runs_missing_read_source = []
    yellow_runs_missing_extra_reading_anchor = []
    unexpected_highlights = []
    micro_detail_failures = []
    public_preamble_leaks = []

    source_paragraphs = source_map.get("paragraphs", []) if source_map else []
    allowed_author_years = set()
    if source_map:
        for paragraph in source_paragraphs:
            for run in paragraph.get("runs", []):
                citation = run.get("in_text_citation")
                if citation:
                    allowed_author_years.add(citation)

    visible_paragraph_index = 0
    for paragraph in doc.paragraphs:
        if not paragraph.text.strip():
            format_checks["no_empty_spacer_paragraphs"] = False
            failures.append({"type": "empty_spacer_paragraph"})
            continue
        visible_paragraph_index += 1
        kind = paragraph_kind_from_map(source_map, visible_paragraph_index, paragraph.text)
        source_para = source_paragraphs[visible_paragraph_index - 1] if visible_paragraph_index - 1 < len(source_paragraphs) else {}
        preamble_hits = public_preamble_hits(paragraph.text)
        if preamble_hits:
            format_checks["no_public_preamble"] = False
            public_preamble_leaks.append({"paragraph": visible_paragraph_index, "hits": preamble_hits, "text": paragraph.text[:160]})

        if paragraph.paragraph_format.line_spacing != 1.5:
            format_checks["line_spacing_1_5"] = False
            failures.append({"type": "line_spacing_not_1_5", "paragraph": visible_paragraph_index, "line_spacing": paragraph.paragraph_format.line_spacing})

        space_before = paragraph_spacing_pt(paragraph, "space_before")
        space_after = paragraph_spacing_pt(paragraph, "space_after")
        if not close(space_before, 0.0, PT_TOL) or not close(space_after, 0.0, PT_TOL):
            format_checks["no_paragraph_spacing"] = False
            failures.append(
                {
                    "type": "paragraph_spacing_not_zero",
                    "paragraph": visible_paragraph_index,
                    "space_before_pt": round(space_before, 3),
                    "space_after_pt": round(space_after, 3),
                }
            )

        if kind == "title" and paragraph.alignment != WD_ALIGN_PARAGRAPH.CENTER:
            format_checks["title_centered"] = False
            failures.append({"type": "title_not_centered", "paragraph": visible_paragraph_index})
        elif kind in {"subtitle", "heading"} and paragraph.alignment != WD_ALIGN_PARAGRAPH.LEFT:
            format_checks["subtitles_left"] = False
            failures.append({"type": "subtitle_or_heading_not_left", "paragraph": visible_paragraph_index})
        elif kind == "body" and paragraph.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY:
            format_checks["body_justified"] = False
            failures.append({"type": "body_not_justified", "paragraph": visible_paragraph_index})

        if kind == "body":
            if source_map and not source_para.get("lecture_anchors"):
                paragraphs_missing_lecture_anchor.append(visible_paragraph_index)

        source_runs = source_para.get("runs", []) if source_para else []
        visible_runs = [run for run in paragraph.runs if run.text]
        for r_idx, run in enumerate(visible_runs, start=1):
            if run_font_name(run) != "Arial":
                format_checks["arial"] = False
                failures.append({"type": "run_font_not_arial", "paragraph": visible_paragraph_index, "run": r_idx, "font": run_font_name(run)})
            if kind == "subtitle":
                subtitle_size = run_font_size_pt(run)
                if run.bold is True or run.italic is True or (subtitle_size is not None and subtitle_size > 12.0 + PT_TOL):
                    format_checks["question_subtitle_plain"] = False
                    failures.append(
                        {
                            "type": "question_subtitle_not_plain",
                            "paragraph": visible_paragraph_index,
                            "run": r_idx,
                            "bold": run.bold,
                            "italic": run.italic,
                            "font_size_pt": subtitle_size,
                        }
                    )

            source_run = source_runs[r_idx - 1] if r_idx - 1 < len(source_runs) else {}
            wc = len(words(run.text))
            if source_run.get("micro_detail_insert"):
                if source_run.get("source_type") not in {"extra_reading_book", *GREEN_SOURCE_TYPES}:
                    micro_detail_failures.append({"paragraph": visible_paragraph_index, "run": r_idx, "type": "micro_detail_requires_verified_extra_source"})
                if not source_run.get("parent_ppt_or_source_slot"):
                    micro_detail_failures.append({"paragraph": visible_paragraph_index, "run": r_idx, "type": "micro_detail_parent_slot_missing"})
                if not source_run.get("source_anchor"):
                    micro_detail_failures.append({"paragraph": visible_paragraph_index, "run": r_idx, "type": "micro_detail_insert_missing_source_anchor"})
                if not source_run.get("inserted_phrase"):
                    micro_detail_failures.append({"paragraph": visible_paragraph_index, "run": r_idx, "type": "micro_detail_missing_inserted_phrase"})
                if source_run.get("claim_delta") not in {None, "", "precision_only", "none"}:
                    micro_detail_failures.append({"paragraph": visible_paragraph_index, "run": r_idx, "type": "micro_detail_claim_delta_not_precision_only"})
            if kind == "body":
                total_body_words += wc
            highlight = run.font.highlight_color
            if highlight == WD_COLOR_INDEX.YELLOW:
                yellow_words += wc
                if source_run.get("source_type") != "extra_reading_book" or not source_run.get("source_anchor"):
                    yellow_runs_missing_extra_reading_anchor.append({"paragraph": visible_paragraph_index, "run": r_idx, "text": run.text[:120]})
            elif highlight == WD_COLOR_INDEX.BRIGHT_GREEN:
                green_words += wc
                citation = source_run.get("in_text_citation")
                if not citation and not AUTHOR_YEAR_RE.search(run.text):
                    green_runs_missing_citation.append({"paragraph": visible_paragraph_index, "run": r_idx, "text": run.text[:120]})
                if source_run.get("source_type") not in GREEN_SOURCE_TYPES or not source_was_read(source_run):
                    green_runs_missing_read_source.append({"paragraph": visible_paragraph_index, "run": r_idx, "text": run.text[:120]})
            elif highlight is not None:
                unexpected_highlights.append({"paragraph": visible_paragraph_index, "run": r_idx, "highlight": str(highlight)})

    if paragraphs_missing_lecture_anchor:
        failures.append({"type": "paragraphs_missing_lecture_anchor", "paragraphs": paragraphs_missing_lecture_anchor})
    if green_runs_missing_citation:
        failures.append({"type": "green_highlight_missing_citation", "runs": green_runs_missing_citation})
    if green_runs_missing_read_source:
        failures.append({"type": "green_highlight_missing_read_original_source", "runs": green_runs_missing_read_source})
    if yellow_runs_missing_extra_reading_anchor:
        failures.append({"type": "yellow_highlight_missing_extra_reading_anchor", "runs": yellow_runs_missing_extra_reading_anchor})
    if unexpected_highlights:
        warnings.append({"type": "unexpected_highlight_colour", "runs": unexpected_highlights})
    if micro_detail_failures:
        failures.append({"type": "micro_detail_source_map_failures", "runs": micro_detail_failures})
    if public_preamble_leaks:
        failures.append({"type": "public_preamble_leak", "paragraphs": public_preamble_leaks})

    extra_reading_ratio = yellow_words / total_body_words if total_body_words else 0.0
    extra_status = (source_map or {}).get("extra_reading_status")
    if yellow_words and extra_reading_ratio > 0.15:
        failures.append({"type": "extra_reading_ratio_above_15_percent", "ratio": extra_reading_ratio})
    if extra_status in {"supplied_found", "found", "chapter_found"} and 0 < extra_reading_ratio < 0.05:
        warnings.append({"type": "extra_reading_ratio_low_no_padding_required", "ratio": extra_reading_ratio})

    used_citations = set(AUTHOR_YEAR_RE.findall("\n".join(p.text for p in doc.paragraphs)))
    if source_map and allowed_author_years and not used_citations.issubset(allowed_author_years):
        failures.append({"type": "essay_contains_author_year_not_in_source_map", "citations": sorted(used_citations - allowed_author_years)})

    report = {
        "docx": str(docx_path),
        "status": "pass" if not failures else "fail",
        "format": format_checks,
        "source_grounding": {
            "paragraphs_missing_lecture_anchor": paragraphs_missing_lecture_anchor,
            "green_runs_missing_citation": green_runs_missing_citation,
            "yellow_runs_missing_extra_reading_anchor": yellow_runs_missing_extra_reading_anchor,
            "green_runs_missing_read_original_source": green_runs_missing_read_source,
            "micro_detail_failures": micro_detail_failures,
            "public_preamble_leaks": public_preamble_leaks,
            "extra_reading_ratio": round(extra_reading_ratio, 4),
            "total_body_words": total_body_words,
            "yellow_words": yellow_words,
            "green_words": green_words,
        },
        "qa_flags": [failure["type"] for failure in failures],
        "failures": failures,
        "warnings": warnings,
    }
    return report


def collect_docx(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.glob("*.docx"))
    return [path]



def create_bad_docx(path: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    p = doc.add_paragraph("This essay will discuss a source route without grounding.")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    run = p.runs[0]
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    doc.save(path)


def self_test() -> dict[str, Any]:
    import tempfile
    try:
        from generate_example_essay_docx import inline_positive_essay, write_essay
    except Exception as exc:  # pragma: no cover
        return {"pass": False, "failures": [{"type": "generator_import_failed", "error": str(exc)}]}
    with tempfile.TemporaryDirectory(prefix="docx_format_linter_selftest_") as tmp:
        root = Path(tmp)
        out = root / "out"
        qa = root / "qa"
        out.mkdir()
        qa.mkdir()
        good_doc = write_essay(inline_positive_essay(), out, qa, 1)
        good_result = lint_docx(Path(good_doc["docx_path"]), Path(good_doc["source_map"]))
        bad = root / "bad.docx"
        create_bad_docx(bad)
        bad_result = lint_docx(bad, None)
    failures = []
    if good_result.get("status") != "pass":
        failures.append({"type": "good_inline_docx_rejected", "result": good_result})
    if bad_result.get("status") == "pass":
        failures.append({"type": "bad_inline_docx_accepted", "result": bad_result})
    return {"pass": not failures, "good": good_result, "bad": bad_result, "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description="Lint Example Essay DOCX formatting and source highlighting.")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source-map", type=Path)
    parser.add_argument("--check-language", action="store_true", help="Also run the complete Example Essay language linter.")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    if not args.paths:
        print(json.dumps({"status": "fail", "reports": [{"qa_flags": ["missing_paths_or_self_test"]}]}, indent=2))
        return 1

    reports = []
    for path in args.paths:
        for docx_path in collect_docx(path):
            try:
                report = lint_docx(docx_path, args.source_map)
                if args.check_language:
                    if lint_language_records is None or load_docx_records is None:
                        report["status"] = "fail"
                        report.setdefault("qa_flags", []).append("example_essay_language_linter_unavailable")
                        report["language"] = {"pass": False, "fail_reasons": ["example_essay_language_linter_unavailable"]}
                    else:
                        language_report = lint_language_records(load_docx_records(docx_path))
                        report["language"] = language_report
                        if not language_report.get("pass"):
                            report["status"] = "fail"
                            report.setdefault("qa_flags", []).append("example_essay_language_lint_failed")
                reports.append(report)
            except Exception as exc:
                reports.append({"docx": str(docx_path), "status": "fail", "qa_flags": ["docx_lint_error"], "error": str(exc)})

    result = {
        "status": "pass" if all(report.get("status") == "pass" for report in reports) else "fail",
        "reports": reports,
    }
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
