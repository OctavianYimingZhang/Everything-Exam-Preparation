from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any


def read_output(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        return html.unescape("\n".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw)))
    return path.read_text(encoding="utf-8", errors="ignore")


def lint(route: str, source_scan: dict[str, Any], output_text: str) -> dict[str, Any]:
    failures = []
    fragments = source_scan.get("fragments", [])
    roles = set(source_scan.get("source_roles") or [f.get("role") for f in fragments])
    words = len(re.findall(r"\w+", output_text))
    info_units = max(len(fragments), len(source_scan.get("documents", [])))
    if route == "exam_prep_notes" and info_units >= 4 and words < 120:
        failures.append({"check": "too_short_for_source_pack", "words": words, "source_units": info_units})
    if words > max(12000, info_units * 900):
        failures.append({"check": "too_verbose_for_source_pack", "words": words, "source_units": info_units})
    copied = 0
    for frag in fragments[:80]:
        text = re.sub(r"\s+", " ", str(frag.get("text", ""))).strip()
        if len(text.split()) >= 16 and text[:160] in output_text:
            copied += 1
    if copied >= 3:
        failures.append({"check": "copied_source_text", "count": copied})
    if roles.intersection({"practical_material", "data_problem_material"}) and not re.search(r"method|control|calculation|graph|table|limitation", output_text, flags=re.I):
        failures.append({"check": "practice_material_missing"})
    return {"status": "fail" if failures else "pass", "failures": failures}


def self_test() -> int:
    scan = {"source_roles": ["lecture_notes"], "fragments": [{"text": "Concept mechanism and limitation."}]}
    assert lint("exam_prep_notes", scan, "Concept mechanism and limitation explained for revision with method detail.")["status"] == "pass"
    print("output_sufficiency_linter self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=False, default="exam_prep_notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.source_scan or not args.output:
        parser.error("--source-scan and --output are required")
    scan = json.loads(Path(args.source_scan).read_text(encoding="utf-8"))
    result = lint(args.route, scan, read_output(Path(args.output)))
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
