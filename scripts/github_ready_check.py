#!/usr/bin/env python3
"""Run the local GitHub-ready QA gate for this Skill repository."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run_command(name: str, command: list[str], *, expect_failure: bool = False) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    passed = proc.returncode != 0 if expect_failure else proc.returncode == 0
    return {
        "name": name,
        "command": " ".join(command),
        "returncode": proc.returncode,
        "expected_failure": expect_failure,
        "status": "pass" if passed else "fail",
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def public_safety_scan() -> dict[str, Any]:
    patterns = [
        "/" + "Users/",
        "One" + "Drive",
        "Cloud" + "Storage",
        "octavian" + "zhang",
        "Desk" + "top",
        "University of " + "Manchester",
        "School of " + "Biological",
    ]
    regex = re.compile("|".join(re.escape(pattern) for pattern in patterns))
    hits = []
    for path in ROOT.rglob("*"):
        if any(part in {".git", "__pycache__", ".venv", ".pytest_cache", ".mypy_cache", ".skill_backups"} for part in path.parts) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if regex.search(text):
            hits.append(str(path.relative_to(ROOT)))
    return {
        "name": "public_safety_scan",
        "command": "internal public safety scan",
        "status": "pass" if not hits else "fail",
        "hits": hits,
    }


def git_status_check(require_clean: bool) -> dict[str, Any]:
    proc = subprocess.run(["git", "status", "--short"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    dirty = bool(proc.stdout.strip())
    passed = proc.returncode == 0 and (not require_clean or not dirty)
    return {
        "name": "git_status",
        "command": "git status --short",
        "status": "pass" if passed else "fail",
        "dirty": dirty,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run GitHub-ready checks.")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    py = sys.executable
    checks: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="sbs_github_ready_") as tmp:
        tmp_dir = Path(tmp)
        positive_dir = tmp_dir / "positive_docx"
        negative_dir = tmp_dir / "negative_docx"
        author_led_citation_dir = tmp_dir / "author_led_citation_docx"
        public_preamble_dir = tmp_dir / "public_preamble_docx"
        deliverable_dir = tmp_dir / "deliverable_docx"
        deliverable_qa_dir = tmp_dir / "deliverable_docx_internal_qa"
        knowledge_walkthrough_dir = tmp_dir / "knowledge_walkthrough_docx"
        knowledge_walkthrough_qa_dir = tmp_dir / "knowledge_walkthrough_internal_qa"
        exam_prep_notes_dir = tmp_dir / "exam_prep_notes_docx"
        exam_prep_notes_qa_dir = tmp_dir / "exam_prep_notes_internal_qa"
        bad_public_dir = tmp_dir / "bad_public_output"
        bad_workbook_dir = tmp_dir / "bad_public_workbook"
        citation_fallback_dir = tmp_dir / "citation_fallback"
        past_paper_extract_dir = tmp_dir / "past_paper_question_extract"
        fragment_index_dir = tmp_dir / "fragment_index"
        planner_dir = tmp_dir / "planner"
        workflow_plan_path = planner_dir / "workflow_plan.json"
        default_no_paper_plan_path = planner_dir / "default_no_paper_plan.json"
        default_with_paper_plan_path = planner_dir / "default_with_paper_plan.json"
        style_plan_path = planner_dir / "style_plan.json"
        bad_exam_prep_mapping_path = planner_dir / "bad_exam_prep_public_mapping.json"
        input_readiness_path = planner_dir / "input_readiness.json"
        visual_readiness_path = planner_dir / "visual_input_readiness.json"
        workflow_plan_preview_path = planner_dir / "workflow_plan.md"
        run_status_path = planner_dir / "run_status.json"
        lineage_report_path = planner_dir / "lineage_report.json"
        bad_public_dir.mkdir(parents=True, exist_ok=True)
        (bad_public_dir / "example_essay_manifest.json").write_text("{}", encoding="utf-8")
        bad_workbook_dir.mkdir(parents=True, exist_ok=True)
        (bad_workbook_dir / "legacy_output.xlsx").write_bytes(b"placeholder")
        bad_exam_prep_mapping = json.loads((ROOT / "tests/fixtures/exam_prep_notes/valid_exam_prep_notes_plan.json").read_text(encoding="utf-8"))
        bad_exam_prep_mapping["public_output_points"][0]["source_card_ids"] = ["missing_card"]
        bad_exam_prep_mapping["public_output_points"][0]["covered_atomic_units"].append("aku_unmapped")
        bad_exam_prep_mapping["public_output_points"][0]["blocks"][0]["covered_atomic_units"].append("aku_not_in_point")
        bad_exam_prep_mapping["point_coverage_bindings"][0]["covered_atomic_units"] = ["aku_definition"]
        bad_exam_prep_mapping["point_coverage_bindings"][0]["missing_protected_items"] = ["aku_mechanism"]
        bad_exam_prep_mapping_path.parent.mkdir(parents=True, exist_ok=True)
        bad_exam_prep_mapping_path.write_text(json.dumps(bad_exam_prep_mapping, indent=2), encoding="utf-8")
        checks.extend(
            [
                run_command("compile_scripts", [py, "-m", "compileall", "-q", "scripts"]),
                run_command("ontology_contract", [py, "scripts/ontology_linter.py"]),
                run_command("action_writer_coverage", [py, "scripts/validate_action_writer_coverage.py"]),
                run_command("interaction_contract", [py, "scripts/validate_interaction_contract.py"]),
                run_command("workflow_planning_contract", [py, "scripts/validate_workflow_planning_contract.py"]),
                run_command("student_output_contract", [py, "scripts/validate_student_output_contract.py"]),
                run_command("skill_maintenance_doctor_offline", [py, "scripts/skill_maintenance.py", "doctor", "--offline", "--skip-health", "--json"]),
                run_command(
                    "workflow_plan_fixture",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_mcq_exam_prep.json",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan.json",
                        "--output",
                        str(workflow_plan_path),
                    ],
                ),
                run_command(
                    "workflow_plan_default_without_past_papers_keeps_prediction_modules_off",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_exam_prep_no_past_papers.json",
                        "--output",
                        str(default_no_paper_plan_path),
                        "--require-module",
                        "source_baseline_notes_plan",
                        "--require-module",
                        "baseline_coverage_floor_qa",
                        "--require-module",
                        "exam_overlay_pass",
                        "--require-module",
                        "overlay_did_not_damage_coverage_qa",
                        "--require-module",
                        "knowledge_only_rendering_gate",
                        "--require-module",
                        "exam_prep_notes_linter",
                        "--forbid-module",
                        "exam_regime",
                        "--forbid-module",
                        "past_paper_questions",
                        "--forbid-module",
                        "question_archetypes",
                        "--forbid-module",
                        "examiner_operations",
                    ],
                ),
                run_command(
                    "workflow_plan_default_with_past_papers_enables_exam_evidence_modules",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_exam_prep_with_past_papers.json",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan.json",
                        "--output",
                        str(default_with_paper_plan_path),
                        "--require-module",
                        "exam_regime",
                        "--require-module",
                        "past_paper_questions",
                        "--require-module",
                        "question_archetypes",
                        "--require-module",
                        "examiner_operations",
                        "--require-module",
                        "knowledge_only_rendering_gate",
                    ],
                ),
                run_command(
                    "workflow_plan_style_examples_enable_example_learning",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_exam_prep_no_past_papers.json",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan_style_example.json",
                        "--output",
                        str(style_plan_path),
                        "--require-module",
                        "example_learning",
                        "--require-module",
                        "transferable_rule_synthesis",
                        "--require-module",
                        "rule_promotion_gate",
                        "--require-module",
                        "example_transfer_linter",
                    ],
                ),
                run_command(
                    "example_transfer_linter_accepts_valid_review_ledger",
                    [
                        py,
                        "scripts/example_transfer_linter.py",
                        "tests/fixtures/example_learning/valid_example_review_ledger.json",
                    ],
                ),
                run_command(
                    "example_transfer_linter_rejects_direct_example_copying",
                    [
                        py,
                        "scripts/example_transfer_linter.py",
                        "tests/fixtures/example_learning/invalid_example_review_ledger.json",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "workflow_plan_knowledge_walkthrough_fixture",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_knowledge_walkthrough.json",
                        "--output",
                        str(planner_dir / "knowledge_walkthrough_plan_route.json"),
                        "--require-module",
                        "route_docx_style_profile",
                        "--require-module",
                        "knowledge_only_rendering_gate",
                        "--require-module",
                        "knowledge_walkthrough_docx_style_linter",
                    ],
                ),
                run_command(
                    "workflow_plan_knowledge_walkthrough_format_reference_enables_example_learning",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_knowledge_walkthrough.json",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan_format_reference.json",
                        "--output",
                        str(planner_dir / "knowledge_walkthrough_format_reference_plan.json"),
                        "--require-module",
                        "example_learning",
                        "--require-module",
                        "transferable_rule_synthesis",
                        "--require-module",
                        "rule_promotion_gate",
                        "--require-module",
                        "example_transfer_linter",
                    ],
                ),
                run_command(
                    "input_readiness_fixture",
                    [
                        py,
                        "scripts/input_readiness_check.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_mcq_exam_prep.json",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan.json",
                        "--output",
                        str(input_readiness_path),
                    ],
                ),
                run_command(
                    "input_readiness_visual_warning_fixture",
                    [
                        py,
                        "scripts/input_readiness_check.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_exam_prep_no_past_papers.json",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan_visual_warning.json",
                        "--output",
                        str(visual_readiness_path),
                        "--require-warning-id",
                        "warn_visual_inspection_needed",
                    ],
                ),
                run_command(
                    "exam_prep_notes_plan_contract_fixture",
                    [
                        py,
                        "scripts/validate_exam_prep_notes_plan.py",
                        "tests/fixtures/exam_prep_notes/valid_exam_prep_notes_plan.json",
                    ],
                ),
                run_command(
                    "exam_prep_notes_plan_rejects_invalid_visible_card",
                    [
                        py,
                        "scripts/validate_exam_prep_notes_plan.py",
                        "tests/fixtures/exam_prep_notes/invalid_knowledge_card_plan.json",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "exam_prep_notes_plan_rejects_public_mapping_gaps",
                    [
                        py,
                        "scripts/validate_exam_prep_notes_plan.py",
                        str(bad_exam_prep_mapping_path),
                    ],
                    expect_failure=True,
                ),
                run_command("source_information_profiler_self_test", [py, "scripts/source_information_profiler.py", "--self-test"]),
                run_command("source_scale_budget_linter_self_test", [py, "scripts/source_scale_budget_linter.py", "--self-test"]),
                run_command(
                    "exam_prep_notes_linter_generic_protected_item_fixture",
                    [
                        py,
                        "scripts/exam_prep_notes_linter.py",
                        "tests/fixtures/exam_prep_notes/clinical_target_discovery/final_notes.md",
                        "--protected-items",
                        "tests/fixtures/exam_prep_notes/clinical_target_discovery/protected_items.json",
                    ],
                ),
                run_command(
                    "exam_prep_notes_linter_rejects_legacy_compressed_protected_items",
                    [
                        py,
                        "scripts/exam_prep_notes_linter.py",
                        "tests/fixtures/exam_prep_notes/clinical_target_discovery/bad_final_notes.md",
                        "--protected-items",
                        "tests/fixtures/exam_prep_notes/clinical_target_discovery/protected_items.json",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "exam_prep_notes_linter_knowledge_only_fixture",
                    [
                        py,
                        "scripts/exam_prep_notes_linter.py",
                        "tests/fixtures/exam_prep_notes/knowledge_only_rendering/final_notes.md",
                    ],
                ),
                run_command(
                    "exam_prep_notes_linter_rejects_advisory_leakage",
                    [
                        py,
                        "scripts/exam_prep_notes_linter.py",
                        "tests/fixtures/exam_prep_notes/knowledge_only_rendering/bad_final_notes.md",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "exam_prep_notes_linter_omics_atomic_density",
                    [
                        py,
                        "scripts/exam_prep_notes_linter.py",
                        "tests/fixtures/exam_prep_notes/omics_source_first_density/final_notes.md",
                        "--ledger",
                        "tests/fixtures/exam_prep_notes/omics_source_first_density/atomic_ledger.json",
                        "--min-modules",
                        "19",
                        "--require-module-term",
                        "PCR primer logic",
                        "--require-module-term",
                        "BLAST homology orthology paralogy",
                        "--require-module-term",
                        "Genetic manipulation CRISPR homologous recombination",
                    ],
                ),
                run_command(
                    "exam_prep_notes_linter_rejects_omics_broad_cards",
                    [
                        py,
                        "scripts/exam_prep_notes_linter.py",
                        "tests/fixtures/exam_prep_notes/omics_source_first_density/bad_final_notes.md",
                        "--ledger",
                        "tests/fixtures/exam_prep_notes/omics_source_first_density/atomic_ledger.json",
                        "--min-modules",
                        "19",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "exam_prep_notes_docx_generate",
                    [
                        py,
                        "scripts/generate_exam_prep_notes_docx.py",
                        "--plan",
                        "tests/fixtures/exam_prep_notes/valid_exam_prep_notes_plan.json",
                        "--output-dir",
                        str(exam_prep_notes_dir),
                        "--qa-dir",
                        str(exam_prep_notes_qa_dir),
                        "--clean",
                        "--strict",
                        "--deliverable-only",
                    ],
                ),
                run_command("exam_prep_docx_style_lint", [py, "scripts/exam_prep_docx_style_linter.py", str(exam_prep_notes_dir)]),
                run_command("exam_prep_docx_style_linter_rejects_bad_style", [py, "scripts/exam_prep_docx_style_linter.py", "--self-test-bad"], expect_failure=True),
                run_command("exam_prep_notes_public_output", [py, "scripts/final_deliverable_linter.py", str(exam_prep_notes_dir), "--allowed", ".docx"]),
                run_command(
                    "workflow_plan_render_fixture",
                    [
                        py,
                        "scripts/render_workflow_plan.py",
                        "--plan",
                        str(workflow_plan_path),
                        "--output",
                        str(workflow_plan_preview_path),
                    ],
                ),
                run_command(
                    "run_status_fixture",
                    [
                        py,
                        "scripts/run_status_report.py",
                        "--plan",
                        str(workflow_plan_path),
                        "--output",
                        str(run_status_path),
                    ],
                ),
                run_command(
                    "workflow_plan_missing_input_blocks",
                    [
                        py,
                        "scripts/plan_workflow.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_missing_lecture.json",
                        "--fail-on-blockers",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "input_readiness_missing_input_blocks",
                    [
                        py,
                        "scripts/input_readiness_check.py",
                        "--config",
                        "tests/fixtures/planner/skill_config_missing_lecture.json",
                        "--fail-on-blockers",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "fragment_index_fixture",
                    [
                        py,
                        "scripts/build_fragment_index.py",
                        "--source-scan",
                        "tests/fixtures/control_plane/source_scan.json",
                        "--output-dir",
                        str(fragment_index_dir),
                    ],
                ),
                run_command(
                    "ontology_runtime_fixture",
                    [
                        py,
                        "scripts/ontology_validator.py",
                        "--objects-dir",
                        "tests/fixtures/control_plane/runtime_good/ontology_objects",
                        "--links",
                        "tests/fixtures/control_plane/runtime_good/ontology_links/links.jsonl",
                    ],
                ),
                run_command(
                    "ontology_runtime_rejects_cross_target_support",
                    [
                        py,
                        "scripts/ontology_validator.py",
                        "--objects-dir",
                        "tests/fixtures/control_plane/runtime_bad/ontology_objects",
                        "--links",
                        "tests/fixtures/control_plane/runtime_bad/ontology_links/links.jsonl",
                    ],
                    expect_failure=True,
                ),
                run_command(
                    "run_manifest_lineage_fixture",
                    [
                        py,
                        "scripts/run_manifest_linter.py",
                        "--manifest",
                        "tests/fixtures/control_plane/run_manifest.json",
                        "--lineage-events",
                        "tests/fixtures/control_plane/lineage_events.jsonl",
                    ],
                ),
                run_command(
                    "lineage_report_fixture",
                    [
                        py,
                        "scripts/lineage_report.py",
                        "--manifest",
                        "tests/fixtures/control_plane/run_manifest.json",
                        "--lineage-events",
                        "tests/fixtures/control_plane/lineage_events.jsonl",
                        "--output",
                        str(lineage_report_path),
                    ],
                ),
                run_command("workbook_language_fixture", [py, "scripts/essay_style_linter.py", "--fixture", "benchmarks/kp_essay_style_linter_fixtures.json"]),
                run_command("example_essay_language_fixture", [py, "scripts/example_essay_language_linter.py", "--fixture", "benchmarks/example_essay_language_linter_fixtures.json"]),
                run_command("essay_theme_prediction_language", [py, "scripts/essay_theme_prediction_linter.py"]),
                run_command(
                    "citation_fallback_fixture",
                    [
                        py,
                        "scripts/lecture_citation_resolver.py",
                        "--input",
                        "tests/fixtures/citation_fallback/no_citation_lecture.txt",
                        "--output-dir",
                        str(citation_fallback_dir),
                        "--classic-search-if-no-citations",
                    ],
                ),
                run_command("citation_fallback_lint", [py, "scripts/citation_fallback_linter.py", "--dir", str(citation_fallback_dir), "--require-classic-plan"]),
                run_command("cross_subject_metadata", [py, "scripts/cross_subject_regression_check.py", "--metadata-only", "--suite", "benchmarks/cross_subject_regression_suite.json"]),
                run_command("method_long_answer_metadata", [py, "scripts/cross_subject_regression_check.py", "--metadata-only", "--suite", "benchmarks/method_long_answer_suite.json"]),
                run_command("past_paper_prediction_metadata", [py, "scripts/cross_subject_regression_check.py", "--metadata-only", "--suite", "benchmarks/past_paper_prediction_suite.json"]),
                run_command(
                    "past_paper_question_extract_fixture",
                    [
                        py,
                        "scripts/extract_past_paper_questions.py",
                        "tests/fixtures/past_paper_question_extraction/fake_mixed_paper_2025.txt",
                        "--target-group-key",
                        "Benchmark_Generic",
                        "--current-regime-key",
                        "current_2025",
                        "--output-dir",
                        str(past_paper_extract_dir),
                    ],
                ),
                run_command(
                    "past_paper_prediction_lint",
                    [
                        py,
                        "scripts/past_paper_prediction_linter.py",
                        "--input",
                        str(past_paper_extract_dir / "past_paper_questions.json"),
                        "--suite",
                        "benchmarks/past_paper_prediction_suite.json",
                    ],
                ),
                run_command("identity_trigger_scan", [py, "scripts/no_identity_trigger_linter.py"]),
                run_command(
                    "knowledge_walkthrough_docx_generate",
                    [
                        py,
                        "scripts/generate_knowledge_walkthrough_docx.py",
                        "--plan",
                        "tests/fixtures/knowledge_walkthrough/knowledge_walkthrough_plan.json",
                        "--output-dir",
                        str(knowledge_walkthrough_dir),
                        "--qa-dir",
                        str(knowledge_walkthrough_qa_dir),
                        "--clean",
                        "--strict",
                        "--deliverable-only",
                    ],
                ),
                run_command("knowledge_walkthrough_lint", [py, "scripts/knowledge_walkthrough_linter.py", str(knowledge_walkthrough_dir)]),
                run_command("knowledge_walkthrough_linter_rejects_bad_style", [py, "scripts/knowledge_walkthrough_linter.py", "--self-test-bad"], expect_failure=True),
                run_command("knowledge_walkthrough_public_output", [py, "scripts/final_deliverable_linter.py", str(knowledge_walkthrough_dir), "--allowed", ".docx"]),
                run_command(
                    "positive_docx_generate_strict",
                    [
                        py,
                        "scripts/generate_example_essay_docx.py",
                        "--plan",
                        "tests/fixtures/example_essay_docx/positive_docx_plan.json",
                        "--output-dir",
                        str(positive_dir),
                        "--clean",
                        "--strict",
                    ],
                ),
            ]
        )
        checks.append(run_command("positive_docx_format_and_language", [py, "scripts/docx_format_linter.py", str(positive_dir), "--check-language"]))
        checks.append(run_command("negative_format_fixture_build", [py, "tests/fixtures/example_essay_docx/build_negative_format_fixture.py"]))
        checks.append(
            run_command(
                "docx_format_linter_rejects_bad_spacing_and_layout",
                [py, "scripts/docx_format_linter.py", "tests/fixtures/example_essay_docx/negative_format_fixture.docx"],
                expect_failure=True,
            )
        )
        checks.append(
            run_command(
                "deliverable_only_docx_generate",
                [
                    py,
                    "scripts/generate_example_essay_docx.py",
                    "--plan",
                    "tests/fixtures/example_essay_docx/positive_docx_plan.json",
                    "--output-dir",
                    str(deliverable_dir),
                    "--qa-dir",
                    str(deliverable_qa_dir),
                    "--clean",
                    "--strict",
                    "--deliverable-only",
                ],
            )
        )
        checks.append(run_command("public_output_has_no_helper_artifacts", [py, "scripts/final_deliverable_linter.py", str(deliverable_dir)]))
        checks.append(
            run_command(
                "public_output_rejects_helper_artifacts",
                [py, "scripts/final_deliverable_linter.py", str(bad_public_dir)],
                expect_failure=True,
            )
        )
        checks.append(
            run_command(
                "public_output_rejects_legacy_workbook",
                [py, "scripts/final_deliverable_linter.py", str(bad_workbook_dir)],
                expect_failure=True,
            )
        )
        checks.append(
            run_command(
                "negative_docx_strict_rejects_bad_source_plan",
                [
                    py,
                    "scripts/generate_example_essay_docx.py",
                    "--plan",
                    "tests/fixtures/example_essay_docx/negative_source_plan.json",
                    "--output-dir",
                    str(negative_dir),
                    "--clean",
                    "--strict",
                ],
                expect_failure=True,
            )
        )
        checks.append(
            run_command(
                "negative_docx_strict_rejects_author_led_citation_prose",
                [
                    py,
                    "scripts/generate_example_essay_docx.py",
                    "--plan",
                    "tests/fixtures/example_essay_docx/author_led_citation_plan.json",
                    "--output-dir",
                    str(author_led_citation_dir),
                    "--clean",
                    "--strict",
                ],
                expect_failure=True,
            )
        )
        checks.append(
            run_command(
                "negative_docx_strict_rejects_public_preamble_leaks",
                [
                    py,
                    "scripts/generate_example_essay_docx.py",
                    "--plan",
                    "tests/fixtures/example_essay_docx/public_preamble_plan.json",
                    "--output-dir",
                    str(public_preamble_dir),
                    "--clean",
                    "--strict",
                ],
                expect_failure=True,
            )
        )

    checks.append(public_safety_scan())
    checks.append(git_status_check(require_clean=args.require_clean))

    passed = all(check.get("status") == "pass" for check in checks)
    result = {
        "status": "pass" if passed else "fail",
        "checks": checks,
    }
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
