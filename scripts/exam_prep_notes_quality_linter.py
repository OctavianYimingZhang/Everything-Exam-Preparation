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


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        return html.unescape("\n".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw)))
    return path.read_text(encoding="utf-8", errors="ignore")


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
    result = lint_text(read_text(Path(args.input)), plan)
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
