from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

BASE_ROLES = {"lecture_slides", "lecture_notes", "official_course_notes"}
PRACTICE_ROLES = {"past_paper", "mark_scheme", "answer_key", "practical_material", "data_problem_material"}


def route_scopes(source_scan: dict[str, Any], route: str) -> dict[str, str]:
    return {
        str(decision.get("source_id")): str(decision.get("evidence_scope"))
        for decision in source_scan.get("source_decisions", [])
        if decision.get("route") == route
    }


def check_readiness(route: str, source_scan: dict[str, Any]) -> dict[str, Any]:
    roles = set(source_scan.get("source_roles") or [d.get("role") for d in source_scan.get("documents", [])])
    notes_scopes = route_scopes(source_scan, "exam_prep_notes")
    blocks = []
    warnings = []
    if notes_scopes:
        has_course_baseline = "factual_course_content" in set(notes_scopes.values())
    else:
        has_course_baseline = bool(roles.intersection(BASE_ROLES))
    if route in {"exam_prep_notes", "mcq_addon", "short_answer_addon", "long_answer_practical_addon", "essay_addon"} and not has_course_baseline:
        blocks.append({"component": "course_source_baseline", "missing": sorted(BASE_ROLES)})
    if route in {"mcq_addon", "short_answer_addon", "long_answer_practical_addon", "essay_addon"} and "past_paper" not in roles:
        warnings.append({"component": "exam_mode_emphasis", "missing": ["past_paper"], "effect": "mode can use prompt only"})
    if route == "long_answer_practical_addon" and not roles.intersection({"practical_material", "data_problem_material"}):
        blocks.append({"component": "practical_data_addon", "missing": ["practical_material", "data_problem_material"]})
    return {"status": "block" if blocks else "pass", "blocked_components": blocks, "warnings": warnings}


def self_test() -> int:
    scan = {"source_roles": ["lecture_notes"]}
    assert check_readiness("exam_prep_notes", scan)["status"] == "pass"
    assert check_readiness("long_answer_practical_addon", scan)["status"] == "block"
    scoped = {
        "source_roles": ["lecture_notes"],
        "source_decisions": [{"source_id": "S1", "route": "exam_prep_notes", "evidence_scope": "style_only"}],
    }
    assert check_readiness("exam_prep_notes", scoped)["status"] == "block"
    print("input_readiness_check self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", default="exam_prep_notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.source_scan:
        parser.error("--source-scan is required")
    scan = json.loads(Path(args.source_scan).read_text(encoding="utf-8"))
    out = check_readiness(args.route, scan)
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
