#!/usr/bin/env python3
"""Public-release checks for the exam-prep skill."""
from __future__ import annotations

import argparse
import compileall
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/input_and_evidence_protocol.md",
    "references/exam_prep_core_workflow.md",
    "references/exam_mode_and_addons_protocol.md",
    "references/essay_exam_prep_protocol.md",
    "references/language_quality_contract.md",
    "references/runtime_qa_release_protocol.md",
    "scripts/plan_workflow.py",
]

PRIVATE_PATTERNS = ["/" + "Users/", "One" + "Drive", "Cloud" + "Storage", "octavian" + "zhang", "Desk" + "top", "University of " + "Manchester", "School of " + "Biological"]
SKIP_PARTS = {".git", "__pycache__"}

CLUTTER_PATH_PREFIXES = ("bench" + "marks/", "tests/" + "fixtures/")
CLUTTER_NAME_PATTERNS = (
    re.compile(r"(^|/)" + "fa" + "ke_" + r"[^/]*$"),
    re.compile(r"(^|/)negative_" + r"[^/]*$"),
    re.compile(r"(^|/)positive_" + r"[^/]*$"),
    re.compile(r"(^|/)" + r"[^/]*" + "_fixture" + r"\.[^/]*$"),
)
CLUTTER_TEXT_PATTERNS = ("Example" + "ReviewLedger", "Language" + "Delta", "UnitExample" + "Contribution")



def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(name: str, command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode:
        print(result.stdout)
        fail(f"{name} failed")


def check_required() -> None:
    missing = [rel for rel in REQUIRED if not (ROOT / rel).exists()]
    if missing:
        fail("missing required files: " + ", ".join(missing))


def check_generated_absent() -> None:
    blocked = [ROOT / "custom_gpt_knowledge", ROOT / "dist", ROOT / "build", ROOT / ".pytest_cache"]
    present = [str(path.relative_to(ROOT)) for path in blocked if path.exists()]
    if present:
        fail("generated or local-only paths are present: " + ", ".join(present))


def check_private_strings() -> None:
    regex = re.compile("|".join(re.escape(pattern) for pattern in PRIVATE_PATTERNS))
    hits: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_PARTS for part in path.parts) or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if regex.search(text):
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        fail("private strings found in: " + ", ".join(hits))



def check_clutter_absent() -> None:
    path_hits: list[str] = []
    text_hits: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT))
        if rel.startswith(CLUTTER_PATH_PREFIXES) or any(pattern.search(rel) for pattern in CLUTTER_NAME_PATTERNS):
            path_hits.append(rel)
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(pattern in text for pattern in CLUTTER_TEXT_PATTERNS):
            text_hits.append(rel)
    if path_hits or text_hits:
        fail("committed example/fixture clutter found: " + ", ".join(sorted(path_hits + text_hits)))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--require-clean", action="store_true")
    args = parser.parse_args()

    check_required()
    check_generated_absent()
    check_private_strings()
    check_clutter_absent()
    if not compileall.compile_dir(ROOT / "scripts", quiet=1):
        fail("script compilation failed")
    run("identity trigger scan", [sys.executable, "scripts/no_identity_trigger_linter.py", "--forbid-legacy-label"])
    run("workflow planning contract", [sys.executable, "scripts/validate_workflow_planning_contract.py"])
    run("interaction contract", [sys.executable, "scripts/validate_interaction_contract.py"])
    run("student output contract", [sys.executable, "scripts/validate_student_output_contract.py"])
    run("workflow planner self-test", [sys.executable, "scripts/plan_workflow.py", "--self-test"])
    run("input readiness self-test", [sys.executable, "scripts/input_readiness_check.py", "--self-test"])
    run("source extraction self-test", [sys.executable, "scripts/extract_sources.py", "--self-test"])
    run("past paper extraction self-test", [sys.executable, "scripts/extract_past_paper_questions.py", "--self-test"])
    run("public lecture notes renderer", [sys.executable, "scripts/public_lecture_notes_renderer.py", "--self-test"])
    run("public notes docx generator", [sys.executable, "scripts/generate_public_lecture_notes_docx.py", "--self-test"])
    run("deliverable surface linter", [sys.executable, "scripts/deliverable_surface_linter.py", "--self-test"])
    run("example essay docx generator", [sys.executable, "scripts/generate_example_essay_docx.py", "--self-test"])
    run("citation fallback linter", [sys.executable, "scripts/citation_fallback_linter.py", "--self-test"])
    run("example essay language linter", [sys.executable, "scripts/example_essay_language_linter.py", "--self-test"])
    run("past-paper prediction linter", [sys.executable, "scripts/past_paper_prediction_linter.py", "--self-test"])
    run("notes exam-ready language linter", [sys.executable, "scripts/notes_exam_ready_language_linter.py", "--self-test"])
    run("module teaching depth linter", [sys.executable, "scripts/module_teaching_depth_linter.py", "--self-test"])
    run("notes readability layout linter", [sys.executable, "scripts/notes_readability_layout_linter.py", "--self-test"])
    run("output sufficiency linter", [sys.executable, "scripts/output_sufficiency_linter.py", "--self-test"])
    run("zero mention lint", [sys.executable, "scripts/zero_mention_lint.py", "--self-test"])
    run("knowledge surface lint", [sys.executable, "scripts/knowledge_surface_linter.py", "--self-test"])
    run("scientific precision lint", [sys.executable, "scripts/scientific_precision_linter.py", "--self-test"])
    if args.require_clean:
        check_generated_absent()
    print("OK: public release checks passed")


if __name__ == "__main__":
    main()
