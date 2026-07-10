#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import plan_workflow  # noqa: E402
import soleil_adapter  # noqa: E402

NOW = "2026-07-10T12:00:00Z"
LATER = "2026-07-10T12:01:00Z"
LATEST = "2026-07-10T12:02:00Z"
EXPECTED_SUCCESS_LIFECYCLE = [
    "source_ready",
    "route_or_brief_locked",
    "permissions_confirmed",
    "plan_approved",
    "running",
    "qa_passed",
]


def confirmed_decision(decision_id: str, value: Any) -> dict[str, Any]:
    return {
        "decision_id": decision_id,
        "value": value,
        "status": "explicitly_confirmed",
        "confirmed_at": NOW,
    }


def confirmed_permission(permission_id: str, scope: str) -> dict[str, Any]:
    return {
        "permission_id": permission_id,
        "scope": scope,
        "status": "explicitly_confirmed",
        "confirmed_at": NOW,
    }


def executable_payload(route_id: str, *, outcome: str = "qa_passed") -> dict[str, Any]:
    decisions = [
        confirmed_decision("material_type_source_roles", {"source-fixture": "lecture_material"}),
        confirmed_decision("planning_approval", True),
    ]
    if route_id in plan_workflow.NOTES_CHOICE_ROUTES:
        decisions.append(confirmed_decision("notes_output_choice", False))
    if route_id == "mixed_exam_preparation":
        decisions.append(confirmed_decision("confirmed_mixed_routes", ["mcq_preparation", "short_answer_preparation"]))
    if route_id == "assessment_blueprint":
        decisions.append(confirmed_decision("assessment_blueprint_scope", ["unit-fixture"]))
    route_review_decisions: dict[str, list[tuple[str, Any]]] = {
        "mcq_preparation": [("mcq_research_report_choice", "generate_report")],
        "short_answer_preparation": [("short_answer_research_report_choice", "generate_report")],
        "long_answer_preparation": [("long_answer_detailed_analysis_choice", "detailed_analysis")],
        "worked_solution_preparation": [("worked_solution_teaching_choice", "teach_each_question")],
        "essay_preparation": [
            ("essay_example_essay_choice", "generate_examples"),
            ("essay_example_essay_count", 2),
            ("essay_question_source", "generate_from_material"),
        ],
        "online_essay_exam_drafting": [
            ("online_essay_allowed_source_set", "all_confirmed_sources"),
            ("online_essay_citation_expectation", "citations_required"),
            ("online_essay_output_format", "docx_draft"),
        ],
        "mixed_exam_preparation": [
            ("mcq_research_report_choice", "generate_report"),
            ("short_answer_research_report_choice", "generate_report"),
        ],
    }
    decisions.extend(
        confirmed_decision(decision_id, value)
        for decision_id, value in route_review_decisions.get(route_id, [])
    )

    permissions = [
        confirmed_permission("local_execution", "Allow this approved task to run through the authenticated local executor."),
    ]
    if route_id == "online_essay_exam_drafting":
        permissions.extend([
            confirmed_permission("online_materials_use", "Online Materials may be used as supporting evidence."),
            confirmed_permission("lecture_materials_use", "Lecture Materials may be used as primary evidence."),
            confirmed_permission(
                "online_essay_complete_draft_permission",
                "The assessment rules permit assistance with a complete draft.",
            ),
        ])

    metadata: dict[str, Any] = {"target_question": "Explain the fixture mechanism."}
    if route_id == "answer_evaluation":
        metadata.update({
            "student_answer": "The receptor activates a kinase cascade.",
            "evaluation_criteria": ["receptor activation", "kinase cascade"],
        })
    if route_id == "timed_practice":
        metadata.update({
            "assessment_blueprint": {"units": ["unit-fixture"]},
            "duration_minutes": 45,
        })

    execution_result: dict[str, Any] = {
        "outcome": outcome,
        "artifacts": [
            {
                "artifact_id": f"artifact-{route_id}",
                "artifact_type": "route_output",
                "opaque_local_ref": f"local-run:{route_id}:result",
                "status": "qa_passed" if outcome == "qa_passed" else "failed",
            }
        ],
        "qa": {
            "passed": outcome == "qa_passed",
            "checks": [{"check_id": "fixture_execution", "passed": outcome == "qa_passed"}],
        },
        "failure": None,
    }
    if outcome == "failed":
        execution_result["failure"] = {
            "code": "fixture_execution_failed",
            "message": "The fixture executor returned a structured failure.",
            "retryable": True,
        }

    return {
        "run_id": f"run-{route_id}-caller",
        "academic_task_context": {
            "contract": "AcademicTaskContext",
            "version": 1,
            "context_id": f"ctx-{route_id}-fixture",
            "created_at": NOW,
            "original_prompt": f"Execute the explicitly confirmed {route_id} route.",
            "route_selection": {"route_id": route_id, "status": "explicitly_confirmed"},
            "course_or_case": {"kind": "course", "stable_id": "BIO101", "label": "Biology"},
            "source_references": [
                {"source_id": "source-fixture", "trust_status": "trusted", "locator_ids": ["page-4"]}
            ],
            "relevant_memory": [],
            "permissions": permissions,
            "decisions": decisions,
            "requested_output_language": "en",
            "metadata": metadata,
        },
        "source_fragments": [
            {
                "id": "fragment-fixture",
                "source_id": "source-fixture",
                "source_name": "Lecture.pdf",
                "text": "Receptor activation initiates a kinase cascade.",
                "locator": "page 4",
                "page_number": 4,
                "knowledge_roles": ["mechanism"],
            }
        ],
        "execution_result": execution_result,
    }


