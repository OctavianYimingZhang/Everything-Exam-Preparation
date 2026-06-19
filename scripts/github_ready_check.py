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


def tracked_files() -> list[Path]:
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, text=True, capture_output=True)
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
    files = [
        "SKILL.md",
        "README.md",
        "skill_manifest.json",
        "scripts/validate_skill_contracts.py",
        "scripts/github_ready_check.py",
        "scripts/build_review_questions.py",
        "scripts/publish_skill.py",
        ".github/workflows/ci.yml",
        ".github/workflows/skill-health.yml",
    ]
    missing_files = [name for name in files if not (ROOT / name).exists()]
    terms = {
        "SKILL.md": missing_terms("SKILL.md", ["knowledge-only", "visible formulas", "distinct DOCX filename", "Auto-diagnosis review plan", "human review", "Essay Question and Example Essay enrichment"]),
        "references/exam_prep_notes_protocol.md": missing_terms("references/exam_prep_notes_protocol.md", ["Formula Visibility", "formula_block", "workflow", "black-and-white academic paper tables", "Notes coverage comes from the full set of lecture and course knowledge units"]),
        "references/exam_mode_and_addons_protocol.md": missing_terms("references/exam_mode_and_addons_protocol.md", ["human review", "Exam type", "Material type", "output set confirmation", "complete worked-solution notes", "question-derived high-frequency knowledge points for the add-on"]),
        "references/input_and_evidence_protocol.md": missing_terms("references/input_and_evidence_protocol.md", ["human review", "source roles", "Material type"]),
        "scripts/plan_workflow.py": missing_terms("scripts/plan_workflow.py", ["human_review_required", "review_status", "auto_diagnosis", "review_targets"]),
        "scripts/build_review_questions.py": missing_terms("scripts/build_review_questions.py", ["request_user_input", "exam_type_route", "material_type_source_roles", "output_file_set"]),
        "scripts/generate_exam_prep_notes_docx.py": missing_terms("scripts/generate_exam_prep_notes_docx.py", ["def output_path", "def visible_formula", "safe_docx_name"]),
    }
    terms = {name: missing for name, missing in terms.items() if missing}
    failures = {
        "missing_files": missing_files,
        "missing_terms": terms,
        "non_english_cjk_locations": cjk_locations(),
        "fixed_filename_locations": prohibited_filename_locations(),
        "prohibited_wording_locations": prohibited_wording_locations(),
    }
    return {
        "status": "ok" if not any(failures.values()) else "error",
        "files": {name: (ROOT / name).exists() for name in files},
        "failures": failures,
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
