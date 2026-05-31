#!/usr/bin/env python3
"""Shared source-scale budget rules for exam-prep public outputs."""

from __future__ import annotations

from math import ceil
from typing import Any


PAGE_SLIDE_FLOORS = [
    (10, 8, 420, "tiny"),
    (20, 12, 1000, "short"),
    (80, 25, 3000, "compact"),
    (200, 50, 5800, "reference_scale"),
    (500, 105, 14000, "large_course"),
    (800, 150, 20000, "broad_course"),
    (10**9, 180, 25000, "very_broad_course"),
]

SOURCE_UNIT_FLOORS = [
    (3, 8, 420, "tiny"),
    (8, 20, 2500, "compact"),
    (15, 40, 4500, "medium"),
    (30, 80, 9000, "large_course"),
    (10**9, 120, 14000, "broad_course"),
]


def positive_int(value: Any) -> int:
    return value if isinstance(value, int) and value > 0 else 0


def source_scale_budget(plan: dict[str, Any]) -> dict[str, Any] | None:
    budget = plan.get("source_scale_budget") or plan.get("SourceScaleBudget")
    return budget if isinstance(budget, dict) else None


def infer_source_units(plan: dict[str, Any]) -> int:
    budget = source_scale_budget(plan)
    if budget:
        for key in ["source_units_count", "readable_source_blocks"]:
            value = positive_int(budget.get(key))
            if value:
                return value
    seen: set[str] = set()
    for module in plan.get("course_modules", []) or []:
        if not isinstance(module, dict):
            continue
        for source in module.get("source_lectures", []) or []:
            if str(source).strip():
                seen.add(str(source).strip())
    if seen:
        return len(seen)
    lecture_order = plan.get("lecture_order")
    if isinstance(lecture_order, list) and lecture_order:
        return len(lecture_order)
    lectures = plan.get("lectures") or plan.get("legacy_lectures")
    if isinstance(lectures, list) and lectures:
        return len(lectures)
    return 0


def infer_source_pages_or_slides(plan: dict[str, Any]) -> int:
    budget = source_scale_budget(plan)
    if not budget:
        return 0
    return positive_int(budget.get("source_pages_or_slides_estimate"))


def infer_protected_knowledge_units(plan: dict[str, Any]) -> int:
    budget = source_scale_budget(plan)
    if not budget:
        return 0
    return positive_int(budget.get("protected_knowledge_units_total"))


def _floor_from_table(value: int, table: list[tuple[int, int, int, str]]) -> tuple[int, int, str]:
    if value <= 0:
        return 0, 0, "unknown"
    for threshold, units, words, band in table:
        if value <= threshold:
            return units, words, band
    return table[-1][1], table[-1][2], table[-1][3]


def floor_for_source_units(source_units: int) -> tuple[int, int]:
    units, words, _band = _floor_from_table(source_units, SOURCE_UNIT_FLOORS)
    return units, words


def floor_for_source_scale(plan: dict[str, Any]) -> dict[str, Any]:
    source_units = infer_source_units(plan)
    pages_or_slides = infer_source_pages_or_slides(plan)
    protected_units = infer_protected_knowledge_units(plan)

    unit_floor, unit_words, unit_band = _floor_from_table(source_units, SOURCE_UNIT_FLOORS)
    page_floor, page_words, page_band = _floor_from_table(pages_or_slides, PAGE_SLIDE_FLOORS)

    min_public_units = max(unit_floor, page_floor)
    min_visible_words = max(unit_words, page_words)
    scale_band = page_band if page_floor >= unit_floor and pages_or_slides else unit_band

    if protected_units > 10:
        protected_public_units = min(260, max(12, ceil(protected_units * 0.55)))
        protected_visible_words = min(40000, max(1200, protected_units * 85))
        if protected_public_units > min_public_units:
            scale_band = "protected_knowledge_dense"
        min_public_units = max(min_public_units, protected_public_units)
        min_visible_words = max(min_visible_words, protected_visible_words)

    return {
        "source_units": source_units,
        "source_pages_or_slides_estimate": pages_or_slides,
        "protected_knowledge_units_total": protected_units,
        "minimum_public_units": min_public_units,
        "minimum_visible_words": min_visible_words,
        "scale_band": scale_band,
    }


def required_floor_with_declared_budget(plan: dict[str, Any]) -> dict[str, Any]:
    floor = floor_for_source_scale(plan)
    budget = source_scale_budget(plan)
    if not budget:
        return floor
    target_units = positive_int(budget.get("target_public_units_min"))
    target_words = positive_int(budget.get("target_words_min"))
    floor["declared_target_public_units_min"] = target_units
    floor["declared_target_words_min"] = target_words
    floor["minimum_public_units"] = max(floor["minimum_public_units"], target_units)
    floor["minimum_visible_words"] = max(floor["minimum_visible_words"], target_words)
    return floor
