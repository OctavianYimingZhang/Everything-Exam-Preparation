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
    indexed.sort(key=lambda item: (item["academic_content_score"], item["explanation_need_score"], item["exam_signal_score"]), reverse=True)
    return {
        "schema_version": 2,
        "route": route,
        "fragment_count": len(indexed),
        "coverage_profile": {
            "knowledge_signal_counts": signal_counts(indexed),
            "knowledge_unit_candidate_count": sum(len(item.get("knowledge_unit_candidates", [])) for item in indexed),
        },
        "fragments": indexed,
    }


def load_scan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    scan = {
        "documents": [{"id": "S1", "name": "notes", "category": "knowledge_material"}],
        "fragments": [{
            "id": "F1",
            "source_id": "S1",
            "text": "Explain the mechanism.",
            "knowledge_signals": ["mechanism", "application"],
            "knowledge_roles": ["mechanism", "exam_application"],
        }],
    }
    out = build_index(scan)
    assert out["fragment_count"] == 1
    assert out["fragments"][0]["exam_signal_score"] >= 1
    assert out["fragments"][0]["academic_content_score"] >= 1
    assert out["coverage_profile"]["knowledge_signal_counts"]["mechanism"] == 1


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
