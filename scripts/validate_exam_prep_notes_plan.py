#!/usr/bin/env python3
"""Validate ExamPrepNotesPlan coverage and student-visible knowledge cards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from knowledge_only_rendering_rules import forbidden_advisory_heading_hits, forbidden_advisory_phrase_hits
from source_scale_budget_rules import floor_for_source_scale


REQUIRED_TOP_LEVEL = {
    "notes_plan_id",
    "target_group_key",
    "source_scale_budget",
    "course_sections",
    "lecture_mapping",
    "knowledge_cards",
    "public_output_points",
    "output_language_profile",
    "route_docx_style_profile",
    "render_decisions",
    "point_coverage_bindings",
    "official_definition_records",
    "atomic_knowledge_ledger_binding",
    "source_baseline_binding",
    "exam_emphasis_binding",
    "exam_overlay_binding",
    "question_type_addons",
    "content_coverage_checks",
    "student_visible_structure",
    "forbidden_student_fields",
    "qa_flags",
    "qa_status",
}

REQUIRED_CARD_FIELDS = {
    "card_id",
    "kp_id",
    "section_id",
    "lecture_session_id",
    "module_id",
    "module_title",
    "source_baseline_card_id",
    "priority",
    "exam_specificity",
    "core_exam_claim",
    "exam_ready_knowledge_synthesis",
    "protected_source_items_covered",
    "source_anchors",
    "coverage_status",
    "student_visible",
}

ALLOWED_PRIORITY = {"★★★", "★★", "★"}
ALLOWED_COVERAGE = {"tested", "partially_tested", "fresh", "saturated", "unknown"}
ALLOWED_QA_STATUS = {"pass", "warn", "block"}
ALLOWED_EXAM_SPECIFICITY = {
    "definition",
    "mechanism",
    "criteria list",
    "comparison",
    "calculation",
    "graph interpretation",
    "method workflow",
    "case justification",
    "background",
}
ALLOWED_POINT_KINDS = {
    "definition",
    "mechanism",
    "method_workflow",
    "criteria_list",
    "comparison",
    "calculation",
    "graph_or_data_interpretation",
    "canonical_example",
    "compact_background",
}
ALLOWED_BLOCK_TYPES = {
    "definitions",
    "key_points",
    "criteria",
    "steps",
    "mechanism",
    "equation",
    "calculation_logic",
    "graph_logic",
    "comparison",
    "example",
    "limitation",
}
FORBIDDEN_PUBLIC_HEADINGS = {
    "Exam Specificity",
    "Core Exam Claim",
    "Exam Use",
    "Common Error / Trap",
    "Must Master",
    "Course-Level Exam Map",
    "How To Answer This Exam",
}
FORBIDDEN_CARD_FIELDS = {
    "priority_label",
    "exam_function",
    "exam_ready_synthesis",
    "evidence_or_example_function",
}


def is_forbidden_heading(value: Any) -> bool:
    text = str(value or "").strip().rstrip(":")
    forbidden = {heading.casefold() for heading in FORBIDDEN_PUBLIC_HEADINGS}
    forbidden.update(heading.casefold() for heading in forbidden_advisory_heading_hits(str(value or "")))
    return text.casefold() in forbidden


def collect_advisory_failures(value: Any, field: str, owner: str) -> list[dict[str, Any]]:
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value or "")
    return [
        {"type": "public_knowledge_only_advisory_phrase", "owner": owner, "field": field, "phrase": phrase}
        for phrase in forbidden_advisory_phrase_hits(text)
    ] + [
        {"type": "public_knowledge_only_advisory_heading", "owner": owner, "field": field, "heading": heading}
        for heading in forbidden_advisory_heading_hits(text)
    ]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and any(str(item).strip() for item in value)


def number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate(plan: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for field in sorted(REQUIRED_TOP_LEVEL - set(plan)):
        failures.append({"type": "missing_top_level_field", "field": field})

    if plan.get("qa_status") not in ALLOWED_QA_STATUS:
        failures.append({"type": "invalid_qa_status", "qa_status": plan.get("qa_status")})

    budget = plan.get("source_scale_budget")
    if not isinstance(budget, dict):
        failures.append({"type": "missing_source_scale_budget"})
    else:
        floor = floor_for_source_scale(plan)
        floor_units = int(floor["minimum_public_units"])
        floor_words = int(floor["minimum_visible_words"])
        target_units = budget.get("target_public_units_min")
        target_words = budget.get("target_words_min")
        if not isinstance(target_units, int) or target_units < 0:
            failures.append({"type": "source_scale_budget_missing_target_public_units_min"})
        elif target_units < floor_units:
            failures.append(
                {
                    "type": "source_scale_budget_target_public_units_min_below_floor",
                    "declared": target_units,
                    "minimum": floor_units,
                }
            )
        if not isinstance(target_words, int) or target_words < 0:
            failures.append({"type": "source_scale_budget_missing_target_words_min"})
        elif target_words < floor_words:
            failures.append(
                {
                    "type": "source_scale_budget_target_words_min_below_floor",
                    "declared": target_words,
                    "minimum": floor_words,
                }
            )

    if not isinstance(plan.get("course_sections"), list) or not plan.get("course_sections"):
        failures.append({"type": "course_sections_empty"})
    for section in plan.get("course_sections", []):
        if not isinstance(section, dict):
            failures.append({"type": "course_section_not_object"})
            continue
        if not non_empty_list(section.get("source_anchors")):
            failures.append({"type": "course_section_missing_source_anchors", "section_id": section.get("section_id")})

    if not isinstance(plan.get("lecture_mapping"), list) or not plan.get("lecture_mapping"):
        failures.append({"type": "lecture_mapping_empty"})
    for lecture in plan.get("lecture_mapping", []):
        if not isinstance(lecture, dict):
            failures.append({"type": "lecture_mapping_not_object"})
            continue
        if not non_empty_list(lecture.get("source_anchors")):
            failures.append({"type": "lecture_mapping_missing_source_anchors", "lecture_session_id": lecture.get("lecture_session_id")})

    cards = plan.get("knowledge_cards", [])
    card_ids: set[str] = set()
    visible_card_ids: set[str] = set()
    if not isinstance(cards, list) or not cards:
        failures.append({"type": "knowledge_cards_empty"})
        cards = []
    for index, card in enumerate(cards, start=1):
        if not isinstance(card, dict):
            failures.append({"type": "knowledge_card_not_object", "index": index})
            continue
        card_id = str(card.get("card_id") or "")
        if card_id:
            card_ids.add(card_id)
        for field in sorted(REQUIRED_CARD_FIELDS - set(card)):
            failures.append({"type": "knowledge_card_missing_field", "card_id": card.get("card_id"), "field": field})
        for field in sorted(FORBIDDEN_CARD_FIELDS & set(card)):
            failures.append({"type": "knowledge_card_forbidden_legacy_field", "card_id": card.get("card_id"), "field": field})
        if card.get("student_visible") is True:
            if card_id:
                visible_card_ids.add(card_id)
            if card.get("priority") not in ALLOWED_PRIORITY:
                failures.append({"type": "student_visible_card_invalid_priority", "card_id": card.get("card_id"), "priority": card.get("priority")})
            if card.get("exam_specificity") not in ALLOWED_EXAM_SPECIFICITY:
                failures.append({"type": "student_visible_card_invalid_exam_specificity", "card_id": card.get("card_id"), "exam_specificity": card.get("exam_specificity")})
            if not str(card.get("module_title") or "").strip():
                failures.append({"type": "student_visible_card_missing_module_title", "card_id": card.get("card_id")})
            if not str(card.get("source_baseline_card_id") or "").strip():
                failures.append({"type": "student_visible_card_missing_source_baseline_card_id", "card_id": card.get("card_id")})
            if not non_empty_list(card.get("source_anchors")):
                failures.append({"type": "student_visible_card_missing_source_anchors", "card_id": card.get("card_id")})
            if not non_empty_list(card.get("protected_source_items_covered")):
                failures.append({"type": "student_visible_card_missing_protected_source_items", "card_id": card.get("card_id")})
            if card.get("coverage_status") not in ALLOWED_COVERAGE:
                failures.append({"type": "student_visible_card_invalid_coverage_status", "card_id": card.get("card_id"), "coverage_status": card.get("coverage_status")})

    points = plan.get("public_output_points", [])
    if not isinstance(points, list) or not points:
        failures.append({"type": "public_output_points_empty"})
        points = []
    point_ids: set[str] = set()
    point_units_by_id: dict[str, set[str]] = {}
    rendered_card_ids: set[str] = set()
    covered_atomic_items: set[str] = set()
    for index, point in enumerate(points, start=1):
        if not isinstance(point, dict):
            failures.append({"type": "public_output_point_not_object", "index": index})
            continue
        point_id = str(point.get("point_id") or "")
        if not point_id:
            failures.append({"type": "public_output_point_missing_point_id", "index": index})
        else:
            point_ids.add(point_id)
        for field in ["lecture_session_id", "point_title", "priority", "point_kind", "main_text", "blocks", "covered_atomic_units"]:
            if field not in point:
                failures.append({"type": "public_output_point_missing_field", "point_id": point_id, "field": field})
        source_card_ids = [str(item) for item in point.get("source_card_ids", []) if str(item).strip()] if isinstance(point.get("source_card_ids"), list) else []
        if not source_card_ids:
            failures.append({"type": "public_output_point_missing_source_card_ids", "point_id": point_id})
        for source_card_id in source_card_ids:
            if source_card_id not in card_ids:
                failures.append({"type": "public_output_point_unknown_source_card", "point_id": point_id, "card_id": source_card_id})
            else:
                rendered_card_ids.add(source_card_id)
        if point.get("priority") not in ALLOWED_PRIORITY:
            failures.append({"type": "public_output_point_invalid_priority", "point_id": point_id, "priority": point.get("priority")})
        if point.get("point_kind") not in ALLOWED_POINT_KINDS:
            failures.append({"type": "public_output_point_invalid_kind", "point_id": point_id, "point_kind": point.get("point_kind")})
        if is_forbidden_heading(point.get("point_title")):
            failures.append({"type": "public_output_point_forbidden_internal_title", "point_id": point_id, "title": point.get("point_title")})
        failures.extend(collect_advisory_failures(point.get("point_title"), "point_title", point_id))
        failures.extend(collect_advisory_failures(point.get("main_text"), "main_text", point_id))
        if not str(point.get("main_text") or "").strip():
            failures.append({"type": "public_output_point_missing_main_text", "point_id": point_id})
        if not non_empty_list(point.get("covered_atomic_units")):
            failures.append({"type": "public_output_point_missing_atomic_coverage", "point_id": point_id})
        else:
            point_units = {str(item) for item in point.get("covered_atomic_units", []) if str(item).strip()}
            point_units_by_id[point_id] = point_units
            covered_atomic_items.update(point_units)
        blocks = point.get("blocks", [])
        if not isinstance(blocks, list):
            failures.append({"type": "public_output_point_blocks_not_list", "point_id": point_id})
            blocks = []
        block_covered_units: set[str] = set()
        for block_index, block in enumerate(blocks, start=1):
            if not isinstance(block, dict):
                failures.append({"type": "public_point_block_not_object", "point_id": point_id, "index": block_index})
                continue
            if block.get("block_type") not in ALLOWED_BLOCK_TYPES:
                failures.append({"type": "public_point_block_invalid_type", "point_id": point_id, "block_type": block.get("block_type")})
            if is_forbidden_heading(block.get("label")):
                failures.append({"type": "public_point_block_forbidden_internal_label", "point_id": point_id, "label": block.get("label")})
            failures.extend(collect_advisory_failures(block.get("label"), "block_label", point_id))
            failures.extend(collect_advisory_failures(block.get("content"), "block_content", point_id))
            content = block.get("content")
            if isinstance(content, list):
                if not non_empty_list(content):
                    failures.append({"type": "public_point_block_empty_content", "point_id": point_id, "block_type": block.get("block_type")})
            elif not str(content or "").strip():
                failures.append({"type": "public_point_block_empty_content", "point_id": point_id, "block_type": block.get("block_type")})
            block_units = block.get("covered_atomic_units", [])
            if not non_empty_list(block_units):
                failures.append({"type": "public_point_block_missing_atomic_coverage", "point_id": point_id, "block_type": block.get("block_type")})
            else:
                block_unit_set = {str(item) for item in block_units if str(item).strip()}
                block_covered_units.update(block_unit_set)
                unknown_block_units = sorted(block_unit_set - point_units_by_id.get(point_id, set()))
                if unknown_block_units:
                    failures.append({"type": "public_point_block_coverage_not_in_point", "point_id": point_id, "units": unknown_block_units})
        if blocks:
            missing_block_units = sorted(point_units_by_id.get(point_id, set()) - block_covered_units)
            if missing_block_units:
                failures.append({"type": "public_output_point_atomic_unit_missing_from_blocks", "point_id": point_id, "units": missing_block_units})

    for card_id in sorted(visible_card_ids - rendered_card_ids):
        failures.append({"type": "student_visible_card_missing_public_output_point", "card_id": card_id})

    language_profile = plan.get("output_language_profile", {})
    if not isinstance(language_profile, dict):
        failures.append({"type": "output_language_profile_not_object"})
    else:
        if not non_empty_list(language_profile.get("output_language_policy")):
            failures.append({"type": "output_language_profile_missing_policy"})
        if not non_empty_list(language_profile.get("public_label_policy")):
            failures.append({"type": "output_language_profile_missing_label_policy"})
        if "explicit_language_request" not in language_profile:
            failures.append({"type": "output_language_profile_missing_explicit_language_request"})
        if language_profile.get("user_requested_mixed_language") is True and language_profile.get("explicit_language_request") is not True:
            failures.append({"type": "mixed_language_without_explicit_user_request"})

    style_profile = plan.get("route_docx_style_profile", {})
    if not isinstance(style_profile, dict):
        failures.append({"type": "route_docx_style_profile_not_object"})
    else:
        if style_profile.get("route") != "exam_prep_notes_docx":
            failures.append({"type": "route_docx_style_profile_invalid_route", "route": style_profile.get("route")})
        margin_cm = number_or_none(style_profile.get("margin_cm"))
        line_spacing = number_or_none(style_profile.get("line_spacing"))
        if margin_cm is None or abs(margin_cm - 2.0) > 0.2:
            failures.append({"type": "route_docx_style_profile_bad_margin", "margin_cm": style_profile.get("margin_cm")})
        if line_spacing is None or not (1.45 <= line_spacing <= 1.55):
            failures.append({"type": "route_docx_style_profile_bad_line_spacing", "line_spacing": style_profile.get("line_spacing")})
        if style_profile.get("body_alignment") != "justified":
            failures.append({"type": "route_docx_style_profile_body_not_justified", "body_alignment": style_profile.get("body_alignment")})
        if style_profile.get("title_alignment") != "left":
            failures.append({"type": "route_docx_style_profile_title_not_left", "title_alignment": style_profile.get("title_alignment")})
        if style_profile.get("heading_alignment") != "left":
            failures.append({"type": "route_docx_style_profile_heading_not_left", "heading_alignment": style_profile.get("heading_alignment")})
        if style_profile.get("image_alignment") != "center":
            failures.append({"type": "route_docx_style_profile_image_not_center", "image_alignment": style_profile.get("image_alignment")})
        if style_profile.get("text_color") != "black":
            failures.append({"type": "route_docx_style_profile_text_not_black", "text_color": style_profile.get("text_color")})
        if style_profile.get("theme_colours_allowed") is not False:
            failures.append({"type": "route_docx_style_profile_theme_colours_not_disabled"})
        if style_profile.get("blue_heading_styles_allowed") is not False:
            failures.append({"type": "route_docx_style_profile_blue_heading_styles_not_disabled"})

    render_decisions = plan.get("render_decisions", [])
    if not isinstance(render_decisions, list):
        failures.append({"type": "render_decisions_not_list"})
        render_decisions = []
    hidden_fields = {
        str(item.get("source_field") or "")
        for item in render_decisions
        if isinstance(item, dict) and item.get("decision") == "hide_internal_field"
    }
    for internal_field in ["exam_specificity", "core_exam_claim", "exam_use", "common_error_or_trap", "must_master"]:
        if internal_field not in hidden_fields:
            failures.append({"type": "internal_field_missing_hide_render_decision", "field": internal_field})

    bindings = plan.get("point_coverage_bindings", [])
    if not isinstance(bindings, list) or not bindings:
        failures.append({"type": "point_coverage_bindings_empty"})
        bindings = []
    for binding in bindings:
        if not isinstance(binding, dict):
            failures.append({"type": "point_coverage_binding_not_object"})
            continue
        if binding.get("point_id") not in point_ids:
            failures.append({"type": "point_coverage_binding_unknown_point", "point_id": binding.get("point_id")})
        if not non_empty_list(binding.get("covered_atomic_units")):
            failures.append({"type": "point_coverage_binding_missing_atomic_coverage", "point_id": binding.get("point_id")})
        else:
            binding_units = {str(item) for item in binding.get("covered_atomic_units", []) if str(item).strip()}
            point_units = point_units_by_id.get(str(binding.get("point_id") or ""), set())
            if point_units and binding_units != point_units:
                failures.append({
                    "type": "point_coverage_binding_atomic_units_mismatch",
                    "point_id": binding.get("point_id"),
                    "binding_only": sorted(binding_units - point_units),
                    "point_only": sorted(point_units - binding_units),
                })
        if binding.get("protected_items_preserved") is not True:
            failures.append({"type": "point_coverage_binding_protected_items_not_preserved", "point_id": binding.get("point_id")})
        if non_empty_list(binding.get("missing_protected_items")):
            failures.append({"type": "point_coverage_binding_missing_protected_items", "point_id": binding.get("point_id"), "missing": binding.get("missing_protected_items")})
        if binding.get("qa_status") not in ALLOWED_QA_STATUS:
            failures.append({"type": "point_coverage_binding_invalid_qa_status", "point_id": binding.get("point_id"), "qa_status": binding.get("qa_status")})

    ledger_binding = plan.get("atomic_knowledge_ledger_binding", {})
    if isinstance(ledger_binding, dict) and ledger_binding.get("missing_units"):
        failures.append({"type": "atomic_knowledge_ledger_binding_has_missing_units", "missing_units": ledger_binding.get("missing_units")})

    baseline = plan.get("source_baseline_binding", {})
    if not isinstance(baseline, dict):
        failures.append({"type": "source_baseline_binding_not_object"})
    else:
        if not str(baseline.get("baseline_plan_id") or "").strip():
            failures.append({"type": "source_baseline_binding_missing_baseline_plan_id"})
        if baseline.get("coverage_floor_status") not in ALLOWED_QA_STATUS:
            failures.append({"type": "source_baseline_binding_invalid_coverage_floor_status", "coverage_floor_status": baseline.get("coverage_floor_status")})

    emphasis = plan.get("exam_emphasis_binding", {})
    if not isinstance(emphasis, dict):
        failures.append({"type": "exam_emphasis_binding_not_object"})
    else:
        if "formal_papers_used" not in emphasis:
            failures.append({"type": "exam_emphasis_binding_missing_formal_papers_used"})
        if not isinstance(emphasis.get("compatible_question_types", []), list):
            failures.append({"type": "exam_emphasis_binding_question_types_not_list"})
        if not isinstance(emphasis.get("limitations", []), list):
            failures.append({"type": "exam_emphasis_binding_limitations_not_list"})

    overlay = plan.get("exam_overlay_binding", {})
    if not isinstance(overlay, dict):
        failures.append({"type": "exam_overlay_binding_not_object"})
    else:
        if not str(overlay.get("overlay_id") or "").strip():
            failures.append({"type": "exam_overlay_binding_missing_overlay_id"})
        if overlay.get("overlay_status") not in ALLOWED_QA_STATUS:
            failures.append({"type": "exam_overlay_binding_invalid_overlay_status", "overlay_status": overlay.get("overlay_status")})
        if overlay.get("protected_items_preserved") is not True:
            failures.append({"type": "exam_overlay_binding_protected_items_not_preserved"})

    checks = plan.get("content_coverage_checks", [])
    if not isinstance(checks, list) or not checks:
        failures.append({"type": "content_coverage_checks_empty"})
    for check in checks:
        if not isinstance(check, dict):
            failures.append({"type": "content_coverage_check_not_object"})
            continue
        if check.get("status") not in ALLOWED_QA_STATUS:
            failures.append({"type": "content_coverage_check_invalid_status", "check_id": check.get("check_id"), "status": check.get("status")})

    return {
        "pass": not failures,
        "counts": {
            "course_sections": len(plan.get("course_sections", [])) if isinstance(plan.get("course_sections"), list) else 0,
            "lecture_mapping": len(plan.get("lecture_mapping", [])) if isinstance(plan.get("lecture_mapping"), list) else 0,
            "knowledge_cards": len(cards),
            "public_output_points": len(points),
            "point_coverage_bindings": len(bindings),
            "content_coverage_checks": len(checks) if isinstance(checks, list) else 0,
        },
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = validate(load_json(args.plan))
    except Exception as exc:
        result = {"pass": False, "failures": [{"type": "read_error", "error": str(exc)}]}
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
