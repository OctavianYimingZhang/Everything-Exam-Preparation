#!/usr/bin/env python3
"""Validate student-facing output policy files and contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "SKILL.md",
    "references/exam_prep_core_workflow.md",
    "references/student_facing_output_policy.md",
    "references/exam_prep_notes_protocol.md",
    "references/knowledge_walkthrough_docx_protocol.md",
    "references/knowledge_surface_protocol.md",
    "schemas/student_output_contract.schema.json",
    "schemas/knowledge_walkthrough_plan.schema.json",
    "schemas/knowledge_surface_contract.schema.json",
    "schemas/atomic_knowledge_ledger.schema.json",
    "scripts/generate_exam_prep_notes_docx.py",
    "scripts/exam_prep_docx_style_linter.py",
    "scripts/source_scale_budget_linter.py",
    "scripts/docx_layout_surface_normalizer.py",
    "scripts/generate_knowledge_walkthrough_docx.py",
    "scripts/knowledge_walkthrough_linter.py",
    "scripts/knowledge_surface_linter.py",
]

REQUIRED_PRESETS = {"knowledge_walkthrough_docx", "exam_prep_notes_docx"}

FORBIDDEN_VISIBLE_FIELDS = {
    "source_anchor",
    "confidence",
    "evidence",
    "examiner_operation",
    "discriminator_axis",
    "practice_mcq",
    "answer_key",
    "contrast_table",
    "separate_trap_bank",
    "mark_producing_schema",
    "reference_expansion",
    "exam_specificity",
    "core_exam_claim",
    "exam_use",
    "common_error_or_trap",
    "must_master",
}


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
    for schema_name, schema in [("skill_config", skill_schema), ("workflow_plan", workflow_schema)]:
        enum = set(schema.get("properties", {}).get("output_mode", {}).get("properties", {}).get("preset", {}).get("enum", []))
        if schema_name == "workflow_plan":
            enum = set(schema.get("properties", {}).get("selected_preset", {}).get("enum", []))
        for required_preset in sorted(REQUIRED_PRESETS):
            if required_preset not in enum:
                failures.append({"type": "missing_student_output_preset", "preset": required_preset, "schema": schema_name})

    plan_text = read(root / "scripts/plan_workflow.py")
    for required_preset in sorted(REQUIRED_PRESETS):
        if required_preset not in plan_text:
            failures.append({"type": "planner_missing_student_output_preset", "preset": required_preset})

    skill = read(root / "SKILL.md")
    core_workflow = read(root / "references/exam_prep_core_workflow.md")
    policy = read(root / "references/student_facing_output_policy.md")
    exam_prep_notes = read(root / "references/exam_prep_notes_protocol.md")
    walkthrough = read(root / "references/knowledge_walkthrough_docx_protocol.md")
    knowledge_surface = read(root / "references/knowledge_surface_protocol.md")
    scale_linter = read(root / "scripts/source_scale_budget_linter.py")
    style_linter = read(root / "scripts/exam_prep_docx_style_linter.py")
    combined = "\n".join([skill, core_workflow, policy, exam_prep_notes, walkthrough, knowledge_surface, scale_linter, style_linter])

    for term in [
        "SourceRoleMap",
        "NonKnowledgeNoiseFilter",
        "SourceScaleBudget",
        "source-adaptive coverage budget",
        "coverage_floor",
        "source_units_count",
        "minimum_visible_coverage_floor",
        "ExaminableKnowledgeUnit",
        "subject_knowledge",
        "non_knowledge_noise",
        "CourseModule",
        "Course Knowledge Map",
        "raw slide bullets",
        "file-title course maps",
        "connected explanation",
        "theme colours",
        "blue heading styles",
        "KnowledgeSurfaceContract",
        "NonKnowledgeGate",
        "SurfaceLabelDecision",
        "LabelDecision",
        "semantic_sparse",
        "source_route_narration",
        "ai_process_or_provenance",
        "rigid_template_bucket",
        "colon-slot fragmentation",
        "shorthand arrow chains",
        "EssayAdaptiveBudget",
    ]:
        if term not in combined:
            failures.append({"type": "student_policy_missing_term", "term": term})
    for field in sorted(FORBIDDEN_VISIBLE_FIELDS):
        if field not in combined:
            failures.append({"type": "student_policy_missing_forbidden_field", "field": field})

    contract = load_json(root / "schemas/student_output_contract.schema.json")
    surface_schema = load_json(root / "schemas/knowledge_surface_contract.schema.json")
    walkthrough_schema = load_json(root / "schemas/knowledge_walkthrough_plan.schema.json")
    if "route_docx_style_profile" not in walkthrough_schema.get("required", []):
        failures.append({"type": "knowledge_walkthrough_schema_missing_route_style_profile"})
    style_profile = walkthrough_schema.get("properties", {}).get("route_docx_style_profile", {})
    style_props = style_profile.get("properties", {})
    if style_props.get("route", {}).get("const") != "knowledge_walkthrough_docx":
        failures.append({"type": "knowledge_walkthrough_schema_bad_style_route"})
    if style_props.get("body_alignment", {}).get("const") != "justified":
        failures.append({"type": "knowledge_walkthrough_schema_body_not_justified"})
    if style_props.get("heading_alignment", {}).get("const") != "left":
        failures.append({"type": "knowledge_walkthrough_schema_heading_not_left"})
    if style_props.get("image_alignment", {}).get("const") != "center":
        failures.append({"type": "knowledge_walkthrough_schema_image_not_center"})
    line_spacing = style_props.get("line_spacing", {})
    if line_spacing.get("minimum") != 1.45 or line_spacing.get("maximum") != 1.55:
        failures.append({"type": "knowledge_walkthrough_schema_line_spacing_not_1_5"})

    if surface_schema.get("title") != "KnowledgeSurfaceContract":
        failures.append({"type": "knowledge_surface_schema_bad_title"})
    surface_text = json.dumps(surface_schema, ensure_ascii=False)
    for term in [
        "allowed_public_functions",
        "forbidden_public_functions",
        "label_policy",
        "density_policy",
        "surface_label_decisions",
        "source_route_narration",
        "ai_process_or_provenance",
        "rigid_template_bucket",
        "mechanism_detail_target_ratio",
        "extra_reading_target_ratio",
    ]:
        if term not in surface_text:
            failures.append({"type": "knowledge_surface_schema_missing_term", "term": term})
    contract_text = json.dumps(contract, ensure_ascii=False)
    for legacy in ["必备", "重点", "补充"]:
        if legacy in policy + exam_prep_notes + contract_text:
            failures.append({"type": "legacy_priority_label_still_visible", "label": legacy})
    for field in sorted(FORBIDDEN_VISIBLE_FIELDS):
        if field not in contract_text:
            failures.append({"type": "student_output_schema_missing_forbidden_field", "field": field})

    return {
        "pass": not failures,
        "counts": {"required_files": len(REQUIRED_FILES), "forbidden_visible_fields": len(FORBIDDEN_VISIBLE_FIELDS)},
        "failures": failures,
    }


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
        args.output.parent.mkdir(parents=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
