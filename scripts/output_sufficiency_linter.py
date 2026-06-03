from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any


def read_output(path: Path) -> tuple[str, int]:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            media_count = sum(1 for name in zf.namelist() if name.startswith("word/media/"))
        return html.unescape("\n".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw))), media_count
    return path.read_text(encoding="utf-8", errors="ignore"), 0


def selected_visual_count(plan: dict[str, Any] | None) -> int:
    if not plan:
        return 0
    selected = (plan.get("visual_decisions") or {}).get("selected_visual_ids") or []
    return max(len(selected), len(plan.get("visuals") or []))


def lint(route: str, source_scan: dict[str, Any], output_text: str, media_count: int = 0, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    failures = []
    warnings = []
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
    planned_visuals = selected_visual_count(plan)
    if planned_visuals and media_count < planned_visuals:
        failures.append({"check": "planned_visuals_not_embedded", "planned": planned_visuals, "embedded": media_count})
    elif source_scan.get("visual_source_references") and media_count == 0 and not ((plan or {}).get("visual_decisions") or {}).get("skip_reason"):
        warnings.append({
            "check": "source_visuals_unselected_without_recorded_skip_reason",
            "count": len(source_scan.get("visual_source_references", [])),
        })
    return {"status": "fail" if failures else "pass", "failures": failures, "warnings": warnings}


def self_test() -> int:
    scan = {"source_roles": ["lecture_notes"], "fragments": [{"text": "Concept mechanism and limitation."}]}
    assert lint("exam_prep_notes", scan, "Concept mechanism and limitation explained for revision with method detail.")["status"] == "pass"
    planned = {"visual_decisions": {"selected_visual_ids": ["V1"]}, "visuals": [{"visual_id": "V1"}]}
    assert lint("exam_prep_notes", scan, "Text with enough explanation for revision.", 0, planned)["status"] == "fail"
    print("output_sufficiency_linter self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=False, default="exam_prep_notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--output")
    parser.add_argument("--plan")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.source_scan or not args.output:
        parser.error("--source-scan and --output are required")
    scan = json.loads(Path(args.source_scan).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8")) if args.plan else None
    output_text, media_count = read_output(Path(args.output))
    result = lint(args.route, scan, output_text, media_count, plan)
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
