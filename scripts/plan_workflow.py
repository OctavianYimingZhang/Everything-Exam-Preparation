#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_ACTIONS = [
    "source_inventory",
    "fragment_index",
    "practice_material_knowledge_signal_review",
    "human_review_exam_material_output_confirmation",
    "coverage_calibration",
    "course_knowledge_map",
    "notes_generation_if_user_accepts",
]

EXTRA_READING_ESSAY_ACTIONS = [
    "extra_reading_discovery",
    "extra_reading_topic_matching",
    "extra_reading_essay_enrichment",
]

ONLINE_ESSAY_EXAM_ACTIONS = [
    "source_inventory",
    "fragment_index",
    "online_essay_exam_material_diagnosis",
    "human_review_exam_material_output_confirmation",
    "online_materials_permission_review",
    "lecture_materials_permission_review",
    "online_essay_exam_brief_lock",
    "extra_reading_discovery_if_allowed",
    "allowed_source_evidence_map",
    "thesis_or_central_answer_options",
    "paragraph_level_structure_plan",
    "critical_analysis_plan",
    "planning_approval",
    "online_essay_exam_draft_generation",
    "online_essay_exam_qa",
]

ASSESSMENT_BLUEPRINT_ACTIONS = [
    "source_inventory",
    "fragment_index",
    "human_review_exam_material_output_confirmation",
    "relevant_everything_university_memory_load",
    "assessment_blueprint_generation",
    "assessment_blueprint_qa",
]

ANSWER_EVALUATION_ACTIONS = [
    "source_inventory",
    "fragment_index",
    "human_review_exam_material_output_confirmation",
    "answer_and_evaluation_criteria_confirmation",
    "source_grounded_answer_evaluation",
    "mastery_history_update_if_enabled",
]

TIMED_PRACTICE_ACTIONS = [
    "source_inventory",
    "fragment_index",
    "human_review_exam_material_output_confirmation",
    "assessment_blueprint_load_or_generation",
    "timed_practice_duration_confirmation",
    "timed_practice_generation",
    "mastery_history_context_load_if_enabled",
]

ROUTES: dict[str, list[str]] = {
    "exam_prep_notes": BASE_ACTIONS + [
        "exam_prep_notes",
    ],
    "mcq_preparation": BASE_ACTIONS + [
        "mcq_result_only_high_frequency_knowledge_report",
    ],
    "short_answer_preparation": BASE_ACTIONS + [
        "short_answer_result_only_high_frequency_knowledge_report",
    ],
    "long_answer_preparation": BASE_ACTIONS + [
        "long_answer_practical_data_problem_specific_research_report",
    ],
    "worked_solution_preparation": BASE_ACTIONS + [
        "worked_solution_specific_research_report",
    ],
    "essay_preparation": BASE_ACTIONS + EXTRA_READING_ESSAY_ACTIONS + [
        "essay_specific_research_report",
    ],
    "online_essay_exam_drafting": ONLINE_ESSAY_EXAM_ACTIONS,
    "mixed_exam_preparation": BASE_ACTIONS + [
        "mixed_specific_research_reports",
    ],
    "question_solving": [
        "source_inventory",
        "fragment_index",
        "target_question_analysis",
        "match_question_to_knowledge_unit",
        "strict_same_knowledge_point_question_retrieval",
        "question_solution_report",
    ],
    "question_organizing": [
        "source_inventory",
        "fragment_index",
        "lecture_order_knowledge_map",
        "past_paper_practice_question_extraction",
        "sort_questions_by_latest_matching_lecture",
        "organized_questions_docx",
    ],
    "assessment_blueprint": ASSESSMENT_BLUEPRINT_ACTIONS,
    "answer_evaluation": ANSWER_EVALUATION_ACTIONS,
    "timed_practice": TIMED_PRACTICE_ACTIONS,
}

ROUTE_OUTPUTS = {
    "mcq_preparation": ["docx_notes", "mcq_exam_type_related_addon"],
    "short_answer_preparation": ["docx_notes", "short_answer_exam_type_related_addon"],
    "long_answer_preparation": ["docx_notes", "long_answer_practical_data_problem_exam_type_related_addon"],
    "worked_solution_preparation": ["docx_notes", "practical_worked_solutions_docx"],
    "essay_preparation": ["docx_notes", "essay_exam_type_related_addon"],
    "online_essay_exam_drafting": ["online_essay_exam_draft", "online_essay_exam_draft_docx_if_requested"],
    "mixed_exam_preparation": ["docx_notes", "exam_type_related_addon_docx"],
    "question_solving": ["question_solution_report"],
    "question_organizing": ["organized_questions_docx"],
    "assessment_blueprint": ["assessment_blueprint"],
    "answer_evaluation": ["answer_evaluation_report"],
    "timed_practice": ["timed_practice_session"],
}

ROUTE_LABELS = {
    "exam_prep_notes": "Notes",
    "mcq_preparation": "MCQ",
    "short_answer_preparation": "Short Answer",
    "long_answer_preparation": "Long Answer or Practical/Data/Problem",
    "worked_solution_preparation": "Worked Solutions",
    "essay_preparation": "Essay",
    "online_essay_exam_drafting": "Online Essay Exam",
    "mixed_exam_preparation": "Mixed",
    "question_solving": "Question Solving",
    "question_organizing": "Question Organization",
    "assessment_blueprint": "Assessment Blueprint",
    "answer_evaluation": "Answer Evaluation",
    "timed_practice": "Timed Practice",
}

