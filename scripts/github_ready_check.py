from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
FORBIDDEN_TEXT = [
    "ontology",
    "Ontology",
    "Palantir",
    "Snowflake",
    "snowflake",
    "Databricks",
    "databricks",
    "lakehouse",
    "Delta Lake",
    "medallion",
    "bronze",
    "silver",
    "gold",
    "serving layer",
    "Excel-first",
    "SBS",
    "Lecture_Knowledge_Walkthrough",
    "Lecture Knowledge Walkthrough",
    "knowledge_walkthrough",
    "knowledge_walkthrough_docx",
    "public_lecture_notes",
    "public lecture notes",
    "PublicLectureNotesPlan",
    "Public Lecture Notes",
]
FORBIDDEN_PATH_PARTS = [
    "benchmarks",
    "tests/fixtures",
    "custom_gpt_knowledge",
    "ontology",
]
FORBIDDEN_FILENAME_FRAGMENTS = [
    "fake_",
    "negative_",
    "positive_",
    "_fixture",
    "example_review_ledger",
    "language_delta",
    "unit_example_contribution",
]
STALE_SCRIPT_NAMES = [
    "archetype_models.py",
    "citation_fallback_linter.py",
    "citation_rendering_rules.py",
    "essay_theme_prediction_linter.py",
    "exam_prep_notes_linter.py",
    "example_essay_language_linter.py",
    "example_essay_source_audit.py",
    "extra_reading_chapter_matcher.py",
    "extract_past_paper_questions.py",
    "generate_example_essay_docx.py",
    "generate_public_lecture_notes_docx.py",
    "knowledge_only_rendering_rules.py",
    "knowledge_surface_linter.py",
    "lecture_citation_resolver.py",
    "module_teaching_depth_linter.py",
    "no_identity_trigger_linter.py",
    "notes_exam_ready_language_linter.py",
    "notes_readability_layout_linter.py",
    "past_paper_prediction_linter.py",
    "public_lecture_notes_renderer.py",
    "runtime_audit.py",
    "scientific_precision_linter.py",
    "skill_maintenance.py",
    "target_grouper.py",
    "validate_exam_prep_notes_plan.py",
    "validate_interaction_contract.py",
    "validate_student_output_contract.py",
    "validate_workflow_planning_contract.py",
    "zero_mention_lint.py",
]
EXPECTED_REFERENCES = 6
EXPECTED_SCHEMAS = 13
EXPECTED_SCRIPTS = 13
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".toml", ".ini"}
READABILITY_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml"}
LOCAL_OUTPUT_SUFFIXES = {".docx", ".pptx", ".pdf", ".xlsx", ".zip"}


def tracked_repo_files() -> set[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        return set()
    return {item for item in result.stdout.decode("utf-8", errors="ignore").split("\0") if item}


def ignored_by_git(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    result = subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT)
    return result.returncode == 0


def iter_repo_files():
    tracked = tracked_repo_files()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if ".git" in rel.parts or "__pycache__" in rel.parts:
            continue
        rel_text = rel.as_posix()
        if rel_text not in tracked and ignored_by_git(path):
            continue
        yield path


def add_failure(failures: list[str], message: str) -> None:
    failures.append(message)


def check_file_sets(failures: list[str]) -> None:
    refs = list((ROOT / "references").glob("*.md"))
    schemas = list((ROOT / "schemas").glob("*.json"))
    scripts = list((ROOT / "scripts").glob("*.py"))
    if len(refs) != EXPECTED_REFERENCES:
        add_failure(failures, f"expected {EXPECTED_REFERENCES} reference files, found {len(refs)}")
    if len(schemas) != EXPECTED_SCHEMAS:
        add_failure(failures, f"expected {EXPECTED_SCHEMAS} schema files, found {len(schemas)}")
    if len(scripts) != EXPECTED_SCRIPTS:
        add_failure(failures, f"expected {EXPECTED_SCRIPTS} script files, found {len(scripts)}")


def check_paths(failures: list[str]) -> None:
    for path in iter_repo_files():
        rel = path.relative_to(ROOT)
        rel_text = rel.as_posix()
        for part in FORBIDDEN_PATH_PARTS:
            if part in rel_text:
                add_failure(failures, f"forbidden path part {part}: {rel_text}")
        for frag in FORBIDDEN_FILENAME_FRAGMENTS:
            if frag in path.name:
                add_failure(failures, f"forbidden filename fragment {frag}: {rel_text}")
        if path.suffix.lower() in LOCAL_OUTPUT_SUFFIXES and path.name not in {"LICENSE"}:
            add_failure(failures, f"local generated or source-pack file must not be committed: {rel_text}")


def check_text(failures: list[str]) -> None:
    for path in iter_repo_files():
        if path.resolve() == SELF or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        rel = path.relative_to(ROOT).as_posix()
        for term in FORBIDDEN_TEXT:
            if term.lower() in lowered:
                add_failure(failures, f"forbidden stale text {term!r} in {rel}")
        for name in STALE_SCRIPT_NAMES:
            if name in text:
                add_failure(failures, f"stale deleted script reference {name} in {rel}")


def check_readability(failures: list[str]) -> None:
    for path in iter_repo_files():
        if path.suffix.lower() not in READABILITY_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if len(text) > 240 and text.count("\n") < 2:
            rel = path.relative_to(ROOT).as_posix()
            add_failure(failures, f"formatted source file appears compressed into one line: {rel}")


def check_yaml_syntax(failures: list[str]) -> None:
    for folder, pattern in [(".github/workflows", "*.yml"), ("agents", "*.yaml")]:
        for path in (ROOT / folder).glob(pattern):
            try:
                parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:
                rel = path.relative_to(ROOT).as_posix()
                add_failure(failures, f"invalid yaml {rel}: {type(exc).__name__}: {exc}")
                continue
            if not isinstance(parsed, dict):
                rel = path.relative_to(ROOT).as_posix()
                add_failure(failures, f"yaml root must be a mapping: {rel}")


def check_manifest_commands(failures: list[str]) -> None:
    manifest = json.loads((ROOT / "skill_manifest.json").read_text(encoding="utf-8"))
    for cmd in manifest.get("health_commands", []):
        parts = cmd.split()
        for part in parts:
            if part.startswith("scripts/") and part.endswith(".py") and not (ROOT / part).exists():
                add_failure(failures, f"manifest references missing script: {part}")


def run_health_commands(failures: list[str]) -> None:
    manifest = json.loads((ROOT / "skill_manifest.json").read_text(encoding="utf-8"))
    for cmd in manifest.get("health_commands", []):
        if "github_ready_check.py --ci" in cmd:
            continue
        result = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            add_failure(failures, f"health command failed: {cmd}\n{result.stdout}")


def run(ci: bool = False) -> int:
    failures: list[str] = []
    check_file_sets(failures)
    check_paths(failures)
    check_text(failures)
    check_readability(failures)
    check_yaml_syntax(failures)
    check_manifest_commands(failures)
    if ci:
        run_health_commands(failures)
    if failures:
        print(json.dumps({"status": "fail", "failures": failures}, indent=2))
        return 1
    print(json.dumps({"status": "pass"}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()
    return run(args.ci)

if __name__ == "__main__":
    raise SystemExit(main())
