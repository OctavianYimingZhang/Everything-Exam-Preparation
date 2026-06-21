#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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

ROUTES: dict[str, list[str]] = {
    "exam_prep_notes": BASE_ACTIONS + [
        "exam_prep_notes",
    ],
    "mcq_preparation": BASE_ACTIONS + [
        "mcq_specific_research_report",
    ],
    "short_answer_preparation": BASE_ACTIONS + [
        "short_answer_specific_research_report",
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
}

ROUTE_OUTPUTS = {
    "mcq_preparation": ["docx_notes", "mcq_exam_type_related_addon"],
    "short_answer_preparation": ["docx_notes", "short_answer_exam_type_related_addon"],
    "long_answer_preparation": ["docx_notes", "long_answer_practical_data_problem_exam_type_related_addon"],
    "worked_solution_preparation": ["docx_notes", "practical_worked_solutions_docx"],
    "essay_preparation": ["docx_notes", "essay_exam_type_related_addon"],
    "mixed_exam_preparation": ["docx_notes", "exam_type_related_addon_docx"],
    "question_solving": ["question_solution_report"],
    "question_organizing": ["organized_questions_docx"],
}

ROUTE_LABELS = {
    "exam_prep_notes": "Notes",
    "mcq_preparation": "MCQ",
    "short_answer_preparation": "Short Answer",
    "long_answer_preparation": "Long Answer or Practical/Data/Problem",
    "worked_solution_preparation": "Worked Solutions",
    "essay_preparation": "Essay",
    "mixed_exam_preparation": "Mixed",
    "question_solving": "Question Solving",
    "question_organizing": "Question Organization",
}


def detect_route(prompt: str) -> str:
    p = (prompt or "").lower()
    if any(k in p for k in ["organize past paper", "organise past paper", "sort past paper", "organize practice", "organise practice", "question organizer", "question list"]):
        return "question_organizing"
    if any(k in p for k in ["solve this question", "how to solve", "how do i solve", "work through this question", "question walkthrough", "same knowledge point"]):
        return "question_solving"
    if any(k in p for k in ["essay", "in-campus", "model essay", "example essay", "thesis"]):
        return "essay_preparation"
    if any(k in p for k in ["mcq", "sba", "single best", "multiple choice", "true/false"]):
        return "mcq_preparation"
    if any(k in p for k in ["short answer", "saq", "definition", "define", "state", "list question"]):
        return "short_answer_preparation"
    if any(k in p for k in ["worked answer", "worked solution", "calculate", "derive", "derivation", "estimate", "prove", "proof", "problem"]):
        return "worked_solution_preparation"
    if any(k in p for k in ["long answer", "walkthrough", "practical", "data"]):
        return "long_answer_preparation"
    if any(k in p for k in ["exam mode", "exam format", "how is", "diagnose", "identify format", "mixed"]):
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


def auto_diagnosis(route: str, outputs: list[str], summary: dict[str, Any]) -> dict[str, Any]:
    source_hints = summary.get("source_hints", {})
    question_material = summary.get("question_material", {})
    coverage_profile = summary.get("coverage_profile", {})
    role_counts = coverage_profile.get("knowledge_role_counts", {})
    mixed_or_unclear = bool(
        len([count for count in source_hints.values() if count]) > 1
        or bool(source_hints.get("other_material"))
        or (question_material.get("has_past_paper_questions") and question_material.get("has_practical_questions"))
    )
    return {
        "status": "preliminary",
        "route": route,
        "exam_type": ROUTE_LABELS.get(route, route),
        "material_roles": source_hints,
        "knowledge_role_counts": role_counts,
        "question_material": question_material,
        "proposed_outputs": outputs,
        "mixed_or_unclear": mixed_or_unclear,
        "review_requirement": "Confirm or correct route, source roles, route-specific follow-up choices, and whether Notes should be generated before generating public Notes, Specific Research Reports, add-ons, or worked solutions.",
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


def plan(prompt: str, source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    route = detect_route(prompt)
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
        "Display the Auto-diagnosis review plan and complete human review before generating public Notes, Specific Research Reports, add-ons, or worked solutions.",
        "Ask the user to confirm the Exam type and whether Notes should be generated.",
        "Generate Notes before the exam-specific report when the user accepts Notes; skip Notes when the user declines them.",
        "Use coverage calibration to map knowledge signals into knowledge units before writing notes.",
        "Use practice material as knowledge-signal evidence for repeated concepts, methods, calculations, source difficulty, and coverage density.",
        "Keep public Notes as knowledge-explanation documents; route confirmed exam types to separate Specific Research Reports.",
        "For mixed exam formats, activate every confirmed exam-type Sub Skill.",
        "For calculation, derivation, estimate, proof, data, or problem material, build a separate worked-solution teaching DOCX.",
        "For question solving, explain the target question, show matching knowledge, and retrieve only strict same-knowledge-point questions from user-supplied material.",
        "For question organization, generate a DOCX question list ordered by lecture order and containing questions only.",
    ]
    if extra_reading_requested(prompt) and route != "essay_preparation":
        notes.append("Extra Reading was requested, but Extra Reading is available only when the confirmed Exam type includes essay.")
    return {
        "schema_version": 2,
        "route": route,
        "human_review_required": True,
        "review_status": "pending_user_confirmation",
        "review_targets": [
            {
                "id": "exam_type_route",
                "purpose": "confirm or correct the preliminary Exam type and route before writing",
            },
            {
                "id": "material_type_source_roles",
                "purpose": "confirm or correct Material type and source roles before using sources",
            },
            {
                "id": "notes_output_choice",
                "purpose": "confirm whether Notes should be generated before the exam-specific report",
            },
        ],
        "auto_diagnosis": auto_diagnosis(route, outputs, summary),
        "proposed_outputs": outputs,
        "outputs": outputs,
        "output_status": "proposed_until_human_review",
        "output_name_policy": "Use user-requested filenames when supplied; otherwise generate a clear DOCX filename from the source, course, prompt, or note title.",
        "actions": actions,
        "source_summary": summary,
        "notes": notes,
    }


def load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    assert detect_route("make MCQ notes") == "mcq_preparation"
    assert detect_route("short answer definitions") == "short_answer_preparation"
    assert detect_route("give essay plans") == "essay_preparation"
    out = plan("prepare this course", {"documents": [{"source_hint": "knowledge_material", "knowledge_signals": ["definition"]}], "fragments": [{"knowledge_signals": ["mechanism"], "knowledge_roles": ["mechanism"]}]})
    assert out["route"] == "exam_prep_notes"
    assert "exam_habit_analysis_if_practice_material_exists" not in [action["id"] for action in out["actions"]]
    assert any(action["id"] == "practice_material_knowledge_signal_review" for action in out["actions"])
    assert any(action["id"] == "human_review_exam_material_output_confirmation" for action in out["actions"])
    assert any(action["id"] == "coverage_calibration" for action in out["actions"])
    assert not any(action["id"] == "extra_reading_discovery" for action in out["actions"])
    assert out["human_review_required"] is True
    assert out["review_status"] == "pending_user_confirmation"
    assert [target["id"] for target in out["review_targets"]] == ["exam_type_route", "material_type_source_roles", "notes_output_choice"]
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
    assert plan("short answer definitions")["outputs"] == ["docx_notes", "short_answer_exam_type_related_addon"]
    assert plan("long answer worked problem")["outputs"] == ["docx_notes", "practical_worked_solutions_docx"]
    assert plan("essay plans")["outputs"] == ["docx_notes", "essay_exam_type_related_addon"]
    assert plan("solve this question")["outputs"] == ["question_solution_report"]
    assert plan("organize past paper questions")["outputs"] == ["organized_questions_docx"]
    assert any(action["id"] == "extra_reading_essay_enrichment" for action in plan("essay plans")["actions"])
    assert not any(action["id"] == "extra_reading_essay_enrichment" for action in plan("use extra reading in these notes")["actions"])
    assert plan("prepare this course")["auto_diagnosis"]["mixed_or_unclear"] is False
    assert plan("identify exam format")["route"] == "mixed_exam_preparation"
    assert any(action["id"] == "human_review_exam_material_output_confirmation" for action in plan("identify exam format")["actions"])
    assert out["source_summary"]["coverage_profile"]["knowledge_signal_counts"]["mechanism"] == 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="make notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = plan(args.prompt, load_json(args.source_scan))
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
