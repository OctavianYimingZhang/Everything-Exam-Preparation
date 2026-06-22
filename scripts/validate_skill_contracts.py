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
FOCUSED_SKILL_FILES = [
    "skills/exam-prep-index/SKILL.md",
    "skills/exam-prep-notes/SKILL.md",
    "skills/exam-prep-slide-triage/SKILL.md",
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


def json_readable(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def tracked_files() -> list[Path]:
    proc = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True, capture_output=True)
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


def manifest_sync_failures() -> list[str]:
    manifest_path = ROOT / "skill_manifest.json"
    if not manifest_path.exists():
        return ["skill_manifest.json missing"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"skill_manifest.json unreadable: {exc}"]
    failures: list[str] = []
    plan_text = read_text(ROOT / "scripts/plan_workflow.py")
    questions_text = read_text(ROOT / "scripts/build_review_questions.py")
    for route in manifest.get("routes", []) or []:
        route = str(route)
        if route not in plan_text:
            failures.append(f"route {route} missing from scripts/plan_workflow.py")
        if route not in questions_text:
            failures.append(f"route {route} missing from scripts/build_review_questions.py")
    for skill in manifest.get("focused_skills", []) or []:
        name = str(skill.get("name") or "")
        path = str(skill.get("path") or "")
        route = str(skill.get("route") or "")
        if path and not (ROOT / path).exists():
            failures.append(f"focused skill path missing for {name}: {path}")
        if name and name not in read_text(ROOT / "skill_manifest.json"):
            failures.append(f"focused skill name missing from manifest text: {name}")
        if route and route != "index" and route not in plan_text and route not in questions_text and route != "extra_reading_enrichment" and route != "notes_material_analysis":
            failures.append(f"focused skill route {route} for {name} is not referenced by route scripts")
    return failures


def script_self_test(script: str) -> str | None:
    proc = subprocess.run([sys.executable, str(ROOT / script), "--self-test"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return None
    return f"{script}: {proc.stderr.strip() or proc.stdout.strip() or proc.returncode}"


def check_all() -> dict[str, Any]:
    files = [
        "SKILL.md",
        "README.md",
        "skill_manifest.json",
        "scripts/publish_skill.py",
        "scripts/build_review_questions.py",
        "scripts/exam_mode_tools.py",
        *FOCUSED_SKILL_FILES,
    ]
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
                "whether Notes should be generated",
                "Essay Question and Example Essay enrichment",
                "Past Paper-driven recurrence report",
                "result-only",
                "Question Solving",
                "Question Organization",
                "strict same-knowledge-point",
                "organized_questions_docx",
                "coverage_policy: lecture_unit_complete",
                "Notes and Reports are intentionally separate",
                "broad Notes coverage",
                "exam-prep-slide-triage",
                "slide_decision",
                "merge_with_previous",
                "detailed_explanation_allowed",
                "slide_triage_audit",
                "Online Essay Exam",
                "online_essay_exam_drafting",
                "Online Materials and Lecture Materials permissions",
                "drafting branch rather than a Specific Research Report",
            ],
        ),
        "references/online_essay_exam_protocol.md": require_terms(
            "references/online_essay_exam_protocol.md",
            [
                "Online Essay Exam is a first-class drafting branch",
                "not a subtype of ordinary Essay Question",
                "48 hours is metadata",
                "must not become separate public Types",
                "Online Materials are required, optional, forbidden, or unclear",
                "Lecture Materials may be used as primary evidence",
                "Missing source-permission answers remain plan-changing unresolved items",
                "locked brief",
                "evidence map",
                "Planning Approval",
                "draft",
                "QA",
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
                "Question and practice material calibrate Specific Research Report emphasis",
                "Notes and Reports are intentionally separate",
                "coverage_policy: lecture_unit_complete",
                "Lecture-Unit Complete Coverage",
                "broad lecture reconstruction",
                "concise exam-priority reinforcement",
                "core_lecture_content",
                "supporting_example",
                "reading_reference",
                "admin_or_boilerplate",
                "low_exam_relevance_context",
                "coverage_audit",
                "Slide Triage Before Notes",
                "exam-prep-slide-triage",
                "not a detail-level grading system",
                "slide_decision",
                "merge_with_previous",
                "detailed_explanation_allowed",
                "slide_triage_audit",
                "Specific Research Reports must not use slide triage",
            ],
        ),
        "references/exam_mode_and_addons_protocol.md": require_terms(
            "references/exam_mode_and_addons_protocol.md",
            [
                "Exam Type Related",
                "Specific Research Reports",
                "Practice material can still inform Notes coverage",
                "question-based Specific Research Report",
                "practical_worked_solutions_docx",
                "human review",
                "Exam type",
                "Material type",
                "Notes generation choice",
                "Mixed",
                "complete worked-solution notes",
                "exam-answering ability",
                "user-confirmed route and Notes decision",
                "Past Paper-driven recurrence algorithm",
                "result-only",
                "question_solution_report",
                "organized_questions_docx",
                "strict same-knowledge-point",
                "latest matching lecture",
                "concise exam-priority reinforcement",
                "coverage_policy: lecture_unit_complete",
                "must not narrow",
                "Slide triage is a Notes material-analysis step",
                "slide_decision",
                "slide_triage_audit",
                "Online Essay Exam",
                "Online Materials",
                "Lecture Materials",
            ],
        ),
        "references/extra_reading_workflow.md": require_terms(
            "references/extra_reading_workflow.md",
            [
                "Essay Question and Example Essay enrichment",
                "Online Essay Exam enrichment",
                "confirmed source permissions",
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
                "online_material",
                "Online Materials are required, optional, forbidden, or unclear",
                "Lecture Materials may be used as primary evidence",
                "strict same-knowledge-point retrieval",
                "latest matching unit",
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
        "schemas/exam_prep_notes_plan.schema.json": require_terms(
            "schemas/exam_prep_notes_plan.schema.json",
            [
                "\"document_kind\"",
                "\"docx_notes\"",
                "\"coverage_policy\"",
                "\"lecture_unit_complete\"",
                "\"coverage_audit\"",
                "\"lecture_sources\"",
                "\"content_triage\"",
                "\"core_lecture_content\"",
                "\"slide_triage_audit\"",
                "\"merge_with_previous_count\"",
                "\"excluded_reasons\"",
            ],
        ),
        "scripts/extract_sources.py": require_terms(
            "scripts/extract_sources.py",
            [
                "LECTURE_FILENAME_RE",
                "is_lecture_source",
                "content_triage",
                "core_lecture_content",
                "reading_reference",
                "admin_or_boilerplate",
                "notes_obligation",
                "PPTX_SLIDE_XML_RE",
                "read_pptx_slide_texts",
                "slide_triage",
                "slide_decision",
                "merge_with_previous",
                "detailed_explanation_allowed",
            ],
        ),
        "scripts/build_fragment_index.py": require_terms(
            "scripts/build_fragment_index.py",
            [
                "lecture_source_order_for_notes",
                "content_triage_counts",
                "notes_obligation_counts",
                "lecture_sources",
                "slide_triage_audit",
                "notes_generation_fragments",
                "detailed_knowledge_fragments",
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
                "worked_solution_specific_research_report",
                "question_solution_report",
                "organized_questions_docx",
                "strict_same_knowledge_point_question_retrieval",
                "online_essay_exam_drafting",
                "online_materials_permission_review",
                "lecture_materials_permission_review",
                "online_essay_exam_source_permissions",
                "48h essay",
            ],
        ),
        "scripts/build_review_questions.py": require_terms(
            "scripts/build_review_questions.py",
            [
                "request_user_input",
                "exam_type_route",
                "material_type_source_roles",
                "notes_output_choice",
                "Auto-diagnosis review plan",
                "follow_up_question_batches",
                "essay_example_essay_count",
                "mcq_research_report_choice",
                "short_answer_research_report_choice",
                "long_answer_detailed_analysis_choice",
                "worked_solution_teaching_choice",
                "Online Essay Exam",
                "online_essay_online_materials_permission",
                "online_essay_lecture_materials_permission",
                "online_essay_allowed_source_set",
                "online_essay_citation_expectation",
                "online_essay_output_format",
            ],
        ),
        "scripts/exam_mode_tools.py": require_terms(
            "scripts/exam_mode_tools.py",
            [
                "build_question_solver_pack",
                "strict_same_knowledge_point_questions",
                "organize_questions_by_lecture_order",
                "write_organized_questions_docx",
                "solve-question",
                "organize-questions",
                "build_mcq_saq_recurrence_report",
                "past_paper_question_records_from_scan",
            ],
        ),
        "README.md": require_terms(
            "README.md",
            [
                "human review",
                "Exam type",
                "Material type",
                "whether Notes should be generated",
                "Multiple Skill system",
                "focused sibling Skills",
                "scripts/build_review_questions.py",
                "exam-relevant knowledge",
                "Specific Research Report",
                "exam-prep-question-solver",
                "exam-prep-question-organizer",
                "question_solution_report",
                "organized_questions_docx",
                "coverage_policy: lecture_unit_complete",
                "broad lecture reconstruction",
                "concise exam-priority reinforcement",
                "core_lecture_content",
                "exam-prep-slide-triage",
                "slide_triage_audit",
            ],
        ),
        "skill_manifest.json": require_terms(
            "skill_manifest.json",
            [
                "multi_skill_system",
                "focused_skills",
                "removed_focused_skills",
                "exam-prep-index",
                "exam-prep-worked-solutions",
                "exam-prep-question-solver",
                "exam-prep-question-organizer",
                "exam-prep-slide-triage",
                "exam-prep-online-essay-exam",
                "online_essay_exam_policy",
                "online_essay_exam_drafting",
                "notes_material_analysis",
                "question_solving",
                "question_organizing",
            ],
        ),
        "agents/openai.yaml": require_terms(
            "agents/openai.yaml",
            [
                "human_review",
                "public_content",
                "internal_workflow_record",
                "multi_skill_system",
                "focused_skills",
                "Auto-diagnosis review plan",
                "request_user_input",
                "Exam type",
                "Material type",
                "Notes generation choice",
                "exam-prep-question-solver",
                "exam-prep-question-organizer",
                "exam-prep-slide-triage",
                "exam-prep-online-essay-exam",
                "slide_triage",
                "Online Essay Exam",
                "Online Materials and Lecture Materials permissions",
                "question_solution_report",
                "organized_questions_docx",
            ],
        ),
        "scripts/publish_skill.py": require_terms(
            "scripts/publish_skill.py",
            [
                "discover_focused_skills",
                "sync_focused_skill",
                "cleanup_removed_focused_skills",
                "focused_skills",
                "DEFAULT_LOCAL_SKILL_ROOT",
            ],
        ),
    }
    for focused_path in FOCUSED_SKILL_FILES:
        missing_terms[focused_path] = require_terms(
            focused_path,
            [
                "description:",
                "When this Skill is read from the source checkout",
            ],
        )
    missing_terms = {name: terms for name, terms in missing_terms.items() if terms}
    cjk = cjk_locations()
    prohibited_names = prohibited_filename_locations()
    prohibited_wording = prohibited_wording_locations()
    script_self_tests = [
        failure
        for failure in [
            script_self_test("scripts/extract_sources.py"),
            script_self_test("scripts/build_fragment_index.py"),
            script_self_test("scripts/plan_workflow.py"),
            script_self_test("scripts/build_review_questions.py"),
            script_self_test("scripts/exam_mode_tools.py"),
        ]
        if failure
    ]
    failures = {
        "missing_files": missing_files,
        "invalid_schemas": invalid_schemas,
        "missing_terms": missing_terms,
        "manifest_sync_failures": manifest_sync_failures(),
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
