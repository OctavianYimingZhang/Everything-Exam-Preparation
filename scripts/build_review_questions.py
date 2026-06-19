#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROUTE_LABELS = {
    "exam_prep_notes": "Notes",
    "exam_mode_diagnosis": "Exam mode diagnosis",
    "mcq_preparation": "MCQ",
    "short_answer_preparation": "Short Answer",
    "long_answer_preparation": "Long Answer or Practical/Data/Problem",
    "worked_solution_preparation": "Worked Solutions",
    "essay_preparation": "Essay",
    "mixed_exam_preparation": "Mixed",
}

ROUTE_SHORT_LABELS = {
    "exam_prep_notes": "Notes",
    "exam_mode_diagnosis": "Diagnosis",
    "mcq_preparation": "MCQ",
    "short_answer_preparation": "Short Answer",
    "long_answer_preparation": "Long Answer",
    "worked_solution_preparation": "Worked",
    "essay_preparation": "Essay",
    "mixed_exam_preparation": "Mixed",
}

ROLE_LABELS = {
    "knowledge_material": "knowledge material",
    "practice_material": "practice material",
    "marking_material": "marking material",
    "style_reference": "style reference",
    "extra_reading_source": "Extra Reading",
    "other_material": "mixed or unclear material",
}

ROLE_SHORT_LABELS = {
    "knowledge_material": "Knowledge",
    "practice_material": "Practice",
    "marking_material": "Marking",
    "style_reference": "Style",
    "extra_reading_source": "Extra Reading",
    "other_material": "Unclear",
}

OUTPUT_LABELS = {
    "docx_notes": "Notes",
    "exam_type_related_addon_docx": "Exam Type Related add-on",
    "mcq_exam_type_related_addon": "MCQ add-on",
    "short_answer_exam_type_related_addon": "Short Answer add-on",
    "long_answer_practical_data_problem_exam_type_related_addon": "Long Answer or Practical/Data/Problem add-on",
    "essay_exam_type_related_addon": "Essay add-on",
    "practical_worked_solutions_docx": "Worked Solutions",
    "chat_report": "chat diagnosis",
}


def load_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def documents(source_scan: dict[str, Any]) -> list[dict[str, Any]]:
    docs = source_scan.get("documents", [])
    return docs if isinstance(docs, list) else []


def fragments(source_scan: dict[str, Any]) -> list[dict[str, Any]]:
    frags = source_scan.get("fragments", [])
    return frags if isinstance(frags, list) else []


def count_source_roles(source_scan: dict[str, Any], workflow_plan: dict[str, Any]) -> dict[str, int]:
    plan_roles = (
        workflow_plan.get("auto_diagnosis", {}).get("material_roles")
        or workflow_plan.get("source_summary", {}).get("source_hints")
        or {}
    )
    if plan_roles:
        return {str(key): int(value) for key, value in plan_roles.items() if value}
    counts: dict[str, int] = {}
    for doc in documents(source_scan):
        role = str(doc.get("source_hint") or doc.get("category") or "").strip()
        if role:
            counts[role] = counts.get(role, 0) + 1
    return counts


def count_knowledge_roles(source_scan: dict[str, Any], workflow_plan: dict[str, Any]) -> dict[str, int]:
    plan_roles = (
        workflow_plan.get("auto_diagnosis", {}).get("knowledge_role_counts")
        or workflow_plan.get("source_summary", {}).get("coverage_profile", {}).get("knowledge_role_counts")
        or {}
    )
    if plan_roles:
        return {str(key): int(value) for key, value in plan_roles.items() if value}
    counts: dict[str, int] = {}
    for item in documents(source_scan) + fragments(source_scan):
        for role in item.get("knowledge_roles", []) or []:
            role = str(role)
            counts[role] = counts.get(role, 0) + 1
    return counts


