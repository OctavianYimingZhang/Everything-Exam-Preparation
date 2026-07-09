#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXAM_WORDS = ["define", "state", "list", "explain", "compare", "evaluate", "discuss", "calculate", "interpret", "which", "essay"]
ACADEMIC_SIGNALS = {
    "definition": 3,
    "mechanism": 4,
    "method": 3,
    "comparison": 3,
    "calculation": 3,
    "data_interpretation": 3,
    "evidence": 3,
    "learning_objective": 2,
    "term_density": 2,
    "application": 2,
    "explanatory_example": 1,
}
EXPLANATION_SIGNALS = {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation", "evidence", "application"}


def exam_signal_score(text: str) -> int:
    lower = (text or "").lower()
    return sum(lower.count(word) for word in EXAM_WORDS)


def academic_content_score(signals: list[str]) -> int:
    return sum(ACADEMIC_SIGNALS.get(signal, 0) for signal in signals)


def explanation_need_score(signals: list[str], text: str) -> int:
    score = sum(1 for signal in signals if signal in EXPLANATION_SIGNALS)
    if len(re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or "")) >= 35:
        score += 1
    return score


def signal_counts(fragments: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for frag in fragments:
        for signal in frag.get("knowledge_signals", []):
            counts[signal] = counts.get(signal, 0) + 1
    return counts


def value_counts(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "")
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def slide_position(item: dict[str, Any]) -> int:
    return int(item.get("slide_number") or item.get("page_number") or item.get("fragment_order") or 10_000)


def slide_triage_audit(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for item in items:
        if not item.get("slide_decision"):
            continue
        source_id = str(item.get("source_id") or item.get("source_name") or "unknown")
        record = by_source.setdefault(source_id, {
            "source_id": item.get("source_id"),
            "source_name": item.get("source_name"),
            "lecture_order": item.get("lecture_order"),
            "use_count": 0,
            "merge_with_previous_count": 0,
            "exclude_count": 0,
            "excluded_reasons": {},
            "excluded_slides": [],
        })
        decision = str(item.get("slide_decision"))
        if decision == "use":
            record["use_count"] += 1
        elif decision == "merge_with_previous":
            record["merge_with_previous_count"] += 1
        elif decision == "exclude":
            record["exclude_count"] += 1
            reason = str(item.get("triage_reason") or "unspecified")
            record["excluded_reasons"][reason] = record["excluded_reasons"].get(reason, 0) + 1
            record["excluded_slides"].append({
                "locator": item.get("locator"),
                "slide_number": item.get("slide_number"),
                "page_number": item.get("page_number"),
                "likely_slide_title": item.get("likely_slide_title"),
                "triage_reason": reason,
            })
    return sorted(by_source.values(), key=lambda record: int(record.get("lecture_order") or 10_000))


def notes_route(route: str) -> bool:
    return route in {"exam_prep_notes", "mcq_preparation", "short_answer_preparation", "long_answer_preparation", "worked_solution_preparation", "essay_preparation", "mixed_exam_preparation"}


def build_index(source_scan: dict[str, Any] | None, route: str = "exam_prep_notes") -> dict[str, Any]:
    source_scan = source_scan or {"documents": [], "fragments": []}
    docs = {doc.get("id"): doc for doc in source_scan.get("documents", [])}
    indexed = []
    for frag in source_scan.get("fragments", []):
        source = docs.get(frag.get("source_id"), {})
        text = str(frag.get("text") or "")
        signals = list(frag.get("knowledge_signals", []) or [])
        roles = list(frag.get("knowledge_roles", []) or [])
        indexed.append({
            "id": frag.get("id"),
            "source_id": frag.get("source_id"),
            "source_name": frag.get("source_name") or source.get("name"),
            "category": frag.get("category") or source.get("category") or "other_material",
            "locator": frag.get("locator"),
            "slide_number": frag.get("slide_number"),
            "page_number": frag.get("page_number"),
            "time_offset_seconds": frag.get("time_offset_seconds"),
            "time_range": frag.get("time_range"),
            "provenance": frag.get("provenance") or {
                "source_id": frag.get("source_id"),
                "source_name": frag.get("source_name") or source.get("name"),
                "locator": frag.get("locator"),
                "page_number": frag.get("page_number"),
                "slide_number": frag.get("slide_number"),
                "time_offset_seconds": frag.get("time_offset_seconds"),
                "time_range": frag.get("time_range"),
            },
            "likely_slide_title": frag.get("likely_slide_title"),
            "source_order": frag.get("source_order") or source.get("source_order") or 0,
            "fragment_order": frag.get("fragment_order") or 0,
            "lecture_order": frag.get("lecture_order") or source.get("lecture_order"),
            "lecture_source": bool(frag.get("lecture_source") or source.get("lecture_source")),
            "content_triage": frag.get("content_triage") or source.get("content_triage") or "core_lecture_content",
            "notes_obligation": frag.get("notes_obligation") or source.get("notes_obligation") or "must_cover",
            "slide_decision": frag.get("slide_decision"),
            "notes_role": frag.get("notes_role"),
            "detailed_explanation_allowed": frag.get("detailed_explanation_allowed"),
            "triage_reason": frag.get("triage_reason"),
            "text": text,
            "knowledge_signals": signals,
            "knowledge_roles": roles,
            "knowledge_unit_candidates": frag.get("knowledge_unit_candidates", []),
            "exam_signal_score": exam_signal_score(text),
            "academic_content_score": academic_content_score(signals),
            "explanation_need_score": explanation_need_score(signals, text),
            "knowledge_role_summary": ", ".join(roles),
            "preview": re.sub(r"\s+", " ", text)[:220],
        })
    if notes_route(route):
        indexed.sort(key=lambda item: (
            int(item.get("lecture_order") or 10_000),
            int(item.get("source_order") or 10_000),
            slide_position(item),
            int(item.get("fragment_order") or 10_000),
        ))
    else:
        indexed.sort(key=lambda item: (item["academic_content_score"], item["explanation_need_score"], item["exam_signal_score"]), reverse=True)
    lecture_sources = [
        {
            "source_id": doc.get("id"),
            "source_name": doc.get("name"),
            "lecture_order": doc.get("lecture_order"),
        }
        for doc in source_scan.get("documents", [])
        if doc.get("lecture_source")
    ]
    notes_generation_fragments = [item for item in indexed if item.get("slide_decision") != "exclude"]
    detailed_knowledge_fragments = [
        item for item in notes_generation_fragments
        if item.get("slide_decision") is None or item.get("detailed_explanation_allowed") is True
    ]
    return {
        "schema_version": 2,
        "route": route,
        "fragment_count": len(indexed),
        "ordering_policy": "lecture_source_order_for_notes" if notes_route(route) else "score_order_for_report_analysis",
        "coverage_profile": {
            "knowledge_signal_counts": signal_counts(indexed),
            "content_triage_counts": value_counts(indexed, "content_triage"),
            "notes_obligation_counts": value_counts(indexed, "notes_obligation"),
            "slide_decision_counts": value_counts(indexed, "slide_decision"),
            "notes_role_counts": value_counts(indexed, "notes_role"),
            "slide_triage_audit": slide_triage_audit(indexed),
            "lecture_sources": lecture_sources,
            "lecture_source_count": len(lecture_sources),
            "knowledge_unit_candidate_count": sum(len(item.get("knowledge_unit_candidates", [])) for item in indexed),
        },
        "notes_generation_fragments": notes_generation_fragments if notes_route(route) else indexed,
        "detailed_knowledge_fragments": detailed_knowledge_fragments if notes_route(route) else indexed,
        "fragments": indexed,
    }


def load_scan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    scan = {
        "documents": [{"id": "S1", "name": "notes", "category": "knowledge_material", "lecture_source": True}],
        "fragments": [{
            "id": "F10",
            "source_id": "S1",
            "text": "Later topic boundary.",
            "source_order": 1,
            "fragment_order": 1,
            "slide_number": 10,
            "slide_decision": "use",
            "notes_role": "structure_marker",
            "detailed_explanation_allowed": False,
            "knowledge_signals": ["heading_or_topic_boundary"],
            "knowledge_roles": ["knowledge_unit_boundary"],
        }, {
            "id": "F2",
            "source_id": "S1",
            "text": "Explain the mechanism.",
            "source_order": 1,
            "fragment_order": 3,
            "slide_number": 2,
            "time_range": {"start_seconds": 12, "end_seconds": 20},
            "provenance": {"source_name": "notes", "slide_number": 2, "time_range": {"start_seconds": 12, "end_seconds": 20}},
            "slide_decision": "use",
            "notes_role": "knowledge_source",
            "detailed_explanation_allowed": True,
            "knowledge_signals": ["mechanism", "application"],
            "knowledge_roles": ["mechanism", "exam_application"],
        }, {
            "id": "F0",
            "source_id": "S1",
            "text": "Reading: textbook chapter and recommended reading.",
            "source_order": 1,
            "fragment_order": 2,
            "slide_number": 3,
            "content_triage": "reading_reference",
            "notes_obligation": "exclude_unless_directly_examinable",
            "slide_decision": "exclude",
            "notes_role": "non_teaching_material",
            "detailed_explanation_allowed": False,
            "triage_reason": "reading_or_textbook_reference_without_teaching_content",
            "knowledge_signals": [],
            "knowledge_roles": [],
        }],
    }
    out = build_index(scan)
    assert out["fragment_count"] == 3
    assert out["ordering_policy"] == "lecture_source_order_for_notes"
    assert [frag["id"] for frag in out["fragments"]] == ["F2", "F0", "F10"]
    assert [frag["id"] for frag in out["notes_generation_fragments"]] == ["F2", "F10"]
    assert [frag["id"] for frag in out["detailed_knowledge_fragments"]] == ["F2"]
    assert out["fragments"][0]["exam_signal_score"] >= 1
    assert out["fragments"][0]["academic_content_score"] >= 1
    assert out["coverage_profile"]["knowledge_signal_counts"]["mechanism"] == 1
    assert out["coverage_profile"]["notes_obligation_counts"]["exclude_unless_directly_examinable"] == 1
    assert out["coverage_profile"]["slide_decision_counts"]["exclude"] == 1
    assert out["coverage_profile"]["slide_triage_audit"][0]["exclude_count"] == 1
    assert out["fragments"][0]["provenance"]["slide_number"] == 2
    assert out["fragments"][0]["time_range"]["start_seconds"] == 12


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-scan")
    parser.add_argument("--route", default="exam_prep_notes")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = build_index(load_scan(args.source_scan), args.route)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
