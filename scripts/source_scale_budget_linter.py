#!/usr/bin/env python3
"""Check that notes plans and generated DOCX outputs are not under-sized for the source scale.

The check is deliberately conservative. It does not reward padding. It only blocks
obvious failures where a broad source pack is collapsed into a small practical-style
summary without enough examinable knowledge units or visible words.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None  # type: ignore


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_words(text: str) -> int:
    return len([token for token in text.replace("\n", " ").split(" ") if token.strip()])


def docx_text(path: Path) -> str:
    if Document is None:
        raise RuntimeError("python-docx is required to inspect DOCX files")
    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())


def infer_source_units(plan: dict[str, Any]) -> int:
    budget = plan.get("source_scale_budget") or plan.get("SourceScaleBudget")
    if isinstance(budget, dict):
        for key in ["source_units_count", "readable_source_blocks", "protected_knowledge_units_total"]:
            value = budget.get(key)
            if isinstance(value, int) and value > 0:
                return value
    seen: set[str] = set()
    for module in plan.get("course_modules", []) or []:
        if not isinstance(module, dict):
            continue
        for source in module.get("source_lectures", []) or []:
            if str(source).strip():
                seen.add(str(source).strip())
    if seen:
        return len(seen)
    lecture_order = plan.get("lecture_order")
    if isinstance(lecture_order, list) and lecture_order:
        return len(lecture_order)
    lectures = plan.get("lectures") or plan.get("legacy_lectures")
    if isinstance(lectures, list) and lectures:
        return len(lectures)
    return 0


def count_public_units(plan: dict[str, Any]) -> int:
    count = 0
    for module in plan.get("course_modules", []) or []:
        if isinstance(module, dict):
            count += len([unit for unit in module.get("examinable_units", []) or [] if isinstance(unit, dict)])
    if count:
        return count
    for lecture in plan.get("lectures", []) or []:
        if isinstance(lecture, dict):
            count += len([module for module in lecture.get("modules", []) or [] if isinstance(module, dict)])
    return count


def floor_for_source_units(source_units: int) -> tuple[int, int]:
    if source_units <= 0:
        return (0, 0)
    if source_units <= 3:
        return (8, 1000)
    if source_units <= 8:
        return (20, 2500)
    if source_units <= 15:
        return (40, 4500)
    return (70, 8000)


def lint_plan(plan: dict[str, Any], *, docx_path: Path | None = None) -> dict[str, Any]:
    source_units = infer_source_units(plan)
    public_units = count_public_units(plan)
    min_units, min_words = floor_for_source_units(source_units)
    failures: list[dict[str, Any]] = []
    if source_units and public_units < min_units:
        failures.append(
            {
                "type": "coverage_floor_public_units_too_low",
                "source_units": source_units,
                "public_units": public_units,
                "minimum_public_units": min_units,
            }
        )
    visible_words = None
    if docx_path is not None:
        visible_words = count_words(docx_text(docx_path))
        if source_units and visible_words < min_words:
            failures.append(
                {
                    "type": "coverage_floor_visible_words_too_low",
                    "source_units": source_units,
                    "visible_words": visible_words,
                    "minimum_visible_words": min_words,
                }
            )
    return {
        "pass": not failures,
        "source_units": source_units,
        "public_units": public_units,
        "minimum_public_units": min_units,
        "visible_words": visible_words,
        "minimum_visible_words": min_words,
        "failures": failures,
    }


def self_test() -> dict[str, Any]:
    bad_plan = {
        "source_scale_budget": {"source_units_count": 18},
        "course_modules": [
            {
                "module_title": "Membrane excitability",
                "module_function": "Broad course compressed too far.",
                "source_lectures": [f"Module {idx}" for idx in range(1, 19)],
                "examinable_units": [{"title": f"Unit {idx}", "explanation": "Short."} for idx in range(1, 10)],
            }
        ],
    }
    good_plan = {
        "source_scale_budget": {"source_units_count": 4},
        "course_modules": [
            {
                "module_title": "Practical data handling",
                "module_function": "Focused practical pack.",
                "source_lectures": ["Practical 1", "Practical 2", "Mock", "Postlab"],
                "examinable_units": [
                    {"title": f"Unit {idx}", "explanation": "A connected explanation of the examinable idea."}
                    for idx in range(1, 24)
                ],
            }
        ],
    }
    bad = lint_plan(bad_plan)
    good = lint_plan(good_plan)
    failures: list[dict[str, Any]] = []
    if bad["pass"]:
        failures.append({"type": "bad_plan_not_rejected", "result": bad})
    if not good["pass"]:
        failures.append({"type": "good_plan_rejected", "result": good})
    return {"pass": not failures, "bad_result": bad, "good_result": good, "failures": failures}


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
        result = lint_plan(load_json(args.plan), docx_path=args.docx)
    else:
        result = {"pass": False, "failures": [{"type": "missing_plan_or_self_test"}]}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
