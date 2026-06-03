from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path

EXPECTED = {
    "exam_prep_notes": "Exam_Preparation_Notes.docx",
    "essay_addon": "Example_Essay.docx",
}
INTERNAL_SUFFIXES = {".json", ".jsonl", ".log", ".tmp"}
INTERNAL_MARKERS = ["qa flag", "source map", "confidence band", "internal manifest", "extraction note", "ai process"]


def stale_term(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_PUBLIC_SURFACES = [
    r"\bVisual aids\b",
    r"\bVisual aid for\b",
    rf"\b{re.escape(stale_term('Lecture ', 'Knowledge ', 'Walkthrough'))}\b",
    rf"\b{re.escape(stale_term('Lecture', '_Knowledge', '_Walkthrough'))}\b",
    r"\bDevelopment decisions are affected by this topic because\b",
]


def docx_text_and_xml(path: Path) -> tuple[str, str, str, int, int, int]:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        if "word/document.xml" not in names:
            raise ValueError("missing word/document.xml")
        doc = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        styles = zf.read("word/styles.xml").decode("utf-8", errors="ignore") if "word/styles.xml" in names else ""
        media_count = sum(1 for name in names if name.startswith("word/media/"))
        drawing_count = doc.count("<w:drawing>")
        table_count = doc.count("<w:tbl>")
    chunks = re.findall(r"<w:t[^>]*>(.*?)</w:t>", doc)
    text = html.unescape("\n".join(chunks) if chunks else re.sub(r"<[^>]+>", " ", doc))
    return text, doc, styles, media_count, drawing_count, table_count


def plan_blocks(plan: dict | None) -> list[dict]:
    if not plan:
        return []
    blocks = []
    for section in plan.get("sections", []) or []:
        blocks.extend(block for block in section.get("blocks", []) or [] if isinstance(block, dict))
    return blocks


def planned_visual_count(plan: dict | None) -> int:
    if not plan:
        return 0
    selected = (plan.get("visual_decisions") or {}).get("selected_visual_ids") or []
    return max(len(selected), len(plan.get("visuals") or []))


def planned_table_count(plan: dict | None) -> int:
    return sum(1 for block in plan_blocks(plan) if block.get("render_mode") == "compact_table")


def planned_image_block_count(plan: dict | None) -> int:
    return sum(1 for block in plan_blocks(plan) if block.get("render_mode") == "image_plus_kp_list")


def load_internal_plan(path: Path) -> dict | None:
    plan_path = path / "internal" / "Exam_Preparation_Notes.plan.json"
    if not plan_path.exists():
        return None
    return json.loads(plan_path.read_text(encoding="utf-8"))


def lint(route: str, path: Path, plan: dict | None = None) -> dict:
    failures = []
    expected = EXPECTED.get(route)
    if path.is_dir():
        if route == "exam_prep_notes":
            internal_plan = path / "internal" / "Exam_Preparation_Notes.plan.json"
            internal_scan = path / "internal" / "source_scan.json"
            if not internal_plan.exists():
                failures.append({"check": "internal_plan_json_missing", "expected": "internal/Exam_Preparation_Notes.plan.json"})
            if not internal_scan.exists():
                failures.append({"check": "internal_source_scan_missing", "expected": "internal/source_scan.json"})
            if plan is None and internal_plan.exists():
                plan = load_internal_plan(path)
        if expected:
            docx_path = path / expected
            if not docx_path.exists():
                failures.append({"check": "expected_docx_missing", "expected": expected})
        else:
            found = list(path.glob("*.docx"))
            docx_path = found[0] if found else None
        for item in path.iterdir():
            if item.suffix.lower() in INTERNAL_SUFFIXES:
                failures.append({"check": "internal_file_in_output_folder", "path": item.name})
    else:
        docx_path = path
        if expected and path.name != expected:
            failures.append({"check": "unexpected_docx_name", "expected": expected, "actual": path.name})
    if docx_path and docx_path.exists():
        try:
            text, doc, styles, media_count, drawing_count, table_count = docx_text_and_xml(docx_path)
            if "Arial" not in styles and "Arial" not in doc:
                failures.append({"check": "font_not_arial"})
            if 'w:top="1417"' not in doc:
                failures.append({"check": "margin_not_2_5_cm"})
            if 'w:line="360"' not in doc and 'w:line="360"' not in styles:
                failures.append({"check": "line_spacing_not_1_5"})
            if not re.search(r'w:jc w:val="both"', doc + styles):
                failures.append({"check": "body_not_justified"})
            lowered = text.lower()
            hits = [m for m in INTERNAL_MARKERS if m in lowered]
            if hits:
                failures.append({"check": "internal_surface_text", "markers": hits})
            surface_hits = [pattern for pattern in FORBIDDEN_PUBLIC_SURFACES if re.search(pattern, text, flags=re.I)]
            if surface_hits:
                failures.append({"check": "forbidden_public_surface", "patterns": surface_hits})
            for cx in re.findall(r'cx="(\d+)"', doc):
                if int(cx) > 3474720:
                    failures.append({"check": "image_too_wide"})
            expected_visuals = planned_visual_count(plan)
            if expected_visuals and media_count < expected_visuals:
                failures.append({"check": "planned_visuals_missing_from_docx", "planned": expected_visuals, "embedded": media_count})
            if planned_image_block_count(plan) and (media_count == 0 or drawing_count == 0):
                failures.append({"check": "planned_image_blocks_missing_docx_images", "image_blocks": planned_image_block_count(plan), "media": media_count, "drawings": drawing_count})
            expected_tables = planned_table_count(plan)
            if expected_tables and table_count < expected_tables:
                failures.append({"check": "planned_tables_missing_from_docx", "planned": expected_tables, "embedded": table_count})
            visual_decisions = (plan or {}).get("visual_decisions") or {}
            if (
                (plan or {}).get("visual_policy") == "auto_source_visuals"
                and int(visual_decisions.get("candidate_count") or 0) > 0
                and int(visual_decisions.get("selected_count") or 0) == 0
                and not visual_decisions.get("rejected_visuals")
            ):
                failures.append({"check": "auto_source_visuals_no_selection"})
        except Exception as exc:
            failures.append({"check": "docx_openability", "error": type(exc).__name__})
    return {"status": "fail" if failures else "pass", "failures": failures}


def self_test() -> int:
    from generate_exam_prep_notes_docx import generate, sample_strict_plan, write_minimal_docx
    with tempfile.TemporaryDirectory() as td:
        image_path = Path(td) / "visual.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0P\x0f\x00\x05\x83\x02\x7f\x9756W\x00\x00\x00\x00IEND\xaeB`\x82")
        plan = sample_strict_plan(image_path)
        generate(plan, Path(td))
        internal = Path(td) / "internal"
        internal.mkdir()
        (internal / "Exam_Preparation_Notes.plan.json").write_text(json.dumps(plan), encoding="utf-8")
        (internal / "source_scan.json").write_text(json.dumps({"source_decisions": []}), encoding="utf-8")
        assert lint("exam_prep_notes", Path(td), plan)["status"] == "pass"
        bad = Path(td) / "Exam_Preparation_Notes_bad.docx"
        write_minimal_docx(bad, [("Exam Preparation Notes", "Title", "center"), ("Visual aids", "Heading1", "left")])
        assert lint("exam_prep_notes", bad)["status"] == "fail"
    print("deliverable_surface_linter self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", default="exam_prep_notes")
    parser.add_argument("--path")
    parser.add_argument("--plan")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.path:
        parser.error("--path is required")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8")) if args.plan else None
    result = lint(args.route, Path(args.path), plan)
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
