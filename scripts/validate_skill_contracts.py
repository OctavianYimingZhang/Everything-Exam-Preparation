#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "outputs"}
PROHIBITED_EXACT_NAME = "_".join(["Exam", "Preparation", "Notes"]) + ".docx"
PROHIBITED_RENDERER_CONSTANT = "OUTPUT" + "_NAME ="


def json_readable(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def tracked_files() -> list[Path]:
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return [ROOT / line for line in proc.stdout.splitlines() if line.strip()]
    return [path for path in ROOT.rglob("*") if path.is_file()]


def is_scanned_source(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_PARTS for part in rel.parts):
        return False
    return path.suffix in TEXT_SUFFIXES or path.name.endswith(".schema.json")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def cjk_locations() -> list[str]:
    failures: list[str] = []
    pattern = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
    for path in tracked_files():
        if not is_scanned_source(path):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                failures.append(f"{path.relative_to(ROOT)}:{line_no}")
                break
    return failures


def prohibited_filename_locations() -> list[str]:
    failures: list[str] = []
    for path in tracked_files():
        if not is_scanned_source(path):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            if PROHIBITED_EXACT_NAME in line or PROHIBITED_RENDERER_CONSTANT in line:
                failures.append(f"{path.relative_to(ROOT)}:{line_no}")
    return failures


def require_terms(path: str, terms: list[str]) -> list[str]:
    text = read_text(ROOT / path)
    return [term for term in terms if term not in text]


def check_all() -> dict[str, Any]:
    files = ["SKILL.md", "README.md", "skill_manifest.json", "scripts/publish_skill.py"]
    schemas = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "schemas").glob("*.schema.json"))
    missing_files = [name for name in files if not (ROOT / name).exists()]
    invalid_schemas = [name for name in schemas if not json_readable(ROOT / name)]
    missing_terms = {
        "SKILL.md": require_terms(
            "SKILL.md",
            [
                "knowledge-only",
                "visible formulas",
                "Do not treat an exact filename as part of the Skill contract.",
            ],
        ),
        "references/exam_prep_notes_protocol.md": require_terms(
            "references/exam_prep_notes_protocol.md",
            [
                "knowledge-only teaching notes",
                "Formula Visibility",
                "formula_block",
                "Loose top-level planning fields are internal.",
            ],
        ),
        "references/language_quality_contract.md": require_terms(
            "references/language_quality_contract.md",
            [
                "compatibility entrypoint",
                "formula visibility",
                "knowledge-only",
            ],
        ),
        "scripts/generate_exam_prep_notes_docx.py": require_terms(
            "scripts/generate_exam_prep_notes_docx.py",
            [
                "def visible_formula",
                "def output_path",
                "safe_docx_name",
                "formula_block",
                "INTERNAL_PUBLIC_HEADINGS",
            ],
        ),
    }
    missing_terms = {name: terms for name, terms in missing_terms.items() if terms}
    cjk = cjk_locations()
    prohibited_names = prohibited_filename_locations()
    failures = {
        "missing_files": missing_files,
        "invalid_schemas": invalid_schemas,
        "missing_terms": missing_terms,
        "non_english_cjk_locations": cjk,
        "fixed_filename_locations": prohibited_names,
    }
    ok = not any(failures.values())
    return {
        "status": "ok" if ok else "error",
        "files": {name: (ROOT / name).exists() for name in files},
        "schemas": {name: json_readable(ROOT / name) for name in schemas},
        "failures": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="all")
    parser.add_argument("--schema")
    parser.add_argument("--input")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert check_all()["status"] == "ok"
        return
    result = check_all()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "ok":
        sys.exit(1)


if __name__ == "__main__":
    main()
