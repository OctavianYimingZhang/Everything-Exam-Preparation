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
    "coverage_calibration",
    "extra_reading_discovery",
    "extra_reading_topic_matching",
    "course_knowledge_map",
    "extra_reading_notes_enrichment",
]

ROUTES: dict[str, list[str]] = {
    "exam_prep_notes": BASE_ACTIONS + [
        "exam_prep_notes",
    ],
    "exam_mode_diagnosis": ["source_inventory", "exam_mode_diagnosis"],
    "mcq_preparation": BASE_ACTIONS + [
        "mcq_exam_habit_analysis",
        "mcq_notes_enrichment",
    ],
    "short_answer_preparation": BASE_ACTIONS + [
        "short_answer_habit_analysis",
        "definition_and_mark_point_highlights",
        "explain_answer_examples",
    ],
    "long_answer_preparation": BASE_ACTIONS + [
        "practice_question_walkthroughs",
        "example_answers",
    ],
    "essay_preparation": BASE_ACTIONS + [
        "exam_ready_essay_paragraphs",
        "extra_reading_essay_enrichment",
        "module_covering_essay_questions",
        "example_essays",
    ],
}

ROUTE_OUTPUTS = {
    "exam_mode_diagnosis": ["chat_report"],
    "mcq_preparation": ["mcq_exam_type_related_addon"],
    "short_answer_preparation": ["short_answer_exam_type_related_addon"],
    "long_answer_preparation": ["long_answer_practical_data_problem_exam_type_related_addon"],
    "essay_preparation": ["essay_exam_type_related_addon"],
}


def detect_route(prompt: str) -> str:
    p = (prompt or "").lower()
    if any(k in p for k in ["essay", "in-campus", "model essay", "example essay", "thesis"]):
        return "essay_preparation"
    if any(k in p for k in ["mcq", "sba", "single best", "multiple choice", "true/false"]):
        return "mcq_preparation"
    if any(k in p for k in ["short answer", "saq", "definition", "define", "state", "list question"]):
        return "short_answer_preparation"
    if any(k in p for k in ["long answer", "walkthrough", "worked answer", "practical", "data", "problem", "calculate"]):
        return "long_answer_preparation"
    if any(k in p for k in ["exam mode", "exam format", "how is", "diagnose", "identify format"]):
        return "exam_mode_diagnosis"
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
        },
        "coverage_profile": {
            "knowledge_signal_counts": signal_counts,
            "knowledge_role_counts": role_counts,
            "knowledge_unit_candidate_count": unit_candidates,
        },
    }


def question_addon_required(source_scan: dict[str, Any] | None) -> bool:
    if not source_scan:
        return False
    for doc in source_scan.get("documents", []) or []:
        signals = doc.get("question_signals", {}) or {}
        if signals.get("has_past_paper") or signals.get("has_practical_questions"):
            return True
    return False


def plan(prompt: str, source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    route = detect_route(prompt)
    actions = [{"id": action, "purpose": action.replace("_", " ")} for action in ROUTES[route]]
    outputs = ROUTE_OUTPUTS.get(route, ["docx_notes"])
    if route == "exam_prep_notes" and question_addon_required(source_scan):
        outputs = ["docx_notes", "exam_type_related_addon_docx"]
        actions.append({
            "id": "question_based_exam_type_related_addon",
            "purpose": "build separate exam type related addon from past paper or question practical material",
        })
    return {
        "schema_version": 2,
        "route": route,
        "outputs": outputs,
        "output_name_policy": "Use user-requested filenames when supplied; otherwise generate a clear DOCX filename from the source, course, prompt, or note title.",
        "actions": actions,
        "source_summary": source_summary(source_scan),
        "notes": [
            "Use source hints as rough provenance labels.",
            "Use coverage calibration to map knowledge signals into knowledge units before writing notes.",
            "Use practice material as knowledge-signal evidence for repeated concepts, methods, calculations, source difficulty, and coverage density.",
            "Use Extra Reading to add molecular detail, mechanism explanation, experimental evidence, and essay depth.",
            "Keep plain Notes explanation-only; route Past Paper and question Practical material to a separate Exam Type Related DOCX.",
        ],
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
    assert any(action["id"] == "coverage_calibration" for action in out["actions"])
    assert any(action["id"] == "extra_reading_discovery" for action in out["actions"])
    assert out["outputs"] == ["docx_notes"]
    past = plan("prepare this course", {
        "documents": [{"source_hint": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True}}],
        "fragments": [{"knowledge_signals": ["calculation"], "knowledge_roles": ["calculation"]}],
    })
    assert past["outputs"] == ["docx_notes", "exam_type_related_addon_docx"]
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
    assert plan("make MCQ notes")["outputs"] == ["mcq_exam_type_related_addon"]
    assert plan("short answer definitions")["outputs"] == ["short_answer_exam_type_related_addon"]
    assert plan("long answer worked problem")["outputs"] == ["long_answer_practical_data_problem_exam_type_related_addon"]
    assert plan("essay plans")["outputs"] == ["essay_exam_type_related_addon"]
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
