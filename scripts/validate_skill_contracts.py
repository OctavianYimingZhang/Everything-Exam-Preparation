#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

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
CANONICAL_CONTRACT_FILES = [
    "contracts/plugin-capability-manifest-v2.schema.json",
    "contracts/academic-task-context-v1.schema.json",
    "contracts/task-run-state-v1.schema.json",
    "contracts/source-record-v1.schema.json",
    "contracts/local-bridge-protocol-v1.schema.json",
]
CONTEXT_FIXTURES = [
    "tests/fixtures/academic_task_context_answer_evaluation.json",
    "tests/fixtures/academic_task_context_mixed_gate.json",
    "tests/fixtures/academic_task_context_online_permissions.json",
]


def json_readable(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def yaml_readable(path: Path) -> bool:
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


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
        manifest = read_json(manifest_path)
    except Exception as exc:
        return [f"skill_manifest.json unreadable: {exc}"]
    failures: list[str] = []
    plan_text = read_text(ROOT / "scripts/plan_workflow.py")
    questions_text = read_text(ROOT / "scripts/build_review_questions.py")
    plugin_router = manifest.get("plugin_router_skill") or {}
    router_path = str(plugin_router.get("path") or "")
    if not router_path:
        failures.append("plugin_router_skill missing from skill_manifest.json")
    elif not (ROOT / router_path).exists():
        failures.append(f"plugin router skill path missing: {router_path}")
    plugin_path = ROOT / ".codex-plugin" / "plugin.json"
    if plugin_path.exists():
        try:
            plugin = read_json(plugin_path)
            if plugin.get("skills") != "./skills/":
                failures.append(".codex-plugin/plugin.json skills must point to ./skills/")
            if plugin.get("version") != manifest.get("plugin_version"):
                failures.append(".codex-plugin/plugin.json version is not synchronized with skill_manifest.json")
        except Exception as exc:
            failures.append(f".codex-plugin/plugin.json unreadable: {exc}")
    else:
        failures.append(".codex-plugin/plugin.json missing")
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
    capability_path = ROOT / str(manifest.get("capability_manifest") or "")
    if not manifest.get("capability_manifest"):
        failures.append("capability_manifest missing from skill_manifest.json")
    elif not capability_path.exists():
        failures.append(f"capability manifest missing: {capability_path.relative_to(ROOT)}")
    else:
        try:
            capability = read_json(capability_path)
        except Exception as exc:
            failures.append(f"capability manifest unreadable: {exc}")
            capability = {}
        if capability.get("contract") != "PluginCapabilityManifest" or capability.get("version") != 2:
            failures.append("plugin capability manifest must use PluginCapabilityManifest v2")
        if capability.get("plugin_id") != manifest.get("skill_id"):
            failures.append("plugin capability manifest plugin_id is not synchronized with skill_manifest.json")
        if capability.get("plugin_version") != manifest.get("plugin_version"):
            failures.append("plugin capability manifest plugin_version is not synchronized with skill_manifest.json")
        if capability.get("default_output_language") != "en":
            failures.append("plugin capability manifest default_output_language must be en")
        if 1 not in (capability.get("supported_context_versions") or []):
            failures.append("plugin capability manifest must support AcademicTaskContext v1")
        route_contracts = capability.get("routes") or []
        contract_route_ids = [str(item.get("route_id") or "") for item in route_contracts if isinstance(item, dict)]
        if contract_route_ids != list(manifest.get("routes") or []):
            failures.append("plugin capability manifest routes are not synchronized with skill_manifest.json")
        focused_names = {str(skill.get("name") or "") for skill in manifest.get("focused_skills", []) or []}
        for item in route_contracts:
            if not isinstance(item, dict):
                failures.append("plugin capability manifest contains a non-object route")
                continue
            route_id = str(item.get("route_id") or "")
            if item.get("owning_skill") not in focused_names:
                failures.append(f"route {route_id} has unknown owning_skill {item.get('owning_skill')}")
            if not item.get("required_inputs"):
                failures.append(f"route {route_id} has no required_inputs declaration")
            if not item.get("gates"):
                failures.append(f"route {route_id} has no gates declaration")
            required_gate_ids = {
                str(gate.get("gate_id") or "")
                for gate in item.get("gates") or []
                if isinstance(gate, dict) and gate.get("required") is True
            }
            missing_lifecycle_gates = {"local_execution_permission", "planning_approval"} - required_gate_ids
            if missing_lifecycle_gates:
                failures.append(
                    f"route {route_id} is missing execution lifecycle gates: {', '.join(sorted(missing_lifecycle_gates))}"
                )
            if not item.get("outputs"):
                failures.append(f"route {route_id} has no outputs declaration")
            adapter = item.get("adapter_entrypoint") or {}
            if adapter.get("type") != "python" or adapter.get("value") != "scripts/soleil_adapter.py":
                failures.append(f"route {route_id} has an invalid adapter_entrypoint")
            if 1 not in (item.get("supported_context_versions") or []):
                failures.append(f"route {route_id} does not support AcademicTaskContext v1")
            triggers = item.get("triggers") or {}
            if triggers.get("direct_invocation") is not True:
                failures.append(f"route {route_id} must declare direct invocation support")
        required_new_routes = {"assessment_blueprint", "answer_evaluation", "timed_practice"}
        missing_new_routes = sorted(required_new_routes - set(contract_route_ids))
        if missing_new_routes:
            failures.append(f"plugin capability manifest missing new routes: {', '.join(missing_new_routes)}")
    if manifest.get("default_output_language") != "en":
        failures.append("skill_manifest.json default_output_language must be en")
    if 1 not in (manifest.get("supported_context_versions") or []):
        failures.append("skill_manifest.json must support AcademicTaskContext v1")
    if manifest.get("route_adapter") != "scripts/soleil_adapter.py":
        failures.append("skill_manifest.json route_adapter must be scripts/soleil_adapter.py")
    mastery = manifest.get("mastery_history") or {}
    if mastery.get("default_enabled") is not True or mastery.get("scope") != "per_course":
        failures.append("mastery_history must be default-enabled and per-course")
    if set(mastery.get("operations") or []) != {"enable", "disable", "export", "delete"}:
        failures.append("mastery_history must expose enable, disable, export, and delete")
    if mastery.get("entrypoint") != "scripts/mastery_history.py":
        failures.append("mastery_history entrypoint must be scripts/mastery_history.py")
    for contract_path in CANONICAL_CONTRACT_FILES:
        if not (ROOT / contract_path).exists() or not json_readable(ROOT / contract_path):
            failures.append(f"canonical contract missing or unreadable: {contract_path}")
    return failures


def context_fixture_failures() -> list[str]:
    failures: list[str] = []
    for name in CONTEXT_FIXTURES:
        path = ROOT / name
        if not path.exists():
            failures.append(f"{name} missing")
            continue
        try:
            payload = read_json(path)
            context = payload.get("academic_task_context") or {}
            if context.get("contract") != "AcademicTaskContext" or context.get("version") != 1:
                failures.append(f"{name} does not contain AcademicTaskContext v1")
            route = str((context.get("route_selection") or {}).get("route_id") or "")
            if route not in {"assessment_blueprint", "answer_evaluation", "timed_practice", "mixed_exam_preparation", "online_essay_exam_drafting"}:
                failures.append(f"{name} has an unexpected route fixture: {route}")
            if not str(context.get("original_prompt") or "").strip():
                failures.append(f"{name} has an empty original_prompt")
        except Exception as exc:
            failures.append(f"{name} unreadable: {exc}")
    return failures


def agent_registry_failures() -> list[str]:
    failures: list[str] = []
    try:
        manifest = read_json(ROOT / "skill_manifest.json")
    except Exception as exc:
        return [f"skill_manifest.json unreadable for agent registry checks: {exc}"]
    focused_names = [str(skill.get("name") or "") for skill in manifest.get("focused_skills", []) or []]
    routes = {str(route) for route in manifest.get("routes", []) or []}
    human_review_targets = {str(target) for target in manifest.get("human_review_targets", []) or []}
    yaml_files = [
        "agents/openai.yaml",
        "agents/prompt_cards.yaml",
        "agents/presets.yaml",
        "agents/setup_wizard.yaml",
        "skills/exam-prep-slide-triage/agents/openai.yaml",
    ]
    for name in yaml_files:
        path = ROOT / name
        if not path.exists():
            failures.append(f"{name} missing")
        elif not yaml_readable(path):
            failures.append(f"{name} unreadable as YAML")
    if failures:
        return failures

    openai = read_yaml(ROOT / "agents/openai.yaml")
    multi = openai.get("multi_skill_system") or {}
    if multi.get("plugin_router_skill") != (manifest.get("plugin_router_skill") or {}).get("path"):
        failures.append("agents/openai.yaml plugin_router_skill is not synchronized with skill_manifest.json")
    if list(multi.get("focused_skills") or []) != focused_names:
        failures.append("agents/openai.yaml focused_skills is not synchronized with skill_manifest.json")
    if list(multi.get("removed_focused_skills") or []) != list(manifest.get("removed_focused_skills") or []):
        failures.append("agents/openai.yaml removed_focused_skills is not synchronized with skill_manifest.json")
    examples = ((openai.get("source_hints") or {}).get("examples")) or []
    if len(examples) < 7 or not all(isinstance(item, str) for item in examples):
        failures.append("agents/openai.yaml source_hints.examples must be a flat list of source-hint strings")

    prompt_cards = read_yaml(ROOT / "agents/prompt_cards.yaml").get("prompt_cards") or []
    prompt_routes = {str(item.get("route") or "") for item in prompt_cards if isinstance(item, dict)}
    missing_prompt_routes = sorted(routes - prompt_routes)
    if missing_prompt_routes:
        failures.append(f"agents/prompt_cards.yaml missing routes: {', '.join(missing_prompt_routes)}")

    presets = read_yaml(ROOT / "agents/presets.yaml").get("presets") or {}
    preset_routes = set(presets.keys()) if isinstance(presets, dict) else set()
    missing_preset_routes = sorted(routes - preset_routes)
    if missing_preset_routes:
        failures.append(f"agents/presets.yaml missing routes: {', '.join(missing_preset_routes)}")

    setup = read_yaml(ROOT / "agents/setup_wizard.yaml").get("setup_wizard") or {}
    setup_targets = set(((setup.get("human_review") or {}).get("targets")) or [])
    missing_targets = sorted(human_review_targets - setup_targets)
    if missing_targets:
        failures.append(f"agents/setup_wizard.yaml missing human-review targets: {', '.join(missing_targets)}")
    return failures


def script_self_test(script: str) -> str | None:
    proc = subprocess.run([sys.executable, str(ROOT / script), "--self-test"], cwd=ROOT, text=True, capture_output=True)
    if proc.returncode == 0:
        return None
    return f"{script}: {proc.stderr.strip() or proc.stdout.strip() or proc.returncode}"


def python_test(script: str) -> str | None:
    proc = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, text=True, capture_output=True)
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
        "scripts/assessment_tools.py",
        "scripts/mastery_history.py",
        "scripts/soleil_adapter.py",
        "tests/test_soleil_adapter.py",
        "plugin_capability_manifest.json",
        *CANONICAL_CONTRACT_FILES,
        *CONTEXT_FIXTURES,
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
                "source rules and explicit assessment permission for a complete draft",
                "drafting branch rather than a Specific Research Report",
                "confirmed_mixed_routes",
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
                "Missing permission answers remain plan-changing unresolved items",
                "complete draft additionally requires an explicitly allowed assessment-draft permission",
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
                "Direct Invocation Gate",
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
                "TIMECODE_RE",
                "timed_text_units",
                "time_offset_seconds",
                "time_range",
                "provenance_record",
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
                "time_offset_seconds",
                "time_range",
                "provenance",
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
                "online_essay_exam_complete_draft_permission",
                "48h essay",
                "confirmed_mixed_routes",
                "how do i answer",
                "sort practice",
                "academic_task_context",
                "original_prompt",
                "route_selection",
                "source_fragments",
                "relevant_memory",
                "assessment_blueprint",
                "answer_evaluation",
                "timed_practice",
                "mastery_history",
                "time_range",
                "default_output_language",
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
                "confirmed_mixed_routes",
                "mixed_component_routes_question",
                "assessment_blueprint_scope",
                "answer_evaluation_criteria",
                "timed_practice_duration",
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
                "fragment_provenance",
                "time_offset_seconds",
                "time_range",
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
                "plugin_router_skill",
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
                "plugin_capability_manifest.json",
                "supported_context_versions",
                "route_adapter",
                "mastery_history",
                "assessment_blueprint",
                "answer_evaluation",
                "timed_practice",
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
                "Online Materials and Lecture Materials rules plus explicit complete-draft permission",
                "question_solution_report",
                "organized_questions_docx",
                "plugin_router_skill",
            ],
        ),
        "scripts/publish_skill.py": require_terms(
            "scripts/publish_skill.py",
            [
                "discover_focused_skills",
                "sync_focused_skill",
                "copy_child_local_resources",
                "cleanup_removed_focused_skills",
                "focused_skills",
                "DEFAULT_LOCAL_SKILL_ROOT",
                "is_package_root",
                "\"outputs\"",
            ],
        ),
        "plugin_capability_manifest.json": require_terms(
            "plugin_capability_manifest.json",
            [
                "PluginCapabilityManifest",
                "default_output_language",
                "owning_skill",
                "required_inputs",
                "gates",
                "outputs",
                "adapter_entrypoint",
                "supported_context_versions",
                "assessment_blueprint",
                "answer_evaluation",
                "timed_practice",
                "local_execution_permission",
                "planning_approval",
            ],
        ),
        "scripts/assessment_tools.py": require_terms(
            "scripts/assessment_tools.py",
            ["build_assessment_blueprint", "evaluate_answer", "build_timed_practice", "page_number", "slide_number", "time_range"],
        ),
        "scripts/mastery_history.py": require_terms(
            "scripts/mastery_history.py",
            ["default_enabled", "per-course", "enable", "disable", "export", "delete"],
        ),
        "scripts/soleil_adapter.py": require_terms(
            "scripts/soleil_adapter.py",
            [
                "AcademicTaskContext",
                "TaskRunState",
                "original_prompt",
                "route_selection",
                "source_fragments",
                "relevant_memory",
                "run_id",
                "execution_result",
                "local_execution",
                "permissions_confirmed",
                "plan_approved",
                "running",
                "qa_passed",
                "failed",
            ],
        ),
        "tests/test_soleil_adapter.py": require_terms(
            "tests/test_soleil_adapter.py",
            [
                "test_every_declared_route_preserves_run_id_and_full_success_lifecycle",
                "test_failed_execution_preserves_full_ordered_lifecycle",
                "test_online_essay_denial_blocks_running_and_approved_permission_executes",
            ],
        ),
    }
    for focused_path in FOCUSED_SKILL_FILES:
        missing_terms[focused_path] = require_terms(
            focused_path,
            [
                "description:",
                "When this Skill is read from the source checkout",
                "Direct Invocation Gate",
                "English",
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
            script_self_test("scripts/publish_skill.py"),
            script_self_test("scripts/essay_exam_tools.py"),
            script_self_test("scripts/extra_reading_tools.py"),
            script_self_test("scripts/generate_exam_prep_notes_docx.py"),
            script_self_test("scripts/input_readiness_check.py"),
            script_self_test("scripts/assessment_tools.py"),
            script_self_test("scripts/mastery_history.py"),
            script_self_test("scripts/soleil_adapter.py"),
        ]
        if failure
    ]
    focused_tests = [failure for failure in [python_test("tests/test_soleil_adapter.py")] if failure]
    failures = {
        "missing_files": missing_files,
        "invalid_schemas": invalid_schemas,
        "missing_terms": missing_terms,
        "manifest_sync_failures": manifest_sync_failures(),
        "agent_registry_failures": agent_registry_failures(),
        "context_fixture_failures": context_fixture_failures(),
        "script_self_tests": script_self_tests,
        "focused_tests": focused_tests,
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
