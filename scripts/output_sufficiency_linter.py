from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

LISTABLE_REASONS = {
    "source_numbered_list",
    "source_bulleted_list",
    "past_paper_list_question",
    "criteria_set",
    "taxonomy_or_contrast",
    "short_answer_mark_points",
    "definition_group",
}


def read_output(path: Path) -> tuple[str, int, int]:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            media_count = sum(1 for name in zf.namelist() if name.startswith("word/media/"))
            table_count = raw.count("<w:tbl>")
        return html.unescape("\n".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw))), media_count, table_count
    return path.read_text(encoding="utf-8", errors="ignore"), 0, 0


def selected_visual_count(plan: dict[str, Any] | None) -> int:
    if not plan:
        return 0
    selected = (plan.get("visual_decisions") or {}).get("selected_visual_ids") or []
    return max(len(selected), len(plan.get("visuals") or []))


def planned_table_count(plan: dict[str, Any] | None) -> int:
    if not plan:
        return 0
    return sum(
        1
        for section in plan.get("sections", []) or []
        for block in section.get("blocks", []) or []
        if isinstance(block, dict) and block.get("render_mode") == "compact_table"
    )


def iter_plan_blocks(plan: dict[str, Any] | None):
    if not plan:
        return
    for section in plan.get("sections", []) or []:
        for block in section.get("blocks", []) or []:
            if isinstance(block, dict):
                yield block


def listable_block_count(plan: dict[str, Any] | None) -> int:
    return sum(1 for block in iter_plan_blocks(plan) or [] if block.get("listability_reason") in LISTABLE_REASONS)


def structure_score(output_text: str, media_count: int, table_count: int) -> dict[str, Any]:
    bullet_count = len(re.findall(r"(?m)^\s*[-•]\s+", output_text))
    word_count = len(re.findall(r"\w+", output_text))
    return {
        "words": word_count,
        "bullets": bullet_count,
        "tables": table_count,
        "media": media_count,
        "effective_units": word_count / 55 + bullet_count * 0.6 + table_count * 4 + media_count * 3,
    }


def lint(
    route: str,
    source_scan: dict[str, Any],
    output_text: str,
    media_count: int = 0,
    plan: dict[str, Any] | None = None,
    table_count: int = 0,
) -> dict[str, Any]:
    failures = []
    warnings = []
    fragments = source_scan.get("fragments", [])
    roles = set(source_scan.get("source_roles") or [f.get("role") for f in fragments])
    structure = structure_score(output_text, media_count, table_count)
    words = structure["words"]
    info_units = max(len(fragments), len(source_scan.get("documents", [])))
    required_units = max(2, info_units * 0.75)
    if route == "exam_prep_notes" and info_units >= 4 and words < 120 and structure["effective_units"] < required_units:
        warnings.append({"check": "short_for_source_pack", "words": words, "source_units": info_units})
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
    visual_decisions = (plan or {}).get("visual_decisions") or {}
    if (
        (plan or {}).get("visual_policy") == "auto_source_visuals"
        and int(visual_decisions.get("candidate_count") or 0) > 0
        and int(visual_decisions.get("selected_count") or 0) == 0
        and not visual_decisions.get("rejected_visuals")
    ):
        failures.append({"check": "auto_source_visuals_without_selected_or_rejected_candidates"})
    planned_tables = planned_table_count(plan)
    if planned_tables and table_count < planned_tables:
        failures.append({"check": "planned_tables_not_rendered_as_docx_tables", "planned": planned_tables, "embedded": table_count})
    listable_blocks = listable_block_count(plan)
    if listable_blocks >= 3 and structure["bullets"] + table_count < listable_blocks:
        failures.append({
            "check": "listable_source_rendered_too_paragraph_heavy",
            "listable_blocks": listable_blocks,
            "bullets": structure["bullets"],
            "tables": table_count,
        })
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
    table_plan = {"sections": [{"blocks": [{"render_mode": "compact_table"}]}]}
    assert lint("exam_prep_notes", scan, "Feature Exam use", 0, table_plan, 0)["status"] == "fail"
    listable_plan = {
        "sections": [
            {
                "blocks": [
                    {"render_mode": "paragraph", "listability_reason": "criteria_set"},
                    {"render_mode": "paragraph", "listability_reason": "taxonomy_or_contrast"},
                    {"render_mode": "paragraph", "listability_reason": "source_numbered_list"},
                ]
            }
        ]
    }
    assert lint("exam_prep_notes", scan, "One paragraph only.", 0, listable_plan, 0)["status"] == "fail"
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
    output_text, media_count, table_count = read_output(Path(args.output))
    result = lint(args.route, scan, output_text, media_count, plan, table_count)
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
