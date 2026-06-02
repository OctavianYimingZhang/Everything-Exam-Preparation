from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def build_index(source_scan: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for frag in source_scan.get("fragments", []):
        text = normalise(str(frag.get("text", "")))
        if not text:
            continue
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        rows.append({
            "fragment_id": frag.get("id") or digest,
            "source_id": frag.get("source_id"),
            "role": frag.get("role"),
            "hash": digest,
            "terms": sorted(set(re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())))[:30],
            "text": text,
        })
    return {"fragments": rows, "coverage_units": [{"fragment_id": r["fragment_id"], "role": r["role"]} for r in rows]}


def self_test() -> int:
    scan = {"fragments": [{"id": "F1", "source_id": "S1", "role": "lecture_notes", "text": "Mechanism explains graph interpretation."}]}
    out = build_index(scan)
    assert out["fragments"] and out["coverage_units"]
    print("build_fragment_index self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.source_scan:
        parser.error("--source-scan is required")
    data = json.loads(Path(args.source_scan).read_text(encoding="utf-8"))
    out = build_index(data)
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