NOTES_CHOICE_ROUTES = {
    "exam_prep_notes",
    "mcq_preparation",
    "short_answer_preparation",
    "long_answer_preparation",
    "worked_solution_preparation",
    "essay_preparation",
    "online_essay_exam_drafting",
    "mixed_exam_preparation",
}

ONLINE_MATERIAL_PERMISSION_IDS = {"online_materials_use", "online_essay_online_materials_permission"}
LECTURE_MATERIAL_PERMISSION_IDS = {"lecture_materials_use", "online_essay_lecture_materials_permission"}
COMPLETE_DRAFT_PERMISSION_IDS = {"online_essay_complete_draft_permission", "online_essay_assessment_draft_permission"}


def prompt_has_any(prompt: str, signals: list[str]) -> bool:
    return any(signal in prompt for signal in signals)


def detect_route(prompt: str) -> str:
    p = (prompt or "").lower()
    if prompt_has_any(p, ["assessment blueprint", "exam blueprint", "assessment coverage blueprint"]):
        return "assessment_blueprint"
    if prompt_has_any(p, ["evaluate my answer", "evaluate this answer", "mark my answer", "answer evaluation", "grade this answer"]):
        return "answer_evaluation"
    if prompt_has_any(p, ["timed practice", "timed mock", "practice timer", "timed session"]):
        return "timed_practice"
    if prompt_has_any(p, [
        "organize past paper",
        "organise past paper",
        "organize past-paper",
        "organise past-paper",
        "sort past paper",
        "sort past-paper",
        "organize practice",
        "organise practice",
        "sort practice",
        "collect practice",
        "compile practice",
        "collect past paper",
        "compile past paper",
        "question organizer",
        "question organiser",
        "question organization",
        "question organisation",
        "question list",
        "questions by lecture order",
        "questions by lecture",
    ]):
        return "question_organizing"
    if prompt_has_any(p, [
        "solve this question",
        "solve question",
        "answer this question",
        "how to solve",
        "how do i solve",
        "how to answer",
        "how do i answer",
        "work through this question",
        "work through question",
        "question walkthrough",
        "same knowledge point",
    ]):
        return "question_solving"
    online_essay_signals = [
        "online essay exam",
        "online exam essay",
        "online essay",
        "online essay draft",
        "draft online essay",
        "draft this online essay",
        "write online essay answer",
        "take-home essay exam",
        "take home essay exam",
        "take-home exam essay",
        "take home exam essay",
        "take-home essay",
        "take home essay",
        "open-book essay exam",
        "open book essay exam",
        "open-book exam essay",
        "open book exam essay",
        "open-book essay",
        "open book essay",
        "48h essay",
        "48-hour essay",
        "48 hour essay",
    ]
    if prompt_has_any(p, online_essay_signals):
        return "online_essay_exam_drafting"
    if prompt_has_any(p, [
        "essay",
        "essay draft",
        "draft this essay",
        "draft an essay answer",
        "write an essay answer",
        "in-campus",
        "in campus",
        "model essay",
        "example essay",
        "thesis",
    ]):
        return "essay_preparation"
    if prompt_has_any(p, ["mcq", "sba", "single best", "multiple choice", "true/false"]):
        return "mcq_preparation"
    if prompt_has_any(p, ["short answer", "saq", "definition", "define", "state", "list question"]):
        return "short_answer_preparation"
    if prompt_has_any(p, ["worked answer", "worked solution", "calculate", "derive", "derivation", "estimate", "prove", "proof", "problem"]):
        return "worked_solution_preparation"
    if prompt_has_any(p, ["long answer", "walkthrough", "practical", "data"]):
        return "long_answer_preparation"
    if prompt_has_any(p, ["exam mode", "exam format", "how is", "diagnose", "identify format", "mixed"]):
        return "mixed_exam_preparation"
    return "exam_prep_notes"


def source_summary(source_scan: dict[str, Any] | None) -> dict[str, Any]:
    if not source_scan:
        return {"document_count": 0, "fragment_count": 0, "source_hints": {}, "coverage_profile": {}}
    cats: dict[str, int] = {}
    signal_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    unit_candidates = 0
    for doc in source_scan.get("documents", []):
        cat = str(doc.get("source_hint") or doc.get("category") or "other_material")
        cats[cat] = cats.get(cat, 0) + 1
        for signal in doc.get("knowledge_signals", []) or []:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        for role in doc.get("knowledge_roles", []) or []:
            role_counts[role] = role_counts.get(role, 0) + 1
        unit_candidates += len(doc.get("knowledge_unit_candidates", []) or [])
    for frag in source_scan.get("fragments", []):
        for signal in frag.get("knowledge_signals", []) or []:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
        for role in frag.get("knowledge_roles", []) or []:
            role_counts[role] = role_counts.get(role, 0) + 1
        unit_candidates += len(frag.get("knowledge_unit_candidates", []) or [])
    return {
        "document_count": len(source_scan.get("documents", [])),
        "fragment_count": len(source_scan.get("fragments", [])),
        "source_hints": cats,
        "question_material": {
            "has_past_paper_questions": any(doc.get("question_signals", {}).get("has_past_paper") for doc in source_scan.get("documents", [])),
            "has_practical_questions": any(doc.get("question_signals", {}).get("has_practical_questions") for doc in source_scan.get("documents", [])),
            "has_practical_worked_questions": any(doc.get("question_signals", {}).get("has_practical_worked_questions") for doc in source_scan.get("documents", [])),
        },
        "coverage_profile": {
            "knowledge_signal_counts": signal_counts,
            "knowledge_role_counts": role_counts,
            "knowledge_unit_candidate_count": unit_candidates,
        },
    }