def question_flags(source_scan: dict[str, Any], workflow_plan: dict[str, Any]) -> dict[str, bool]:
    plan_flags = (
        workflow_plan.get("auto_diagnosis", {}).get("question_material")
        or workflow_plan.get("source_summary", {}).get("question_material")
        or {}
    )
    flags = {
        "has_past_paper_questions": bool(plan_flags.get("has_past_paper_questions")),
        "has_practical_questions": bool(plan_flags.get("has_practical_questions")),
        "has_practical_worked_questions": bool(plan_flags.get("has_practical_worked_questions")),
        "has_questions": False,
    }
    for doc in documents(source_scan):
        signals = doc.get("question_signals", {}) or {}
        flags["has_past_paper_questions"] = flags["has_past_paper_questions"] or bool(signals.get("has_past_paper"))
        flags["has_practical_questions"] = flags["has_practical_questions"] or bool(signals.get("has_practical_questions"))
        flags["has_practical_worked_questions"] = flags["has_practical_worked_questions"] or bool(signals.get("has_practical_worked_questions"))
        flags["has_questions"] = flags["has_questions"] or bool(signals.get("has_questions"))
    flags["has_questions"] = flags["has_questions"] or any(
        flags[name]
        for name in ["has_past_paper_questions", "has_practical_questions", "has_practical_worked_questions"]
    )
    return flags


def short_counts(counts: dict[str, int], labels: dict[str, str] | None = None) -> str:
    if not counts:
        return "no clear role counts"
    labels = labels or {}
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    parts = [f"{labels.get(key, key)}: {value}" for key, value in ordered[:4]]
    return ", ".join(parts)


def output_names(outputs: list[str]) -> str:
    if not outputs:
        return "no public output"
    return " + ".join(OUTPUT_LABELS.get(output, output) for output in outputs)


def proposed_outputs(workflow_plan: dict[str, Any]) -> list[str]:
    outputs = workflow_plan.get("proposed_outputs") or workflow_plan.get("outputs") or []
    return [str(output) for output in outputs]


def option(label: str, description: str) -> dict[str, str]:
    return {"label": label, "description": description}


def unique_options(options: list[dict[str, str]], limit: int = 3) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in options:
        label = item["label"]
        key = label.replace(" (Recommended)", "")
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
        if len(out) == limit:
            break
    return out


def exam_type_question(workflow_plan: dict[str, Any], source_scan: dict[str, Any]) -> dict[str, Any]:
    route = str(workflow_plan.get("route") or workflow_plan.get("auto_diagnosis", {}).get("route") or "exam_prep_notes")
    route_label = ROUTE_LABELS.get(route, route)
    route_short_label = ROUTE_SHORT_LABELS.get(route, route_label)
    flags = question_flags(source_scan, workflow_plan)
    role_counts = count_source_roles(source_scan, workflow_plan)
    knowledge_roles = count_knowledge_roles(source_scan, workflow_plan)
    has_calculation = any(role in knowledge_roles for role in ["calculation", "data_interpretation", "problem_solving"])
    mixed = (
        bool(workflow_plan.get("auto_diagnosis", {}).get("mixed_or_unclear"))
        or len([value for value in role_counts.values() if value]) > 1
        or bool(role_counts.get("other_material"))
    )
    options = [
        option(
            f"{route_short_label} route (Recommended)",
            f"Use the preliminary {route_label} route from the prompt and source scan; question signals are {flags}.",
        )
    ]
    if mixed:
        options.append(option(
            "Mixed route",
            "Keep multiple exam signals active and ask again if the route needs splitting after source review.",
        ))
    if flags["has_practical_worked_questions"] or has_calculation:
        options.append(option(
            "Worked solutions",
            "Prioritise worked-solution teaching notes because calculation, derivation, data, or problem signals are visible.",
        ))
    if flags["has_past_paper_questions"] or flags["has_practical_questions"]:
        options.append(option(
            "Question add-on",
            "Treat question material as an Exam Type Related add-on while keeping Notes knowledge-only.",
        ))
    if route != "exam_prep_notes":
        options.append(option(
            "Notes route",
            "Use the supplied material mainly for explanation-only Notes instead of an exam-mode add-on.",
        ))
    options.append(option(
        "Diagnosis report",
        "Stop at exam-mode diagnosis if the source pack is not yet ready for Notes or add-on drafting.",
    ))
    return {
        "header": "Exam Type",
        "id": "exam_type_route",
        "question": "Confirm or correct the Exam type and route before any public output is drafted.",
        "options": unique_options(options),
    }


