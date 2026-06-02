#!/usr/bin/env python3
"""Validate citation fallback artefacts for Example Essay mode."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any


def lint_dir(path: Path, require_classic_plan: bool = False) -> dict[str, Any]:
    failures: list[str] = []
    log_path = path / "citation_resolution_log.json"
    if not log_path.exists():
        failures.append("citation_resolution_log_missing")
    else:
        log = json.loads(log_path.read_text(encoding="utf-8"))
        if require_classic_plan and "lecture_slide_citation_absent_classic_experiment_search_required" not in log.get("qa_flags", []):
            failures.append("classic_experiment_fallback_flag_missing")

    plan_path = path / "classic_experiment_search_plan.json"
    if require_classic_plan:
        if not plan_path.exists():
            failures.append("classic_experiment_search_plan_missing")
        else:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            if plan.get("desired_verified_sources", 0) < 3:
                failures.append("classic_experiment_desired_count_too_low")
            if len(plan.get("academic_search_queries", [])) < 3:
                failures.append("classic_experiment_search_queries_missing")
            if len(plan.get("selection_standard", [])) < 4:
                failures.append("classic_experiment_selection_standard_missing")
    return {"pass": not failures, "failures": failures}


def self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="citation_fallback_selftest_") as tmp:
        root = Path(tmp)
        good = root / "good"
        bad = root / "bad"
        good.mkdir()
        bad.mkdir()
        (good / "citation_resolution_log.json").write_text(json.dumps({"qa_flags": ["lecture_slide_citation_absent_classic_experiment_search_required"]}), encoding="utf-8")
        (good / "classic_experiment_search_plan.json").write_text(json.dumps({
            "desired_verified_sources": 3,
            "academic_search_queries": ["classic experiment source", "replication study", "review source"],
            "selection_standard": ["primary source", "relevant method", "verified citation", "not lecture hearsay"],
        }), encoding="utf-8")
        (bad / "citation_resolution_log.json").write_text(json.dumps({"qa_flags": []}), encoding="utf-8")
        good_result = lint_dir(good, require_classic_plan=True)
        bad_result = lint_dir(bad, require_classic_plan=True)
    failures = []
    if not good_result["pass"]:
        failures.append({"type": "good_inline_case_rejected", "result": good_result})
    if bad_result["pass"]:
        failures.append({"type": "bad_inline_case_accepted", "result": bad_result})
    return {"pass": not failures, "good": good_result, "bad": bad_result, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check citation fallback output.")
    parser.add_argument("--dir", type=Path)
    parser.add_argument("--require-classic-plan", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
    elif args.dir:
        result = lint_dir(args.dir, require_classic_plan=args.require_classic_plan)
    else:
        result = {"pass": False, "failures": ["missing_dir_or_self_test"]}
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
