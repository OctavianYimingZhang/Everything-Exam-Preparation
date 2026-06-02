#!/usr/bin/env python3
"""Runtime audit utilities for optional internal audit packages."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_MANIFEST_KEYS = {"run_id", "task_type", "sources", "outputs"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def lint_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    failures = []
    missing = sorted(REQUIRED_MANIFEST_KEYS - set(manifest))
    if missing:
        failures.append({"type": "manifest_missing_keys", "missing": missing})
    for index, source in enumerate(manifest.get("sources", []), start=1):
        if not source.get("id") or not source.get("role"):
            failures.append({"type": "source_missing_id_or_role", "index": index})
    return {"pass": not failures, "failures": failures}


def lineage_report(manifest: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "run_id": manifest.get("run_id"),
        "request_scope": manifest.get("request_scope"),
        "source_count": len(manifest.get("source_hashes", {})) or len(manifest.get("sources", [])),
        "artifact_count": len(manifest.get("artifacts", [])) or len(manifest.get("outputs", [])),
        "lineage_event_count": len(events),
        "action_counts": dict(Counter(str(event.get("action_type", "unknown")) for event in events)),
        "status_counts": dict(Counter(str(event.get("status", "unknown")) for event in events)),
        "qa_summary": manifest.get("qa_summary", {}),
    }


def run_status(plan: dict[str, Any]) -> dict[str, Any]:
    actions = plan.get("actions", []) or []
    blockers = plan.get("blockers", []) or []
    return {
        "plan_id": plan.get("plan_id"),
        "selected_preset": plan.get("selected_preset"),
        "target_group_key": plan.get("target_group_key"),
        "action_count": len(actions),
        "blocker_count": len(blockers),
        "status": "blocked" if blockers else "ready",
        "next_actions": [action.get("module") for action in actions[:5]],
    }


def render_plan(plan: dict[str, Any]) -> str:
    lines = [f"# WorkflowPlan: {plan.get('plan_id', 'unknown')}", "", f"Preset: {plan.get('selected_preset')}", f"Target: {plan.get('target_group_key')}", "", "## Actions"]
    for action in plan.get("actions", []) or []:
        lines.append(f"- {action.get('module')}: {action.get('action_type')}")
    if plan.get("blockers"):
        lines.extend(["", "## Blockers"])
        for blocker in plan.get("blockers", []) or []:
            lines.append(f"- {blocker.get('missing_input') or blocker.get('message') or blocker}")
    return "\n".join(lines) + "\n"


def gap_report(paths: list[Path]) -> dict[str, Any]:
    gaps = []
    for path in paths:
        try:
            payload = load_json(path)
        except Exception as exc:
            gaps.append({"path": str(path), "status": "read_error", "error": str(exc)})
            continue
        status = "pass" if payload.get("pass") is True or payload.get("status") in {"pass", "ok"} else "gap"
        gaps.append({"path": str(path), "status": status, "failures": payload.get("failures") or payload.get("qa_flags") or []})
    return {"pass": all(item["status"] == "pass" for item in gaps), "gaps": gaps}


def self_test() -> dict[str, Any]:
    manifest = {"run_id": "R1", "task_type": "exam_prep", "sources": [{"id": "s1", "role": "lecture"}], "outputs": [{"path": "Lecture_Knowledge_Walkthrough.docx"}]}
    bad_manifest = {"run_id": "R2", "sources": [{}]}
    events = [{"action_type": "source_inventory", "status": "pass"}, {"action_type": "render", "status": "pass"}]
    plan = {"plan_id": "P1", "selected_preset": "exam_prep_notes_docx", "target_group_key": "T", "actions": [{"module": "source_inventory", "action_type": "CreateSourceInventory"}], "blockers": []}
    good = lint_manifest(manifest)
    bad = lint_manifest(bad_manifest)
    lineage = lineage_report(manifest, events)
    status = run_status(plan)
    failures = []
    if not good["pass"]:
        failures.append({"type": "good_manifest_rejected", "result": good})
    if bad["pass"]:
        failures.append({"type": "bad_manifest_accepted", "result": bad})
    if lineage["lineage_event_count"] != 2:
        failures.append({"type": "lineage_wrong", "lineage": lineage})
    if status["status"] != "ready":
        failures.append({"type": "status_wrong", "status": status})
    return {"pass": not failures, "good": good, "bad": bad, "lineage": lineage, "status": status, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    lint_p = sub.add_parser("lint-manifest")
    lint_p.add_argument("--manifest", type=Path, required=True)
    lineage_p = sub.add_parser("lineage")
    lineage_p.add_argument("--manifest", type=Path, required=True)
    lineage_p.add_argument("--events", type=Path, required=True)
    status_p = sub.add_parser("status")
    status_p.add_argument("--workflow-plan", type=Path, required=True)
    render_p = sub.add_parser("render-plan")
    render_p.add_argument("--workflow-plan", type=Path, required=True)
    gaps_p = sub.add_parser("gaps")
    gaps_p.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.self_test:
        result: Any = self_test()
    elif args.command == "lint-manifest":
        result = lint_manifest(load_json(args.manifest))
    elif args.command == "lineage":
        result = lineage_report(load_json(args.manifest), load_jsonl(args.events))
    elif args.command == "status":
        result = run_status(load_json(args.workflow_plan))
    elif args.command == "render-plan":
        result = render_plan(load_json(args.workflow_plan))
    elif args.command == "gaps":
        result = gap_report(args.paths)
    else:
        result = {"pass": False, "failures": [{"type": "missing_command_or_self_test"}]}

    text = result if isinstance(result, str) else json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(text)
    if isinstance(result, dict) and result.get("pass") is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
