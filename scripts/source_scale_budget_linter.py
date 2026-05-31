#!/usr/bin/env python3
"""Check that notes plans and generated DOCX outputs are not under-sized for the source scale.

The check is deliberately conservative. It does not reward padding. It only blocks
obvious failures where a broad source pack is collapsed into a small practical-style
summary without enough examinable knowledge units or visible words.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None  # type: ignore

from source_scale_budget_rules import (
    floor_for_source_scale,
    infer_source_units,
    required_floor_with_declared_budget,
    source_scale_budget,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_words(text: str) -> int:
    return len([token for token in text.replace("\n", " ").split(" ") if token.strip()])


def docx_text(path: Path) -> str:
    if Document is None:
        raise RuntimeError("python-docx is required to inspect DOCX files")
    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())


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


def declared_budget_floor(plan: dict[str, Any]) -> tuple[int | None, int | None, str | None]:
    budget = source_scale_budget(plan)
    if not budget:
        return None, None, "missing_source_scale_budget"
    floor = required_floor_with_declared_budget(plan)
    return int(floor["minimum_public_units"]), int(floor["minimum_visible_words"]), None


def lint_plan(plan: dict[str, Any], *, docx_path: Path | None = None) -> dict[str, Any]:
    source_units = infer_source_units(plan)
    public_units = count_public_units(plan)
    declared_units, declared_words, budget_failure = declared_budget_floor(plan)
    scale_floor = floor_for_source_scale(plan)
    min_units = declared_units if declared_units is not None else int(scale_floor["minimum_public_units"])
    min_words = declared_words if declared_words is not None else int(scale_floor["minimum_visible_words"])
    failures: list[dict[str, Any]] = []
    if budget_failure:
        failures.append({"type": budget_failure})
    budget = source_scale_budget(plan)
    if isinstance(budget, dict):
        target_units = budget.get("target_public_units_min")
        target_words = budget.get("target_words_min")
        if isinstance(target_units, int) and target_units < int(scale_floor["minimum_public_units"]):
            failures.append(
                {
                    "type": "target_public_units_min_below_source_scale_floor",
                    "declared_target_public_units_min": target_units,
                    "minimum_public_units": int(scale_floor["minimum_public_units"]),
                }
            )
        if isinstance(target_words, int) and target_words < int(scale_floor["minimum_visible_words"]):
            failures.append(
                {
                    "type": "target_words_min_below_source_scale_floor",
                    "declared_target_words_min": target_words,
                    "minimum_visible_words": int(scale_floor["minimum_visible_words"]),
                }
            )
    if isinstance(budget, dict) and budget.get("coverage_floor_status") == "block":
        failures.append({"type": "coverage_floor_status_blocks_release"})
    has_source_scale = any(
        int(scale_floor[key]) > 0
        for key in ["source_units", "source_pages_or_slides_estimate", "protected_knowledge_units_total"]
    )
    if has_source_scale and public_units < min_units:
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
        if has_source_scale and visible_words < min_words:
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
        "source_pages_or_slides_estimate": scale_floor["source_pages_or_slides_estimate"],
        "protected_knowledge_units_total": scale_floor["protected_knowledge_units_total"],
        "scale_band": scale_floor["scale_band"],
        "public_units": public_units,
        "minimum_public_units": min_units,
        "visible_words": visible_words,
        "minimum_visible_words": min_words,
        "failures": failures,
    }


def self_test() -> dict[str, Any]:
    bad_plan = {
        "source_scale_budget": {
            "source_units_count": 22,
            "source_pages_or_slides_estimate": 867,
            "target_public_units_min": 70,
            "target_words_min": 8000,
        },
        "course_modules": [
            {
                "module_title": "Broad course compressed too far",
                "module_function": "Broad course compressed too far.",
                "source_lectures": [f"Lecture {idx}" for idx in range(1, 23)],
                "examinable_units": [
                    {"title": f"Unit {idx}", "explanation": "Short."} for idx in range(1, 81)
                ],
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
