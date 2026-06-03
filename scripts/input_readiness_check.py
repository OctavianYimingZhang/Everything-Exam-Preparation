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


def check_readiness(scan: dict[str, Any] | None, route: str = "exam_prep_notes") -> dict[str, Any]:
    scan = scan or {"documents": [], "fragments": []}
    return {
        "schema_version": 2,
        "route": route,
        "status": "ok",
        "source_hint_counts": count_hints(scan),
        "document_count": len(scan.get("documents", [])),
        "fragment_count": len(scan.get("fragments", [])),
        "observations": (scan.get("summary") or {}).get("extraction_notes", []),
    }


def load_scan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    scan = {"documents": [{"id": "S1", "source_hint": "knowledge_material", "text_chars": 10}], "fragments": [{"id": "F1"}]}
    result = check_readiness(scan, "exam_prep_notes")
    assert result["status"] == "ok"


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
