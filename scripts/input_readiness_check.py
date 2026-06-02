#!/usr/bin/env python3
"""Report whether a SkillConfig has the source classes required by its preset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from plan_workflow import PRESET_REQUIRED_CLASSES, available_source_classes, blocker_for_missing, load_json, missing_required_classes, modules_for_preset, normalize_preset


VISUAL_AFFECTED_PRESETS = {
    "exam_prep_notes_docx",
    "knowledge_walkthrough_docx",
    "mcq_exam_prep",
    "short_answer_exam_prep",
    "long_answer_project_scenario_prep",
    "essay_exam_prep",
}


def visual_warning_sources(source_scan: dict[str, Any] | None) -> list[str]:
    if not source_scan:
        return []
    sources = []
    for item in source_scan.get("files", []):
        if not isinstance(item, dict):
            continue
        limitations = item.get("limitations") if isinstance(item.get("limitations"), list) else []
        visual_required = bool(item.get("visual_inspection_required")) or "visual_inspection_required" in limitations
        visual_status = str(item.get("visual_inspection_status") or "")
        if visual_required or visual_status.startswith(("required", "recommended")):
            sources.append(str(item.get("name") or item.get("path") or "unknown_source"))
    return sources


def build_report(config: dict[str, Any], source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    output_mode = config.get("output_mode", {})
    selected_preset = normalize_preset(str(output_mode.get("preset") or "exam_prep_notes_docx"))
    required = PRESET_REQUIRED_CLASSES[selected_preset]
    available = available_source_classes(config, source_scan)
    missing = missing_required_classes(required, available)
    modules = modules_for_preset(selected_preset, available, config, source_scan)
    blockers = [blocker_for_missing(index, item, selected_preset, modules) for index, item in enumerate(missing, start=1)]
    warnings: list[dict[str, Any]] = []

    source_inputs = config.get("source_inputs", {})
    source_policy = config.get("source_policy", {})
    if not source_inputs.get("extra_reading_books_or_papers") and source_policy.get("allow_online_academic_search"):
        warnings.append(
            {
                "warning_id": "warn_online_reading_needed",
                "severity": "info",
                "message": "No supplied extra reading was listed; online academic search may be needed only for directly relevant enrichment.",
            }
        )
    if source_inputs.get("exemplars_or_feedback") and not source_policy.get("treat_examples_as_style_only", True):
        warnings.append(
            {
                "warning_id": "warn_example_policy",
                "severity": "warning",
                "message": "Examples or feedback should be style/workflow evidence only unless independently verified from target sources.",
            }
        )
    visual_sources = visual_warning_sources(source_scan)
    if selected_preset in VISUAL_AFFECTED_PRESETS and visual_sources:
        warnings.append(
            {
                "warning_id": "warn_visual_inspection_needed",
                "severity": "warning",
                "message": "Some sources contain image, diagram, table, figure, or presentation content that may need visual inspection before claims are made.",
                "sources": visual_sources,
            }
        )

    project = config.get("project", {})
    return {
        "report_id": f"input_readiness_{selected_preset}",
        "selected_preset": selected_preset,
        "target_group_key": str(project.get("target_group_key") or "unspecified_target"),
        "required_source_classes": required,
        "available_source_classes": sorted(available),
        "missing_required": missing,
        "blockers": blockers,
        "warnings": warnings,
        "can_run": not blockers,
    }



def self_test() -> dict[str, Any]:
    lecture_scan = {"files": [{"role": "lecture_slide", "status": "ok", "visual_inspection_required": True, "name": "inline lecture source"}]}
    ready_config = {
        "project": {"target_group_key": "inline_self_test"},
        "source_inputs": {"lecture_slides": ["inline lecture source"]},
        "output_mode": {"preset": "essay_exam_prep"},
        "source_policy": {"treat_examples_as_style_only": True},
    }
    missing_config = {
        "project": {"target_group_key": "inline_self_test"},
        "source_inputs": {"formal_past_papers": ["inline paper source"]},
        "output_mode": {"preset": "essay_exam_prep"},
    }
    ready = build_report(ready_config, lecture_scan)
    missing = build_report(missing_config, {"files": [{"role": "formal_past_paper", "status": "ok"}]})
    cases = [
        {"name": "ready_essay_route", "passed": ready["can_run"] and ready["selected_preset"] == "essay_exam_prep"},
        {"name": "visual_warning_inline", "passed": any(item.get("warning_id") == "warn_visual_inspection_needed" for item in ready.get("warnings", []))},
        {"name": "missing_lecture_blocks", "passed": not missing["can_run"] and "lecture_or_official_notes" in missing["missing_required"]},
    ]
    failures = [case for case in cases if not case["passed"]]
    return {"pass": not failures, "cases": cases, "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--source-scan", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-on-blockers", action="store_true")
    parser.add_argument("--require-warning-id", action="append", default=[])
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    if not args.config:
        print(json.dumps({"status": "fail", "error": "missing_config_or_self_test"}, indent=2), file=sys.stderr)
        return 1

    try:
        config = load_json(args.config)
        source_scan = load_json(args.source_scan) if args.source_scan else None
        report = build_report(config, source_scan)
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    warning_ids = {warning.get("warning_id") for warning in report.get("warnings", [])}
    missing_warnings = [warning_id for warning_id in args.require_warning_id if warning_id not in warning_ids]
    if missing_warnings:
        print(json.dumps({"status": "fail", "missing_warning_ids": missing_warnings}, indent=2), file=sys.stderr)
        return 1
    if args.fail_on_blockers and report["blockers"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
