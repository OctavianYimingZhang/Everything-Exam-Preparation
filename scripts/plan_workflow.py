#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PRIMARY_OUTPUT = "Exam_Preparation_Notes.docx"

ROUTES: dict[str, list[str]] = {
    "exam_prep_notes": [
        "source_inventory",
        "fragment_index",
        "course_knowledge_map",
        "exam_habit_analysis_if_practice_material_exists",
        "exam_prep_notes",
    ],
    "exam_mode_diagnosis": ["source_inventory", "exam_mode_diagnosis"],
    "mcq_preparation": [
        "source_inventory",
        "fragment_index",
        "course_knowledge_map",
        "mcq_exam_habit_analysis",
        "mcq_notes_enrichment",
    ],
    "short_answer_preparation": [
        "source_inventory",
        "fragment_index",
        "course_knowledge_map",
        "short_answer_habit_analysis",
        "definition_and_mark_point_highlights",
        "explain_answer_examples",
    ],
    "long_answer_preparation": [
        "source_inventory",
        "fragment_index",
        "course_knowledge_map",
        "practice_question_walkthroughs",
        "example_answers",
    ],
    "essay_preparation": [
        "source_inventory",
        "fragment_index",
        "course_knowledge_map",
        "exam_ready_essay_paragraphs",
        "module_covering_essay_questions",
        "example_essays",
    ],
}

ROUTE_OUTPUTS = {
    "exam_mode_diagnosis": ["chat_report"],
    "essay_preparation": [PRIMARY_OUTPUT, "Example_Essay.docx"],
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
        return {"document_count": 0, "fragment_count": 0, "categories": {}}
    cats: dict[str, int] = {}
    for doc in source_scan.get("documents", []):
        cat = str(doc.get("category") or "other_material")
        cats[cat] = cats.get(cat, 0) + 1
    return {
        "document_count": len(source_scan.get("documents", [])),
        "fragment_count": len(source_scan.get("fragments", [])),
        "categories": cats,
    }


def plan(prompt: str, source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    route = detect_route(prompt)
    actions = [{"id": action, "purpose": action.replace("_", " ")} for action in ROUTES[route]]
    outputs = ROUTE_OUTPUTS.get(route, [PRIMARY_OUTPUT])
    return {
        "schema_version": 2,
        "route": route,
        "outputs": outputs,
        "actions": actions,
        "source_summary": source_summary(source_scan),
        "notes": [
            "Use knowledge material to explain the course.",
            "Use practice material to identify repeated topics, command words, question types, and answer habits.",
            "Connect knowledge to likely answer use in the selected exam mode.",
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
    out = plan("prepare this course", {"documents": [{"category": "knowledge_material"}], "fragments": [1, 2]})
    assert out["route"] == "exam_prep_notes"
    assert out["source_summary"]["fragment_count"] == 2


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