def material_question(workflow_plan: dict[str, Any], source_scan: dict[str, Any]) -> dict[str, Any]:
    roles = count_source_roles(source_scan, workflow_plan)
    if not roles:
        roles = {"other_material": max(1, len(documents(source_scan)))}
    dominant_role = sorted(roles.items(), key=lambda item: (-item[1], item[0]))[0][0]
    dominant_label = ROLE_LABELS.get(dominant_role, dominant_role.replace("_", " "))
    dominant_short_label = ROLE_SHORT_LABELS.get(dominant_role, dominant_label.title())
    if len([value for value in roles.values() if value]) > 1:
        recommended = option(
            "Mixed roles (Recommended)",
            f"Use the detected source-role split: {short_counts(roles, ROLE_LABELS)}.",
        )
    else:
        recommended = option(
            f"{dominant_short_label} (Recommended)",
            f"Treat the source pack mainly as {dominant_label}; detected role counts are {short_counts(roles, ROLE_LABELS)}.",
        )
    options = [recommended]
    if dominant_role != "knowledge_material":
        options.append(option(
            "Knowledge material",
            "Reclassify the main readable files as course-facing knowledge material for Notes coverage.",
        ))
    if dominant_role != "practice_material":
        options.append(option(
            "Practice material",
            "Treat question-like files as practice material that informs exam add-ons and Notes coverage signals.",
        ))
    if "marking_material" in roles:
        options.append(option(
            "Marking material",
            "Use mark schemes, answer keys, or solutions as answer evidence and verification support.",
        ))
    if "extra_reading_source" in roles:
        options.append(option(
            "Extra Reading",
            "Use research, textbook, DOI, PMID, or reference-like material for essay-style enrichment and matched knowledge-unit support.",
        ))
    custom_option = option(
        "Custom roles",
        "Provide corrected source roles file by file where the automatic source hints are incomplete.",
    )
    options.append(custom_option)
    selected_options = unique_options(options, limit=2)
    if not any(item["label"] == "Custom roles" for item in selected_options):
        selected_options.append(custom_option)
    return {
        "header": "Materials",
        "id": "material_type_source_roles",
        "question": "Confirm or correct Material type and source roles before sources are used for writing.",
        "options": selected_options,
    }


def output_question(workflow_plan: dict[str, Any], source_scan: dict[str, Any]) -> dict[str, Any]:
    outputs = proposed_outputs(workflow_plan)
    route = str(workflow_plan.get("route") or "exam_prep_notes")
    flags = question_flags(source_scan, workflow_plan)
    label = output_names(outputs)
    if outputs == ["docx_notes"]:
        recommended_label = "Notes focus (Recommended)"
    elif outputs == ["docx_notes", "exam_type_related_addon_docx"]:
        recommended_label = "Notes + Add-on (Recommended)"
    elif outputs == ["docx_notes", "practical_worked_solutions_docx"]:
        recommended_label = "Notes + Worked (Recommended)"
    elif outputs == ["practical_worked_solutions_docx"]:
        recommended_label = "Worked focus (Recommended)"
    elif outputs:
        recommended_label = "Proposed set (Recommended)"
    else:
        recommended_label = "Diagnosis report (Recommended)"
    options = [
        option(
            recommended_label,
            f"Generate the preliminary output set: {label}.",
        )
    ]
    if outputs != ["docx_notes"]:
        options.append(option(
            "Notes focus",
            "Generate explanation Notes as the selected output set and keep add-on or worked-solution outputs for a separate request.",
        ))
    elif flags["has_past_paper_questions"] or flags["has_practical_questions"]:
        options.append(option(
            "Notes + Add-on",
            "Generate Notes plus a separate Exam Type Related add-on from question or practical material.",
        ))
    elif flags["has_practical_worked_questions"] or "practical_worked_solutions_docx" in outputs:
        options.append(option(
            "Notes + Worked",
            "Generate Notes plus detailed worked-solution teaching notes for calculation, data, or problem material.",
        ))
    elif route != "exam_prep_notes":
        options.append(option(
            "Add-on focus",
            "Generate the route-specific exam add-on as the selected output set and keep full explanation Notes for a separate request.",
        ))
    custom_option = option(
        "Custom outputs",
        "Specify the exact file set before rendering begins.",
    )
    options.append(custom_option)
    selected_options = unique_options(options, limit=2)
    if not any(item["label"] == "Custom outputs" for item in selected_options):
        selected_options.append(custom_option)
    return {
        "header": "Outputs",
        "id": "output_file_set",
        "question": "Confirm the final output file set before DOCX, add-on, or worked-solution rendering.",
        "options": selected_options,
    }


