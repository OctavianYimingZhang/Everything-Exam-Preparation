#!/usr/bin/env python3
"""Validate the standalone Everything Exam Preparation Plugin."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the dependency preflight
    Draft202012Validator = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EXPECTED_SKILLS = [
    "everything-exam-preparation",
    "exam-prep-atlas",
    "exam-prep-analysis",
    "exam-prep-notes",
    "exam-prep-practice",
    "exam-prep-essay",
]
FOCUSED_PROTOCOLS = {
    "exam-prep-atlas": "references/course_atlas_protocol.md",
    "exam-prep-analysis": "references/exam_intelligence_protocol.md",
    "exam-prep-notes": "references/exam_prep_notes_protocol.md",
    "exam-prep-practice": "references/exam_mode_and_addons_protocol.md",
    "exam-prep-essay": "references/essay_exam_prep_protocol.md",
}
REQUIRED_ATLAS_MEMBERS = {
    "course_manifest.json",
    "sources.json",
    "relations.json",
    "past_paper_links.json",
    "public/web_index.json",
    "audit/coverage_ledger.json",
    "audit/exclusions.json",
    "audit/manual_review.json",
    "qa_report.md",
    "checksums.sha256",
}
ANALYSIS_METRICS = {
    "formal_occurrence_count",
    "distinct_formal_years",
    "formal_year_coverage",
    "auxiliary_occurrence_count",
    "format_diversity",
    "explicit_mark_exposure",
    "retention",
    "cross_year_stability",
    "mapping_coverage",
    "unresolved_mapping_count",
}
ANNOTATION_TYPES = {
    "thesis",
    "claim",
    "evidence",
    "analysis",
    "limitation",
    "synthesis",
    "paragraph function",
    "adaptation notes",
}
PROHIBITED_EXTERNAL_PATTERNS = {
    "coursework sibling": re.compile("coursework" + r"[-_ ]" + "killer", re.I),
    "university sibling": re.compile("everything" + r"[-_ ]" + "university", re.I),
    "external persistent store": re.compile("memory" + r"[_ ]" + "root|artifact" + r"[_ ]" + "registry", re.I),
    "external Plugin path": re.compile(r"\.\./(?:" + "Coursework|Everything" + "-University)", re.I),
}


class ValidationError(RuntimeError):
    pass


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise ValidationError(f"Missing file: {relative}")
    return path.read_text(encoding="utf-8")


def load_json(relative: str) -> dict[str, Any]:
    try:
        value = json.loads(read_text(relative))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON: {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected JSON object: {relative}")
    return value


def load_yaml(relative: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(read_text(relative))
    except yaml.YAMLError as exc:
        raise ValidationError(f"Invalid YAML: {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected YAML object: {relative}")
    return value


def frontmatter(relative: str) -> tuple[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", read_text(relative), re.DOTALL)
    if not match:
        raise ValidationError(f"Missing Skill frontmatter: {relative}")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            raise ValidationError(f"Invalid Skill frontmatter line: {relative}: {line}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if set(fields) != {"name", "description"} or not NAME_PATTERN.fullmatch(fields["name"]):
        raise ValidationError(f"Skill frontmatter must contain only valid name and description: {relative}")
    if len(fields["description"]) < 40:
        raise ValidationError(f"Skill description is too short: {relative}")
    return fields["name"], fields["description"]


def actual_files(directory: str, suffix: str, prefix: str = "") -> set[str]:
    root = ROOT / directory
    return {
        path.relative_to(ROOT).as_posix()
        for path in root.glob(f"{prefix}*{suffix}")
        if path.is_file()
    }


def check_manifest() -> dict[str, Any]:
    manifest = load_json("skill_manifest.json")
    if manifest.get("schema_version") != 4 or manifest.get("plugin_version") != "4.0.0":
        raise ValidationError("Manifest must declare schema 4 and Plugin version 4.0.0")
    if not VERSION_PATTERN.fullmatch(str(manifest.get("plugin_version") or "")):
        raise ValidationError("Plugin version must use strict semantic versioning")
    architecture = manifest.get("architecture") or {}
    if (
        manifest.get("standalone") is not True
        or architecture.get("router") != EXPECTED_SKILLS[0]
        or architecture.get("source_processor") != "scripts/extract_sources.py"
        or architecture.get("external_plugin_calls") is not False
    ):
        raise ValidationError("Manifest does not declare the standalone architecture")

    entries = manifest.get("public_skills")
    if not isinstance(entries, list) or [item.get("name") for item in entries if isinstance(item, dict)] != EXPECTED_SKILLS:
        raise ValidationError("Public Skill architecture or order is incorrect")
    for item in entries:
        name = str(item.get("name") or "")
        if item.get("path") != f"skills/{name}/SKILL.md" or not item.get("purpose"):
            raise ValidationError(f"Invalid public Skill declaration: {item!r}")

    declared_references = set(manifest.get("references") or [])
    declared_schemas = set(manifest.get("schemas") or [])
    declared_tools = set((manifest.get("tools") or {}).values())
    declared_tests = set(manifest.get("tests") or [])
    if declared_references != actual_files("references", ".md"):
        raise ValidationError("Manifest references do not match references/*.md")
    if declared_schemas != actual_files("schemas", ".json"):
        raise ValidationError("Manifest schemas do not match schemas/*.json")
    if declared_tools != actual_files("scripts", ".py"):
        raise ValidationError("Manifest tools do not match scripts/*.py")
    if declared_tests != actual_files("tests", ".py", "test_"):
        raise ValidationError("Manifest tests do not match tests/test_*.py")
    for relative in declared_references | declared_schemas | declared_tools | declared_tests:
        read_text(str(relative))
    return manifest


def check_skills_and_metadata(manifest: dict[str, Any]) -> None:
    root_name, _ = frontmatter("SKILL.md")
    if root_name != EXPECTED_SKILLS[0]:
        raise ValidationError("Root SKILL.md must be the Router")
    live = {
        path.name for path in (ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }
    if live != set(EXPECTED_SKILLS):
        raise ValidationError(f"Live Skills differ from manifest: {sorted(live)}")
    for name in EXPECTED_SKILLS:
        relative = f"skills/{name}/SKILL.md"
        actual, _ = frontmatter(relative)
        if actual != name:
            raise ValidationError(f"Skill identity mismatch: {relative}")
        content = read_text(relative)
        if "input_and_evidence_protocol.md" not in content:
            raise ValidationError(f"Skill omits the shared source/result contract: {name}")
        if name != EXPECTED_SKILLS[0] and "extract_sources.py" not in content:
            raise ValidationError(f"Focused Skill cannot process raw sources independently: {name}")
        protocol = FOCUSED_PROTOCOLS.get(name)
        if protocol and Path(protocol).name not in content:
            raise ValidationError(f"Focused Skill omits its own protocol: {name}")

    version = manifest["plugin_version"]
    plugin = load_json(".codex-plugin/plugin.json")
    if plugin.get("name") != EXPECTED_SKILLS[0] or plugin.get("version") != version or plugin.get("skills") != "./skills/":
        raise ValidationError("Plugin identity, version, or Skill path drifted")
    if "apps" in plugin or "mcpServers" in plugin or "hooks" in plugin:
        raise ValidationError("Plugin declares a companion component that does not exist")
    interface = plugin.get("interface") or {}
    if not interface.get("displayName") or not interface.get("shortDescription") or not interface.get("longDescription"):
        raise ValidationError("Plugin interface metadata is incomplete")
    if len(interface.get("defaultPrompt") or []) > 3:
        raise ValidationError("Plugin may expose at most three default prompts")

    agent = load_yaml("agents/openai.yaml")
    if agent.get("version") != version or agent.get("default_skill") != EXPECTED_SKILLS[0]:
        raise ValidationError("agents/openai.yaml identity or version drifted")
    focused = set(EXPECTED_SKILLS[1:])
    presets = load_yaml("agents/presets.yaml").get("presets") or {}
    cards = load_yaml("agents/prompt_cards.yaml").get("prompt_cards") or []
    if {item.get("skill") for item in presets.values()} != focused:
        raise ValidationError("Agent presets must cover the focused Skills exactly")
    if {item.get("skill") for item in cards} != focused:
        raise ValidationError("Prompt cards must cover the focused Skills exactly")
    load_yaml("agents/setup_wizard.yaml")


def repository_sources() -> list[Path]:
    selected: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", "__pycache__", ".skill_assets", ".pytest_cache"} for part in relative.parts):
            continue
        if path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".py", ".txt"}:
            selected.append(path)
    return selected


def check_independence(manifest: dict[str, Any]) -> None:
    for path in repository_sources():
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PROHIBITED_EXTERNAL_PATTERNS.items():
            if pattern.search(text):
                raise ValidationError(f"{relative} contains prohibited {label} dependency language")
    router = read_text("scripts/route_request.py")
    if '"plugin_calls": []' not in router or "out_of_scope_assessed_coursework" not in router:
        raise ValidationError("Router does not prove local refusal without external calls")
    root = read_text("SKILL.md").lower()
    for boundary in ("currently assessed coursework", "university timetables", "do not invoke or route"):
        if boundary not in root:
            raise ValidationError(f"Root boundary is missing: {boundary}")
    if manifest.get("architecture", {}).get("external_plugin_calls") is not False:
        raise ValidationError("External Plugin calls must remain disabled")


def check_schemas(manifest: dict[str, Any]) -> None:
    if Draft202012Validator is None:
        raise ValidationError("jsonschema is required; install requirements.txt before validation")
    for relative in manifest.get("schemas") or []:
        schema = load_json(relative)
        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:
            raise ValidationError(f"Invalid JSON Schema: {relative}: {exc}") from exc


def require_tokens(relative: str, tokens: set[str], label: str) -> None:
    text = read_text(relative).casefold()
    missing = sorted(token for token in tokens if token.casefold() not in text)
    if missing:
        raise ValidationError(f"{label} is missing: {', '.join(missing)}")


def check_source_contract() -> None:
    require_tokens(
        "scripts/extract_sources.py",
        {
            "expanded_source_inputs", "read_docx_paragraph_units", "read_image_text",
            "atlas", "analysis", "cache_dir", "embedded_ai_instruction",
            "formal_past_paper", "official_mock_specimen", "mark_scheme",
        },
        "Shared source processor",
    )
    require_tokens(
        "references/input_and_evidence_protocol.md",
        {"pptx", "pdf", "docx", "image", "zip", "timestamp", "incomplete", "optional task-local cache"},
        "Source protocol",
    )


def check_atlas_contract() -> None:
    require_tokens("references/course_atlas_protocol.md", REQUIRED_ATLAS_MEMBERS, "Course Atlas protocol")
    require_tokens(
        "schemas/atlas_node.schema.json",
        {
            "node_id", "node_type", "parent_id", "title", "explanation", "sequence_index",
            "keywords", "aliases", "source_refs", "relation_ids", "knowledge_status",
        },
        "Atlas node schema",
    )
    require_tokens(
        "scripts/validate_course_atlas.py",
        {"checksums.sha256", "modules/", "manual_review", "raw"},
        "Course Atlas validator",
    )


def check_analysis_contract() -> None:
    combined = "\n".join([
        read_text("references/exam_intelligence_protocol.md"),
        read_text("scripts/exam_intelligence_tools.py"),
        read_text("schemas/question_family.schema.json"),
    ]).casefold()
    for metric in ANALYSIS_METRICS:
        if metric not in combined:
            raise ValidationError(f"Exam Analysis omits metric: {metric}")
    for role in ("formal_past_paper", "official_mock_specimen", "practice_worksheet", "lecture_material", "mark_scheme"):
        if role not in combined:
            raise ValidationError(f"Exam Analysis omits source role: {role}")
    for boundary in ("official assessment weighting", "predict", "public", "audit"):
        if boundary not in combined:
            raise ValidationError(f"Exam Analysis omits boundary: {boundary}")


def check_notes_contract() -> None:
    combined = "\n".join([
        read_text("SKILL.md"),
        read_text("skills/exam-prep-notes/SKILL.md"),
        read_text("references/exam_prep_notes_protocol.md"),
    ]).casefold()
    for phrase in (
        "knowledge-only", "course-complete", "assessment strategy", "question banks",
        "essay", "revision schedules", "do not create a companion",
    ):
        if phrase not in combined:
            raise ValidationError(f"Notes boundary is missing: {phrase}")
    generator = read_text("scripts/generate_exam_prep_notes_docx.py")
    geometry = {
        r"(?m)^MARGIN_TWIPS\s*=\s*1134\s*$": "2 cm margins",
        r"(?m)^BODY_HALF_POINTS\s*=\s*22\s*$": "Arial 11 pt body",
        r"(?m)^HEADING1_HALF_POINTS\s*=\s*31\s*$": "15.5 pt first heading",
    }
    for pattern, label in geometry.items():
        if not re.search(pattern, generator):
            raise ValidationError(f"Notes renderer omits {label}")


def check_practice_contract() -> None:
    practice_script = read_text("scripts/exam_mode_tools.py")
    combined = "\n".join([
        read_text("skills/exam-prep-practice/SKILL.md"),
        read_text("references/exam_mode_and_addons_protocol.md"),
        practice_script,
    ]).casefold()
    for phrase in (
        "solution_book", "major question", "general approach", "docx", "pdf",
        "json", "batch", "continuous", "heading", "table", "formula", "callout",
    ):
        if phrase not in combined:
            raise ValidationError(f"Practice solution-book contract is missing: {phrase}")
    for status in ("correct", "partial", "incorrect", "contradicted", "missing"):
        if status not in combined:
            raise ValidationError(f"Practice answer status is missing: {status}")
    for forbidden in (
        "build_mcq_saq_recurrence_report",
        '"build-mcq-report"',
        '"build-short-answer-report"',
        '"build-mcq-saq-report"',
    ):
        if forbidden in practice_script:
            raise ValidationError(
                f"Practice exposes an Analysis-owned recurrence command or builder: {forbidden}"
            )


def check_essay_contract() -> None:
    combined = "\n".join([
        read_text("skills/exam-prep-essay/SKILL.md"),
        read_text("references/essay_exam_prep_protocol.md"),
        read_text("scripts/essay_exam_tools.py"),
    ]).casefold()
    for annotation in ANNOTATION_TYPES:
        if annotation not in combined and annotation.replace(" ", "_") not in combined:
            raise ValidationError(f"Essay annotation is missing: {annotation}")
    for phrase in (
        "clean", "annotated", "shared", "canonical", "closed", "course sources",
        "past papers", "doi", "currently assessed",
    ):
        if phrase not in combined:
            raise ValidationError(f"Essay contract is missing: {phrase}")


def run_check(command: list[str]) -> None:
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise ValidationError(f"Command failed: {' '.join(command)}\n{detail}")


def check_runtime() -> None:
    run_check([sys.executable, "-m", "compileall", "-q", "scripts", "tests"])
    for relative in (
        "scripts/route_request.py",
        "scripts/extract_sources.py",
        "scripts/generate_exam_prep_notes_docx.py",
        "scripts/exam_mode_tools.py",
        "scripts/essay_exam_tools.py",
        "scripts/publish_skill.py",
    ):
        run_check([sys.executable, relative, "--self-test"])
    run_check([sys.executable, "scripts/exam_intelligence_tools.py", "self-test"])
    run_check([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"])
    if shutil.which("soffice"):
        run_check([sys.executable, "scripts/generate_exam_prep_notes_docx.py", "--render-self-test"])
    if (ROOT / ".git").exists():
        run_check(["git", "diff", "--check"])


def main() -> int:
    try:
        manifest = check_manifest()
        check_skills_and_metadata(manifest)
        check_independence(manifest)
        check_schemas(manifest)
        check_source_contract()
        check_atlas_contract()
        check_analysis_contract()
        check_notes_contract()
        check_practice_contract()
        check_essay_contract()
        check_runtime()
    except (ValidationError, KeyError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: standalone Everything Exam Preparation Plugin {manifest['plugin_version']} validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
