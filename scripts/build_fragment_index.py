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


def exam_notes_source_scopes(source_scan: dict[str, Any]) -> dict[str, str]:
    return {
        str(decision.get("source_id")): str(decision.get("evidence_scope"))
        for decision in source_scan.get("source_decisions", [])
        if decision.get("route") == "exam_prep_notes"
    }


def fragment_allowed_for_notes(frag: dict[str, Any], scopes: dict[str, str]) -> bool:
    source_id = str(frag.get("source_id") or "")
    if scopes:
        return scopes.get(source_id) == "factual_course_content"
    return str(frag.get("role") or "") in {"lecture_slides", "lecture_notes", "official_course_notes", "practical_material", "data_problem_material", "extra_reading"}


def build_index(source_scan: dict[str, Any], route: str = "exam_prep_notes") -> dict[str, Any]:
    rows = []
    scopes = exam_notes_source_scopes(source_scan)
    for frag in source_scan.get("fragments", []):
        if route == "exam_prep_notes" and not fragment_allowed_for_notes(frag, scopes):
            continue
        text = normalise(str(frag.get("text", "")))
        if not text:
            continue
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        rows.append({
            "fragment_id": frag.get("id") or digest,
            "source_id": frag.get("source_id"),
            "role": frag.get("role"),
            "evidence_scope": scopes.get(str(frag.get("source_id") or ""), frag.get("evidence_scope")),
            "hash": digest,
            "terms": sorted(set(re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())))[:30],
            "text": text,
        })
    return {"fragments": rows, "coverage_units": [{"fragment_id": r["fragment_id"], "role": r["role"]} for r in rows]}


def self_test() -> int:
    scan = {
        "source_decisions": [
            {"source_id": "S1", "route": "exam_prep_notes", "evidence_scope": "factual_course_content"},
            {"source_id": "S2", "route": "exam_prep_notes", "evidence_scope": "style_only"},
        ],
        "fragments": [
            {"id": "F1", "source_id": "S1", "role": "lecture_notes", "text": "Mechanism explains graph interpretation."},
            {"id": "F2", "source_id": "S2", "role": "previous_generated_output", "text": "Do not treat this old output as facts."},
        ],
    }
    out = build_index(scan)
    assert len(out["fragments"]) == 1 and out["fragments"][0]["source_id"] == "S1"
    print("build_fragment_index self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-scan")
    parser.add_argument("--route", default="exam_prep_notes")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.source_scan:
        parser.error("--source-scan is required")
    data = json.loads(Path(args.source_scan).read_text(encoding="utf-8"))
    out = build_index(data, args.route)
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
