#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SKILLS = {
    "everything-exam-preparation": "skills/everything-exam-preparation/SKILL.md",
    "exam-prep-notes": "skills/exam-prep-notes/SKILL.md",
    "exam-prep-practice": "skills/exam-prep-practice/SKILL.md",
    "exam-prep-essay": "skills/exam-prep-essay/SKILL.md",
}
REFERENCES = {
    "references/input_and_evidence_protocol.md",
    "references/exam_prep_notes_protocol.md",
    "references/exam_mode_and_addons_protocol.md",
    "references/essay_exam_prep_protocol.md",
}
CORE_SCRIPTS = {
    "scripts/extract_sources.py",
    "scripts/generate_exam_prep_notes_docx.py",
    "scripts/exam_mode_tools.py",
    "scripts/essay_exam_tools.py",
    "scripts/publish_skill.py",
    "scripts/validate_skill_contracts.py",
}
RETIRED_SKILLS = {
    "exam-prep-index",
    "exam-prep-slide-triage",
    "exam-prep-mcq",
    "exam-prep-short-answer",
    "exam-prep-long-answer",
    "exam-prep-worked-solutions",
    "exam-prep-online-essay-exam",
    "exam-prep-extra-reading",
    "exam-prep-question-solver",
    "exam-prep-question-organizer",
    "exam-prep-exam-mode",
}
RETIRED_PATHS = {
    "plugin_capability_manifest.json",
    "contracts",
    "schemas",
    "tests",
    "scripts/build_fragment_index.py",
    "scripts/input_readiness_check.py",
    "scripts/assessment_tools.py",
    "scripts/extra_reading_tools.py",
    "scripts/plan_workflow.py",
    "scripts/build_review_questions.py",
    "scripts/soleil_adapter.py",
    "scripts/mastery_history.py",
    "scripts/github_ready_check.py",
}
RETIRED_LANGUAGE = {
    "Auto-diagnosis": re.compile(r"auto[- ]diagnosis", re.I),
    "Direct Invocation Gate": re.compile(r"direct invocation gate", re.I),
    "Soleil": re.compile(r"\bsoleil\b", re.I),
    "TaskRunState": re.compile(r"taskrunstate|task run state", re.I),
    "Local Bridge": re.compile(r"local bridge", re.I),
    "mastery history": re.compile(r"mastery history|mastery_history", re.I),
    "thirteen routes": re.compile(r"13 routes|thirteen routes", re.I),
}


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def load_yaml(relative: str) -> dict[str, Any]:
    value = yaml.safe_load((ROOT / relative).read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def frontmatter_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"\A---\s*\n.*?^name:\s*([a-z0-9-]+)\s*$.*?^---\s*$", text, re.M | re.S)
    return match.group(1) if match else None


def source_files() -> list[Path]:
    selected: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", "outputs", "__pycache__", ".skill_assets"} for part in relative.parts):
            continue
        if path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".py"}:
            selected.append(path)
    return selected