def auto_diagnosis(
    route: str,
    outputs: list[str],
    summary: dict[str, Any],
    route_selection_status: str = "suggested",
) -> dict[str, Any]:
    source_hints = summary.get("source_hints", {})
    question_material = summary.get("question_material", {})
    coverage_profile = summary.get("coverage_profile", {})
    role_counts = coverage_profile.get("knowledge_role_counts", {})
    mixed_or_unclear = bool(
        len([count for count in source_hints.values() if count]) > 1
        or bool(source_hints.get("other_material"))
        or (question_material.get("has_past_paper_questions") and question_material.get("has_practical_questions"))
    )
    if route == "online_essay_exam_drafting":
        review_requirement = "Confirm or correct route, source roles, route-specific follow-up choices, Online Materials and Lecture Materials rules, explicit assessment permission for a complete draft, and whether Notes should be generated before generating any Online Essay Exam plan or draft."
    elif route == "mixed_exam_preparation":
        review_requirement = "Confirm or correct route, selected Mixed component routes, source roles, route-specific follow-up choices, and whether Notes should be generated before generating public Notes, Specific Research Reports, add-ons, or worked solutions."
    elif route not in NOTES_CHOICE_ROUTES:
        review_requirement = "Confirm or correct route, source roles, and route-specific required inputs before generating public output."
    else:
        review_requirement = "Confirm or correct route, source roles, route-specific follow-up choices, and whether Notes should be generated before generating public Notes, Specific Research Reports, add-ons, or worked solutions."
    return {
        "status": "route_explicitly_confirmed" if route_selection_status == "explicitly_confirmed" else "preliminary",
        "route": route,
        "exam_type": ROUTE_LABELS.get(route, route),
        "material_roles": source_hints,
        "knowledge_role_counts": role_counts,
        "question_material": question_material,
        "proposed_outputs": outputs,
        "mixed_or_unclear": mixed_or_unclear,
        "review_requirement": review_requirement,
    }


def question_addon_required(source_scan: dict[str, Any] | None) -> bool:
    if not source_scan:
        return False
    for doc in source_scan.get("documents", []) or []:
        signals = doc.get("question_signals", {}) or {}
        if (signals.get("has_past_paper") and not signals.get("has_practical_worked_questions")) or (signals.get("has_practical_questions") and not signals.get("has_practical_worked_questions")):
            return True
    return False


def practical_worked_required(source_scan: dict[str, Any] | None) -> bool:
    if not source_scan:
        return False
    return any((doc.get("question_signals", {}) or {}).get("has_practical_worked_questions") for doc in source_scan.get("documents", []) or [])


def extra_reading_requested(prompt: str) -> bool:
    p = (prompt or "").lower()
    return any(k in p for k in ["extra reading", "external evidence", "research article", "journal article", "doi", "pmid"])


def confirmed_decision(decisions: list[dict[str, Any]], decision_id: str) -> Any:
    candidates = [
        decision
        for decision in decisions
        if isinstance(decision, dict)
        and decision.get("decision_id") == decision_id
        and decision.get("status") == "explicitly_confirmed"
    ]
    resolution = explicit_decision_resolution(decisions, decision_id)
    if resolution.get("status") == "resolved":
        return resolution.get("value")
    if len(candidates) == 1 and confirmation_time(candidates[0].get("confirmed_at")) is None:
        return candidates[0].get("value")
    return None


