from __future__ import annotations

import argparse
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


def docx_text_and_xml(path: Path) -> tuple[str, str, str]:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        if "word/document.xml" not in names:
            raise ValueError("missing word/document.xml")
        doc = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        styles = zf.read("word/styles.xml").decode("utf-8", errors="ignore") if "word/styles.xml" in names else ""
    text = re.sub(r"<[^>]+>", " ", doc)
    return text, doc, styles


def lint(route: str, path: Path) -> dict:
    failures = []
    expected = EXPECTED.get(route)
    if path.is_dir():
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
    if docx_path and docx_path.exists():
        try:
            text, doc, styles = docx_text_and_xml(docx_path)
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
            for cx in re.findall(r'cx="(\d+)"', doc):
                if int(cx) > 3474720:
                    failures.append({"check": "image_too_wide"})
        except Exception as exc:
            failures.append({"check": "docx_openability", "error": type(exc).__name__})
    return {"status": "fail" if failures else "pass", "failures": failures}


def self_test() -> int:
    from generate_exam_prep_notes_docx import generate
    with tempfile.TemporaryDirectory() as td:
        generate({"title": "Exam Preparation Notes", "topics": ["Mechanism and limitation are explained for revision."]}, Path(td))
        assert lint("exam_prep_notes", Path(td))["status"] == "pass"
    print("deliverable_surface_linter self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", default="exam_prep_notes")
    parser.add_argument("--path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.path:
        parser.error("--path is required")
    result = lint(args.route, Path(args.path))
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