class SoleilAdapterLifecycleTests(unittest.TestCase):
    def test_every_declared_route_preserves_run_id_and_full_success_lifecycle(self) -> None:
        for route_id in plan_workflow.ROUTES:
            with self.subTest(route_id=route_id):
                payload = executable_payload(route_id)
                state = soleil_adapter.adapt(payload, at=NOW)
                self.assertEqual(state["run_id"], payload["run_id"])
                self.assertEqual(state["route_id"], route_id)
                self.assertEqual(
                    [entry["state"] for entry in state["state_history"]],
                    EXPECTED_SUCCESS_LIFECYCLE,
                )
                self.assertEqual(state["state"], "qa_passed")
                self.assertTrue(state["qa"]["passed"])
                self.assertIsNone(state["failure"])

    def test_failed_execution_preserves_full_ordered_lifecycle(self) -> None:
        payload = executable_payload("answer_evaluation", outcome="failed")
        state = soleil_adapter.adapt(payload, at=NOW)
        self.assertEqual(state["run_id"], payload["run_id"])
        self.assertEqual(
            [entry["state"] for entry in state["state_history"]],
            EXPECTED_SUCCESS_LIFECYCLE[:-1] + ["failed"],
        )
        self.assertFalse(state["qa"]["passed"])
        self.assertEqual(state["failure"]["code"], "fixture_execution_failed")

    def test_execution_requires_local_permission_and_planning_approval(self) -> None:
        no_permission = executable_payload("mcq_preparation")
        no_permission["academic_task_context"]["permissions"] = []
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(no_permission, at=NOW)

        no_approval = executable_payload("mcq_preparation")
        no_approval["academic_task_context"]["decisions"] = [
            decision
            for decision in no_approval["academic_task_context"]["decisions"]
            if decision["decision_id"] != "planning_approval"
        ]
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(no_approval, at=NOW)

        undated_approval = executable_payload("mcq_preparation")
        next(
            decision
            for decision in undated_approval["academic_task_context"]["decisions"]
            if decision["decision_id"] == "planning_approval"
        )["confirmed_at"] = None
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(undated_approval, at=NOW)

    def test_manifest_required_inputs_block_execution_for_every_declared_input(self) -> None:
        missing_inputs = executable_payload("question_solving")
        missing_inputs.pop("source_fragments")
        missing_inputs["academic_task_context"]["metadata"].pop("target_question")
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(missing_inputs, at=NOW)

        planning_only = copy.deepcopy(missing_inputs)
        planning_only.pop("execution_result")
        state = soleil_adapter.adapt(planning_only, at=NOW)
        self.assertEqual(state["state"], "permissions_confirmed")
        self.assertEqual(
            state["plan"]["required_input_status"]["unresolved"],
            ["target_question", "source_fragments"],
        )

    def test_generated_route_reviews_block_execution_until_explicitly_confirmed(self) -> None:
        unresolved = executable_payload("online_essay_exam_drafting")
        required_reviews = {
            "online_essay_allowed_source_set",
            "online_essay_citation_expectation",
            "online_essay_output_format",
        }
        unresolved["academic_task_context"]["decisions"] = [
            decision
            for decision in unresolved["academic_task_context"]["decisions"]
            if decision["decision_id"] not in required_reviews
        ]
        unresolved["academic_task_context"]["decisions"].append(
            confirmed_decision("online_essay_output_format", None)
        )
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(unresolved, at=NOW)

        planning_only = copy.deepcopy(unresolved)
        planning_only.pop("execution_result")
        state = soleil_adapter.adapt(planning_only, at=NOW)
        self.assertEqual(state["state"], "permissions_confirmed")
        self.assertEqual(
            set(state["plan"]["required_review_status"]["unresolved"]),
            required_reviews,
        )

    def test_online_essay_denial_blocks_running_and_approved_permission_executes(self) -> None:
        denied = executable_payload("online_essay_exam_drafting")
        complete_draft_permission = next(
            permission
            for permission in denied["academic_task_context"]["permissions"]
            if permission["permission_id"] == "online_essay_complete_draft_permission"
        )
        complete_draft_permission["status"] = "denied"
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(denied, at=NOW)

        planning_only = copy.deepcopy(denied)
        planning_only.pop("execution_result")
        state = soleil_adapter.adapt(planning_only, at=NOW)
        self.assertEqual(state["state"], "route_or_brief_locked")
        self.assertEqual(state["plan"]["permission_gate"]["status"], "denied")
        self.assertEqual(
            state["plan"]["execution_blockers"][0]["id"],
            "online_essay_complete_draft_permission_denied",
        )

        approved = executable_payload("online_essay_exam_drafting")
        approved_state = soleil_adapter.adapt(approved, at=NOW)
        self.assertEqual(approved_state["state"], "qa_passed")

        source_use_denied = executable_payload("online_essay_exam_drafting")
        next(
            permission
            for permission in source_use_denied["academic_task_context"]["permissions"]
            if permission["permission_id"] == "online_materials_use"
        )["status"] = "denied"
        source_use_denied_state = soleil_adapter.adapt(source_use_denied, at=NOW)
        self.assertEqual(source_use_denied_state["state"], "qa_passed")
        self.assertIn(
            "online_materials_use",
            source_use_denied_state["plan"]["permission_gate"]["denied_permission_ids"],
        )

    def test_later_or_conflicting_complete_draft_denial_blocks_execution(self) -> None:
        later_denial = executable_payload("online_essay_exam_drafting")
        later_denial["academic_task_context"]["permissions"].append({
            "permission_id": "online_essay_complete_draft_permission",
            "scope": "The assessment rules do not permit a complete draft.",
            "status": "denied",
            "confirmed_at": LATER,
        })
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(later_denial, at=LATEST)

        planning_only = copy.deepcopy(later_denial)
        planning_only.pop("execution_result")
        denied_state = soleil_adapter.adapt(planning_only, at=LATEST)
        self.assertEqual(denied_state["plan"]["permission_gate"]["status"], "denied")
        self.assertEqual(denied_state["state"], "route_or_brief_locked")

        conflict = executable_payload("online_essay_exam_drafting")
        conflict["academic_task_context"]["permissions"].append({
            "permission_id": "online_essay_complete_draft_permission",
            "scope": "The assessment rules do not permit a complete draft.",
            "status": "denied",
            "confirmed_at": NOW,
        })
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(conflict, at=LATER)

        reapproved = copy.deepcopy(later_denial)
        reapproved["academic_task_context"]["permissions"].append(
            confirmed_permission(
                "online_essay_complete_draft_permission",
                "The assessment rules now explicitly permit a complete draft.",
            ) | {"confirmed_at": LATEST}
        )
        reapproved_state = soleil_adapter.adapt(reapproved, at=LATEST)
        self.assertEqual(reapproved_state["state"], "qa_passed")

    def test_later_permission_or_planning_revocation_blocks_execution(self) -> None:
        local_revoked = executable_payload("mcq_preparation")
        local_revoked["academic_task_context"]["permissions"].append({
            "permission_id": "local_execution",
            "scope": "Do not execute this task locally.",
            "status": "denied",
            "confirmed_at": LATER,
        })
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(local_revoked, at=LATEST)

        approval_revoked = executable_payload("mcq_preparation")
        approval_revoked["academic_task_context"]["decisions"].append(
            confirmed_decision("planning_approval", False) | {"confirmed_at": LATER}
        )
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(approval_revoked, at=LATEST)

        approval_conflict = executable_payload("mcq_preparation")
        approval_conflict["academic_task_context"]["decisions"].append(
            confirmed_decision("planning_approval", False)
        )
        with self.assertRaisesRegex(ValueError, "execution_result requires"):
            soleil_adapter.adapt(approval_conflict, at=LATER)

        reapproved = copy.deepcopy(approval_revoked)
        reapproved["academic_task_context"]["decisions"].append(
            confirmed_decision("planning_approval", True) | {"confirmed_at": LATEST}
        )
        reapproved_state = soleil_adapter.adapt(reapproved, at=LATEST)
        self.assertEqual(reapproved_state["state"], "qa_passed")

    def test_invalid_terminal_payload_cannot_claim_qa_success(self) -> None:
        payload = executable_payload("question_solving")
        payload["execution_result"]["qa"]["passed"] = False
        with self.assertRaisesRegex(ValueError, "qa.passed must be true"):
            soleil_adapter.adapt(payload, at=NOW)

        empty_artifact_payload = executable_payload("question_solving")
        empty_artifact_payload["execution_result"]["artifacts"] = []
        with self.assertRaisesRegex(ValueError, "at least one QA-passed artifact"):
            soleil_adapter.adapt(empty_artifact_payload, at=NOW)

    def test_planning_state_preserves_caller_run_id_without_execution(self) -> None:
        payload = executable_payload("assessment_blueprint")
        payload.pop("execution_result")
        state = soleil_adapter.adapt(payload, at=NOW)
        self.assertEqual(state["run_id"], payload["run_id"])
        self.assertEqual(state["state"], "plan_approved")
        self.assertEqual(
            [entry["state"] for entry in state["state_history"]],
            EXPECTED_SUCCESS_LIFECYCLE[:4],
        )


if __name__ == "__main__":
    unittest.main()
