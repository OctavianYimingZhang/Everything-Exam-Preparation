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
    failures: list[str] = []
    for path in tracked_files():
        if not is_scanned_source(path):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            if any(term in line for term in prohibited):
                failures.append(f"{path.relative_to(ROOT)}:{line_no}")
    return failures


def require_terms(path: str, terms: list[str]) -> list[str]:
    text = read_text(ROOT / path)
    return [term for term in terms if term not in text]


def script_self_test(script: str) -> str | None:
    proc = subprocess.run([sys.executable, str(ROOT / script), "--self-test"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return None
    return f"{script}: {proc.stderr.strip() or proc.stdout.strip() or proc.returncode}"


def check_all() -> dict[str, Any]:
    files = ["SKILL.md", "README.md", "skill_manifest.json", "scripts/publish_skill.py", "scripts/build_review_questions.py"]
    schemas = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "schemas").glob("*.schema.json"))
    missing_files = [name for name in files if not (ROOT / name).exists()]
    invalid_schemas = [name for name in schemas if not json_readable(ROOT / name)]
    missing_terms = {
        "SKILL.md": require_terms(
            "SKILL.md",
            [
                "knowledge-only",
                "visible formulas",
                "distinct DOCX filename",
                "Default output language is English",
                "Exam Type Related",
                "academic source visuals",
                "Practical Worked Solutions",
                "Auto-diagnosis review plan",
                "human review",
                "Exam type",
                "Material type",
                "output set",
                "Essay Question and Example Essay enrichment",
                "question-derived high-frequency knowledge points for the add-on",
            ],
        ),
        "references/exam_prep_notes_protocol.md": require_terms(
            "references/exam_prep_notes_protocol.md",
            [
                "knowledge-only teaching notes",
                "Formula Visibility",
                "Visual Rendering",
                "lecture and exam-relevant knowledge",
                "black-and-white academic paper tables",
                "domain-neutral",
                "formula_block",
                "image_plus_kp_list",
                "worked_example",
                "Loose top-level planning fields are internal.",
                "Notes coverage comes from the full set of lecture and course knowledge units",
                "Question and practice material calibrate add-on emphasis",
            ],
        ),
        "references/exam_mode_and_addons_protocol.md": require_terms(
            "references/exam_mode_and_addons_protocol.md",
            [
                "Exam Type Related",
                "separate outputs",
                "Practice material can still inform Notes coverage",
                "question-based Exam Type Related DOCX",
                "practical_worked_solutions_docx",
                "human review",
                "Exam type",
                "Material type",
                "output set confirmation",
                "Mixed",
                "complete worked-solution notes",
                "exam-answering ability",
                "user-confirmed final output set",
                "question-derived high-frequency knowledge points for the add-on",
            ],
        ),
        "references/extra_reading_workflow.md": require_terms(
            "references/extra_reading_workflow.md",
            [
                "Essay Question and Example Essay enrichment",
                "essay-enrichment sources",
                "do not decide general Notes depth",
            ],
        ),
        "references/input_and_evidence_protocol.md": require_terms(
            "references/input_and_evidence_protocol.md",
            [
                "human review",
                "source roles",
                "Material type",
                "Auto-diagnosis review plan",
                "Essay Question and Example Essay enrichment",
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
                "image_plus_kp_list",
                "worked_example",
                "INTERNAL_PUBLIC_HEADINGS",
            ],
        ),
        "scripts/plan_workflow.py": require_terms(
            "scripts/plan_workflow.py",
            [
                "human_review_required",
                "review_status",
                "auto_diagnosis",
                "review_targets",
                "human_review_exam_material_output_confirmation",
                "worked_solution_teaching_notes",
            ],
        ),
        "scripts/build_review_questions.py": require_terms(
            "scripts/build_review_questions.py",
            [
                "request_user_input",
                "exam_type_route",
                "material_type_source_roles",
                "output_file_set",
                "Auto-diagnosis review plan",
            ],
        ),
        "README.md": require_terms(
            "README.md",
            [
                "human review",
                "Exam type",
                "Material type",
                "output set confirmation",
                "scripts/build_review_questions.py",
                "exam-relevant knowledge",
                "question-derived high-frequency knowledge points for the add-on",
            ],
        ),
        "agents/openai.yaml": require_terms(
            "agents/openai.yaml",
            [
                "human_review",
                "public_content",
                "internal_workflow_record",
                "Auto-diagnosis review plan",
                "request_user_input",
                "Exam type",
                "Material type",
                "output set confirmation",
            ],
        ),
    }
    missing_terms = {name: terms for name, terms in missing_terms.items() if terms}
    cjk = cjk_locations()
    prohibited_names = prohibited_filename_locations()
    prohibited_wording = prohibited_wording_locations()
    script_self_tests = [
        failure
        for failure in [
            script_self_test("scripts/plan_workflow.py"),
            script_self_test("scripts/build_review_questions.py"),
        ]
        if failure
    ]
    failures = {
        "missing_files": missing_files,
        "invalid_schemas": invalid_schemas,
        "missing_terms": missing_terms,
        "script_self_tests": script_self_tests,
        "non_english_cjk_locations": cjk,
        "fixed_filename_locations": prohibited_names,
        "prohibited_wording_locations": prohibited_wording,
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
