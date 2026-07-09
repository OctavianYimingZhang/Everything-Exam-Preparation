#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import plan_workflow

PLUGIN_ID = "everything-exam-preparation"
CONTEXT_CONTRACT = "AcademicTaskContext"
TASK_STATE_CONTRACT = "TaskRunState"
SUPPORTED_CONTEXT_VERSION = 1


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("adapter input must be a JSON object")
    return data


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_academic_task_context(context: dict[str, Any]) -> None:
    if context.get("contract") != CONTEXT_CONTRACT:
        raise ValueError("academic_task_context.contract must be AcademicTaskContext")
    if context.get("version") != SUPPORTED_CONTEXT_VERSION:
        raise ValueError("unsupported AcademicTaskContext version")
    for field in [
        "context_id",
        "created_at",
        "original_prompt",
        "route_selection",
        "course_or_case",
        "source_references",
        "relevant_memory",
        "permissions",
        "decisions",
    ]:
        if field not in context:
            raise ValueError(f"academic_task_context.{field} is required")
    if not str(context.get("original_prompt") or "").strip():
        raise ValueError("academic_task_context.original_prompt must be non-empty")
    selection = context.get("route_selection")
    if not isinstance(selection, dict) or not selection.get("route_id"):
        raise ValueError("academic_task_context.route_selection.route_id is required")
    if selection.get("status") not in {"suggested", "explicitly_confirmed"}:
        raise ValueError("route_selection.status must be suggested or explicitly_confirmed")
    if str(selection["route_id"]) not in plan_workflow.ROUTES:
        raise ValueError(f"unsupported route_id: {selection['route_id']}")


def source_scan_from_payload(context: dict[str, Any], source_fragments: list[dict[str, Any]]) -> dict[str, Any]:
    references = context.get("source_references") or []
    documents = []
    for index, reference in enumerate(references, 1):
        documents.append({
            "id": reference.get("source_id"),
            "source_order": index,
            "source_hint": reference.get("source_hint") or "other_material",
            "category": reference.get("source_hint") or "other_material",
            "trust_status": reference.get("trust_status"),
            "locator_ids": list(reference.get("locator_ids") or []),
            "checksum_sha256": reference.get("checksum_sha256"),
        })
    known_ids = {str(item.get("id")) for item in documents}
    for fragment in source_fragments:
        source_id = str(fragment.get("source_id") or "")
        if source_id and source_id not in known_ids:
            documents.append({
                "id": source_id,
                "name": fragment.get("source_name"),
                "source_order": len(documents) + 1,
                "source_hint": fragment.get("source_hint") or fragment.get("category") or "other_material",
                "category": fragment.get("source_hint") or fragment.get("category") or "other_material",
                "trust_status": fragment.get("trust_status") or "unreviewed",
            })
            known_ids.add(source_id)
    return {"schema_version": 2, "documents": documents, "fragments": source_fragments}


def confirmed_decision(context: dict[str, Any], decision_id: str) -> Any:
    for decision in context.get("decisions") or []:
        if decision.get("decision_id") == decision_id and decision.get("status") == "explicitly_confirmed":
            return decision.get("value")
    return None


def confirmed_permissions(context: dict[str, Any]) -> set[str]:
    return {
        str(permission.get("permission_id"))
        for permission in context.get("permissions") or []
        if permission.get("status") in {"explicitly_confirmed", "denied"}
    }


def online_essay_permissions_confirmed(context: dict[str, Any]) -> bool:
    confirmed = confirmed_permissions(context)
    online_ids = {"online_materials_use", "online_essay_online_materials_permission"}
    lecture_ids = {"lecture_materials_use", "online_essay_lecture_materials_permission"}
    return bool(confirmed & online_ids) and bool(confirmed & lecture_ids)


def state_history_for(context: dict[str, Any], workflow_plan: dict[str, Any], at: str) -> list[dict[str, Any]]:
    history = [{
        "state": "source_ready",
        "at": at,
        "actor": "plugin",
        "reason": "AcademicTaskContext and supplied source fragments were accepted by the adapter.",
    }]
    route_selection = context.get("route_selection") or {}
    if route_selection.get("status") == "explicitly_confirmed":
        history.append({
            "state": "route_or_brief_locked",
            "at": at,
            "actor": "user",
            "reason": "The adapter preserved the explicitly confirmed route instead of re-detecting it.",
        })
    route = str(workflow_plan.get("route") or "")
    if route == "online_essay_exam_drafting" and route_selection.get("status") == "explicitly_confirmed":
        if online_essay_permissions_confirmed(context):
            history.append({
                "state": "permissions_confirmed",
                "at": at,
                "actor": "user",
                "reason": "Online Materials and Lecture Materials permissions are explicitly resolved as allowed or denied.",
            })
    if (
        confirmed_decision(context, "planning_approval") is True
        and route_selection.get("status") == "explicitly_confirmed"
        and not workflow_plan.get("pending_review_targets")
    ):
        history.append({
            "state": "plan_approved",
            "at": at,
            "actor": "user",
            "reason": "Planning approval is explicitly confirmed in AcademicTaskContext decisions.",
        })
    return history


