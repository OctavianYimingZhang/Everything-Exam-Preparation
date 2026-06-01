#!/usr/bin/env python3
"""Lint public lecture notes for exam-ready direct prose."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None  # type: ignore


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")

SOURCE_NARRATION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "source_narration_course_frames",
        re.compile(r"\bthe\s+course\s+(?:frames?|begins?|introduces?|presents?|covers?|emphasises|emphasizes|uses)\b", re.I),
    ),
    (
        "source_narration_lecture_frames",
        re.compile(r"\bthe\s+(?:lecture|lectures|lecture\s+material|module)\s+(?:frames?|begins?|introduces?|presents?|covers?|emphasises|emphasizes|uses|states?)\b", re.I),
    ),
    (
        "source_narration_source_identifies",
        re.compile(r"\bthe\s+(?:source|sources|source\s+material|uploaded\s+material|material)\s+(?:identif(?:y|ies)|states?|says?|shows?|explains?|describes?|emphasises|emphasizes|uses)\b", re.I),
    ),
    (
        "source_route_claim",
        re.compile(r"\b(?:according\s+to|based\s+on|drawn\s+from|taken\s+from)\s+(?:the\s+)?(?:lecture|source|slides?|uploaded\s+material|course\s+material)\b", re.I),
    ),
]

META_PREAMBLE = re.compile(
    r"\b(?:source\s+scope|extraction\s+limitation|this\s+pack\s+uses|this\s+document\s+uses|"
    r"the\s+notes\s+are\s+organised|the\s+notes\s+are\s+organized|this\s+walkthrough\s+is\s+based\s+on)\b",
    re.I,
)

WEAK_PUBLIC_OPENERS = re.compile(
    r"^\s*(?:this\s+(?:section|module|lecture|part)\s+(?:explains|covers|introduces|shows)|"
    r"in\s+this\s+(?:section|module|lecture)|the\s+following\s+(?:section|module|notes))\b",
    re.I,
)

DIRECT_KNOWLEDGE_MARKERS = re.compile(
    r"\b(?:is|are|has|have|means|refers?\s+to|describes?|defines?|differs?|distinguishes|separates|links|"
    r"forms?|moves?|allows?|converts|controls|depends\s+on|requires|enables|limits|drives|produces|measures|calculates)\b",
    re.I,
)

ANALYTIC_MARKERS = re.compile(
    r"\b(?:because|by|through|therefore|so|whereas|although|while|thereby|as\s+a\s+result|consequently|"
    r"this\s+(?:means|shows|demonstrates|limits|explains|prevents)|matters\s+because|"
    r"distinguishes|rules?\s+out|supports|indicates|implies|enables|constrains|limits|prevents|changes?|combined)\b",
    re.I,
)

EXAMPLE_MARKERS = re.compile(r"\b(?:for\s+example|example|case\s+study|including|such\s+as)\b", re.I)
EXAMPLE_INTERPRETATION = re.compile(r"\b(?:shows|demonstrates|illustrate|illustrates|supports|indicates|implies|because|therefore|means\s+that)\b", re.I)
BROAD_IMPORTANCE = re.compile(r"\b(?:this\s+matters|this\s+is\s+important|this\s+is\s+critical|the\s+important\s+point)\b", re.I)
IMPORTANCE_WITH_CONSEQUENCE = re.compile(r"\b(?:because|therefore|so|means\s+that|limits|enables|prevents|explains|allows|requires)\b", re.I)
NEGATIVE_FRAMING = re.compile(r"\b(?:not\s+(?:only|merely|simply|just|a|an|the)|rather\s+than|not\s+.+?\s+but)\b", re.I)

INVENTORY_LINE = re.compile(
    r"\b(?:includes?|contains?|consists\s+of|covers?|involves?)\b[^.!?]{0,180}(?:,|;)[^.!?]{0,180}(?:,|;)",
    re.I,
)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def sentences(text: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(str(text).strip()) if match.group(0).strip()]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def docx_text(path: Path) -> str:
    if Document is None:
        raise RuntimeError("python-docx is required to inspect DOCX files")
    doc = Document(path)
    return "\n".join(paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip())


def iter_modules(plan: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    modules: list[tuple[str, dict[str, Any]]] = []
    for lecture_index, lecture in enumerate(plan.get("public_lecture_sections", []) or [], start=1):
        if not isinstance(lecture, dict):
            continue
        for module_index, module in enumerate(lecture.get("modules", []) or [], start=1):
            if isinstance(module, dict):
                modules.append((f"public_lecture_sections[{lecture_index}].modules[{module_index}]", module))
    return modules


def block_text(block: Any) -> str:
    if not isinstance(block, dict):
        return str(block or "")
    label = str(block.get("label") or "").strip()
    content = block.get("content")
    if isinstance(content, list):
        rendered = "; ".join(str(item).strip() for item in content if str(item).strip())
    else:
        rendered = str(content or "").strip()
    return f"{label}: {rendered}" if label and rendered else (label or rendered)


def module_text(module: dict[str, Any]) -> str:
    chunks = [
        str(module.get("module_title") or ""),
        str(module.get("explanation") or ""),
    ]
    chunks.extend(block_text(block) for block in module.get("blocks", []) or [])
    return "\n".join(chunk for chunk in chunks if chunk.strip())


def public_text(plan: dict[str, Any]) -> str:
    chunks = [str(plan.get("title") or "")]
    for lecture in plan.get("public_lecture_sections", []) or []:
        if not isinstance(lecture, dict):
            continue
        chunks.append(str(lecture.get("lecture_title") or ""))
        chunks.append(str(lecture.get("lecture_scope") or ""))
        for _, module in iter_modules({"public_lecture_sections": [lecture]}):
            chunks.append(module_text(module))
    return "\n".join(chunk for chunk in chunks if chunk.strip())


def lint_text(text: str) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for failure_type, pattern in SOURCE_NARRATION_PATTERNS:
        for match in pattern.finditer(text):
            failures.append({"type": failure_type, "text": match.group(0)[:120]})
    if META_PREAMBLE.search(text):
        failures.append({"type": "visible_source_or_extraction_preamble"})
    if WEAK_PUBLIC_OPENERS.search(text):
        failures.append({"type": "weak_public_opener", "text": text.strip()[:160]})
    if BROAD_IMPORTANCE.search(text) and not IMPORTANCE_WITH_CONSEQUENCE.search(text):
        failures.append({"type": "generic_importance_without_consequence"})
    negative_hits = NEGATIVE_FRAMING.findall(text)
    if len(negative_hits) >= 5:
        failures.append({"type": "excessive_negative_framing", "count": len(negative_hits)})
    return failures


def lint_plan(plan: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = lint_text(public_text(plan))
    for where, module in iter_modules(plan):
        title = str(module.get("module_title") or "").strip()
        explanation = str(module.get("explanation") or "").strip()
        text = module_text(module)
        first = sentences(explanation)[0] if sentences(explanation) else explanation
        for failure in lint_text(text):
            failures.append({**failure, "where": where, "module_title": title})
        if first and WEAK_PUBLIC_OPENERS.search(first):
            failures.append({"type": "module_opens_with_meta_commentary", "where": where, "module_title": title})
        if first and not DIRECT_KNOWLEDGE_MARKERS.search(first):
            failures.append({"type": "module_first_sentence_not_direct_knowledge_claim", "where": where, "module_title": title})
        if not ANALYTIC_MARKERS.search(text):
            failures.append({"type": "module_lacks_analytic_consequence_or_boundary", "where": where, "module_title": title})
        if EXAMPLE_MARKERS.search(text) and not EXAMPLE_INTERPRETATION.search(text):
            failures.append({"type": "orphan_example_without_interpretation", "where": where, "module_title": title})
        if INVENTORY_LINE.search(text) and not ANALYTIC_MARKERS.search(text):
            failures.append({"type": "inventory_only_list_without_teaching_function", "where": where, "module_title": title})
        if len(words(explanation)) < 35:
            failures.append({"type": "module_explanation_below_exam_ready_floor", "where": where, "module_title": title})
    return {"pass": not failures, "failures": failures}


def lint_docx(path: Path) -> dict[str, Any]:
    text = docx_text(path)
    failures = lint_text(text)
    return {"pass": not failures, "failures": failures}


def positive_plan() -> dict[str, Any]:
    return {
        "object_type": "PublicLectureNotesPlan",
        "title": "Lecture Knowledge Walkthrough",
        "target_group_key": "sample",
        "source_scale_budget": {
            "source_units_count": 1,
            "readable_source_blocks": 8,
            "protected_knowledge_units_total": 4,
            "excluded_non_knowledge_units_total": 0,
            "target_public_units_min": 2,
            "target_words_min": 100,
            "compression_mode": "explain_not_dump",
            "coverage_floor_status": "pass",
        },
        "output_language_profile": {"output_language": "English", "allow_bilingual": False},
        "route_docx_style_profile": {
            "route": "exam_prep_notes_docx",
            "margin_cm": 2.0,
            "line_spacing": 1.1,
            "body_alignment": "left",
            "title_alignment": "left",
            "heading_alignment": "left",
            "image_alignment": "center",
            "body_font_pt": 10.5,
            "text_color": "black",
            "theme_colours_allowed": False,
            "blue_heading_styles_allowed": False,
        },
        "public_lecture_sections": [
            {
                "lecture_title": "Lecture 1: Measurement logic",
                "modules": [
                    {
                        "module_title": "Wavelength-specific absorbance measures concentration",
                        "knowledge_functions": ["definition_boundary", "calculation_unit_worked_example", "limitation_trap"],
                        "explanation": "Absorbance is a wavelength-specific measurement of how much light a solute removes from a beam. It becomes useful for concentration estimates because the Beer-Lambert relationship links absorbance to path length, extinction coefficient and concentration, so a calibration or known coefficient can convert an optical signal into a quantitative value.",
                        "blocks": [
                            {
                                "block_type": "calculation",
                                "label": "Worked example",
                                "content": "Use A = epsilon c l, keep path length and units explicit, and interpret the result as concentration only within the linear range.",
                            },
                            {
                                "block_type": "limitation",
                                "content": "A high reading is not automatically valid because detector saturation, scattering or the wrong wavelength can break the proportional relationship.",
                            },
                        ],
                    },
                    {
                        "module_title": "Initial slope gives the initial reaction rate",
                        "knowledge_functions": ["method_readout", "graph_data_interpretation", "limitation_trap"],
                        "explanation": "The initial rate is the early linear change in product or substrate signal per unit time. It is used because substrate depletion, product inhibition and enzyme instability become stronger later in the trace, so the initial slope gives the least distorted estimate of enzyme velocity.",
                        "blocks": [
                            {
                                "block_type": "graph_data",
                                "content": "Read the gradient from the first linear section of the curve and avoid later curvature when calculating rate.",
                            }
                        ],
                    },
                ],
            }
        ],
    }


def self_test() -> dict[str, Any]:
    good = lint_plan(positive_plan())
    bad_plan = positive_plan()
    bad_plan["public_lecture_sections"][0]["modules"][0]["explanation"] = (
        "The course frames absorbance as a useful topic. The source material identifies Beer-Lambert, calibration, wavelength and concentration."
    )
    bad = lint_plan(bad_plan)
    inventory_plan = positive_plan()
    inventory_plan["public_lecture_sections"][0]["modules"][0]["explanation"] = (
        "The section includes wavelength, absorbance, path length, extinction coefficient, concentration, calibration and graphing."
    )
    inventory = lint_plan(inventory_plan)
    failures: list[dict[str, Any]] = []
    if not good["pass"]:
        failures.append({"type": "positive_plan_rejected", "result": good})
    if bad["pass"]:
        failures.append({"type": "source_narration_not_rejected", "result": bad})
    if inventory["pass"]:
        failures.append({"type": "inventory_plan_not_rejected", "result": inventory})
    return {"pass": not failures, "positive": good, "source_narration_negative": bad, "inventory_negative": inventory, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--docx", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    elif args.plan:
        result = lint_plan(load_json(args.plan))
    elif args.docx:
        result = lint_docx(args.docx)
    else:
        result = {"pass": False, "failures": [{"type": "missing_plan_docx_or_self_test"}]}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