def build_payload(workflow_plan: dict[str, Any], source_scan: dict[str, Any]) -> dict[str, Any]:
    route = str(workflow_plan.get("route") or workflow_plan.get("auto_diagnosis", {}).get("route") or "exam_prep_notes")
    roles = count_source_roles(source_scan, workflow_plan)
    outputs = proposed_outputs(workflow_plan)
    questions = [
        exam_type_question(workflow_plan, source_scan),
        material_question(workflow_plan, source_scan),
        output_question(workflow_plan, source_scan),
    ]
    return {
        "schema_version": 1,
        "call": "request_user_input",
        "auto_diagnosis_review_plan": {
            "title": "Auto-diagnosis review plan",
            "route": route,
            "exam_type": ROUTE_LABELS.get(route, route),
            "material_type_source_roles": roles,
            "question_material": question_flags(source_scan, workflow_plan),
            "proposed_outputs": outputs,
            "review_sequence": [
                "Show this plan to the user before asking questions.",
                "Ask the Exam type, Material type, and output set questions.",
                "Update the workflow plan from the user's answers before generating public output.",
            ],
        },
        "questions": questions,
    }


def self_test() -> None:
    lecture_scan = {"documents": [{"source_hint": "knowledge_material"}], "fragments": [{"knowledge_roles": ["mechanism"]}]}
    lecture_plan = {"route": "exam_prep_notes", "proposed_outputs": ["docx_notes"], "source_summary": {"source_hints": {"knowledge_material": 1}}}
    lecture = build_payload(lecture_plan, lecture_scan)
    assert len(lecture["questions"]) == 3
    assert lecture["questions"][0]["id"] == "exam_type_route"
    assert lecture["questions"][0]["options"][0]["label"] == "Notes route (Recommended)"
    assert lecture["questions"][2]["options"][0]["label"] == "Notes focus (Recommended)"

    past_scan = {"documents": [{"source_hint": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True}}]}
    past_plan = {"route": "exam_prep_notes", "proposed_outputs": ["docx_notes", "exam_type_related_addon_docx"], "source_summary": {"source_hints": {"practice_material": 1}}}
    past = build_payload(past_plan, past_scan)
    assert "Question add-on" in [item["label"] for item in past["questions"][0]["options"]]
    assert past["questions"][2]["options"][0]["label"] == "Notes + Add-on (Recommended)"

    practical_scan = {"documents": [{"source_hint": "practice_material", "question_signals": {"has_questions": True, "has_practical_questions": True, "has_practical_worked_questions": True}}], "fragments": [{"knowledge_roles": ["calculation"]}]}
    practical_plan = {"route": "worked_solution_preparation", "proposed_outputs": ["practical_worked_solutions_docx"], "source_summary": {"source_hints": {"practice_material": 1}}}
    practical = build_payload(practical_plan, practical_scan)
    assert "Worked solutions" in [item["label"] for item in practical["questions"][0]["options"]]
    assert practical["questions"][2]["options"][0]["label"] == "Worked focus (Recommended)"

    mixed_scan = {"documents": [{"source_hint": "knowledge_material"}, {"source_hint": "practice_material"}, {"source_hint": "other_material"}]}
    mixed_plan = {"route": "exam_prep_notes", "proposed_outputs": ["docx_notes"], "auto_diagnosis": {"mixed_or_unclear": True}}
    mixed = build_payload(mixed_plan, mixed_scan)
    assert mixed["auto_diagnosis_review_plan"]["title"] == "Auto-diagnosis review plan"
    assert mixed["questions"][1]["options"][0]["label"] == "Mixed roles (Recommended)"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build human review questions for exam-preparation routing.")
    parser.add_argument("--workflow-plan")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    payload = build_payload(load_json(args.workflow_plan), load_json(args.source_scan))
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