def task_run_state(
    academic_task_context: dict[str, Any],
    source_fragments: list[dict[str, Any]] | None = None,
    at: str | None = None,
) -> dict[str, Any]:
    validate_academic_task_context(academic_task_context)
    fragments = source_fragments or []
    source_scan = source_scan_from_payload(academic_task_context, fragments)
    workflow_plan = plan_workflow.plan(
        academic_task_context=academic_task_context,
        source_scan=source_scan,
        source_fragments=fragments,
    )
    timestamp = at or now_iso()
    history = state_history_for(academic_task_context, workflow_plan, timestamp)
    route_id = str(workflow_plan["route"])
    digest = hashlib.sha256(f"{academic_task_context['context_id']}:{route_id}".encode("utf-8")).hexdigest()[:20]
    return {
        "contract": TASK_STATE_CONTRACT,
        "version": 1,
        "run_id": f"exam-{digest}",
        "context_id": academic_task_context["context_id"],
        "plugin_id": PLUGIN_ID,
        "route_id": route_id,
        "state": history[-1]["state"],
        "state_history": history,
        "created_at": timestamp,
        "updated_at": timestamp,
        "plan": workflow_plan,
        "artifacts": [],
        "qa": None,
        "failure": None,
    }


def adapt(payload: dict[str, Any], at: str | None = None) -> dict[str, Any]:
    context = payload.get("academic_task_context") if isinstance(payload.get("academic_task_context"), dict) else payload
    fragments = payload.get("source_fragments") if isinstance(payload.get("source_fragments"), list) else []
    return task_run_state(context, fragments, at=at)


def self_test() -> None:
    import build_review_questions

    context = {
        "contract": "AcademicTaskContext",
        "version": 1,
        "context_id": "ctx-exam-0001",
        "created_at": "2026-07-09T12:00:00Z",
        "original_prompt": "Evaluate this response without changing the selected route.",
        "route_selection": {"route_id": "answer_evaluation", "status": "explicitly_confirmed"},
        "course_or_case": {"kind": "course", "stable_id": "BIO101", "label": "Biology"},
        "source_references": [{"source_id": "source-0001", "trust_status": "trusted", "locator_ids": ["page-4"]}],
        "relevant_memory": [{"store": "everything-university/mastery", "record_ids": ["BIO101-unit-2"], "purpose": "reuse prior weakness history"}],
        "permissions": [],
        "decisions": [{"decision_id": "output_language", "value": "fr", "status": "explicitly_confirmed", "confirmed_at": "2026-07-09T12:00:00Z"}],
        "requested_output_language": "fr",
        "metadata": {"student_answer": "A receptor activates a kinase."},
    }
    fragments = [{
        "id": "fragment-0001",
        "source_id": "source-0001",
        "source_name": "Lecture.pdf",
        "text": "A receptor activates a kinase cascade.",
        "page_number": 4,
        "locator": "page 4",
        "knowledge_roles": ["mechanism"],
    }]
    result = task_run_state(context, fragments, at="2026-07-09T12:00:00Z")
    assert result["contract"] == "TaskRunState"
    assert result["route_id"] == "answer_evaluation"
    assert result["state"] == "route_or_brief_locked"
    assert result["plan"]["original_prompt"] == context["original_prompt"]
    assert result["plan"]["route_source"] == "academic_task_context.route_selection"
    assert result["plan"]["output_language"] == "fr"
    assert result["plan"]["source_summary"]["fragment_count"] == 1
    assert result["plan"]["relevant_memory"] == context["relevant_memory"]
    root = Path(__file__).resolve().parents[1]
    fixture = load_json(str(root / "tests/fixtures/academic_task_context_answer_evaluation.json"))
    fixture_result = adapt(fixture, at="2026-07-09T12:00:00Z")
    assert fixture_result["route_id"] == "answer_evaluation"
    assert fixture_result["plan"]["source_fragments"][0]["provenance"]["page_number"] == 4
    fixture_scan = source_scan_from_payload(fixture["academic_task_context"], fixture["source_fragments"])
    fixture_review = build_review_questions.build_payload(fixture_result["plan"], fixture_scan)
    assert [question["id"] for question in fixture_review["questions"]] == ["material_type_source_roles"]
    mixed = adapt(load_json(str(root / "tests/fixtures/academic_task_context_mixed_gate.json")), at="2026-07-09T12:00:00Z")
    assert "confirmed_mixed_routes" in mixed["plan"]["pending_review_targets"]
    online = adapt(load_json(str(root / "tests/fixtures/academic_task_context_online_permissions.json")), at="2026-07-09T12:00:00Z")
    assert online["state"] == "permissions_confirmed"
    assert "online_essay_exam_source_permissions" not in online["plan"]["pending_review_targets"]
    online_payload = load_json(str(root / "tests/fixtures/academic_task_context_online_permissions.json"))
    online_scan = source_scan_from_payload(online_payload["academic_task_context"], online_payload["source_fragments"])
    online_review = build_review_questions.build_payload(online["plan"], online_scan)
    online_followups = [question["id"] for batch in online_review["follow_up_question_batches"] for question in batch]
    assert "online_essay_online_materials_permission" not in online_followups
    assert "online_essay_lecture_materials_permission" not in online_followups
    assert "online_essay_allowed_source_set" in online_followups
    denied_payload = load_json(str(root / "tests/fixtures/academic_task_context_online_permissions.json"))
    denied_payload["academic_task_context"]["permissions"][0]["status"] = "denied"
    denied_payload["academic_task_context"]["permissions"][0]["confirmed_at"] = None
    denied = adapt(denied_payload, at="2026-07-09T12:00:00Z")
    assert denied["state"] == "permissions_confirmed"


def main() -> None:
    parser = argparse.ArgumentParser(description="Adapt AcademicTaskContext v1 to an exam-preparation TaskRunState v1 plan.")
    parser.add_argument("--input")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.input:
        parser.error("--input is required")
    result = adapt(load_json(args.input))
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