def confirmation_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def canonical_decision_value(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        return repr(value)


def explicit_decision_resolution(decisions: list[dict[str, Any]], decision_id: str) -> dict[str, Any]:
    candidates = [
        decision
        for decision in decisions
        if isinstance(decision, dict)
        and decision.get("decision_id") == decision_id
        and decision.get("status") == "explicitly_confirmed"
    ]
    if not candidates:
        return {"status": "unresolved", "value": None}
    dated = [(confirmation_time(decision.get("confirmed_at")), decision) for decision in candidates]
    if any(confirmed_at is None for confirmed_at, _ in dated):
        return {
            "status": "conflict" if len(candidates) > 1 else "unresolved",
            "value": None,
        }
    latest_at = max(confirmed_at for confirmed_at, _ in dated if confirmed_at is not None)
    latest = [
        decision
        for confirmed_at, decision in dated
        if confirmed_at == latest_at
    ]
    values = {canonical_decision_value(decision.get("value")) for decision in latest}
    if len(values) != 1:
        return {"status": "conflict", "value": None}
    return {"status": "resolved", "value": latest[0].get("value")}


def explicit_decision_answered(decisions: list[dict[str, Any]], decision_id: str) -> bool:
    resolution = explicit_decision_resolution(decisions, decision_id)
    if resolution.get("status") != "resolved":
        return False
    value = resolution.get("value")
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def permission_resolution(permissions: list[dict[str, Any]], permission_ids_to_match: set[str]) -> str:
    candidates = [
        permission
        for permission in permissions
        if isinstance(permission, dict)
        and permission.get("permission_id") in permission_ids_to_match
        and permission.get("status") in {"explicitly_confirmed", "denied"}
    ]
    if not candidates:
        return "unresolved"
    states = [
        "denied" if permission.get("status") == "denied" else "allowed"
        for permission in candidates
    ]
    dated = [(confirmation_time(permission.get("confirmed_at")), state) for permission, state in zip(candidates, states)]
    if any(confirmed_at is None for confirmed_at, _ in dated):
        distinct_states = set(states)
        if distinct_states == {"denied"}:
            return "denied"
        return "conflict" if len(candidates) > 1 else "unresolved"
    latest_at = max(confirmed_at for confirmed_at, _ in dated if confirmed_at is not None)
    latest_states = {
        state
        for confirmed_at, state in dated
        if confirmed_at == latest_at
    }
    if len(latest_states) != 1:
        return "conflict"
    return next(iter(latest_states))


def explicit_language_from_prompt(prompt: str) -> str | None:
    text = (prompt or "").lower()
    if any(term in text for term in ["bilingual output", "bilingual answer", "in both english and chinese"]):
        return "bilingual"
    if any(term in text for term in ["in chinese", "chinese output", "answer in chinese", "write in chinese"]):
        return "zh"
    if any(term in text for term in ["in english", "english output", "answer in english", "write in english"]):
        return "en"
    return None


def task_output_language(
    prompt: str,
    decisions: list[dict[str, Any]],
    requested_output_language: str | None = None,
) -> str:
    explicit = confirmed_decision(decisions, "output_language")
    if explicit:
        return str(explicit)
    if requested_output_language:
        return str(requested_output_language)
    return explicit_language_from_prompt(prompt) or "en"


def permission_ids(
    permissions: list[dict[str, Any]],
    statuses: set[str] | None = None,
) -> set[str]:
    accepted_statuses = statuses or {"explicitly_confirmed", "denied"}
    return {
        str(permission.get("permission_id"))
        for permission in permissions
        if permission.get("status") in accepted_statuses
    }


def online_essay_source_permissions_resolved(permissions: list[dict[str, Any]]) -> bool:
    online_state = permission_resolution(permissions, ONLINE_MATERIAL_PERMISSION_IDS)
    lecture_state = permission_resolution(permissions, LECTURE_MATERIAL_PERMISSION_IDS)
    return online_state in {"allowed", "denied"} and lecture_state in {"allowed", "denied"}


def online_essay_complete_draft_permission_resolved(permissions: list[dict[str, Any]]) -> bool:
    return permission_resolution(permissions, COMPLETE_DRAFT_PERMISSION_IDS) in {"allowed", "denied"}


def online_essay_complete_draft_allowed(permissions: list[dict[str, Any]]) -> bool:
    return permission_resolution(permissions, COMPLETE_DRAFT_PERMISSION_IDS) == "allowed"


def online_essay_permissions_confirmed(permissions: list[dict[str, Any]]) -> bool:
    return online_essay_source_permissions_resolved(permissions) and online_essay_complete_draft_allowed(permissions)


def online_essay_permission_gate(permissions: list[dict[str, Any]]) -> dict[str, Any]:
    resolved = permission_ids(permissions)
    denied = permission_ids(permissions, {"denied"})
    online_state = permission_resolution(permissions, ONLINE_MATERIAL_PERMISSION_IDS)
    lecture_state = permission_resolution(permissions, LECTURE_MATERIAL_PERMISSION_IDS)
    draft_state = permission_resolution(permissions, COMPLETE_DRAFT_PERMISSION_IDS)
    source_rules_resolved = online_state in {"allowed", "denied"} and lecture_state in {"allowed", "denied"}
    draft_rule_resolved = draft_state in {"allowed", "denied"}
    draft_allowed = draft_state == "allowed"
    if source_rules_resolved and draft_allowed:
        status = "approved"
    elif "conflict" in {online_state, lecture_state, draft_state}:
        status = "conflict"
    elif draft_state == "denied":
        status = "denied"
    else:
        status = "pending"
    return {
        "status": status,
        "source_rules_resolved": source_rules_resolved,
        "complete_draft_permission_resolved": draft_rule_resolved,
        "complete_draft_allowed": draft_allowed,
        "effective_permission_states": {
            "online_materials_use": online_state,
            "lecture_materials_use": lecture_state,
            "online_essay_complete_draft_permission": draft_state,
        },
        "resolved_permission_ids": sorted(resolved),
        "denied_permission_ids": sorted(denied),
    }


def target(id: str, purpose: str, resolved: bool = False) -> dict[str, Any]:
    return {
        "id": id,
        "purpose": purpose,
        "status": "explicitly_confirmed" if resolved else "pending_user_confirmation",
    }


def source_scan_with_fragments(
    source_scan: dict[str, Any] | None,
    source_fragments: list[dict[str, Any]] | None,
) -> dict[str, Any] | None:
    if not source_fragments:
        return source_scan
    merged = dict(source_scan or {})
    merged.setdefault("documents", [])
    merged["fragments"] = list(source_fragments)
    return merged


def unresolved_required_inputs(route: str, metadata: dict[str, Any], has_source_fragments: bool = False) -> list[str]:
    unresolved: list[str] = []
    if route == "assessment_blueprint" and not has_source_fragments:
        unresolved.append("source_fragments")
    if route == "answer_evaluation":
        if not metadata.get("student_answer"):
            unresolved.append("student_answer")
        if not (metadata.get("evaluation_criteria") or metadata.get("marking_material")):
            unresolved.append("evaluation_criteria_or_marking_material")
    if route == "timed_practice":
        if not metadata.get("assessment_blueprint"):
            unresolved.append("assessment_blueprint")
        if not metadata.get("duration_minutes"):
            unresolved.append("duration_minutes")
    return unresolved


def plan(
    prompt: str = "",
    source_scan: dict[str, Any] | None = None,
    *,
    route_selection: dict[str, Any] | None = None,
    source_fragments: list[dict[str, Any]] | None = None,
    relevant_memory: list[dict[str, Any]] | None = None,
    permissions: list[dict[str, Any]] | None = None,
    decisions: list[dict[str, Any]] | None = None,
    requested_output_language: str | None = None,
    academic_task_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = academic_task_context or {}
    if context:
        prompt = str(context.get("original_prompt") or prompt or "")
        route_selection = context.get("route_selection") if isinstance(context.get("route_selection"), dict) else route_selection
        relevant_memory = list(context.get("relevant_memory") or relevant_memory or [])
        permissions = list(context.get("permissions") or permissions or [])
        decisions = list(context.get("decisions") or decisions or [])
        requested_output_language = str(context.get("requested_output_language") or requested_output_language or "") or None
    relevant_memory = relevant_memory or []
    permissions = permissions or []
    decisions = decisions or []
    metadata = context.get("metadata") if isinstance(context.get("metadata"), dict) else {}
    selected_route = str((route_selection or {}).get("route_id") or "")
    if selected_route:
        if selected_route not in ROUTES:
            raise ValueError(f"unsupported route_id: {selected_route}")
        route = selected_route
        route_source = "academic_task_context.route_selection" if context else "explicit_route_selection"
    else:
        route = detect_route(prompt)
        route_source = "original_prompt_detection"
    route_selection_status = str((route_selection or {}).get("status") or "suggested")
    route_confirmed = route_selection_status == "explicitly_confirmed"
    source_scan = source_scan_with_fragments(source_scan, source_fragments)
    action_ids = list(ROUTES[route])
    if "human_review_exam_material_output_confirmation" not in action_ids:
        insert_at = action_ids.index("source_inventory") + 1 if "source_inventory" in action_ids else 0
        action_ids.insert(insert_at, "human_review_exam_material_output_confirmation")
    actions = [{"id": action, "purpose": action.replace("_", " ")} for action in action_ids]
    outputs = ROUTE_OUTPUTS.get(route, ["docx_notes"])
    if route == "exam_prep_notes" and question_addon_required(source_scan):
        outputs = ["docx_notes", "exam_type_related_addon_docx"]
        actions.append({
            "id": "question_based_exam_type_related_addon",
            "purpose": "build separate exam type related addon from past paper or question practical material",
        })
    if route == "exam_prep_notes" and practical_worked_required(source_scan):
        if outputs == ["docx_notes"]:
            outputs = ["docx_notes", "practical_worked_solutions_docx"]
        elif "practical_worked_solutions_docx" not in outputs:
            outputs.append("practical_worked_solutions_docx")
        actions.append({
            "id": "practical_worked_solutions",
            "purpose": "build detailed worked solutions for practical calculation derivation data or problem questions",
        })
    summary = source_summary(source_scan)
    notes = [
        "Use source hints as rough provenance labels.",
        "Display the Auto-diagnosis review plan and complete human review before generating public Notes, Specific Research Reports, add-ons, worked solutions, or Online Essay Exam drafts.",
        "Ask the user to confirm the Exam type and whether Notes should be generated.",
        "Generate Notes before the exam-specific report when the user accepts Notes; skip Notes when the user declines them.",
        "Use coverage calibration to map knowledge signals into knowledge units before writing notes.",
        "Use Past Papers, Mock Papers, and official exam papers for MCQ or Short Answer high-frequency recurrence; ordinary Practice Material can provide context but does not count toward recurrence.",
        "Keep public Notes as knowledge-explanation documents; route confirmed exam types to separate Specific Research Reports.",
        "For mixed exam formats, activate every confirmed exam-type Sub Skill.",
        "For calculation, derivation, estimate, proof, data, or problem material, build a separate worked-solution teaching DOCX.",
        "For question solving, explain the target question, show matching knowledge, and retrieve only strict same-knowledge-point questions from user-supplied material.",
        "For question organization, generate a DOCX question list ordered by lecture order and containing questions only.",
    ]
    if route not in NOTES_CHOICE_ROUTES:
        notes = [
            "Use source hints as rough provenance labels.",
            "Complete the Direct Invocation Gate for unresolved route, source-role, and route-specific inputs before public output.",
            "Preserve the AcademicTaskContext original prompt, explicit route selection, relevant memory references, and page, slide, or time provenance.",
            "Default public output to English unless the user explicitly overrides the language for this task.",
        ]
    if route == "online_essay_exam_drafting":
        notes.extend([
            "Online Essay Exam is the only new Exam Type and is parallel to MCQ, Short Answer, Long Answer, Worked Solutions, and Essay Question.",
            "Before planning or drafting, ask source-permission questions covering Online Materials and Lecture Materials; unresolved permissions remain plan-changing items.",
            "Do not force Notes before Online Essay Exam drafting; use Notes as optional lecture review support when the user asks for them.",
        ])
    if extra_reading_requested(prompt) and route != "essay_preparation":
        if route == "online_essay_exam_drafting":
            notes.append("Extra Reading was requested; use it for the Online Essay Exam evidence map only when the confirmed source permissions allow it.")
        else:
            notes.append("Extra Reading was requested, but Extra Reading is available only when the confirmed Exam type includes essay.")
    review_targets = [
        target("exam_type_route", "confirm or correct the preliminary Exam type and route before writing", route_confirmed),
        target(
            "material_type_source_roles",
            "confirm or correct Material type and source roles before using sources",
            bool(confirmed_decision(decisions, "material_type_source_roles")),
        ),
    ]
    if route in NOTES_CHOICE_ROUTES:
        review_targets.append(target(
            "notes_output_choice",
            "confirm whether Notes should be generated before the exam-specific report",
            confirmed_decision(decisions, "notes_output_choice") is not None,
        ))
    if route == "online_essay_exam_drafting":
        review_targets.append(target(
            "online_essay_exam_source_permissions",
            "for Online Essay Exam, confirm whether Online Materials and Lecture Materials may be used before planning or drafting",
            online_essay_source_permissions_resolved(permissions),
        ))
        review_targets.append(target(
            "online_essay_exam_complete_draft_permission",
            "confirm that the assessment rules explicitly permit a complete draft before planning or drafting one",
            online_essay_complete_draft_permission_resolved(permissions),
        ))
    if route == "mixed_exam_preparation":
        review_targets.append(target(
            "confirmed_mixed_routes",
            "for Mixed routes, confirm the exact component routes before route-specific follow-up questions or output generation",
            bool(confirmed_decision(decisions, "confirmed_mixed_routes")),
        ))
    if route == "assessment_blueprint":
        review_targets.append(target(
            "assessment_blueprint_scope",
            "confirm the assessment scope and course knowledge units represented by the blueprint",
            bool(confirmed_decision(decisions, "assessment_blueprint_scope")),
        ))
    if route == "answer_evaluation":
        review_targets.append(target(
            "answer_evaluation_criteria",
            "confirm the student answer and source-grounded evaluation criteria before evaluation",
            not unresolved_required_inputs(route, metadata, bool(source_fragments)),
        ))
    if route == "timed_practice":
        review_targets.append(target(
            "timed_practice_duration",
            "confirm the timed-practice duration before generating the session",
            not unresolved_required_inputs(route, metadata, bool(source_fragments)),
        ))
    pending_targets = [item["id"] for item in review_targets if item["status"] != "explicitly_confirmed"]
    course = context.get("course_or_case") if isinstance(context.get("course_or_case"), dict) else None
    history_enabled_decision = confirmed_decision(decisions, "mastery_history_enabled")
    history_enabled = True if history_enabled_decision is None else bool(history_enabled_decision)
    history_course_available = bool(course and course.get("kind") == "course" and course.get("stable_id"))
    diagnosis = auto_diagnosis(route, outputs, summary, route_selection_status)
    permission_gate = online_essay_permission_gate(permissions) if route == "online_essay_exam_drafting" else None
    if permission_gate and permission_gate["status"] == "approved":
        diagnosis["review_requirement"] = "Preserve the resolved source rules and explicit complete-draft permission; confirm only remaining source-role, Notes, allowed-source, citation, output-format, and planning decisions before drafting."
    elif permission_gate and permission_gate["status"] in {"denied", "conflict"}:
        diagnosis["review_requirement"] = "A complete draft is blocked by the user's explicit assessment-permission denial. Planning support may continue, but drafting requires the user to explicitly change that permission."
    review_status = "confirmed" if not pending_targets else "pending_user_confirmation"
    output_status = "proposed_until_human_review"
    execution_blockers: list[dict[str, Any]] = []
    if permission_gate and permission_gate["status"] in {"denied", "conflict"}:
        review_status = "blocked_by_permission_denial"
        output_status = "blocked_by_permission_denial"
        execution_blockers.append({
            "id": (
                "online_essay_permission_conflict"
                if permission_gate["status"] == "conflict"
                else "online_essay_complete_draft_permission_denied"
            ),
            "message": (
                "Conflicting Online Essay Exam permission records must be resolved before execution."
                if permission_gate["status"] == "conflict"
                else "The assessment permission for a complete Online Essay Exam draft was explicitly denied."
            ),
        })
    return {
        "schema_version": 3,
        "context_contract": "AcademicTaskContext",
        "context_version": 1,
        "context_id": context.get("context_id"),
        "original_prompt": prompt,
        "route": route,
        "route_source": route_source,
        "route_selection": {
            "route_id": route,
            "status": route_selection_status,
        },
        "output_language": task_output_language(prompt, decisions, requested_output_language),
        "default_output_language": "en",
        "human_review_required": True,
        "review_status": review_status,
        "review_targets": review_targets,
        "pending_review_targets": pending_targets,
        "auto_diagnosis": diagnosis,
        "proposed_outputs": outputs,
        "outputs": outputs,
        "output_status": output_status,
        "permission_gate": permission_gate,
        "execution_blockers": execution_blockers,
        "output_name_policy": "Use user-requested filenames when supplied; otherwise generate a clear filename in the route's declared output media type from the source, course, prompt, or title.",
        "actions": actions,
        "source_summary": summary,
        "source_fragments": list(source_fragments or []),
        "relevant_memory": relevant_memory,
        "permissions": permissions,
        "decisions": decisions,
        "confirmed_mixed_routes": confirmed_decision(decisions, "confirmed_mixed_routes") or [],
        "course_or_case": course,
        "mastery_history": {
            "default_enabled": True,
            "enabled_for_task": history_enabled and history_course_available,
            "scope": "per_course",
            "course_stable_id": course.get("stable_id") if course else None,
            "status": "enabled" if history_enabled and history_course_available else ("disabled_by_user" if not history_enabled else "course_id_required"),
            "operations": ["enable", "disable", "export", "delete"],
            "adapter": "scripts/mastery_history.py",
        },
        "required_input_status": {
            "unresolved": unresolved_required_inputs(route, metadata, bool(source_fragments)),
        },
        "provenance_contract": {
            "fields": ["source_name", "locator", "page_number", "slide_number", "time_offset_seconds", "time_range"],
            "policy": "preserve page, slide, and time locators from source fragments through public or internal outputs",
        },
        "notes": notes,
    }


def load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    assert detect_route("build an assessment blueprint") == "assessment_blueprint"
    assert detect_route("evaluate this answer") == "answer_evaluation"
    assert detect_route("make a 30 minute timed practice") == "timed_practice"
    assert detect_route("make MCQ notes") == "mcq_preparation"
    assert detect_route("short answer definitions") == "short_answer_preparation"
    assert detect_route("give essay plans") == "essay_preparation"
    assert detect_route("draft this essay") == "essay_preparation"
    assert detect_route("essay draft") == "essay_preparation"
    assert detect_route("Online Essay Exam draft") == "online_essay_exam_drafting"
    assert detect_route("draft this online essay") == "online_essay_exam_drafting"
    assert detect_route("48h essay") == "online_essay_exam_drafting"
    assert detect_route("how do I answer this question") == "question_solving"
    assert detect_route("sort Practice Material by lecture order") == "question_organizing"
    assert detect_route("compile practice questions by lecture order") == "question_organizing"
    out = plan("prepare this course", {"documents": [{"source_hint": "knowledge_material", "knowledge_signals": ["definition"]}], "fragments": [{"knowledge_signals": ["mechanism"], "knowledge_roles": ["mechanism"]}]})
    assert out["route"] == "exam_prep_notes"
    assert "exam_habit_analysis_if_practice_material_exists" not in [action["id"] for action in out["actions"]]
    assert any(action["id"] == "practice_material_knowledge_signal_review" for action in out["actions"])
    assert any(action["id"] == "human_review_exam_material_output_confirmation" for action in out["actions"])
    assert any(action["id"] == "coverage_calibration" for action in out["actions"])
    assert not any(action["id"] == "extra_reading_discovery" for action in out["actions"])
    assert out["human_review_required"] is True
    assert out["review_status"] == "pending_user_confirmation"
    assert [target["id"] for target in out["review_targets"]] == [
        "exam_type_route",
        "material_type_source_roles",
        "notes_output_choice",
    ]
    assert out["auto_diagnosis"]["proposed_outputs"] == ["docx_notes"]
    assert out["proposed_outputs"] == ["docx_notes"]
    assert out["outputs"] == ["docx_notes"]
    past = plan("prepare this course", {
        "documents": [{"source_hint": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True}}],
        "fragments": [{"knowledge_signals": ["calculation"], "knowledge_roles": ["calculation"]}],
    })
    assert past["outputs"] == ["docx_notes", "exam_type_related_addon_docx"]
    assert past["proposed_outputs"] == ["docx_notes", "exam_type_related_addon_docx"]
    assert any(action["id"] == "question_based_exam_type_related_addon" for action in past["actions"])
    practical_without_questions = plan("prepare this course", {
        "documents": [{"source_hint": "knowledge_material", "question_signals": {"has_questions": False, "has_practical_questions": False}}],
        "fragments": [{"knowledge_signals": ["method"], "knowledge_roles": ["method"]}],
    })
    assert practical_without_questions["outputs"] == ["docx_notes"]
    practical_with_questions = plan("prepare this course", {
        "documents": [{"source_hint": "knowledge_material", "question_signals": {"has_questions": True, "has_practical_questions": True}}],
        "fragments": [{"knowledge_signals": ["data_interpretation"], "knowledge_roles": ["data_interpretation"]}],
    })
    assert practical_with_questions["outputs"] == ["docx_notes", "exam_type_related_addon_docx"]
    practical_worked = plan("prepare this course", {
        "documents": [{"source_hint": "knowledge_material", "question_signals": {"has_questions": True, "has_practical_questions": True, "has_practical_worked_questions": True}}],
        "fragments": [{"knowledge_signals": ["calculation"], "knowledge_roles": ["calculation"]}],
    })
    assert practical_worked["outputs"] == ["docx_notes", "practical_worked_solutions_docx"]
    assert practical_worked["auto_diagnosis"]["mixed_or_unclear"] is False
    assert any(action["id"] == "practical_worked_solutions" for action in practical_worked["actions"])
    past_worked = plan("prepare this course", {
        "documents": [{"source_hint": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True, "has_practical_worked_questions": True}}],
        "fragments": [{"knowledge_signals": ["calculation"], "knowledge_roles": ["calculation"]}],
    })
    assert past_worked["outputs"] == ["docx_notes", "practical_worked_solutions_docx"]
    assert plan("make MCQ notes")["outputs"] == ["docx_notes", "mcq_exam_type_related_addon"]
    assert "online_essay_exam_source_permissions" not in [target["id"] for target in plan("make MCQ notes")["review_targets"]]
    assert plan("short answer definitions")["outputs"] == ["docx_notes", "short_answer_exam_type_related_addon"]
    assert "online_essay_exam_source_permissions" not in [target["id"] for target in plan("short answer definitions")["review_targets"]]
    assert plan("long answer worked problem")["outputs"] == ["docx_notes", "practical_worked_solutions_docx"]
    assert plan("essay plans")["outputs"] == ["docx_notes", "essay_exam_type_related_addon"]
    online = plan("Online Essay Exam using online materials")
    assert online["route"] == "online_essay_exam_drafting"
    assert online["outputs"] == ["online_essay_exam_draft", "online_essay_exam_draft_docx_if_requested"]
    assert "online_essay_exam_source_permissions" in [target["id"] for target in online["review_targets"]]
    assert "explicit assessment permission for a complete draft" in online["auto_diagnosis"]["review_requirement"]
    assert "notes_generation_if_user_accepts" not in [action["id"] for action in online["actions"]]
    assert any(action["id"] == "online_materials_permission_review" for action in online["actions"])
    assert any("Online Materials and Lecture Materials" in note for note in online["notes"])
    assert plan("solve this question")["outputs"] == ["question_solution_report"]
    assert plan("organize past paper questions")["outputs"] == ["organized_questions_docx"]
    assert any(action["id"] == "extra_reading_essay_enrichment" for action in plan("essay plans")["actions"])
    assert not any(action["id"] == "extra_reading_essay_enrichment" for action in plan("use extra reading in these notes")["actions"])
    assert plan("prepare this course")["auto_diagnosis"]["mixed_or_unclear"] is False
    assert plan("identify exam format")["route"] == "mixed_exam_preparation"
    assert any(action["id"] == "human_review_exam_material_output_confirmation" for action in plan("identify exam format")["actions"])
    assert "confirmed_mixed_routes" in [target["id"] for target in plan("identify exam format")["review_targets"]]
    assert out["source_summary"]["coverage_profile"]["knowledge_signal_counts"]["mechanism"] == 1
    context = {
        "contract": "AcademicTaskContext",
        "version": 1,
        "context_id": "ctx-exam-0001",
        "created_at": "2026-07-09T12:00:00Z",
        "original_prompt": "Use the route already selected by the user.",
        "route_selection": {"route_id": "answer_evaluation", "status": "explicitly_confirmed"},
        "course_or_case": {"kind": "course", "stable_id": "BIO101", "label": "Biology"},
        "source_references": [{"source_id": "source-0001", "trust_status": "trusted"}],
        "relevant_memory": [{"store": "everything-university/mastery", "record_ids": ["BIO101-K2"], "purpose": "reuse weakness history"}],
        "permissions": [],
        "decisions": [{"decision_id": "output_language", "value": "fr", "status": "explicitly_confirmed"}],
        "requested_output_language": "fr",
        "metadata": {"student_answer": "A receptor activates a kinase.", "evaluation_criteria": ["receptor activation"]},
    }
    fragments = [{"id": "F1", "source_id": "source-0001", "text": "Receptor activation.", "page_number": 3, "knowledge_roles": ["mechanism"]}]
    adapted = plan(academic_task_context=context, source_fragments=fragments)
    assert adapted["route"] == "answer_evaluation"
    assert adapted["route_source"] == "academic_task_context.route_selection"
    assert adapted["original_prompt"] == context["original_prompt"]
    assert adapted["source_summary"]["fragment_count"] == 1
    assert adapted["relevant_memory"] == context["relevant_memory"]
    assert adapted["output_language"] == "fr"
    assert adapted["default_output_language"] == "en"
    assert adapted["review_targets"][0]["status"] == "explicitly_confirmed"
    assert adapted["mastery_history"]["enabled_for_task"] is True
    mixed_context = dict(context)
    mixed_context["route_selection"] = {"route_id": "mixed_exam_preparation", "status": "explicitly_confirmed"}
    mixed_context["decisions"] = []
    mixed_adapted = plan(academic_task_context=mixed_context, source_fragments=fragments)
    assert "confirmed_mixed_routes" in mixed_adapted["pending_review_targets"]
    online_context = dict(context)
    online_context["route_selection"] = {"route_id": "online_essay_exam_drafting", "status": "explicitly_confirmed"}
    online_context["permissions"] = []
    online_adapted = plan(academic_task_context=online_context, source_fragments=fragments)
    assert "online_essay_exam_source_permissions" in online_adapted["pending_review_targets"]
    assert "online_essay_exam_complete_draft_permission" in online_adapted["pending_review_targets"]
    denied_context = dict(online_context)
    denied_context["permissions"] = [
        {"permission_id": "online_materials_use", "scope": "Online Materials", "status": "denied", "confirmed_at": "2026-07-09T12:00:00Z"},
        {"permission_id": "lecture_materials_use", "scope": "Lecture Materials", "status": "explicitly_confirmed", "confirmed_at": "2026-07-09T12:00:00Z"},
        {"permission_id": "online_essay_complete_draft_permission", "scope": "Complete draft", "status": "denied", "confirmed_at": "2026-07-09T12:00:00Z"},
    ]
    denied_plan = plan(academic_task_context=denied_context, source_fragments=fragments)
    assert denied_plan["permission_gate"]["status"] == "denied"
    assert denied_plan["review_status"] == "blocked_by_permission_denial"
    assert denied_plan["output_status"] == "blocked_by_permission_denial"
    assert "online_essay_exam_source_permissions" not in denied_plan["pending_review_targets"]
    assert "online_essay_exam_complete_draft_permission" not in denied_plan["pending_review_targets"]
    assert denied_plan["execution_blockers"][0]["id"] == "online_essay_complete_draft_permission_denied"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="make notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--academic-task-context")
    parser.add_argument("--source-fragments")
    parser.add_argument("--route")
    parser.add_argument("--route-status", choices=["suggested", "explicitly_confirmed"], default="suggested")
    parser.add_argument("--relevant-memory")
    parser.add_argument("--output-language")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    context = load_json(args.academic_task_context)
    fragments = load_json(args.source_fragments)
    memory = load_json(args.relevant_memory)
    result = plan(
        args.prompt,
        load_json(args.source_scan),
        academic_task_context=context,
        source_fragments=(fragments.get("source_fragments") or fragments.get("fragments") or []) if isinstance(fragments, dict) else fragments,
        route_selection={"route_id": args.route, "status": args.route_status} if args.route else None,
        relevant_memory=memory.get("relevant_memory", []) if isinstance(memory, dict) else memory,
        requested_output_language=args.output_language,
    )
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
