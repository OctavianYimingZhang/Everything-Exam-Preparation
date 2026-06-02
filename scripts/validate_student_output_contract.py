#!/usr/bin/env python3
"""Validate student-facing output contracts after protocol consolidation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "references/exam_prep_core_workflow.md",
    "references/input_and_evidence_protocol.md",
    "references/exam_mode_and_addons_protocol.md",
    "references/essay_exam_prep_protocol.md",
    "references/language_quality_contract.md",
    "references/runtime_qa_release_protocol.md",
    "schemas/student_output_contract.schema.json",
    "schemas/public_lecture_notes_plan.schema.json",
    "schemas/knowledge_surface_contract.schema.json",
    "schemas/atomic_knowledge_ledger.schema.json",
    "scripts/generate_public_lecture_notes_docx.py",
    "scripts/public_notes_docx_linter.py",
    "scripts/notes_exam_ready_language_linter.py",
    "scripts/module_teaching_depth_linter.py",
    "scripts/notes_readability_layout_linter.py",
    "scripts/source_scale_budget_linter.py",
    "scripts/docx_layout_surface_normalizer.py",
    "scripts/knowledge_surface_linter.py",
]

REQUIRED_PRESETS = {
    "exam_prep_notes_docx",
    "knowledge_walkthrough_docx",
    "mcq_exam_prep",
    "short_answer_exam_prep",
    "long_answer_project_scenario_prep",
    "essay_exam_prep",
}

FORBIDDEN_VISIBLE_FIELDS = {
    "source_anchor", "confidence", "evidence", "examiner_operation", "discriminator_axis", "practice_mcq", "answer_key", "contrast_table", "separate_trap_bank", "mark_producing_schema", "reference_expansion", "exam_specificity", "core_exam_claim", "exam_use", "common_error_or_trap", "must_master",
}

REQUIRED_SURFACE_TERMS = [
    "SourceRoleMap", "NonKnowledgeNoiseFilter", "SourceScaleBudget", "coverage_floor", "source_units_count", "minimum_visible_coverage_floor", "ExaminableKnowledgeUnit", "subject_knowledge", "non_knowledge_noise", "PublicLectureNotesPlan", "public_lecture_sections", "knowledge_functions", "raw slide bullets", "lecture-first", "connected explanation", "exam-ready direct prose", "micro-module", "module teaching depth", "source narration", "readability layout", "theme colours", "blue heading styles", "KnowledgeSurfaceContract", "NonKnowledgeGate", "SurfaceLabelDecision", "LabelDecision", "semantic_sparse", "source_route_narration", "ai_process_or_provenance", "rigid_template_bucket", "colon-slot fragmentation", "shorthand arrow chains",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate(root: Path) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append({"type": "missing_required_file", "path": rel_path})

    skill_schema = load_json(root / "schemas/skill_config.schema.json")
    workflow_schema = load_json(root / "schemas/workflow_plan.schema.json")
    skill_enum = set(skill_schema.get("properties", {}).get("output_mode", {}).get("properties", {}).get("preset", {}).get("enum", []))
    workflow_enum = set(workflow_schema.get("properties", {}).get("selected_preset", {}).get("enum", []))
    for required_preset in sorted(REQUIRED_PRESETS):
        if required_preset not in skill_enum:
            failures.append({"type": "missing_student_output_preset", "preset": required_preset, "schema": "skill_config"})
        if required_preset not in workflow_enum:
            failures.append({"type": "missing_student_output_preset", "preset": required_preset, "schema": "workflow_plan"})

    plan_text = read(root / "scripts/plan_workflow.py")
    for required_preset in sorted(REQUIRED_PRESETS):
        if required_preset not in plan_text:
            failures.append({"type": "planner_missing_student_output_preset", "preset": required_preset})

    combined = "\n".join(read(root / rel) for rel in [
        "SKILL.md",
        "references/exam_prep_core_workflow.md",
        "references/input_and_evidence_protocol.md",
        "references/exam_mode_and_addons_protocol.md",
        "references/essay_exam_prep_protocol.md",
        "references/language_quality_contract.md",
        "references/runtime_qa_release_protocol.md",
        "scripts/source_scale_budget_linter.py",
        "scripts/public_notes_docx_linter.py",
    ])
    for term in REQUIRED_SURFACE_TERMS:
        if term not in combined:
            failures.append({"type": "student_policy_missing_term", "term": term})
    for field in sorted(FORBIDDEN_VISIBLE_FIELDS):
        if field not in combined:
            failures.append({"type": "student_policy_missing_forbidden_field", "field": field})

    public_schema = load_json(root / "schemas/public_lecture_notes_plan.schema.json")
    if "public_lecture_sections" not in public_schema.get("required", []):
        failures.append({"type": "public_schema_missing_public_lecture_sections"})
    if "output_language_profile" not in public_schema.get("required", []):
        failures.append({"type": "public_schema_missing_output_language_profile"})
    route_enum = public_schema.get("$defs", {}).get("RouteDocxStyleProfile", {}).get("properties", {}).get("route", {}).get("enum", [])
    for route in ["exam_prep_notes_docx", "knowledge_walkthrough_docx"]:
        if route not in route_enum:
            failures.append({"type": "public_schema_missing_route", "route": route})
    style_props = public_schema.get("$defs", {}).get("RouteDocxStyleProfile", {}).get("properties", {})
    if style_props.get("body_alignment", {}).get("const") != "left":
        failures.append({"type": "public_schema_body_not_left"})
    if style_props.get("image_alignment", {}).get("const") != "center":
        failures.append({"type": "public_schema_image_not_center"})

    contract_text = json.dumps(load_json(root / "schemas/student_output_contract.schema.json"), ensure_ascii=False)
    for field in sorted(FORBIDDEN_VISIBLE_FIELDS):
        if field not in contract_text:
            failures.append({"type": "student_output_schema_missing_forbidden_field", "field": field})
    for legacy in ["必备", "重点", "补充"]:
        if legacy in combined + contract_text:
            failures.append({"type": "legacy_priority_label_still_visible", "label": legacy})

    return {"pass": not failures, "counts": {"required_files": len(REQUIRED_FILES)}, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.root)
    except Exception as exc:
        result = {"pass": False, "failures": [{"type": "read_error", "error": str(exc)}]}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
