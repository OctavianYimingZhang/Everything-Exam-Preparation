#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".toml", ".txt"}
SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "outputs"}
PROHIBITED_EXACT_NAME = "_".join(["Exam", "Preparation", "Notes"]) + ".docx"
PROHIBITED_RENDERER_CONSTANT = "OUTPUT" + "_NAME ="
FOCUSED_SKILL_FILES = [
    "skills/exam-prep-index/SKILL.md",
    "skills/exam-prep-notes/SKILL.md",
    "skills/exam-prep-mcq/SKILL.md",
    "skills/exam-prep-short-answer/SKILL.md",
    "skills/exam-prep-long-answer/SKILL.md",
    "skills/exam-prep-worked-solutions/SKILL.md",
    "skills/exam-prep-essay/SKILL.md",
    "skills/exam-prep-online-essay-exam/SKILL.md",
    "skills/exam-prep-extra-reading/SKILL.md",
    "skills/exam-prep-question-solver/SKILL.md",
    "skills/exam-prep-question-organizer/SKILL.md",
]


def tracked_files() -> list[Path]:
    proc = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return [ROOT / line for line in proc.stdout.splitlines() if line.strip()]
    return [path for path in ROOT.rglob("*") if path.is_file()]


def source_file(path: Path) -> bool:
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
    out: list[str] = []
    pattern = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
    for path in tracked_files():
        if not source_file(path):
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), 1):
            if pattern.search(line):
                out.append(f"{path.relative_to(ROOT)}:{line_no}")
                break
    return out


def prohibited_filename_locations() -> list[str]:
    out: list[str] = []
    for path in tracked_files():
        if not source_file(path):
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), 1):
            if PROHIBITED_EXACT_NAME in line or PROHIBITED_RENDERER_CONSTANT in line:
                out.append(f"{path.relative_to(ROOT)}:{line_no}")
    return out


def prohibited_wording_locations() -> list[str]:
    prohibited = [
        "question-" + "only",
        "answer-" + "only",
        "Notes " + "only",
        "Worked " + "only",
        "Diagnosis " + "only",
        "Add-on " + "only",
        "provenance labels " + "only",
        "only " + "knowledge explanations",
        "extra_reading_" + "notes_enrichment",
        "answer_" + "only_worked_solutions",
    ]
    out: list[str] = []
    for path in tracked_files():
        if not source_file(path):
            continue
        for line_no, line in enumerate(read_text(path).splitlines(), 1):
            if any(term in line for term in prohibited):
                out.append(f"{path.relative_to(ROOT)}:{line_no}")
    return out


def missing_terms(path: str, terms: list[str]) -> list[str]:
    text = read_text(ROOT / path)
    return [term for term in terms if term not in text]


def check() -> dict[str, object]:
    import validate_skill_contracts

    result = validate_skill_contracts.check_all()
    return {
        "status": result["status"],
        "gate": "delegates_to_validate_skill_contracts.py",
        "validator": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.parse_args()
    result = check()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "ok":
        sys.exit(1)


if __name__ == "__main__":
    main()
