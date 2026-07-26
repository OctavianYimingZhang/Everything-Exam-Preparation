#!/usr/bin/env python3
"""Validate the manifest-driven Everything Exam Preparation Plugin."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_RETIRED_SKILLS = {
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
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
FIXED_COUNT_PATTERN = re.compile(
    r"\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|\d+)\s+"
    r"(?:(?:public|focused|local)\s+)?Skills?\b",
    re.IGNORECASE,
)


class ValidationError(RuntimeError):
    pass


def load_json(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON: {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected a JSON object: {relative}")
    return value


def load_yaml(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValidationError(f"Invalid YAML: {relative}: {exc}") from exc
    return value if isinstance(value, dict) else {}


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise ValidationError(f"Missing file: {relative}")
    return path.read_text(encoding="utf-8")


def frontmatter(relative: str) -> tuple[str, str]:
    text = read_text(relative)
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValidationError(f"Missing Skill frontmatter: {relative}")
    block = match.group(1)
    name = re.search(r"^name:\s*([^\n]+)$", block, re.MULTILINE)
    description = re.search(r"^description:\s*([^\n]+)$", block, re.MULTILINE)
    extra = [
        line.split(":", 1)[0]
        for line in block.splitlines()
        if ":" in line and not line.startswith(("name:", "description:"))
    ]
    if not name or not description or extra:
        raise ValidationError(f"Skill frontmatter must contain only name and description: {relative}")
    return name.group(1).strip(), description.group(1).strip()


def manifest_skills(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    entries = manifest.get("public_skills")
    if not isinstance(entries, list) or len(entries) < 2:
        raise ValidationError("A Multi-Skill System requires a Router and at least one focused Skill")
    pairs: list[tuple[str, str]] = []
    purposes: list[str] = []
    for item in entries:
        if not isinstance(item, dict):
            raise ValidationError("Each public Skill declaration must be an object")
        name = str(item.get("name", ""))
        relative = str(item.get("path", ""))
        purpose = str(item.get("purpose", ""))
        if not NAME_PATTERN.fullmatch(name) or relative != f"skills/{name}/SKILL.md" or not purpose:
            raise ValidationError(f"Invalid public Skill declaration: {item!r}")
        pairs.append((name, relative))
        purposes.append(purpose)
    if len({name for name, _ in pairs}) != len(pairs):
        raise ValidationError("Public Skill names must be unique")
    router = str(manifest.get("skill_id", ""))
    architecture = manifest.get("architecture", {})
    if pairs[0][0] != router or purposes[0] != "intent_router":
        raise ValidationError("The first public Skill must be the declared Router")
    if architecture.get("router") != router or architecture.get("focused_skill_policy") != "manifest_driven":
        raise ValidationError("Architecture must declare a manifest-driven focused Skill policy")
    return pairs


def check_manifest() -> tuple[dict[str, Any], list[tuple[str, str]], set[str], set[str]]:
    manifest = load_json("skill_manifest.json")
    version = str(manifest.get("plugin_version", ""))
    if manifest.get("schema_version") != 3 or not VERSION_PATTERN.fullmatch(version):
        raise ValidationError("skill_manifest.json must declare schema 3 and a semantic Plugin version")
    if manifest.get("skill_id") != "everything-exam-preparation" or manifest.get("multi_skill_system") is not True:
        raise ValidationError("skill_manifest.json has the wrong Router identity")
    skills = manifest_skills(manifest)
    references = {str(item) for item in manifest.get("references", [])}
    actual_references = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "references").glob("*.md")
    }
    if not references or references != actual_references:
        raise ValidationError("Manifest references must match the live reference files")
    tools = manifest.get("tools", {})
    if not isinstance(tools, dict) or not tools:
        raise ValidationError("skill_manifest.json must declare retained tools")
    tool_paths = {str(relative) for relative in tools.values()}
    actual_scripts = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "scripts").glob("*.py")
    }
    if tool_paths != actual_scripts:
        raise ValidationError("Manifest tools must match the live core scripts")
    for relative in references | tool_paths:
        read_text(relative)
    removed = {str(item) for item in manifest.get("removed_focused_skills", [])}
    if not REQUIRED_RETIRED_SKILLS.issubset(removed):
        raise ValidationError("skill_manifest.json is missing Plugin-owned retired Skills")
    if removed & {name for name, _ in skills}:
        raise ValidationError("A public Skill cannot also be retired")
    return manifest, skills, references, tool_paths


def check_skills(skills: list[tuple[str, str]]) -> None:
    root_name, _ = frontmatter("SKILL.md")
    if root_name != skills[0][0]:
        raise ValidationError("Root SKILL.md must match the Router")
    for expected_name, relative in skills:
        actual_name, description = frontmatter(relative)
        if actual_name != expected_name or len(description) < 40:
            raise ValidationError(f"Invalid Skill metadata: {relative}")
    live = {
        path.name
        for path in (ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    if live != {name for name, _ in skills}:
        raise ValidationError(f"Skill directories differ from the manifest: {sorted(live)}")


def check_metadata(manifest: dict[str, Any], skills: list[tuple[str, str]]) -> None:
    plugin = load_json(".codex-plugin/plugin.json")
    plugin_version = str(plugin.get("version", "")).split("+", 1)[0]
    if plugin.get("name") != "everything-exam-preparation" or plugin_version != manifest["plugin_version"]:
        raise ValidationError("Plugin identity or version drifted")
    if plugin.get("skills") != "./skills/":
        raise ValidationError("Plugin metadata must expose ./skills/")
    agents = load_yaml("agents/openai.yaml")
    if (
        str(agents.get("version", "")).split("+", 1)[0] != manifest["plugin_version"]
        or agents.get("default_skill") != skills[0][0]
        or agents.get("skills_manifest") != "skill_manifest.json"
        or "skills" in agents
    ):
        raise ValidationError("agents/openai.yaml must use the manifest as the Skill source")
    focused = {name for name, _ in skills[1:]}
    presets = load_yaml("agents/presets.yaml").get("presets", {})
    if not isinstance(presets, dict):
        raise ValidationError("agents/presets.yaml presets must be an object")
    preset_skills = {
        str(value.get("skill"))
        for value in presets.values()
        if isinstance(value, dict) and value.get("skill")
    }
    if not preset_skills.issubset(focused):
        raise ValidationError("Agent presets may reference only manifest-declared focused Skills")
    prompt_cards = load_yaml("agents/prompt_cards.yaml").get("prompt_cards", [])
    if not isinstance(prompt_cards, list):
        raise ValidationError("agents/prompt_cards.yaml prompt_cards must be a list")
    card_skills = {
        str(item.get("skill"))
        for item in prompt_cards
        if isinstance(item, dict) and item.get("skill")
    }
    if not card_skills.issubset(focused):
        raise ValidationError("Prompt cards may reference only manifest-declared focused Skills")
    load_yaml("agents/setup_wizard.yaml")


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


def check_retirement(skills: list[tuple[str, str]], references: set[str]) -> None:
    present = sorted(path for path in RETIRED_PATHS if (ROOT / path).exists())
    if present:
        raise ValidationError("Retired paths remain: " + ", ".join(present))
    retired = REQUIRED_RETIRED_SKILLS
    for path in source_files():
        relative = path.relative_to(ROOT).as_posix()
        if relative in {"scripts/validate_skill_contracts.py", "skill_manifest.json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in RETIRED_LANGUAGE.items():
            if pattern.search(text):
                raise ValidationError(f"{relative} still references {label}")
        for name in retired:
            if name in text:
                raise ValidationError(f"{relative} still references retired Skill {name}")
    public_files = [
        "SKILL.md",
        "README.md",
        ".codex-plugin/plugin.json",
        "agents/openai.yaml",
        *(relative for _, relative in skills),
        *references,
    ]
    combined = "\n".join(read_text(path) for path in public_files)
    if FIXED_COUNT_PATTERN.search(combined):
        raise ValidationError("Public guidance must not encode a fixed Skill count")


def check_merged_tools() -> None:
    merged_functions = {
        "scripts/extract_sources.py": ("process_sources", "build_fragment_index", "readiness_report"),
        "scripts/exam_mode_tools.py": ("build_assessment_blueprint", "evaluate_answer", "build_timed_practice"),
        "scripts/essay_exam_tools.py": (
            "discover_extra_reading",
            "build_extra_reading_enrichment",
            "online_essay_permission_status",
        ),
    }
    for relative, functions in merged_functions.items():
        text = read_text(relative)
        for function in functions:
            if f"def {function}(" not in text:
                raise ValidationError(f"{relative} is missing merged function {function}")


def check_notes_policy() -> None:
    root_skill = read_text("SKILL.md")
    skill = read_text("skills/exam-prep-notes/SKILL.md")
    input_protocol = read_text("references/input_and_evidence_protocol.md")
    protocol = read_text("references/exam_prep_notes_protocol.md")
    combined = f"{root_skill}\n{skill}\n{input_protocol}\n{protocol}".lower()
    if "visual-first" in combined:
        raise ValidationError("Notes guidance must use a visual-value gate rather than visual-first composition")
    required = {
        "materially improves": "a material teaching-value threshold for images",
        "no image quota": "an explicit no-quota image policy",
        "original lecture-slide": "source-slide visual priority",
        "knowledge density": "density-adaptive content length",
        "longer paragraphs": "flexible paragraph composition",
        "lecture boundary": "Lecture-boundary page-flow control",
        "knowledge-only": "the knowledge-only Notes artifact boundary",
        "source type never grants permission": "source evidence must not trigger another artifact",
        "do not create a companion": "no unsolicited companion Practice or Essay output",
        "assessment strategy": "assessment-planning content exclusion from public Notes",
        "2 cm margins": "the shared 2 cm Notes page-margin specification",
    }
    for phrase, purpose in required.items():
        if phrase not in combined:
            raise ValidationError(f"Notes guidance is missing {purpose}: {phrase!r}")

    generator = read_text("scripts/generate_exam_prep_notes_docx.py")
    geometry_contract = {
        r"(?m)^MARGIN_TWIPS\s*=\s*1134\s*$": "2 cm margins in Word twips",
        r"(?m)^CONTENT_WIDTH_TWIPS\s*=\s*PAGE_WIDTH_TWIPS\s*-\s*\(2\s*\*\s*MARGIN_TWIPS\)\s*$": (
            "content width derived from both 2 cm side margins"
        ),
        r"(?m)^MAX_IMAGE_WIDTH_EMU\s*=\s*6_120_000\s*$": (
            "the 17 cm image-width ceiling inside the 2 cm margins"
        ),
    }
    for pattern, purpose in geometry_contract.items():
        if not re.search(pattern, generator):
            raise ValidationError(f"Notes generator is missing {purpose}")
    margin_attributes = set(
        re.findall(r'w:(top|right|bottom|left)="\{MARGIN_TWIPS\}"', generator)
    )
    if margin_attributes != {"top", "right", "bottom", "left"}:
        raise ValidationError("Notes generator does not apply the 2 cm margin token on all four sides")


def run_check(command: list[str]) -> None:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise ValidationError(f"Command failed: {' '.join(command)}\n{detail}")


def is_git_worktree() -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def main() -> int:
    try:
        manifest, skills, references, _ = check_manifest()
        check_skills(skills)
        check_metadata(manifest, skills)
        check_retirement(skills, references)
        check_merged_tools()
        check_notes_policy()
        for key in ("sources", "notes", "practice", "essay", "installation"):
            run_check([sys.executable, str(manifest["tools"][key]), "--self-test"])
        if shutil.which("soffice"):
            run_check([sys.executable, str(manifest["tools"]["notes"]), "--render-self-test"])
        if is_git_worktree():
            run_check(["git", "diff", "--check"])
    except (ValidationError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: manifest-driven Everything Exam Preparation Plugin {manifest['plugin_version']} validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