def run_self_test(relative: str) -> str | None:
    process = subprocess.run(
        [sys.executable, str(ROOT / relative), "--self-test"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if process.returncode:
        detail = (process.stderr or process.stdout).strip()
        return f"{relative} self-test failed: {detail}"
    return None


def validate() -> dict[str, Any]:
    failures: list[str] = []

    manifest = load_json("skill_manifest.json")
    plugin = load_json(".codex-plugin/plugin.json")
    for relative in ("agents/openai.yaml", "agents/presets.yaml", "agents/prompt_cards.yaml", "agents/setup_wizard.yaml"):
        try:
            load_yaml(relative)
        except Exception as exc:
            failures.append(f"{relative} is not valid YAML: {exc}")

    if manifest.get("plugin_version") != "3.0.0":
        failures.append("skill_manifest.json plugin_version must be 3.0.0")
    if plugin.get("version") != "3.0.0":
        failures.append(".codex-plugin/plugin.json version must be 3.0.0")
    if "routes" in manifest or "capability_manifest" in manifest:
        failures.append("skill_manifest.json still declares the retired route API")

    declared = {
        str(item.get("name")): str(item.get("path"))
        for item in manifest.get("public_skills", [])
        if isinstance(item, dict)
    }
    if declared != PUBLIC_SKILLS:
        failures.append(f"public Skill declaration mismatch: {declared}")

    actual = {
        path.parent.name: path.relative_to(ROOT).as_posix()
        for path in (ROOT / "skills").glob("*/SKILL.md")
    }
    if actual != PUBLIC_SKILLS:
        failures.append(f"Plugin Skill directory mismatch: {actual}")

    if frontmatter_name(ROOT / "SKILL.md") != "everything-exam-preparation":
        failures.append("root SKILL.md frontmatter name is invalid")
    for name, relative in PUBLIC_SKILLS.items():
        path = ROOT / relative
        if not path.exists():
            failures.append(f"missing public Skill: {relative}")
        elif frontmatter_name(path) != name:
            failures.append(f"{relative} frontmatter name must be {name}")

    actual_references = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "references").glob("*.md")
    }
    if actual_references != REFERENCES:
        failures.append(f"reference set mismatch: {sorted(actual_references)}")

    actual_scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("*.py")
    }
    if actual_scripts != CORE_SCRIPTS:
        failures.append(f"core script set mismatch: {sorted(actual_scripts)}")

    for relative in sorted(RETIRED_PATHS):
        if (ROOT / relative).exists():
            failures.append(f"retired path remains: {relative}")

    removed = set(str(item) for item in manifest.get("removed_focused_skills", []))
    if removed != RETIRED_SKILLS:
        failures.append("removed_focused_skills does not match the Plugin-owned retired entries")

    expected_names = set(PUBLIC_SKILLS)
    openai_skills = set(str(item) for item in load_yaml("agents/openai.yaml").get("skills", []))
    if openai_skills != expected_names:
        failures.append("agents/openai.yaml must declare exactly the four public Skills")

    prompt_cards = load_yaml("agents/prompt_cards.yaml").get("prompt_cards", [])
    card_skills = {str(item.get("skill")) for item in prompt_cards if isinstance(item, dict)}
    if card_skills != expected_names - {"everything-exam-preparation"}:
        failures.append("agents/prompt_cards.yaml must declare Notes, Practice, and Essay")

    plugin_text = json.dumps(plugin, ensure_ascii=False)
    manifest_text = json.dumps(manifest, ensure_ascii=False)
    for name in expected_names:
        if name not in plugin_text + manifest_text:
            failures.append(f"metadata does not expose {name}")

    merged_functions = {
        "scripts/extract_sources.py": ("process_sources", "build_fragment_index", "readiness_report"),
        "scripts/exam_mode_tools.py": ("build_assessment_blueprint", "evaluate_answer", "build_timed_practice"),
        "scripts/essay_exam_tools.py": ("discover_extra_reading", "build_extra_reading_enrichment", "online_essay_permission_status"),
    }
    for relative, functions in merged_functions.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for function in functions:
            if f"def {function}(" not in text:
                failures.append(f"{relative} is missing merged function {function}")

    for path in source_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(ROOT).as_posix()
        if relative == "scripts/validate_skill_contracts.py":
            continue
        for label, pattern in RETIRED_LANGUAGE.items():
            if pattern.search(text):
                failures.append(f"{relative} still references {label}")
        for retired in RETIRED_SKILLS:
            if retired in text and relative != "skill_manifest.json":
                failures.append(f"{relative} still references retired Skill {retired}")

    for relative in (
        "scripts/extract_sources.py",
        "scripts/generate_exam_prep_notes_docx.py",
        "scripts/exam_mode_tools.py",
        "scripts/essay_exam_tools.py",
        "scripts/publish_skill.py",
    ):
        failure = run_self_test(relative)
        if failure:
            failures.append(failure)

    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT, text=True, capture_output=True)
    if diff.returncode:
        failures.append(f"git diff --check failed: {(diff.stderr or diff.stdout).strip()}")

    return {
        "status": "ok" if not failures else "error",
        "version": "3.0.0",
        "public_skills": sorted(PUBLIC_SKILLS),
        "reference_count": len(REFERENCES),
        "core_script_count": len(CORE_SCRIPTS),
        "failures": failures,
    }


def main() -> None:
    result = validate()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["status"] != "ok":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
