#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def count_hints(scan: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for doc in scan.get("documents", []):
        hint = str(doc.get("source_hint") or doc.get("category") or "other_material")
        counts[hint] = counts.get(hint, 0) + 1
    return counts


def coverage_profile(scan: dict[str, Any]) -> dict[str, Any]:
    signal_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    unit_candidates = 0
    for collection in ("documents", "fragments"):
        for item in scan.get(collection, []):
            for signal in item.get("knowledge_signals", []) or []:
                signal_counts[signal] = signal_counts.get(signal, 0) + 1
            for role in item.get("knowledge_roles", []) or []:
                role_counts[role] = role_counts.get(role, 0) + 1
            unit_candidates += len(item.get("knowledge_unit_candidates", []) or [])
    core_signals = {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation", "evidence"}
    return {
        "knowledge_signal_counts": signal_counts,
        "knowledge_role_counts": role_counts,
        "knowledge_unit_candidate_count": unit_candidates,
        "has_knowledge_units": unit_candidates > 0,
        "has_core_knowledge_signals": any(signal in signal_counts for signal in core_signals),
        "has_explanation_need_signals": any(signal in signal_counts for signal in core_signals | {"term_density", "learning_objective"}),
        "has_exam_application_signals": "application" in signal_counts,
    }


def check_readiness(scan: dict[str, Any] | None, route: str = "exam_prep_notes") -> dict[str, Any]:
    scan = scan or {"documents": [], "fragments": []}
    return {
        "schema_version": 2,
        "route": route,
        "status": "ok",
        "source_hint_counts": count_hints(scan),
        "document_count": len(scan.get("documents", [])),
        "fragment_count": len(scan.get("fragments", [])),
        "coverage_profile": coverage_profile(scan),
        "observations": (scan.get("summary") or {}).get("extraction_notes", []),
    }


def load_scan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    scan = {"documents": [{"id": "S1", "source_hint": "knowledge_material", "text_chars": 10}], "fragments": [{"id": "F1", "knowledge_signals": ["definition"], "knowledge_roles": ["concept"], "knowledge_unit_candidates": [{"label": "Topic"}]}]}
    result = check_readiness(scan, "exam_prep_notes")
    assert result["status"] == "ok"
    assert result["coverage_profile"]["has_core_knowledge_signals"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", default="exam_prep_notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = check_readiness(load_scan(args.source_scan), args.route)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
