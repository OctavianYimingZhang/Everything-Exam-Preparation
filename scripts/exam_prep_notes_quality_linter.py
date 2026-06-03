from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

FILLER = ["it is important to note", "this means that", "in conclusion", "the source states", "the course frames", "the lecture material"]
FORBIDDEN_SURFACE_PATTERNS = [
    r"\bThe central relationship is that\b",
    r"because it changes how development evidence is selected, interpreted or used",
    r"\bBoundary note\s*:",
    r"\bThe main limitation is this\b",
    r"\bMethod/readout\s*:",
    r"\bThe method readout is this\b",
    r"\bDiagnostic pattern\s*:",
    r"\bThe graph-data interpretation is this\b",
    r"\bWorked example\s*:\s*The calculation step is this\b",
    r"This worked calculation illustrates how the numeric output changes interpretation",
    r"This example illustrates the module boundary",
    r"These named terms illustrate how the same principle changes the development decision",
    r"The consequence matters because it changes the next development decision",
    r"Treat each listed item as a separate evidence check",
    r"Link each item to efficacy, safety, pharmacokinetics, formulation, quality or authorisation",
]
GENERIC_LABELS = [
    "comparison",
    "example",
    "boundary note",
    "method/readout",
    "diagnostic pattern",
    "worked example",
]
PRACTICAL_TERMS = ["method", "control", "limitation", "calculate", "graph", "table", "readout"]
LISTABLE_REASONS = {
    "source_numbered_list",
    "source_bulleted_list",
    "past_paper_list_question",
    "criteria_set",
    "taxonomy_or_contrast",
    "short_answer_mark_points",
    "definition_group",
}
LIST_RENDER_MODES = {"kp_list", "compact_table", "image_plus_kp_list"}


def sentence_frame(sentence: str) -> str | None:
    words = re.findall(r"[A-Za-z]+", sentence.lower())
    if len(words) < 8:
        return None
    return " ".join(words[:7])


def repeated_sentence_frames(text: str) -> list[dict[str, Any]]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    counts: dict[str, int] = {}
    for sentence in sentences:
        frame = sentence_frame(sentence)
        if frame:
            counts[frame] = counts.get(frame, 0) + 1
    threshold = max(3, len(sentences) // 8)
    return [{"frame": frame, "count": count} for frame, count in sorted(counts.items()) if count > threshold]


def read_docx_surface(path: Path) -> tuple[str, int, int]:
    with zipfile.ZipFile(path) as zf:
        raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        media_count = sum(1 for name in zf.namelist() if name.startswith("word/media/"))
        table_count = raw.count("<w:tbl")
    return html.unescape("\n".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw))), media_count, table_count


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        return read_docx_surface(path)[0]
    return path.read_text(encoding="utf-8", errors="ignore")


def iter_blocks(plan: dict[str, Any]):
    for section in plan.get("sections", []) or []:
        for block in section.get("blocks", []) or []:
            if isinstance(block, dict):
                yield block


def lint_plan(plan: dict[str, Any], docx_media_count: int = 0, docx_table_count: int = 0) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for block in iter_blocks(plan):
        block_id = block.get("block_id")
        reason = block.get("listability_reason")
        mode = block.get("render_mode")
        if reason in LISTABLE_REASONS and mode not in LIST_RENDER_MODES:
            failures.append({
                "check": "listable_content_not_rendered_as_list_or_table",
                "block_id": block_id,
                "reason": reason,
                "render_mode": mode,
            })
        if mode in {"kp_list", "image_plus_kp_list"}:
            for point in block.get("points", []) or []:
                if not isinstance(point, dict):
                    failures.append({"check": "legacy_string_point", "block_id": block_id})
                    continue
                if len(re.findall(r"\w+", str(point.get("explanation", "")))) < 5:
                    failures.append({
                        "check": "bullet_points_are_labels_without_explanation",
                        "block_id": block_id,
                        "label": point.get("label"),
                    })
        if mode == "image_plus_kp_list" and docx_media_count == 0:
            failures.append({"check": "image_plus_kp_list_has_no_embedded_image", "block_id": block_id})
        if mode == "compact_table" and docx_table_count == 0:
            failures.append({"check": "compact_table_has_no_docx_table", "block_id": block_id})
    visual_decisions = plan.get("visual_decisions") or {}
    if (
        plan.get("visual_policy") == "auto_source_visuals"
        and int(visual_decisions.get("candidate_count") or 0) > 0
        and int(visual_decisions.get("selected_count") or 0) == 0
        and not visual_decisions.get("rejected_visuals")
    ):
        failures.append({"check": "source_visual_candidates_unresolved"})
    if int(visual_decisions.get("selected_count") or 0) > 0 and docx_media_count == 0:
        failures.append({"check": "plan_requires_visual_but_docx_has_no_media"})
    return failures


