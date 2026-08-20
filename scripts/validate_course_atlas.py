#!/usr/bin/env python3
"""Validate a self-contained Course Atlas ZIP and its bundled JSON Schemas."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILES = (
    "atlas_node.schema.json",
    "atlas_relation.schema.json",
    "course_atlas_package.schema.json",
)
SCHEMA_VERSION = "1.0"
NODE_TYPES = {"course", "theme", "lecture", "module", "concept", "detail"}
KNOWLEDGE_STATUSES = {"complete", "partial", "incomplete", "uncertain"}
SOURCE_TYPES = {"pptx", "pdf", "docx", "transcript", "image", "text", "markdown", "other"}
RELATION_TYPES = {
    "prerequisite_for",
    "part_of",
    "causes",
    "activates",
    "inhibits",
    "regulates",
    "compares_with",
    "contrasts_with",
    "associated_with",
    "evidence_for",
    "method_for",
    "other",
}
EXCLUSION_CATEGORIES = {
    "attendance",
    "canvas_operation",
    "seats_operation",
    "mentimeter_operation",
    "email_admin",
    "submission_instruction",
    "course_administration",
    "decorative",
    "ai_instruction",
    "other_non_knowledge",
}
REVIEW_ISSUE_TYPES = {"locator", "hierarchy", "coverage", "relation", "content", "other"}
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TIMESTAMP_RE = re.compile(r"^(?P<hours>[0-9]{2,}):(?P<minutes>[0-5][0-9]):(?P<seconds>[0-5][0-9])(?:\.(?P<millis>[0-9]{3}))?$")
CHECKSUM_RE = re.compile(r"^(?P<digest>[0-9a-f]{64})  (?P<path>[^\r\n]+)$")
MODULE_FILE_RE = re.compile(r"^modules/[^/]+\.json$")
RAW_SOURCE_SUFFIXES = {
    ".ppt",
    ".pptx",
    ".pdf",
    ".doc",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
    ".vtt",
    ".srt",
    ".mp3",
    ".mp4",
    ".mov",
    ".wav",
    ".zip",
    ".7z",
    ".rar",
}
FIXED_PACKAGE_FILES = {
    "course_manifest.json",
    "sources.json",
    "modules/hierarchy.json",
    "relations.json",
    "past_paper_links.json",
    "public/web_index.json",
    "audit/coverage_ledger.json",
    "audit/exclusions.json",
    "audit/manual_review.json",
    "qa_report.md",
    "checksums.sha256",
}
PUBLIC_JSON_FILES = {
    "course_manifest.json",
    "sources.json",
    "relations.json",
    "past_paper_links.json",
    "public/web_index.json",
}
FORBIDDEN_PUBLIC_KEYS = {"audit", "coverage_ledger", "exclusions", "manual_review"}

EXCLUSION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "ai_instruction",
        re.compile(
            r"\bignore\s+(?:all\s+|any\s+|the\s+)?previous\s+instructions\b|"
            r"\byou\s+are\s+(?:chatgpt|an?\s+ai|an?\s+language\s+model)\b|"
            r"\bas\s+an?\s+(?:ai|language\s+model)\b|"
            r"\binstructions?\s+for\s+(?:the\s+)?(?:ai|chatgpt|language\s+model)\b|"
            r"\b(?:tell|ask|instruct)\s+(?:the\s+)?(?:ai|chatgpt|language\s+model)\b|"
            r"\bdo\s+not\s+reveal\s+(?:this|the|your)\s+(?:system\s+)?prompt\b|"
            r"\b(?:reveal|print|show|return|output)\b.{0,40}\b(?:system\s+prompt|hidden\s+prompt)\b",
            re.I,
        ),
    ),
    (
        "canvas_operation",
        re.compile(
            r"\b(?:upload|submit|click|log\s*in|open|go\s+to|navigate\s+to|access|visit)\b.{0,60}\bcanvas\b|"
            r"\b(?:use|follow)\b.{0,40}\bcanvas\s+(?:navigation|menu|page|module|course)\b|"
            r"\bcanvas\b.{0,60}\b(?:upload|submit|deadline|navigation|menu|login|log\s*in)\b",
            re.I,
        ),
    ),
    ("seats_operation", re.compile(r"\bseats\b.{0,50}\b(?:check|attendance|app|code|sign)\b|\b(?:check|attendance|app|code|sign)\b.{0,50}\bseats\b", re.I)),
    ("mentimeter_operation", re.compile(r"\bmentimeter\b|\bmenti\.com\b|\bmenti\s+(?:code|access)\b", re.I)),
    ("email_admin", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b|\bemail\s+(?:the\s+)?(?:lecturer|convenor|instructor|office|administrator|staff)\b", re.I)),
    ("submission_instruction", re.compile(r"\b(?:submit|upload)\b.{0,60}\b(?:by|deadline|assignment|assessment|coursework)\b|\bsubmission\s+(?:deadline|instructions?|portal)\b", re.I)),
    (
        "course_administration",
        re.compile(
            r"\b(?:office\s+hours?|module\s+convenor|course\s+representative|assessment\s+deadline|"
            r"timetable\s+change|course\s+registration|module\s+registration|course\s+enrolment|"
            r"module\s+enrolment|course\s+administration)\b",
            re.I,
        ),
    ),
    ("attendance", re.compile(r"\b(?:attendance|sign[- ]?in\s+(?:code|sheet|app))\b|签到", re.I)),
)
DECORATIVE_TEXT = {
    "welcome",
    "welcome!",
    "thank you",
    "thank you!",
    "thanks",
    "questions",
    "questions?",
    "break",
    "coffee break",
}


class AtlasValidationError(ValueError):
    """Raised when an Atlas specification or ZIP violates its contract."""


def _fail(context: str, message: str) -> None:
    raise AtlasValidationError(f"{context}: {message}")


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AtlasValidationError(f"JSON contains duplicate key {key!r}")
        result[key] = value
    return result


def load_json_bytes(data: bytes, context: str) -> Any:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AtlasValidationError(f"{context}: is not UTF-8") from exc
    try:
        return json.loads(text, object_pairs_hook=_no_duplicate_object)
    except json.JSONDecodeError as exc:
        raise AtlasValidationError(f"{context}: invalid JSON ({exc})") from exc


def load_json_file(path: str | Path) -> Any:
    path = Path(path)
    return load_json_bytes(path.read_bytes(), str(path))


def _require_object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(context, "must be an object")
    return value


def _require_list(value: Any, context: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(context, "must be an array")
    return value


def _fields(
    value: Any,
    context: str,
    required: Iterable[str],
    optional: Iterable[str] = (),
) -> dict[str, Any]:
    obj = _require_object(value, context)
    required_set = set(required)
    allowed = required_set | set(optional)
    missing = sorted(required_set - set(obj))
    extra = sorted(set(obj) - allowed)
    if missing:
        _fail(context, f"missing required fields: {', '.join(missing)}")
    if extra:
        _fail(context, f"unexpected fields: {', '.join(extra)}")
    return obj


def _nonempty_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(context, "must be a non-empty string")
    return value


def _identifier(value: Any, context: str) -> str:
    text = _nonempty_string(value, context)
    if not ID_RE.fullmatch(text):
        _fail(context, "must be a package-local identifier without path separators")
    return text


def _nonnegative_int(value: Any, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(context, "must be a non-negative integer")
    return value


def _positive_int(value: Any, context: str) -> int:
    result = _nonnegative_int(value, context)
    if result == 0:
        _fail(context, "must be at least 1")
    return result


def _string_set(value: Any, context: str) -> list[str]:
    items = _require_list(value, context)
    rendered = [_nonempty_string(item, f"{context}[{index}]") for index, item in enumerate(items)]
    if len(set(rendered)) != len(rendered):
        _fail(context, "must not contain duplicates")
    return rendered


def _id_set(value: Any, context: str, *, nonempty: bool = False) -> list[str]:
    items = _require_list(value, context)
    if nonempty and not items:
        _fail(context, "must contain at least one identifier")
    rendered = [_identifier(item, f"{context}[{index}]") for index, item in enumerate(items)]
    if len(set(rendered)) != len(rendered):
        _fail(context, "must not contain duplicates")
    return rendered


def _validate_datetime(value: Any, context: str) -> str:
    text = _nonempty_string(value, context)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AtlasValidationError(f"{context}: must be an ISO 8601 date-time") from exc
    if parsed.tzinfo is None:
        _fail(context, "must include a timezone")
    return text


def _timestamp_millis(value: Any, context: str) -> int:
    text = _nonempty_string(value, context)
    match = TIMESTAMP_RE.fullmatch(text)
    if not match:
        _fail(context, "must use HH:MM:SS or HH:MM:SS.mmm")
    return (
        int(match.group("hours")) * 3_600_000
        + int(match.group("minutes")) * 60_000
        + int(match.group("seconds")) * 1_000
        + int(match.group("millis") or 0)
    )


def _schema_bundle() -> tuple[dict[str, dict[str, Any]], Registry]:
    documents: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for filename in SCHEMA_FILES:
        path = ROOT / "schemas" / filename
        if not path.is_file():
            raise AtlasValidationError(f"missing bundled schema schemas/{filename}")
        schema = load_json_file(path)
        obj = _require_object(schema, f"schemas/{filename}")
        if obj.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            _fail(f"schemas/{filename}", "must declare JSON Schema draft 2020-12")
        if obj.get("$id") != filename:
            _fail(f"schemas/{filename}", f"$id must be {filename!r}")
        try:
            Draft202012Validator.check_schema(obj)
            resource = Resource.from_contents(
                obj,
                default_specification=DRAFT202012,
            )
        except Exception as exc:
            raise AtlasValidationError(
                f"schemas/{filename}: invalid Draft 2020-12 schema ({exc})"
            ) from exc
        documents[filename] = obj
        registry = registry.with_resource(filename, resource)
        registry = registry.with_resource(path.resolve().as_uri(), resource)
    return documents, registry


def validate_schema_documents() -> None:
    _schema_bundle()


def validate_schema_instance(value: Any) -> None:
    """Validate one normalized Atlas build spec with locally resolved refs."""

    documents, registry = _schema_bundle()
    schema = documents["course_atlas_package.schema.json"]
    try:
        Draft202012Validator(schema, registry=registry).validate(value)
    except ValidationError as exc:
        location = ".".join(str(item) for item in exc.absolute_path) or "$"
        raise AtlasValidationError(
            f"spec: JSON Schema validation failed at {location}: {exc.message}"
        ) from exc
    except SchemaError as exc:
        raise AtlasValidationError(
            f"schemas/course_atlas_package.schema.json: invalid schema ({exc.message})"
        ) from exc
    except Exception as exc:
        raise AtlasValidationError(
            f"spec: JSON Schema reference resolution failed ({exc})"
        ) from exc


def _validate_course(value: Any, context: str) -> dict[str, Any]:
    course = _fields(
        value,
        context,
        {"course_id", "title", "language"},
        {"institution", "academic_year"},
    )
    _identifier(course["course_id"], f"{context}.course_id")
    _nonempty_string(course["title"], f"{context}.title")
    language = _nonempty_string(course["language"], f"{context}.language")
    if len(language) < 2:
        _fail(f"{context}.language", "must contain at least two characters")
    for field in ("institution", "academic_year"):
        if field in course:
            _nonempty_string(course[field], f"{context}.{field}")
    return course


def _validate_source(value: Any, context: str) -> dict[str, Any]:
    source = _fields(
        value,
        context,
        {"source_id", "source_type", "display_name", "packaged"},
        {"filename", "source_label", "content_sha256"},
    )
    _identifier(source["source_id"], f"{context}.source_id")
    source_type = source["source_type"]
    if source_type not in SOURCE_TYPES:
        _fail(f"{context}.source_type", f"must be one of {sorted(SOURCE_TYPES)}")
    _nonempty_string(source["display_name"], f"{context}.display_name")
    if source["packaged"] is not False:
        _fail(f"{context}.packaged", "must be false; original sources are never package members")
    if "filename" not in source and "source_label" not in source:
        _fail(context, "requires filename or source_label")
    if source_type != "transcript" and "filename" not in source:
        _fail(context, f"{source_type} sources require filename")
    if "filename" in source:
        filename = _nonempty_string(source["filename"], f"{context}.filename")
        if filename != Path(filename).name or "/" in filename or "\\" in filename or "\x00" in filename:
            _fail(f"{context}.filename", "must be a basename, not a filesystem path")
    if "source_label" in source:
        _nonempty_string(source["source_label"], f"{context}.source_label")
    if "content_sha256" in source and (
        not isinstance(source["content_sha256"], str)
        or not SHA256_RE.fullmatch(source["content_sha256"])
    ):
        _fail(f"{context}.content_sha256", "must be a lowercase SHA-256 digest")
    return source


def _validate_locator(locator_value: Any, source_type: str, context: str) -> dict[str, Any]:
    locator = _require_object(locator_value, context)
    kind = locator.get("kind")
    allowed_kinds = {
        "pptx": {"slide"},
        "pdf": {"page"},
        "docx": {"heading_path", "paragraph_range"},
        "transcript": {"timestamp"},
        "image": {"file"},
        "text": {"heading_path", "line_range"},
        "markdown": {"heading_path", "line_range"},
        "other": {"file"},
    }[source_type]
    if kind not in allowed_kinds:
        _fail(context, f"locator kind {kind!r} is not valid for source type {source_type!r}")
    if kind in {"slide", "page", "paragraph_range", "line_range"}:
        locator = _fields(locator, context, {"kind", "start", "end"})
        start = _positive_int(locator["start"], f"{context}.start")
        end = _positive_int(locator["end"], f"{context}.end")
        if end < start:
            _fail(context, "range end cannot precede range start")
    elif kind == "heading_path":
        locator = _fields(locator, context, {"kind", "heading_path"})
        path = _string_set(locator["heading_path"], f"{context}.heading_path")
        if not path:
            _fail(f"{context}.heading_path", "must contain at least one heading")
    elif kind == "timestamp":
        locator = _fields(locator, context, {"kind", "start", "end"})
        start = _timestamp_millis(locator["start"], f"{context}.start")
        end = _timestamp_millis(locator["end"], f"{context}.end")
        if end < start:
            _fail(context, "timestamp end cannot precede start")
    elif kind == "file":
        locator = _fields(locator, context, {"kind"})
    return locator


def validate_source_ref(
    value: Any,
    sources: dict[str, dict[str, Any]],
    context: str,
) -> dict[str, Any]:
    ref = _require_object(value, context)
    source_id = _identifier(ref.get("source_id"), f"{context}.source_id")
    if source_id not in sources:
        _fail(f"{context}.source_id", f"unknown source {source_id!r}")
    status_value = ref.get("locator_status")
    if status_value == "exact":
        ref = _fields(ref, context, {"source_id", "locator_status", "locator"})
        _validate_locator(ref["locator"], sources[source_id]["source_type"], f"{context}.locator")
    elif status_value == "incomplete":
        ref = _fields(ref, context, {"source_id", "locator_status", "reason"})
        _nonempty_string(ref["reason"], f"{context}.reason")
    else:
        _fail(f"{context}.locator_status", "must be exact or incomplete")
    return ref


def _validate_source_refs(
    value: Any,
    sources: dict[str, dict[str, Any]],
    context: str,
    *,
    nonempty: bool = False,
) -> list[dict[str, Any]]:
    refs = _require_list(value, context)
    if nonempty and not refs:
        _fail(context, "must contain at least one source reference")
    validated = [
        validate_source_ref(ref, sources, f"{context}[{index}]")
        for index, ref in enumerate(refs)
    ]
    fingerprints = [json.dumps(ref, sort_keys=True, ensure_ascii=False) for ref in validated]
    if len(set(fingerprints)) != len(fingerprints):
        _fail(context, "must not contain duplicate source references")
    return validated


def detect_exclusion_category(text: str) -> str | None:
    normalized = " ".join(text.split()).strip()
    if normalized.lower() in DECORATIVE_TEXT:
        return "decorative"
    welcome_label = normalized.rstrip(".!")
    if (
        welcome_label.casefold().startswith("welcome to ")
        and len(welcome_label.split()) <= 8
        and not re.search(r"[,;:?]", welcome_label)
    ):
        return "decorative"
    if re.search(r"\bSEAtS\b", normalized):
        return "seats_operation"
    for category, pattern in EXCLUSION_PATTERNS:
        if pattern.search(normalized):
            return category
    return None


def _validate_public_knowledge_text(node: dict[str, Any], context: str) -> None:
    parts = [
        str(node["title"]),
        str(node["explanation"]),
        *[str(item) for item in node["keywords"]],
        *[str(item) for item in node["aliases"]],
    ]
    for text in [*parts, " ".join(parts)]:
        category = detect_exclusion_category(text)
        if category:
            _fail(context, f"contains excluded {category} content; record it under audit.exclusions instead")


def _validate_node(
    value: Any,
    sources: dict[str, dict[str, Any]],
    context: str,
) -> dict[str, Any]:
    required = {
        "node_id",
        "node_type",
        "parent_id",
        "title",
        "explanation",
        "sequence_index",
        "keywords",
        "aliases",
        "source_refs",
        "relation_ids",
        "knowledge_status",
    }
    node = _fields(value, context, required)
    _identifier(node["node_id"], f"{context}.node_id")
    node_type = node["node_type"]
    if node_type not in NODE_TYPES:
        _fail(f"{context}.node_type", f"must be one of {sorted(NODE_TYPES)}")
    if node_type == "course":
        if node["parent_id"] is not None:
            _fail(f"{context}.parent_id", "course root must have null parent_id")
    else:
        _identifier(node["parent_id"], f"{context}.parent_id")
    _nonempty_string(node["title"], f"{context}.title")
    _nonempty_string(node["explanation"], f"{context}.explanation")
    _nonnegative_int(node["sequence_index"], f"{context}.sequence_index")
    _string_set(node["keywords"], f"{context}.keywords")
    _string_set(node["aliases"], f"{context}.aliases")
    refs = _validate_source_refs(
        node["source_refs"],
        sources,
        f"{context}.source_refs",
        nonempty=node_type in {"concept", "detail"},
    )
    _id_set(node["relation_ids"], f"{context}.relation_ids")
    status_value = node["knowledge_status"]
    if status_value not in KNOWLEDGE_STATUSES:
        _fail(f"{context}.knowledge_status", f"must be one of {sorted(KNOWLEDGE_STATUSES)}")
    if any(ref["locator_status"] == "incomplete" for ref in refs) and status_value != "incomplete":
        _fail(f"{context}.knowledge_status", "must be incomplete when any source locator is incomplete")
    _validate_public_knowledge_text(node, context)
    return node


def _validate_relation(
    value: Any,
    sources: dict[str, dict[str, Any]],
    context: str,
) -> dict[str, Any]:
    relation = _fields(
        value,
        context,
        {
            "relation_id",
            "source_node_id",
            "target_node_id",
            "relation_type",
            "label",
            "explanation",
            "source_refs",
        },
    )
    _identifier(relation["relation_id"], f"{context}.relation_id")
    source_node = _identifier(relation["source_node_id"], f"{context}.source_node_id")
    target_node = _identifier(relation["target_node_id"], f"{context}.target_node_id")
    if source_node == target_node:
        _fail(context, "relation endpoints must differ")
    if relation["relation_type"] not in RELATION_TYPES:
        _fail(f"{context}.relation_type", f"must be one of {sorted(RELATION_TYPES)}")
    _nonempty_string(relation["label"], f"{context}.label")
    _nonempty_string(relation["explanation"], f"{context}.explanation")
    _validate_source_refs(relation["source_refs"], sources, f"{context}.source_refs", nonempty=True)
    category = detect_exclusion_category(f"{relation['label']} {relation['explanation']}")
    if category:
        _fail(context, f"contains excluded {category} content")
    return relation


def _validate_hierarchy(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = node["node_id"]
        if node_id in by_id:
            _fail("nodes", f"duplicate node_id {node_id!r}")
        by_id[node_id] = node
    roots = [node for node in nodes if node["node_type"] == "course"]
    if len(roots) != 1:
        _fail("nodes", "must contain exactly one course root")
    required_types = {"theme", "concept"}
    if not required_types.issubset({node["node_type"] for node in nodes}):
        _fail("nodes", "must contain at least one theme and one concept")
    if not any(node["node_type"] in {"lecture", "module"} for node in nodes):
        _fail("nodes", "must contain at least one lecture or module")
    allowed_parent_types = {
        "theme": {"course"},
        "lecture": {"theme"},
        "module": {"theme"},
        "concept": {"lecture", "module"},
        "detail": {"concept"},
    }
    sibling_positions: set[tuple[str | None, int]] = set()
    for node in nodes:
        position = (node["parent_id"], node["sequence_index"])
        if position in sibling_positions:
            _fail("nodes", f"duplicate sibling sequence_index {node['sequence_index']} under {node['parent_id']!r}")
        sibling_positions.add(position)
        if node["node_type"] == "course":
            continue
        parent = by_id.get(node["parent_id"])
        if parent is None:
            _fail(f"node {node['node_id']}", f"unknown parent_id {node['parent_id']!r}")
        if parent["node_type"] not in allowed_parent_types[node["node_type"]]:
            _fail(
                f"node {node['node_id']}",
                f"{node['node_type']} cannot have parent type {parent['node_type']}",
            )
    return by_id


def _validate_past_paper_link(
    value: Any,
    sources: dict[str, dict[str, Any]],
    node_ids: set[str],
    context: str,
) -> dict[str, Any]:
    link = _fields(
        value,
        context,
        {"link_id", "paper_source_id", "question_label", "node_ids", "source_refs"},
    )
    _identifier(link["link_id"], f"{context}.link_id")
    paper_source_id = _identifier(link["paper_source_id"], f"{context}.paper_source_id")
    if paper_source_id not in sources:
        _fail(f"{context}.paper_source_id", f"unknown source {paper_source_id!r}")
    _nonempty_string(link["question_label"], f"{context}.question_label")
    linked_nodes = _id_set(link["node_ids"], f"{context}.node_ids", nonempty=True)
    unknown_nodes = sorted(set(linked_nodes) - node_ids)
    if unknown_nodes:
        _fail(f"{context}.node_ids", f"unknown nodes: {', '.join(unknown_nodes)}")
    refs = _validate_source_refs(link["source_refs"], sources, f"{context}.source_refs", nonempty=True)
    if paper_source_id not in {ref["source_id"] for ref in refs}:
        _fail(f"{context}.source_refs", "must include the declared paper_source_id")
    return link


def _validate_coverage_record(
    value: Any,
    source_ids: set[str],
    context: str,
) -> dict[str, Any]:
    record = _fields(
        value,
        context,
        {
            "source_id",
            "expected_points",
            "covered_points",
            "excluded_points",
            "unresolved_points",
            "status",
        },
    )
    source_id = _identifier(record["source_id"], f"{context}.source_id")
    if source_id not in source_ids:
        _fail(f"{context}.source_id", f"unknown source {source_id!r}")
    expected = _nonnegative_int(record["expected_points"], f"{context}.expected_points")
    covered = _nonnegative_int(record["covered_points"], f"{context}.covered_points")
    excluded = _nonnegative_int(record["excluded_points"], f"{context}.excluded_points")
    unresolved = _nonnegative_int(record["unresolved_points"], f"{context}.unresolved_points")
    if expected != covered + excluded + unresolved:
        _fail(context, "expected_points must equal covered_points + excluded_points + unresolved_points")
    status_value = record["status"]
    if status_value not in {"complete", "partial", "incomplete", "not_assessed"}:
        _fail(f"{context}.status", "invalid coverage status")
    expected_status = (
        "not_assessed"
        if expected == 0
        else "complete"
        if unresolved == 0
        else "partial"
        if covered + excluded > 0
        else "incomplete"
    )
    if status_value != expected_status:
        _fail(f"{context}.status", f"must be {expected_status!r} for the declared counts")
    return record


def _validate_exclusion_record(
    value: Any,
    sources: dict[str, dict[str, Any]],
    context: str,
) -> dict[str, Any]:
    record = _fields(
        value,
        context,
        {"exclusion_id", "category", "summary", "source_refs", "decision"},
        {"content_sha256"},
    )
    _identifier(record["exclusion_id"], f"{context}.exclusion_id")
    if record["category"] not in EXCLUSION_CATEGORIES:
        _fail(f"{context}.category", f"must be one of {sorted(EXCLUSION_CATEGORIES)}")
    _nonempty_string(record["summary"], f"{context}.summary")
    _validate_source_refs(record["source_refs"], sources, f"{context}.source_refs", nonempty=True)
    if record["decision"] != "excluded":
        _fail(f"{context}.decision", "must be 'excluded'")
    if "content_sha256" in record and (
        not isinstance(record["content_sha256"], str)
        or not SHA256_RE.fullmatch(record["content_sha256"])
    ):
        _fail(f"{context}.content_sha256", "must be a lowercase SHA-256 digest")
    return record


def _validate_manual_review_record(
    value: Any,
    sources: dict[str, dict[str, Any]],
    node_ids: set[str],
    context: str,
) -> dict[str, Any]:
    record = _fields(
        value,
        context,
        {"review_id", "issue_type", "status", "summary", "node_ids", "source_refs"},
    )
    _identifier(record["review_id"], f"{context}.review_id")
    if record["issue_type"] not in REVIEW_ISSUE_TYPES:
        _fail(f"{context}.issue_type", f"must be one of {sorted(REVIEW_ISSUE_TYPES)}")
    if record["status"] not in {"pending", "resolved"}:
        _fail(f"{context}.status", "must be pending or resolved")
    _nonempty_string(record["summary"], f"{context}.summary")
    review_nodes = _id_set(record["node_ids"], f"{context}.node_ids")
    unknown = sorted(set(review_nodes) - node_ids)
    if unknown:
        _fail(f"{context}.node_ids", f"unknown nodes: {', '.join(unknown)}")
    _validate_source_refs(record["source_refs"], sources, f"{context}.source_refs")
    if not review_nodes and not record["source_refs"]:
        _fail(context, "must identify at least one node or source reference")
    return record


def _source_ref_signature(ref: dict[str, Any]) -> str:
    return json.dumps(ref, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _refs_grouped_by_source(refs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for ref in refs:
        grouped.setdefault(ref["source_id"], []).append(ref)
    return grouped


def _unresolved_artifact_evidence(
    nodes: list[dict[str, Any]],
    relations: Iterable[dict[str, Any]],
    past_links: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
) -> tuple[set[str], set[str], list[tuple[str, str | None, str]]]:
    """Return incomplete nodes, unresolved ref signatures, and required review links."""

    incomplete_nodes = {
        node["node_id"]
        for node in nodes
        if node["knowledge_status"] != "complete"
    }
    unresolved_refs: set[str] = set()
    required_links: list[tuple[str, str | None, str]] = []
    for node in nodes:
        if node["node_id"] not in incomplete_nodes:
            continue
        for ref in node["source_refs"]:
            signature = _source_ref_signature(ref)
            unresolved_refs.add(signature)
            required_links.append((f"node {node['node_id']!r}", node["node_id"], signature))
        if not node["source_refs"]:
            required_links.append((f"node {node['node_id']!r}", node["node_id"], ""))
    for kind, records, id_field in (
        ("relation", relations, "relation_id"),
        ("past-paper link", past_links, "link_id"),
        ("exclusion", exclusions, "exclusion_id"),
    ):
        for record in records:
            for ref in record["source_refs"]:
                if ref["locator_status"] != "incomplete":
                    continue
                signature = _source_ref_signature(ref)
                unresolved_refs.add(signature)
                required_links.append((f"{kind} {record[id_field]!r}", None, signature))
    return incomplete_nodes, unresolved_refs, required_links


def _validate_pending_review_links(
    manual_review: list[dict[str, Any]],
    incomplete_nodes: set[str],
    unresolved_refs: set[str],
    required_links: list[tuple[str, str | None, str]],
) -> set[tuple[str, str]]:
    """Require pending review records to point to concrete unresolved evidence.

    The return value identifies standalone incomplete source references introduced
    by a pending review. Those records are real unresolved coverage units, while
    links to an already incomplete artifact are not counted twice.
    """

    pending_nodes: set[str] = set()
    pending_refs: set[str] = set()
    standalone: set[tuple[str, str]] = set()
    for record in manual_review:
        refs = record["source_refs"]
        if record["status"] == "resolved":
            if any(ref["locator_status"] == "incomplete" for ref in refs):
                _fail(
                    f"manual review {record['review_id']!r}",
                    "resolved records cannot retain incomplete source locators",
                )
            continue
        node_matches = set(record["node_ids"]) & incomplete_nodes
        ref_signatures = {_source_ref_signature(ref) for ref in refs}
        ref_matches = ref_signatures & unresolved_refs
        standalone_refs = [
            ref
            for ref in refs
            if ref["locator_status"] == "incomplete"
            and _source_ref_signature(ref) not in unresolved_refs
        ]
        unsupported_exact = [
            ref
            for ref in refs
            if ref["locator_status"] == "exact"
            and _source_ref_signature(ref) not in unresolved_refs
        ]
        if unsupported_exact:
            _fail(
                f"manual review {record['review_id']!r}",
                "pending exact source_refs must match a non-complete node or unresolved artifact",
            )
        if not node_matches and not ref_matches and not standalone_refs:
            _fail(
                f"manual review {record['review_id']!r}",
                "pending record must reference an actual non-complete node or incomplete source locator",
            )
        pending_nodes.update(node_matches)
        pending_refs.update(ref_signatures)
        standalone.update(
            (record["review_id"], ref["source_id"])
            for ref in standalone_refs
        )

    for owner, node_id, signature in required_links:
        if node_id is not None and node_id in pending_nodes:
            continue
        if signature and signature in pending_refs:
            continue
        _fail(
            "spec.audit.manual_review",
            f"requires a pending record linked to unresolved {owner}",
        )
    return standalone


def _derive_coverage_evidence(
    source_ids: set[str],
    nodes: list[dict[str, Any]],
    relations: Iterable[dict[str, Any]],
    past_links: list[dict[str, Any]],
    exclusions: list[dict[str, Any]],
    standalone_reviews: set[tuple[str, str]],
) -> dict[str, dict[str, list[str] | int]]:
    """Derive source coverage from concrete package artifacts.

    One artifact/source pair is one evidence unit. This avoids treating multiple
    locators on the same atomic node as multiple course points while still making
    every declared count traceable to a node, relation, link, exclusion, or
    standalone incomplete review record.
    """

    evidence: dict[str, dict[str, set[str]]] = {
        source_id: {"covered": set(), "excluded": set(), "unresolved": set()}
        for source_id in source_ids
    }

    def add_record(
        kind: str,
        record_id: str,
        refs: list[dict[str, Any]],
        exact_outcome: str,
        *,
        force_unresolved: bool = False,
    ) -> None:
        for source_id, source_refs in _refs_grouped_by_source(refs).items():
            outcome = (
                "unresolved"
                if force_unresolved
                or any(ref["locator_status"] == "incomplete" for ref in source_refs)
                else exact_outcome
            )
            evidence[source_id][outcome].add(f"{kind}:{record_id}")

    for node in nodes:
        add_record(
            "node",
            node["node_id"],
            node["source_refs"],
            "covered",
            force_unresolved=node["knowledge_status"] != "complete",
        )
    for relation in relations:
        add_record("relation", relation["relation_id"], relation["source_refs"], "covered")
    for link in past_links:
        add_record("past_paper_link", link["link_id"], link["source_refs"], "covered")
    for exclusion in exclusions:
        add_record("exclusion", exclusion["exclusion_id"], exclusion["source_refs"], "excluded")
    for review_id, source_id in standalone_reviews:
        evidence[source_id]["unresolved"].add(f"manual_review:{review_id}")

    derived: dict[str, dict[str, list[str] | int]] = {}
    for source_id, outcomes in evidence.items():
        covered_ids = sorted(outcomes["covered"])
        excluded_ids = sorted(outcomes["excluded"])
        unresolved_ids = sorted(outcomes["unresolved"])
        derived[source_id] = {
            "covered_points": len(covered_ids),
            "excluded_points": len(excluded_ids),
            "unresolved_points": len(unresolved_ids),
            "expected_points": len(covered_ids) + len(excluded_ids) + len(unresolved_ids),
            "covered_evidence": covered_ids,
            "excluded_evidence": excluded_ids,
            "unresolved_evidence": unresolved_ids,
        }
    return derived


def validate_build_spec(value: Any) -> dict[str, Any]:
    """Validate the normalized builder input and return indexed state."""

    spec = _fields(
        value,
        "spec",
        {
            "schema_version",
            "package_id",
            "course",
            "nodes",
            "relations",
            "sources",
            "past_paper_links",
            "audit",
        },
        {"generated_at"},
    )
    if spec["schema_version"] != SCHEMA_VERSION:
        _fail("spec.schema_version", f"must be {SCHEMA_VERSION!r}")
    _identifier(spec["package_id"], "spec.package_id")
    course = _validate_course(spec["course"], "spec.course")
    if "generated_at" in spec:
        _validate_datetime(spec["generated_at"], "spec.generated_at")

    source_values = _require_list(spec["sources"], "spec.sources")
    if not source_values:
        _fail("spec.sources", "must contain at least one source")
    sources: dict[str, dict[str, Any]] = {}
    for index, value_item in enumerate(source_values):
        source = _validate_source(value_item, f"spec.sources[{index}]")
        source_id = source["source_id"]
        if source_id in sources:
            _fail("spec.sources", f"duplicate source_id {source_id!r}")
        sources[source_id] = source

    node_values = _require_list(spec["nodes"], "spec.nodes")
    nodes = [
        _validate_node(item, sources, f"spec.nodes[{index}]")
        for index, item in enumerate(node_values)
    ]
    node_by_id = _validate_hierarchy(nodes)
    course_root = next(node for node in nodes if node["node_type"] == "course")
    if course_root["title"] != course["title"]:
        _fail("spec.course.title", "must match the course root node title")

    relation_values = _require_list(spec["relations"], "spec.relations")
    relations: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(relation_values):
        relation = _validate_relation(item, sources, f"spec.relations[{index}]")
        relation_id = relation["relation_id"]
        if relation_id in relations:
            _fail("spec.relations", f"duplicate relation_id {relation_id!r}")
        for endpoint in ("source_node_id", "target_node_id"):
            if relation[endpoint] not in node_by_id:
                _fail(f"spec.relations[{index}].{endpoint}", f"unknown node {relation[endpoint]!r}")
        relations[relation_id] = relation
    for node in nodes:
        for relation_id in node["relation_ids"]:
            relation = relations.get(relation_id)
            if relation is None:
                _fail(f"node {node['node_id']}.relation_ids", f"unknown relation {relation_id!r}")
            if node["node_id"] not in {relation["source_node_id"], relation["target_node_id"]}:
                _fail(f"node {node['node_id']}.relation_ids", f"relation {relation_id!r} does not connect this node")
    for relation in relations.values():
        for endpoint in (relation["source_node_id"], relation["target_node_id"]):
            if relation["relation_id"] not in node_by_id[endpoint]["relation_ids"]:
                _fail(
                    f"relation {relation['relation_id']}",
                    f"endpoint node {endpoint!r} does not list this relation_id",
                )

    past_links_list = _require_list(spec["past_paper_links"], "spec.past_paper_links")
    link_ids: set[str] = set()
    past_links: list[dict[str, Any]] = []
    for index, item in enumerate(past_links_list):
        link = _validate_past_paper_link(
            item,
            sources,
            set(node_by_id),
            f"spec.past_paper_links[{index}]",
        )
        if link["link_id"] in link_ids:
            _fail("spec.past_paper_links", f"duplicate link_id {link['link_id']!r}")
        link_ids.add(link["link_id"])
        past_links.append(link)

    audit = _fields(
        spec["audit"],
        "spec.audit",
        {"coverage_ledger", "exclusions", "manual_review"},
    )
    coverage_values = _require_list(audit["coverage_ledger"], "spec.audit.coverage_ledger")
    coverage: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(coverage_values):
        record = _validate_coverage_record(
            item,
            set(sources),
            f"spec.audit.coverage_ledger[{index}]",
        )
        if record["source_id"] in coverage:
            _fail("spec.audit.coverage_ledger", f"duplicate source_id {record['source_id']!r}")
        coverage[record["source_id"]] = record
    if set(coverage) != set(sources):
        missing = sorted(set(sources) - set(coverage))
        extra = sorted(set(coverage) - set(sources))
        _fail(
            "spec.audit.coverage_ledger",
            f"must contain exactly one record per source (missing={missing}, extra={extra})",
        )

    exclusion_values = _require_list(audit["exclusions"], "spec.audit.exclusions")
    exclusion_ids: set[str] = set()
    exclusions: list[dict[str, Any]] = []
    for index, item in enumerate(exclusion_values):
        record = _validate_exclusion_record(item, sources, f"spec.audit.exclusions[{index}]")
        if record["exclusion_id"] in exclusion_ids:
            _fail("spec.audit.exclusions", f"duplicate exclusion_id {record['exclusion_id']!r}")
        exclusion_ids.add(record["exclusion_id"])
        exclusions.append(record)

    manual_values = _require_list(audit["manual_review"], "spec.audit.manual_review")
    review_ids: set[str] = set()
    pending_count = 0
    manual_review: list[dict[str, Any]] = []
    for index, item in enumerate(manual_values):
        record = _validate_manual_review_record(
            item,
            sources,
            set(node_by_id),
            f"spec.audit.manual_review[{index}]",
        )
        if record["review_id"] in review_ids:
            _fail("spec.audit.manual_review", f"duplicate review_id {record['review_id']!r}")
        review_ids.add(record["review_id"])
        manual_review.append(record)
        if record["status"] == "pending":
            pending_count += 1

    incomplete_nodes, unresolved_refs, required_review_links = _unresolved_artifact_evidence(
        nodes,
        relations.values(),
        past_links,
        exclusions,
    )
    standalone_reviews = _validate_pending_review_links(
        manual_review,
        incomplete_nodes,
        unresolved_refs,
        required_review_links,
    )
    derived_coverage = _derive_coverage_evidence(
        set(sources),
        nodes,
        relations.values(),
        past_links,
        exclusions,
        standalone_reviews,
    )
    count_fields = (
        "expected_points",
        "covered_points",
        "excluded_points",
        "unresolved_points",
    )
    for source_id, record in coverage.items():
        derived = derived_coverage[source_id]
        mismatches = [
            f"{field}={record[field]} (derived {derived[field]})"
            for field in count_fields
            if record[field] != derived[field]
        ]
        if mismatches:
            _fail(
                f"spec.audit.coverage_ledger source {source_id!r}",
                "counts do not match derived artifact evidence: " + ", ".join(mismatches),
            )

    incomplete_locator = any(
        ref["locator_status"] == "incomplete"
        for node in nodes
        for ref in node["source_refs"]
    ) or any(
        ref["locator_status"] == "incomplete"
        for relation in relations.values()
        for ref in relation["source_refs"]
    ) or any(
        ref["locator_status"] == "incomplete"
        for link in past_links
        for ref in link["source_refs"]
    ) or any(
        ref["locator_status"] == "incomplete"
        for exclusion in exclusions
        for ref in exclusion["source_refs"]
    )
    substantive_gap = (
        incomplete_locator
        or any(node["knowledge_status"] != "complete" for node in nodes)
        or any(record["status"] != "complete" for record in coverage.values())
    )
    if substantive_gap and pending_count == 0:
        _fail(
            "spec.audit.manual_review",
            "requires a pending record when locators, knowledge, or coverage remain incomplete",
        )
    validate_schema_instance(spec)
    has_gaps = substantive_gap or pending_count > 0
    return {
        "spec": spec,
        "sources": sources,
        "nodes": nodes,
        "node_by_id": node_by_id,
        "relations": relations,
        "coverage": coverage,
        "derived_coverage": derived_coverage,
        "pending_count": pending_count,
        "has_gaps": has_gaps,
        "course_root_id": course_root["node_id"],
    }


def _safe_zip_name(name: str) -> None:
    if not name or "\\" in name or "\x00" in name:
        _fail("ZIP", f"unsafe member path {name!r}")
    pure = PurePosixPath(name)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        _fail("ZIP", f"unsafe member path {name!r}")


def _read_zip(path: Path) -> dict[str, bytes]:
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise AtlasValidationError(f"{path}: not a readable ZIP package")
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            name = info.filename
            _safe_zip_name(name)
            if name in seen:
                _fail("ZIP", f"duplicate member {name!r}")
            seen.add(name)
            if info.is_dir():
                _fail("ZIP", f"explicit directory entries are not permitted: {name!r}")
            if info.flag_bits & 0x1:
                _fail("ZIP", f"encrypted member is not permitted: {name!r}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode and stat.S_ISLNK(mode):
                _fail("ZIP", f"symbolic link is not permitted: {name!r}")
            suffix = PurePosixPath(name).suffix.lower()
            if suffix in RAW_SOURCE_SUFFIXES:
                _fail("ZIP", f"raw source member is forbidden: {name!r}")
            if name not in FIXED_PACKAGE_FILES and not MODULE_FILE_RE.fullmatch(name):
                _fail("ZIP", f"unexpected member {name!r}")
            try:
                files[name] = archive.read(info)
            except (RuntimeError, zipfile.BadZipFile) as exc:
                raise AtlasValidationError(f"ZIP: cannot read member {name!r}") from exc
    missing = sorted(FIXED_PACKAGE_FILES - set(files))
    if missing:
        _fail("ZIP", f"missing required members: {', '.join(missing)}")
    module_files = sorted(name for name in files if MODULE_FILE_RE.fullmatch(name))
    if module_files == ["modules/hierarchy.json"]:
        _fail("ZIP", "requires at least one lecture/module JSON file")
    return files


def _validate_checksums(files: dict[str, bytes]) -> None:
    try:
        checksum_text = files["checksums.sha256"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AtlasValidationError("checksums.sha256: is not UTF-8") from exc
    lines = checksum_text.splitlines()
    if not lines:
        _fail("checksums.sha256", "must not be empty")
    checksums: dict[str, str] = {}
    for index, line in enumerate(lines, 1):
        match = CHECKSUM_RE.fullmatch(line)
        if not match:
            _fail("checksums.sha256", f"invalid line {index}")
        member = match.group("path")
        _safe_zip_name(member)
        if member == "checksums.sha256":
            _fail("checksums.sha256", "must not checksum itself")
        if member in checksums:
            _fail("checksums.sha256", f"duplicate path {member!r}")
        checksums[member] = match.group("digest")
    expected_names = sorted(set(files) - {"checksums.sha256"})
    if list(checksums) != expected_names:
        _fail("checksums.sha256", "paths must exactly cover package members in sorted order")
    for member in expected_names:
        actual = hashlib.sha256(files[member]).hexdigest()
        if checksums[member] != actual:
            _fail("checksums.sha256", f"digest mismatch for {member!r}")


def _find_forbidden_public_key(value: Any, context: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_PUBLIC_KEYS:
                _fail(context, f"public data contains audit-only key {key!r}")
            _find_forbidden_public_key(child, context)
    elif isinstance(value, list):
        for child in value:
            _find_forbidden_public_key(child, context)


def _validate_wrapper(value: Any, context: str, list_key: str) -> list[Any]:
    wrapper = _fields(value, context, {"schema_version", list_key})
    if wrapper["schema_version"] != SCHEMA_VERSION:
        _fail(f"{context}.schema_version", f"must be {SCHEMA_VERSION!r}")
    return _require_list(wrapper[list_key], f"{context}.{list_key}")


def _unit_ancestor(node_id: str, by_id: dict[str, dict[str, Any]]) -> str | None:
    current = by_id[node_id]
    while current["node_type"] not in {"lecture", "module", "course"}:
        current = by_id[current["parent_id"]]
    if current["node_type"] in {"lecture", "module"}:
        return current["node_id"]
    return None


def _validate_manifest(
    value: Any,
    actual_module_files: list[str],
) -> dict[str, Any]:
    manifest = _fields(
        value,
        "course_manifest.json",
        {
            "schema_version",
            "artifact_type",
            "package_id",
            "generated_at",
            "node_id_scope",
            "course",
            "hierarchy",
            "module_files",
            "public_files",
            "audit_files",
            "counts",
            "qa_status",
        },
    )
    if manifest["schema_version"] != SCHEMA_VERSION:
        _fail("course_manifest.json.schema_version", f"must be {SCHEMA_VERSION!r}")
    if manifest["artifact_type"] != "course_atlas":
        _fail("course_manifest.json.artifact_type", "must be 'course_atlas'")
    _identifier(manifest["package_id"], "course_manifest.json.package_id")
    _validate_datetime(manifest["generated_at"], "course_manifest.json.generated_at")
    if manifest["node_id_scope"] != "package_local":
        _fail("course_manifest.json.node_id_scope", "must be 'package_local'")
    _validate_course(manifest["course"], "course_manifest.json.course")
    hierarchy = _fields(manifest["hierarchy"], "course_manifest.json.hierarchy", {"levels", "unit_types"})
    if hierarchy["levels"] != ["course", "theme", "lecture_or_module", "concept", "detail"]:
        _fail("course_manifest.json.hierarchy.levels", "does not declare the required hierarchy")
    if hierarchy["unit_types"] != ["lecture", "module"]:
        _fail("course_manifest.json.hierarchy.unit_types", "must be ['lecture', 'module']")
    module_files = _string_set(manifest["module_files"], "course_manifest.json.module_files")
    if module_files != actual_module_files:
        _fail("course_manifest.json.module_files", "must list every modules/*.json member in sorted order")
    expected_public = sorted(
        {
            "sources.json",
            "relations.json",
            "past_paper_links.json",
            "public/web_index.json",
            *actual_module_files,
        }
    )
    if manifest["public_files"] != expected_public:
        _fail("course_manifest.json.public_files", "does not match the public package members")
    expected_audit = [
        "audit/coverage_ledger.json",
        "audit/exclusions.json",
        "audit/manual_review.json",
    ]
    if manifest["audit_files"] != expected_audit:
        _fail("course_manifest.json.audit_files", "must list only the three audit members")
    _fields(
        manifest["counts"],
        "course_manifest.json.counts",
        {
            "sources",
            "nodes",
            "relations",
            "past_paper_links",
            "excluded_items",
            "pending_manual_review",
        },
    )
    for key, count in manifest["counts"].items():
        _nonnegative_int(count, f"course_manifest.json.counts.{key}")
    if manifest["qa_status"] not in {"pass", "pass_with_gaps"}:
        _fail("course_manifest.json.qa_status", "must be pass or pass_with_gaps")
    return manifest


def _validate_web_index(
    value: Any,
    state: dict[str, Any],
    node_file: dict[str, str],
    manifest: dict[str, Any],
) -> None:
    web = _fields(
        value,
        "public/web_index.json",
        {
            "schema_version",
            "package_id",
            "course_node_id",
            "node_id_scope",
            "relations_file",
            "nodes",
        },
    )
    if web["schema_version"] != SCHEMA_VERSION:
        _fail("public/web_index.json.schema_version", f"must be {SCHEMA_VERSION!r}")
    if web["package_id"] != manifest["package_id"]:
        _fail("public/web_index.json.package_id", "does not match course_manifest.json")
    if web["course_node_id"] != state["course_root_id"]:
        _fail("public/web_index.json.course_node_id", "does not identify the course root")
    if web["node_id_scope"] != "package_local":
        _fail("public/web_index.json.node_id_scope", "must be 'package_local'")
    if web["relations_file"] != "relations.json":
        _fail("public/web_index.json.relations_file", "must be 'relations.json'")
    entries = _require_list(web["nodes"], "public/web_index.json.nodes")
    by_entry: dict[str, dict[str, Any]] = {}
    entry_fields = {
        "node_id",
        "node_type",
        "parent_id",
        "title",
        "sequence_index",
        "keywords",
        "aliases",
        "knowledge_status",
        "module_file",
    }
    for index, value_item in enumerate(entries):
        entry = _fields(value_item, f"public/web_index.json.nodes[{index}]", entry_fields)
        node_id = _identifier(entry["node_id"], f"public/web_index.json.nodes[{index}].node_id")
        if node_id in by_entry:
            _fail("public/web_index.json.nodes", f"duplicate node_id {node_id!r}")
        node = state["node_by_id"].get(node_id)
        if node is None:
            _fail("public/web_index.json.nodes", f"unknown node_id {node_id!r}")
        for key in entry_fields - {"module_file"}:
            if entry[key] != node[key]:
                _fail(f"public/web_index.json.nodes[{index}].{key}", "does not match its module node")
        if entry["module_file"] != node_file[node_id]:
            _fail(f"public/web_index.json.nodes[{index}].module_file", "does not own this node")
        by_entry[node_id] = entry
    if set(by_entry) != set(state["node_by_id"]):
        _fail("public/web_index.json.nodes", "must contain exactly one compact entry per node")


def render_qa_report(package_id: str, qa_status: str, counts: dict[str, int]) -> bytes:
    """Render the only permitted aggregate QA report representation."""

    lines = [
        "# Course Atlas QA Report",
        "",
        f"Package: {package_id}",
        f"QA status: {qa_status}",
        "",
        "## Aggregate checks",
        "",
        f"- Sources catalogued: {counts['sources']}",
        f"- Nodes validated: {counts['nodes']}",
        f"- Relations validated: {counts['relations']}",
        f"- Past-paper links validated: {counts['past_paper_links']}",
        f"- Excluded items recorded: {counts['excluded_items']}",
        f"- Pending manual-review items: {counts['pending_manual_review']}",
        "- Node identifier scope: package_local",
        "- Original source files included: no",
        "- Public and audit records: separated",
        "- Member checksums: generated for validator verification",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def validate_package(path: str | Path) -> dict[str, Any]:
    """Validate an Atlas ZIP and return an evidence-based summary."""

    validate_schema_documents()
    package_path = Path(path)
    files = _read_zip(package_path)
    _validate_checksums(files)

    json_names = sorted(name for name in files if name.endswith(".json"))
    parsed = {name: load_json_bytes(files[name], name) for name in json_names}
    for name in sorted(PUBLIC_JSON_FILES | {n for n in files if MODULE_FILE_RE.fullmatch(n)}):
        _find_forbidden_public_key(parsed[name], name)

    actual_module_files = sorted(name for name in files if MODULE_FILE_RE.fullmatch(name))
    manifest = _validate_manifest(parsed["course_manifest.json"], actual_module_files)
    sources = _validate_wrapper(parsed["sources.json"], "sources.json", "sources")
    relations = _validate_wrapper(parsed["relations.json"], "relations.json", "relations")
    past_links = _validate_wrapper(parsed["past_paper_links.json"], "past_paper_links.json", "links")
    coverage = _validate_wrapper(
        parsed["audit/coverage_ledger.json"],
        "audit/coverage_ledger.json",
        "records",
    )
    exclusions = _validate_wrapper(
        parsed["audit/exclusions.json"],
        "audit/exclusions.json",
        "records",
    )
    manual_review = _validate_wrapper(
        parsed["audit/manual_review.json"],
        "audit/manual_review.json",
        "records",
    )

    all_nodes: list[dict[str, Any]] = []
    node_file: dict[str, str] = {}
    hierarchy = _fields(
        parsed["modules/hierarchy.json"],
        "modules/hierarchy.json",
        {"schema_version", "scope", "nodes"},
    )
    if hierarchy["schema_version"] != SCHEMA_VERSION or hierarchy["scope"] != "course_and_themes":
        _fail("modules/hierarchy.json", "has the wrong schema_version or scope")
    hierarchy_nodes = _require_list(hierarchy["nodes"], "modules/hierarchy.json.nodes")
    for node in hierarchy_nodes:
        if not isinstance(node, dict) or node.get("node_type") not in {"course", "theme"}:
            _fail("modules/hierarchy.json.nodes", "may contain only course and theme nodes")
        node_id = node.get("node_id")
        if node_id in node_file:
            _fail("modules", f"node {node_id!r} appears more than once")
        node_file[node_id] = "modules/hierarchy.json"
        all_nodes.append(node)

    module_root_to_file: dict[str, str] = {}
    for name in actual_module_files:
        if name == "modules/hierarchy.json":
            continue
        document = _fields(parsed[name], name, {"schema_version", "module_id", "nodes"})
        if document["schema_version"] != SCHEMA_VERSION:
            _fail(f"{name}.schema_version", f"must be {SCHEMA_VERSION!r}")
        module_id = _identifier(document["module_id"], f"{name}.module_id")
        if module_id in module_root_to_file:
            _fail("modules", f"module {module_id!r} has more than one file")
        module_nodes = _require_list(document["nodes"], f"{name}.nodes")
        if not module_nodes or not isinstance(module_nodes[0], dict) or module_nodes[0].get("node_id") != module_id:
            _fail(name, "first node must be the declared module_id")
        if module_nodes[0].get("node_type") not in {"lecture", "module"}:
            _fail(name, "module root must have node_type lecture or module")
        module_root_to_file[module_id] = name
        for node in module_nodes:
            if not isinstance(node, dict) or node.get("node_type") not in {"lecture", "module", "concept", "detail"}:
                _fail(f"{name}.nodes", "contains a node type that does not belong in a module file")
            node_id = node.get("node_id")
            if node_id in node_file:
                _fail("modules", f"node {node_id!r} appears more than once")
            node_file[node_id] = name
            all_nodes.append(node)

    reconstructed_spec = {
        "schema_version": SCHEMA_VERSION,
        "package_id": manifest["package_id"],
        "generated_at": manifest["generated_at"],
        "course": manifest["course"],
        "nodes": all_nodes,
        "relations": relations,
        "sources": sources,
        "past_paper_links": past_links,
        "audit": {
            "coverage_ledger": coverage,
            "exclusions": exclusions,
            "manual_review": manual_review,
        },
    }
    state = validate_build_spec(reconstructed_spec)
    expected_module_roots = {
        node["node_id"]
        for node in state["nodes"]
        if node["node_type"] in {"lecture", "module"}
    }
    if set(module_root_to_file) != expected_module_roots:
        _fail("modules", "must contain exactly one file per lecture/module node")
    for node in state["nodes"]:
        owner = node_file[node["node_id"]]
        if node["node_type"] in {"course", "theme"}:
            if owner != "modules/hierarchy.json":
                _fail("modules", f"hierarchy node {node['node_id']!r} is in the wrong file")
        else:
            expected_root = (
                node["node_id"]
                if node["node_type"] in {"lecture", "module"}
                else _unit_ancestor(node["node_id"], state["node_by_id"])
            )
            if module_root_to_file.get(expected_root) != owner:
                _fail("modules", f"node {node['node_id']!r} is not stored with its lecture/module ancestor")

    _validate_web_index(parsed["public/web_index.json"], state, node_file, manifest)
    expected_status = "pass_with_gaps" if state["has_gaps"] else "pass"
    if manifest["qa_status"] != expected_status:
        _fail("course_manifest.json.qa_status", f"must be {expected_status!r}")
    expected_counts = {
        "sources": len(sources),
        "nodes": len(all_nodes),
        "relations": len(relations),
        "past_paper_links": len(past_links),
        "excluded_items": len(exclusions),
        "pending_manual_review": state["pending_count"],
    }
    if manifest["counts"] != expected_counts:
        _fail("course_manifest.json.counts", "does not match package contents")
    expected_report = render_qa_report(manifest["package_id"], expected_status, expected_counts)
    if files["qa_report.md"] != expected_report:
        _fail("qa_report.md", "must contain only the generated aggregate QA report")

    return {
        "status": "ok",
        "package": str(package_path),
        "package_id": manifest["package_id"],
        "qa_status": expected_status,
        "node_count": len(all_nodes),
        "relation_count": len(relations),
        "source_count": len(sources),
        "pending_manual_review": state["pending_count"],
        "sha256": hashlib.sha256(package_path.read_bytes()).hexdigest(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate hierarchy, provenance, separation, members, and checksums in a Course Atlas ZIP."
    )
    parser.add_argument("package", help="Course Atlas ZIP to validate")
    args = parser.parse_args(argv)
    try:
        result = validate_package(args.package)
    except (AtlasValidationError, OSError, zipfile.BadZipFile) as exc:
        print(f"Course Atlas validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
