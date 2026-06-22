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
    files = [
        "SKILL.md",
        "README.md",
        "skill_manifest.json",
        "scripts/validate_skill_contracts.py",
        "scripts/github_ready_check.py",
        "scripts/build_review_questions.py",
        "scripts/exam_mode_tools.py",
        "scripts/publish_skill.py",
        ".github/workflows/ci.yml",
        ".github/workflows/skill-health.yml",
        *FOCUSED_SKILL_FILES,
    ]
    missing_files = [name for name in files if not (ROOT / name).exists()]
    terms = {
        "SKILL.md": missing_terms("SKILL.md", ["knowledge-only", "visible formulas", "distinct DOCX filename", "Auto-diagnosis review plan", "human review", "Essay Question and Example Essay enrichment", "Question Solving", "Question Organization"]),
        "references/exam_prep_notes_protocol.md": missing_terms("references/exam_prep_notes_protocol.md", ["Formula Visibility", "formula_block", "workflow", "black-and-white academic paper tables", "Notes coverage comes from the full set of lecture and course knowledge units"]),
        "references/exam_mode_and_addons_protocol.md": missing_terms("references/exam_mode_and_addons_protocol.md", ["human review", "Exam type", "Material type", "Notes generation choice", "complete worked-solution notes", "Past Paper-driven recurrence algorithm", "result-only", "question_solution_report", "organized_questions_docx", "strict same-knowledge-point", "Online Essay Exam", "Online Materials", "Lecture Materials"]),
        "references/input_and_evidence_protocol.md": missing_terms("references/input_and_evidence_protocol.md", ["human review", "source roles", "Material type", "strict same-knowledge-point retrieval", "latest matching unit", "online_material", "Online Materials are required, optional, forbidden, or unclear", "Lecture Materials may be used as primary evidence"]),
        "references/online_essay_exam_protocol.md": missing_terms("references/online_essay_exam_protocol.md", ["Online Essay Exam", "online_essay_exam_drafting", "Online Materials", "Lecture Materials", "Planning Approval"]),
        "scripts/plan_workflow.py": missing_terms("scripts/plan_workflow.py", ["human_review_required", "review_status", "auto_diagnosis", "review_targets", "question_solution_report", "organized_questions_docx", "online_essay_exam_drafting", "online_materials_permission_review", "lecture_materials_permission_review"]),
        "scripts/build_review_questions.py": missing_terms("scripts/build_review_questions.py", ["request_user_input", "exam_type_route", "material_type_source_roles", "notes_output_choice", "follow_up_question_batches", "selected_mixed_followup_keys", "online_essay_online_materials_permission", "online_essay_lecture_materials_permission"]),
        "scripts/exam_mode_tools.py": missing_terms("scripts/exam_mode_tools.py", ["build_question_solver_pack", "strict_same_knowledge_point_questions", "organize_questions_by_lecture_order", "write_organized_questions_docx", "build_mcq_saq_recurrence_report", "past_paper_question_records_from_scan"]),
        "scripts/generate_exam_prep_notes_docx.py": missing_terms("scripts/generate_exam_prep_notes_docx.py", ["def output_path", "def visible_formula", "safe_docx_name"]),
        "skill_manifest.json": missing_terms("skill_manifest.json", ["multi_skill_system", "focused_skills", "removed_focused_skills", "exam-prep-index", "exam-prep-worked-solutions", "exam-prep-online-essay-exam", "online_essay_exam_drafting", "exam-prep-question-solver", "exam-prep-question-organizer"]),
        "scripts/publish_skill.py": missing_terms("scripts/publish_skill.py", ["discover_focused_skills", "sync_focused_skill", "cleanup_removed_focused_skills", "focused_skills", "DEFAULT_LOCAL_SKILL_ROOT"]),
    }
    for focused_path in FOCUSED_SKILL_FILES:
        terms[focused_path] = missing_terms(focused_path, ["description:", "When this Skill is read from the source checkout"])
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