def lint_text(text: str, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    failures = []
    warnings = []
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
    long_paragraphs = [p[:80] for p in paragraphs if len(p.split()) > 140]
    if long_paragraphs:
        failures.append({"check": "paragraph_length", "examples": long_paragraphs[:3]})
    filler_hits = [phrase for phrase in FILLER if phrase in text.lower()]
    if filler_hits:
        failures.append({"check": "filler_phrases", "phrases": filler_hits})
    surface_hits = []
    for pattern in FORBIDDEN_SURFACE_PATTERNS:
        hits = re.findall(pattern, text, flags=re.I)
        if hits:
            surface_hits.append({"pattern": pattern, "count": len(hits)})
    if surface_hits:
        failures.append({"check": "forbidden_internal_surface_templates", "patterns": surface_hits})
    repeated_frames = repeated_sentence_frames(text)
    if repeated_frames:
        failures.append({"check": "repeated_generic_sentence_frame", "frames": repeated_frames[:5]})
    label_hits = []
    for label in GENERIC_LABELS:
        label_hits.extend(re.findall(rf"(?im)^\s*{re.escape(label)}\s*:", text))
    word_count = len(re.findall(r"\w+", text))
    if len(label_hits) > max(4, word_count // 700):
        failures.append({"check": "generic_colon_label_overuse", "count": len(label_hits)})
    heading_like = [p for p in paragraphs if len(p.split()) <= 8 and not p.startswith("- ")]
    explanatory = [p for p in paragraphs if len(p.split()) > 12]
    if heading_like and len(heading_like) > max(4, len(explanatory) * 2):
        failures.append({"check": "headings_outnumber_explanation"})
    if len(re.findall(r"source|slide|document", text, flags=re.I)) > max(8, len(paragraphs) // 2):
        failures.append({"check": "source_summary_surface"})
    if plan:
        roles = set(plan.get("source_roles", []))
        if roles.intersection({"practical_material", "data_problem_material"}) and not any(t in text.lower() for t in PRACTICAL_TERMS):
            failures.append({"check": "practical_data_material_ignored"})
    return {"status": "fail" if failures else "pass", "failures": failures, "warnings": warnings}


def self_test() -> int:
    result = lint_text("Enzyme rate\nInitial slope estimates early reaction rate before substrate depletion and supports graph interpretation.\n- Axes define the measured readout.")
    assert result["status"] == "pass"
    bad = lint_text("Heading\n" + "word " * 160)
    assert bad["status"] == "fail"
    templated = lint_text(
        "The central relationship is that EC50 matters because it changes how development evidence is selected, interpreted or used.\n"
        "Boundary note: The main limitation is this: do not overinterpret."
    )
    assert templated["status"] == "fail"
    assert any(f["check"] == "forbidden_internal_surface_templates" for f in templated["failures"])
    repeated = lint_text(
        "Development decisions are affected by this topic because formulation changes exposure.\n"
        "Development decisions are affected by this topic because safety changes dose selection.\n"
        "Development decisions are affected by this topic because efficacy changes trial design.\n"
        "Development decisions are affected by this topic because quality changes release testing.\n"
        "Development decisions are affected by this topic because licensing changes evidence needs."
    )
    assert any(f["check"] == "repeated_generic_sentence_frame" for f in repeated["failures"])
    listable_paragraph = {
        "sections": [
            {
                "blocks": [
                    {
                        "block_id": "B_LIPINSKI",
                        "heading": "Lipinski Rule of 5",
                        "render_mode": "paragraph",
                        "listability_reason": "criteria_set",
                        "source_ids": ["S1"],
                        "paragraph": "Lipinski's rule covers donors, acceptors, mass and logP.",
                    }
                ]
            }
        ]
    }
    assert lint_plan(listable_paragraph)[0]["check"] == "listable_content_not_rendered_as_list_or_table"
    good_list = {
        "sections": [
            {
                "blocks": [
                    {
                        "block_id": "B_IN_VIVO",
                        "heading": "What only in vivo studies can do",
                        "render_mode": "kp_list",
                        "listability_reason": "source_numbered_list",
                        "source_ids": ["S1"],
                        "points": [
                            {
                                "label": "Whole-body effects",
                                "explanation": "Captures integrated physiology that isolated cells cannot reproduce.",
                            }
                        ],
                    }
                ]
            }
        ],
        "visual_policy": "user_requested_text_only",
        "visual_decisions": {"candidate_count": 0, "selected_count": 0, "user_requested_text_only": True},
    }
    assert lint_plan(good_list) == []
    print("exam_prep_notes_quality_linter self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--plan")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.input:
        parser.error("--input is required")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8")) if args.plan else None
    input_path = Path(args.input)
    if input_path.suffix.lower() == ".docx":
        text, media_count, table_count = read_docx_surface(input_path)
    else:
        text, media_count, table_count = read_text(input_path), 0, 0
    result = lint_text(text, plan)
    if plan:
        plan_failures = lint_plan(plan, media_count, table_count)
        result["failures"].extend(plan_failures)
        if plan_failures:
            result["status"] = "fail"
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
