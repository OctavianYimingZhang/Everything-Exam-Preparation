#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def load_json(path: str | None) -> Any:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalized_provenance(item: dict[str, Any]) -> dict[str, Any]:
    nested = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    return {
        "source_id": nested.get("source_id") or item.get("source_id"),
        "source_name": nested.get("source_name") or item.get("source_name"),
        "locator": nested.get("locator") or item.get("locator"),
        "page_number": nested.get("page_number") or item.get("page_number"),
        "slide_number": nested.get("slide_number") or item.get("slide_number"),
        "time_offset_seconds": nested.get("time_offset_seconds") or item.get("time_offset_seconds"),
        "time_range": nested.get("time_range") or item.get("time_range"),
    }


def unit_labels(fragment: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for candidate in fragment.get("knowledge_unit_candidates", []) or []:
        if isinstance(candidate, dict) and candidate.get("label"):
            labels.append(str(candidate["label"]).strip())
    for role in fragment.get("knowledge_roles", []) or []:
        label = str(role).strip().replace("_", " ")
        if label:
            labels.append(label)
    if not labels:
        preview = re.sub(r"\s+", " ", str(fragment.get("text") or "")).strip()
        if preview:
            labels.append(preview[:120])
    out: list[str] = []
    seen: set[str] = set()
    for label in labels:
        key = label.casefold()
        if key not in seen:
            seen.add(key)
            out.append(label)
    return out


def build_assessment_blueprint(
    source_fragments: list[dict[str, Any]],
    route_id: str = "assessment_blueprint",
    relevant_memory: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    units: dict[str, dict[str, Any]] = {}
    for fragment in source_fragments:
        provenance = normalized_provenance(fragment)
        for label in unit_labels(fragment):
            key = label.casefold()
            record = units.setdefault(key, {
                "knowledge_unit": label,
                "source_occurrences": 0,
                "provenance": [],
            })
            record["source_occurrences"] += 1
            if provenance not in record["provenance"]:
                record["provenance"].append(provenance)
    ordered = sorted(units.values(), key=lambda item: (-int(item["source_occurrences"]), str(item["knowledge_unit"])))
    total = sum(int(item["source_occurrences"]) for item in ordered) or 1
    for item in ordered:
        item["source_weight"] = round(int(item["source_occurrences"]) / total, 4)
    memory_units: list[str] = []
    for memory in relevant_memory or []:
        for key in ["weaknesses", "weakness_history", "knowledge_units"]:
            value = memory.get(key)
            if isinstance(value, list):
                for unit in value:
                    label = str(unit.get("knowledge_unit") if isinstance(unit, dict) else unit).strip()
                    if label and label not in memory_units:
                        memory_units.append(label)
    return {
        "contract": "everything-exam-preparation/assessment-blueprint",
        "version": "1.0",
        "route_id": route_id,
        "coverage_basis": "source_fragment_occurrence_not_predicted_marks",
        "knowledge_units": ordered,
        "relevant_memory_weakness_units": memory_units,
        "provenance_fields": ["source_name", "locator", "page_number", "slide_number", "time_offset_seconds", "time_range"],
    }


def evaluate_answer(payload: dict[str, Any]) -> dict[str, Any]:
    answer = str(payload.get("student_answer") or "")
    criteria = payload.get("criteria") or payload.get("expected_concepts") or []
    if not isinstance(criteria, list):
        raise ValueError("criteria must be a list")
    answer_normalized = re.sub(r"\s+", " ", answer).casefold()
    results: list[dict[str, Any]] = []
    for raw in criteria:
        if isinstance(raw, dict):
            criterion_id = str(raw.get("criterion_id") or raw.get("id") or raw.get("label") or "criterion")
            label = str(raw.get("label") or raw.get("expected_concept") or raw.get("text") or criterion_id)
            terms = raw.get("terms") or [label]
            provenance = raw.get("provenance") or []
        else:
            criterion_id = re.sub(r"[^a-z0-9]+", "_", str(raw).casefold()).strip("_") or "criterion"
            label = str(raw)
            terms = [label]
            provenance = []
        normalized_terms = [str(term).strip().casefold() for term in terms if str(term).strip()]
        matched_terms = [term for term in normalized_terms if term in answer_normalized]
        status = "addressed" if normalized_terms and matched_terms else "not_evidenced"
        results.append({
            "criterion_id": criterion_id,
            "label": label,
            "status": status,
            "matched_terms": matched_terms,
            "provenance": provenance,
        })
    addressed = sum(1 for item in results if item["status"] == "addressed")
    coverage = round(addressed / len(results), 4) if results else None
    evaluation_provenance: list[dict[str, Any]] = []
    for item in results:
        raw_provenance = item.get("provenance") or []
        entries = raw_provenance if isinstance(raw_provenance, list) else [raw_provenance]
        for entry in entries:
            if isinstance(entry, dict) and entry not in evaluation_provenance:
                evaluation_provenance.append(entry)
    return {
        "contract": "everything-exam-preparation/answer-evaluation",
        "version": "1.0",
        "evaluation_basis": "explicit_criteria_term_evidence",
        "criteria_count": len(results),
        "addressed_count": addressed,
        "criterion_coverage": coverage,
        "criteria": results,
        "provenance": evaluation_provenance,
        "strengths": [item["label"] for item in results if item["status"] == "addressed"],
        "weaknesses": [item["label"] for item in results if item["status"] == "not_evidenced"],
        "mark_awarded": None,
        "human_review_required": True,
        "history_event": {
            "mastery_units": [item["label"] for item in results if item["status"] == "addressed"],
            "weakness_units": [item["label"] for item in results if item["status"] == "not_evidenced"],
            "provenance": evaluation_provenance,
        },
    }


def build_timed_practice(blueprint: dict[str, Any], duration_minutes: int) -> dict[str, Any]:
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive")
    units = list(blueprint.get("knowledge_units") or [])
    if not units:
        raise ValueError("assessment blueprint has no knowledge units")
    slot_count = min(len(units), duration_minutes)
    selected = units[:slot_count]
    base = duration_minutes // slot_count
    remainder = duration_minutes % slot_count
    cursor = 0
    slots: list[dict[str, Any]] = []
    for idx, unit in enumerate(selected):
        minutes = base + (1 if idx < remainder else 0)
        start = cursor
        cursor += minutes
        slots.append({
            "order": idx + 1,
            "knowledge_unit": unit.get("knowledge_unit"),
            "duration_minutes": minutes,
            "time_provenance": {
                "start_minute": start,
                "end_minute": cursor,
                "allocation_basis": "explicit_total_duration_equal_slots",
            },
            "source_provenance": unit.get("provenance") or [],
        })
    return {
        "contract": "everything-exam-preparation/timed-practice",
        "version": "1.0",
        "duration_minutes": duration_minutes,
        "slots": slots,
        "unallocated_minutes": max(0, duration_minutes - sum(item["duration_minutes"] for item in slots)),
    }


def self_test() -> None:
    fragments = [{
        "source_id": "S1",
        "source_name": "Lecture 1.pdf",
        "page_number": 4,
        "locator": "page 4",
        "knowledge_roles": ["mechanism"],
        "knowledge_unit_candidates": [{"label": "Signal transduction"}],
        "text": "Signal transduction uses receptor activation.",
    }, {
        "source_id": "S2",
        "source_name": "Lecture 2.mp4",
        "time_range": {"start_seconds": 120, "end_seconds": 180},
        "knowledge_unit_candidates": [{"label": "Signal transduction"}],
        "text": "Receptor activation continues.",
    }]
    blueprint = build_assessment_blueprint(fragments, relevant_memory=[{"weaknesses": ["Signal transduction"]}])
    assert blueprint["knowledge_units"][0]["knowledge_unit"] == "Signal transduction"
    assert blueprint["knowledge_units"][0]["source_occurrences"] == 2
    assert blueprint["knowledge_units"][0]["provenance"][0]["page_number"] == 4
    assert blueprint["knowledge_units"][0]["provenance"][1]["time_range"]["start_seconds"] == 120
    evaluation = evaluate_answer({
        "student_answer": "Receptor activation initiates the pathway.",
        "criteria": [
            {"criterion_id": "receptor", "label": "Receptor activation", "terms": ["receptor activation"], "provenance": [{"page_number": 4}]},
            {"criterion_id": "kinase", "label": "Kinase cascade", "terms": ["kinase cascade"]},
        ],
    })
    assert evaluation["criterion_coverage"] == 0.5
    assert evaluation["mark_awarded"] is None
    assert evaluation["history_event"]["provenance"][0]["page_number"] == 4
    timed = build_timed_practice(blueprint, 20)
    assert sum(item["duration_minutes"] for item in timed["slots"]) == 20
    assert timed["slots"][0]["time_provenance"]["start_minute"] == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build assessment blueprints, evaluate answers, and prepare timed practice.")
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    blueprint_parser = subparsers.add_parser("blueprint")
    blueprint_parser.add_argument("--fragments", required=True)
    blueprint_parser.add_argument("--memory")
    blueprint_parser.add_argument("--out")
    evaluation_parser = subparsers.add_parser("evaluate")
    evaluation_parser.add_argument("--input", required=True)
    evaluation_parser.add_argument("--out")
    timed_parser = subparsers.add_parser("timed")
    timed_parser.add_argument("--blueprint", required=True)
    timed_parser.add_argument("--duration-minutes", required=True, type=int)
    timed_parser.add_argument("--out")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.command == "blueprint":
        fragment_payload = load_json(args.fragments) or []
        if isinstance(fragment_payload, dict):
            fragments = fragment_payload.get("source_fragments") or fragment_payload.get("fragments") or []
            context = fragment_payload.get("academic_task_context") or {}
        else:
            fragments = fragment_payload
            context = {}
        memory_payload = load_json(args.memory) if args.memory else None
        if isinstance(memory_payload, dict):
            memory = memory_payload.get("relevant_memory") or (memory_payload.get("academic_task_context") or {}).get("relevant_memory") or []
        else:
            memory = memory_payload or context.get("relevant_memory") or []
        result = build_assessment_blueprint(fragments, relevant_memory=memory)
    elif args.command == "evaluate":
        result = evaluate_answer(load_json(args.input) or {})
    elif args.command == "timed":
        result = build_timed_practice(load_json(args.blueprint) or {}, args.duration_minutes)
    else:
        parser.error("choose blueprint, evaluate, or timed")
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
