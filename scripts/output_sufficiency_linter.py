#!/usr/bin/env python3
"""Check public exam-prep outputs are large enough for the source pack.

This is the canonical output sufficiency checker. It consolidates source
information profiling, SourceScaleBudget rules, source-scale linting, and
optional reference-density comparison.

Student-output terms intentionally covered here: SourceScaleBudget,
coverage_floor, source_units_count, minimum_visible_coverage_floor.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_'/.-]*")
SCIENCE_SIGNAL_RE = re.compile(r"\b(gene|protein|enzyme|receptor|pathway|assay|cell|dose|trial|disease|method|graph|table|calculation)\b", re.I)
ADMIN_RE = re.compile(r"\b(lecture plan|outline|housekeeping|timetable|welcome|learning outcomes?)\b", re.I)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text or "")


def count_words(text: str) -> int:
    return len(words(text))


def positive_int(value: Any, default: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def positive_number(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def slide_number(path: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", path)
    return int(match.group(1)) if match else 0


def xml_text(root: ET.Element) -> str:
    return " ".join(node.text or "" for node in root.iter() if node.tag.endswith("}t") and node.text)


def classify_text_unit(text: str, visual_count: int = 0) -> tuple[bool, float, str]:
    word_count = count_words(text)
    if word_count == 0 and visual_count == 0:
        return False, 0.0, "empty"
    if word_count <= 80 and ADMIN_RE.search(text) and not SCIENCE_SIGNAL_RE.search(text):
        return False, 0.0, "admin_or_plan"
    score = min(2.0, word_count / 90.0) + min(1.2, visual_count * 0.3)
    if SCIENCE_SIGNAL_RE.search(text):
        score += 0.5
    return True, round(max(score, 0.25), 2), "teachable_source_content"


def profile_pptx(path: Path) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        slide_names = sorted([name for name in zf.namelist() if re.search(r"ppt/slides/slide\d+\.xml$", name)], key=slide_number)
        for name in slide_names:
            root = ET.fromstring(zf.read(name))
            text = xml_text(root)
            visual_count = sum(1 for node in root.iter() if node.tag.endswith("}pic") or node.tag.endswith("}graphicFrame"))
            informative, score, reason = classify_text_unit(text, visual_count)
            pages.append({
                "page_index": slide_number(name),
                "page_kind": "slide",
                "word_count": count_words(text),
                "visual_count": visual_count,
                "informative": informative,
                "information_score": score,
                "exclusion_reason": None if informative else reason,
            })
    return {"source_path": str(path), "source_type": "pptx", "pages": pages}


def profile_pdf(path: Path) -> dict[str, Any]:
    if PdfReader is None:
        return {"source_path": str(path), "source_type": "pdf", "pages": [], "error": "pdf_reader_unavailable"}
    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        informative, score, reason = classify_text_unit(text)
        pages.append({
            "page_index": index,
            "page_kind": "page",
            "word_count": count_words(text),
            "informative": informative,
            "information_score": score,
            "exclusion_reason": None if informative else reason,
        })
    return {"source_path": str(path), "source_type": "pdf", "pages": pages}


def profile_text(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()] or [text]
    pages = []
    for index, chunk in enumerate(chunks, start=1):
        informative, score, reason = classify_text_unit(chunk)
        pages.append({
            "page_index": index,
            "page_kind": "text_block",
            "word_count": count_words(chunk),
            "informative": informative,
            "information_score": score,
            "exclusion_reason": None if informative else reason,
        })
    return {"source_path": str(path), "source_type": "text", "pages": pages}


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())
        else:
            files.append(path)
    return sorted(files, key=lambda item: str(item).lower())


def profile_path(path: Path) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for file_path in iter_files([path]):
        suffix = file_path.suffix.lower()
        try:
            if suffix in {".pptx", ".pptm"} or zipfile.is_zipfile(file_path):
                profiles.append(profile_pptx(file_path))
            elif suffix == ".pdf":
                profiles.append(profile_pdf(file_path))
            elif suffix in {".txt", ".md", ".markdown"}:
                profiles.append(profile_text(file_path))
        except Exception as exc:
            profiles.append({"source_path": str(file_path), "source_type": suffix.lstrip("."), "pages": [], "error": str(exc)})
    return profiles


def summarize_profiles(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    pages = [page for profile in profiles for page in profile.get("pages", [])]
    informative = [page for page in pages if page.get("informative")]
    mass = round(sum(float(page.get("information_score") or 0) for page in informative), 2)
    return {
        "source_files_profiled": len([profile for profile in profiles if profile.get("pages")]),
        "raw_pages_or_slides": len(pages),
        "informative_page_count": len(informative),
        "non_informative_page_count": len(pages) - len(informative),
        "information_mass_units": mass,
        "profile_status": "measured" if pages else "missing_readable_pages",
    }


def floor_for_source_scale(source_scale_budget: dict[str, Any] | None = None, **overrides: Any) -> dict[str, int | str]:
    budget = dict(source_scale_budget or {})
    budget.update({key: value for key, value in overrides.items() if value is not None})
    source_units = positive_int(budget.get("source_units_count"), 0)
    informative_pages = positive_int(budget.get("informative_page_count"), 0)
    information_mass = positive_number(budget.get("information_mass_units"), 0.0)
    protected_units = positive_int(budget.get("protected_knowledge_units_total"), 0)

    scale_basis = max(source_units * 5, informative_pages // 2, int(information_mass // 3), protected_units)
    if scale_basis <= 0:
        scale_basis = 8
    minimum_public_units = max(8, scale_basis)
    minimum_visible_words = max(420, minimum_public_units * 130)
    if minimum_public_units >= 120:
        band = "broad_information_mass"
    elif minimum_public_units >= 40:
        band = "large"
    elif minimum_public_units >= 16:
        band = "standard"
    else:
        band = "compact"
    return {
        "scale_band": band,
        "minimum_public_units": minimum_public_units,
        "minimum_visible_words": minimum_visible_words,
        "minimum_visible_coverage_floor": minimum_public_units,
    }


def docx_text(path: Path) -> str:
    if Document is None:
        raise RuntimeError("python-docx unavailable")
    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())


def docx_metrics(path: Path) -> dict[str, Any]:
    text = docx_text(path)
    paragraphs = [part for part in text.splitlines() if part.strip()]
    return {"path": str(path), "paragraphs": len(paragraphs), "visible_words": count_words(text)}


def count_public_units(plan: dict[str, Any]) -> int:
    count = 0
    for lecture in plan.get("public_lecture_sections", []) or []:
        if isinstance(lecture, dict):
            count += len([module for module in lecture.get("modules", []) or [] if isinstance(module, dict)])
    return count


def visible_text_from_plan(plan: dict[str, Any]) -> str:
    parts: list[str] = []
    for lecture in plan.get("public_lecture_sections", []) or []:
        if not isinstance(lecture, dict):
            continue
        parts.append(str(lecture.get("lecture_title") or ""))
        for module in lecture.get("modules", []) or []:
            if not isinstance(module, dict):
                continue
            parts.append(str(module.get("module_title") or ""))
            parts.append(str(module.get("explanation") or ""))
            for block in module.get("blocks", []) or []:
                if isinstance(block, dict):
                    parts.append(str(block.get("content") or ""))
    return "\n".join(parts)


def lint_plan(plan: dict[str, Any], docx_path: Path | None = None, reference_docx: Path | None = None) -> dict[str, Any]:
    budget = plan.get("source_scale_budget") or {}
    floor = floor_for_source_scale(budget)
    public_units = count_public_units(plan)
    visible_words = count_words(docx_text(docx_path)) if docx_path else count_words(visible_text_from_plan(plan))
    failures: list[dict[str, Any]] = []
    if public_units < int(floor["minimum_public_units"]):
        failures.append({"type": "public_units_below_source_scale_floor", "public_units": public_units, "minimum_public_units": floor["minimum_public_units"]})
    if visible_words < int(floor["minimum_visible_words"]):
        failures.append({"type": "visible_words_below_source_scale_floor", "visible_words": visible_words, "minimum_visible_words": floor["minimum_visible_words"]})
    reference = None
    if reference_docx:
        target = docx_metrics(docx_path) if docx_path else {"visible_words": visible_words, "paragraphs": public_units}
        reference = docx_metrics(reference_docx)
        if target["visible_words"] < reference["visible_words"]:
            failures.append({"type": "visible_words_below_reference", "visible_words": target["visible_words"], "reference_visible_words": reference["visible_words"]})
    return {"pass": not failures, "floor": floor, "public_units": public_units, "visible_words": visible_words, "reference": reference, "failures": failures}


def self_test() -> dict[str, Any]:
    good_plan = {
        "source_scale_budget": {"source_units_count": 2, "informative_page_count": 4, "information_mass_units": 5},
        "public_lecture_sections": [{"modules": [{"module_title": f"Module {i}", "explanation": "Enzyme kinetics connects substrate binding to measurable reaction rate because catalytic turnover depends on active-site occupancy and reaction conditions."} for i in range(12)]}],
    }
    bad_plan = {"source_scale_budget": {"source_units_count": 20, "informative_page_count": 120, "information_mass_units": 180}, "public_lecture_sections": [{"modules": [{"module_title": "Thin", "explanation": "Too short."}]}]}
    with tempfile.TemporaryDirectory(prefix="output_sufficiency_") as tmp:
        source = Path(tmp) / "source.txt"
        source.write_text("Enzyme assay mechanism and graph interpretation.\n\nHousekeeping timetable.", encoding="utf-8")
        profile = summarize_profiles(profile_path(source))
    good = lint_plan(good_plan)
    bad = lint_plan(bad_plan)
    failures = []
    if profile["informative_page_count"] != 1:
        failures.append({"type": "profile_wrong", "profile": profile})
    if not good["pass"]:
        failures.append({"type": "good_plan_rejected", "result": good})
    if bad["pass"]:
        failures.append({"type": "bad_plan_accepted", "result": bad})
    return {"pass": not failures, "profile": profile, "good": good, "bad": bad, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", type=Path, default=[])
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--docx", type=Path)
    parser.add_argument("--reference-docx", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
    elif args.source and not args.plan:
        profiles = [profile for path in args.source for profile in profile_path(path)]
        result = {"pass": True, "summary": summarize_profiles(profiles), "profiles": profiles}
    elif args.plan:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
        result = lint_plan(plan, args.docx, args.reference_docx)
    else:
        result = {"pass": False, "failures": [{"type": "missing_source_plan_or_self_test"}]}

    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
