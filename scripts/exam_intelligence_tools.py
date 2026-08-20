#!/usr/bin/env python3
"""Build and validate evidence-safe exam-intelligence JSON packages.

The module deliberately keeps formal recurrence separate from auxiliary
question exposure. It uses only the Python standard library; ``jsonschema`` is
used as an additional validator when it is already available.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1.0"
SOURCE_ROLES = (
    "formal_past_paper",
    "official_mock_specimen",
    "practice_worksheet",
    "lecture_material",
    "mark_scheme",
)
FORMAL_ROLE = "formal_past_paper"
AUXILIARY_ROLES = frozenset({"official_mock_specimen", "practice_worksheet"})
OCCURRENCE_ROLES = frozenset({FORMAL_ROLE, *AUXILIARY_ROLES})
QUESTION_FORMATS = (
    "mcq",
    "short_answer",
    "long_answer",
    "calculation",
    "data_interpretation",
    "essay",
    "other",
)
METRIC_NAMES = (
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
)

METRIC_DEFINITIONS = {
    "formal_occurrence_count": "Question occurrences from formal_past_paper records only.",
    "distinct_formal_years": "Distinct explicit years represented by the family's formal records.",
    "formal_year_coverage": "Family formal years divided by all dated formal years in the corpus.",
    "auxiliary_occurrence_count": "Occurrences from official mocks/specimens and practice worksheets only.",
    "format_diversity": "Distinct formats among formal and auxiliary question occurrences.",
    "explicit_mark_exposure": "Sum of explicitly evidenced marks for formal and auxiliary occurrences; missing marks are not inferred.",
    "retention": "Coverage from the family's first formal year through the newest corpus year, reported only when persistence can be observed.",
    "cross_year_stability": "Evenness of annual formal occurrence counts across the dated formal corpus, using one minus relative mean absolute deviation.",
    "mapping_coverage": "Resolved formal and auxiliary mappings divided by all formal and auxiliary occurrences.",
    "unresolved_mapping_count": "Formal and auxiliary occurrences without a supported course mapping.",
}

LIMITATIONS = [
    "Formal recurrence is calculated only from formal_past_paper records.",
    "Official mocks, specimen papers, and practice worksheets are auxiliary and do not add a formal examination year.",
    "Occurrence and explicit-mark metrics do not establish official assessment weighting or determine a future question.",
]

ROLE_ALIASES = {
    "formal past paper": "formal_past_paper",
    "formal_past_papers": "formal_past_paper",
    "past paper": "formal_past_paper",
    "official mock": "official_mock_specimen",
    "official specimen": "official_mock_specimen",
    "official mock or specimen": "official_mock_specimen",
    "official_mock_or_specimen": "official_mock_specimen",
    "practice worksheet": "practice_worksheet",
    "practice material": "practice_worksheet",
    "lecture material": "lecture_material",
    "course material": "lecture_material",
    "mark scheme": "mark_scheme",
    "answer key": "mark_scheme",
}

QUESTION_START = re.compile(
    r"^\s*(?:q(?:uestion)?\s*\d+[.:)]?|\d+[.)]|\([a-z]\)|[a-z][.)])\s+",
    re.IGNORECASE,
)
MARK_PATTERN = re.compile(r"(?:\[|\()?\s*(\d+(?:\.\d+)?)\s*marks?\s*(?:\]|\))?", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
STOPWORDS = {
    "about", "answer", "calculate", "compare", "define", "describe", "discuss",
    "evaluate", "explain", "following", "from", "give", "identify", "list",
    "marks", "outline", "question", "state", "that", "their", "these", "this",
    "using", "what", "when", "where", "which", "with",
}
ASSERTIVE_PREDICTION = re.compile(
    r"\b(?:will|must|guaranteed\s+to|certain\s+to|certainly)\s+"
    r"(?:appear|be\s+(?:asked|examined|tested)|come\s+up)\b",
    re.IGNORECASE,
)
FAMILY_FUTURE_PREDICTION = re.compile(
    r"\b(?:(?:will|must|guaranteed(?:\s+to)?|certain(?:ly|\s+to)?|sure\s+to|"
    r"expected\s+to|predicted\s+to|likely\s+to|anticipated\s+to)\s+"
    r"(?:appear|be\s+(?:asked|examined|tested)|come\s+up)|"
    r"(?:expected|predicted|likely|probable|guaranteed|certain)\s+"
    r"(?:(?:future|next|upcoming)\s+)?(?:(?:exam(?:ination)?|paper)\s+)?question)\b",
    re.IGNORECASE,
)
FAMILY_WEIGHTING_CLAIM = re.compile(
    r"\b(?:(?:official|confirmed|actual)\s+"
    r"(?:(?:assessment|exam(?:ination)?|module|course)\s+)?weight(?:ing|ed)?\s*"
    r"(?:is|=|:|of|at)?\s*(?:\d+(?:\.\d+)?\s*%|high|medium|low)|"
    r"(?:assessment|exam(?:ination)?|module|course)\s+weight(?:ing|ed)?\s*"
    r"(?:is|=|:|of|at)\s*\d+(?:\.\d+)?\s*%|"
    r"(?:worth|accounts?\s+for|weighted\s+at|carries)\s+\d+(?:\.\d+)?\s*%\s+"
    r"(?:of\s+)?(?:the\s+)?(?:official\s+)?(?:assessment|exam(?:ination)?|module|course))",
    re.IGNORECASE,
)
FAMILY_WEIGHTING_TERM = re.compile(
    r"\b(?:weight(?:ing|ed)?|worth|accounts?\s+for|carries|constitutes|represents|makes?\s+up)\b",
    re.IGNORECASE,
)
FAMILY_ASSESSMENT_CONTEXT = re.compile(
    r"(?:\b(?:official|assessment|exam(?:ination)?|paper|module|course)\b|\d+(?:\.\d+)?\s*%)",
    re.IGNORECASE,
)
FAMILY_EXPECTATION_CUE = re.compile(
    r"\b(?:expected|predicted|likely|probable|anticipated|guaranteed|certain|certainty|sure)\b",
    re.IGNORECASE,
)
FAMILY_FUTURE_CONTEXT = re.compile(
    r"\b(?:future|next|upcoming|exam(?:ination)?|paper|question|topic|appear|asked|tested|"
    r"examined|come\s+up|recur|return|include|included)\b",
    re.IGNORECASE,
)
FORBIDDEN_FIELD = re.compile(
    r"(?:assessment_?weight|predicted_?question|prediction_?probability|"
    r"future_?probability|likelihood|overall_?score|composite_?score)",
    re.IGNORECASE,
)
ALLOWED_GUARDRAIL_FIELDS = {
    "weighting_inference_allowed",
    "certain_prediction_allowed",
    "composite_score_produced",
}


class ExamIntelligenceError(ValueError):
    """Raised when an input or package violates an evidence boundary."""


def _clean_string(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _unique_strings(values: Any) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, Sequence):
        raise ExamIntelligenceError("Expected a string or list of strings")
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = _clean_string(value)
        if clean and clean not in seen:
            result.append(clean)
            seen.add(clean)
    return result


def _normalise_role(value: Any) -> str:
    clean = _clean_string(value).lower().replace("-", "_")
    if clean in SOURCE_ROLES:
        return clean
    alias_key = clean.replace("_", " ")
    role = ROLE_ALIASES.get(clean) or ROLE_ALIASES.get(alias_key)
    if role:
        return role
    raise ExamIntelligenceError(
        f"Unknown source_role {value!r}; expected one of {', '.join(SOURCE_ROLES)}"
    )


def _normalise_year(value: Any) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ExamIntelligenceError("formal_year must be an explicit four-digit year or null")
    if isinstance(value, str) and not re.fullmatch(r"\d{4}", value.strip()):
        raise ExamIntelligenceError("formal_year must be an explicit four-digit year or null")
    try:
        year = int(value)
    except (TypeError, ValueError) as exc:
        raise ExamIntelligenceError("formal_year must be an explicit four-digit year or null") from exc
    if not 1900 <= year <= 2200:
        raise ExamIntelligenceError("formal_year must be between 1900 and 2200")
    return year


def _explicit_year_from_name(*values: Any) -> int | None:
    """Return a year only when a filename/label contains one unambiguous year."""

    years: set[int] = set()
    for value in values:
        for match in re.finditer(r"(?<!\d)((?:19|20|21)\d{2}|2200)(?!\d)", str(value or "")):
            years.add(int(match.group(1)))
    return next(iter(years)) if len(years) == 1 else None


def _normalise_marks(value: Any) -> int | float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ExamIntelligenceError("explicit_marks must be a positive number or null")
    try:
        marks = float(value)
    except (TypeError, ValueError) as exc:
        raise ExamIntelligenceError("explicit_marks must be a positive number or null") from exc
    if not math.isfinite(marks) or marks <= 0:
        raise ExamIntelligenceError("explicit_marks must be a positive number or null")
    return int(marks) if marks.is_integer() else marks


def _explicit_marks_from_text(text: str) -> int | float | None:
    match = MARK_PATTERN.search(text)
    return _normalise_marks(match.group(1)) if match else None


def infer_question_format(text: str, explicit_marks: int | float | None = None) -> str:
    """Return a conservative format label from explicit wording."""

    lower = text.lower()
    if re.search(r"\bwhich of the following\b|\bsingle best\b|\btrue\s*/\s*false\b", lower):
        return "mcq"
    if re.search(r"\bcalculate\b|\bderive\b|\bestimate\b|\bcompute\b", lower):
        return "calculation"
    if re.search(r"\b(?:graph|table|dataset|data)\b.*\b(?:interpret|analyse|analyze)\b", lower):
        return "data_interpretation"
    if re.search(r"\bessay\b|\bto what extent\b", lower):
        return "essay"
    if explicit_marks is not None and explicit_marks >= 15 and re.search(
        r"\b(?:discuss|evaluate|explain|compare|critically)\b", lower
    ):
        return "long_answer"
    if re.search(r"\b(?:define|state|list|name|outline)\b", lower):
        return "short_answer"
    if re.search(r"\b(?:discuss|evaluate|explain|compare|justify|critically)\b", lower):
        return "long_answer"
    return "other"


def _normalise_source(raw: Mapping[str, Any], index: int) -> dict[str, Any]:
    source_id = _clean_string(raw.get("source_id") or raw.get("id") or f"source-{index:03d}")
    source_name = _clean_string(
        raw.get("source_name") or raw.get("name") or raw.get("filename") or source_id
    )
    if not source_id or not source_name:
        raise ExamIntelligenceError("Each source needs a non-empty source_id and source_name")
    role = _normalise_role(raw.get("source_role") or raw.get("role"))
    year = _normalise_year(raw.get("formal_year", raw.get("year")))
    if role != FORMAL_ROLE:
        year = None
    supplied_locator = raw.get("source_locator", raw.get("locator"))
    locator = _clean_string(supplied_locator or source_name)
    locator_status = _clean_string(raw.get("locator_status")).lower()
    if locator_status not in {"complete", "incomplete"}:
        locator_status = "complete" if supplied_locator else "incomplete"
    return {
        "source_id": source_id,
        "source_name": source_name,
        "source_role": role,
        "formal_year": year,
        "source_locator": locator,
        "locator_status": locator_status,
    }


def _normalise_mapping(raw: Any) -> dict[str, Any]:
    mapping = raw if isinstance(raw, Mapping) else {}
    requested_status = _clean_string(mapping.get("status") or mapping.get("mapping_status")).lower()
    lecture_id = _clean_string(mapping.get("lecture_id")) or None
    unit_id = _clean_string(mapping.get("unit_id")) or None
    concept_ids = _unique_strings(mapping.get("concept_ids"))
    evidence = _unique_strings(mapping.get("evidence") or mapping.get("source_refs"))
    has_target = bool(lecture_id or unit_id or concept_ids)
    if requested_status == "resolved" and has_target and evidence:
        return {
            "status": "resolved",
            "lecture_id": lecture_id,
            "unit_id": unit_id,
            "concept_ids": concept_ids,
            "evidence": evidence,
            "unresolved_reason": None,
        }
    reason = _clean_string(mapping.get("unresolved_reason"))
    if not reason:
        if requested_status == "resolved" and not has_target:
            reason = "Resolved status was supplied without a lecture, unit, or concept target."
        elif requested_status == "resolved" and not evidence:
            reason = "Resolved status was supplied without explicit mapping evidence."
        elif has_target:
            reason = "A candidate target was supplied without an explicit supported resolved status."
        else:
            reason = "No explicit course mapping was supplied."
    return {
        "status": "unresolved",
        "lecture_id": None,
        "unit_id": None,
        "concept_ids": [],
        "evidence": evidence,
        "unresolved_reason": reason,
    }


def _normalise_question(
    raw: Mapping[str, Any],
    index: int,
    sources_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    question_id = _clean_string(raw.get("question_id") or raw.get("record_id") or f"question-{index:04d}")
    source_id = _clean_string(raw.get("source_id"))
    if source_id not in sources_by_id:
        raise ExamIntelligenceError(f"Question {question_id!r} references unknown source_id {source_id!r}")
    source = sources_by_id[source_id]
    if raw.get("source_role") is not None:
        supplied_role = _normalise_role(raw.get("source_role"))
        if supplied_role != source["source_role"]:
            raise ExamIntelligenceError(
                f"Question {question_id!r} source_role conflicts with source {source_id!r}"
            )
    question_text = _clean_string(raw.get("question_text") or raw.get("question") or raw.get("text"))
    if not question_text:
        raise ExamIntelligenceError(f"Question {question_id!r} has no question_text")
    supplied_locator = raw.get("source_locator", raw.get("locator"))
    locator = _clean_string(supplied_locator or source["source_locator"])
    locator_status = _clean_string(raw.get("locator_status")).lower()
    if locator_status not in {"complete", "incomplete"}:
        locator_status = "complete" if supplied_locator else source["locator_status"]
    role = str(source["source_role"])
    source_year = source["formal_year"] if role == FORMAL_ROLE else None
    if "formal_year" in raw:
        supplied_year = _normalise_year(raw.get("formal_year"))
        if supplied_year != source_year:
            raise ExamIntelligenceError(
                f"Question {question_id!r} formal_year must match its owning source "
                f"{source_id!r} ({source_year!r})"
            )
    year = source_year
    marks = _normalise_marks(raw.get("explicit_marks", raw.get("marks")))
    if marks is None:
        marks = _explicit_marks_from_text(question_text)
    question_format = _clean_string(raw.get("question_format") or raw.get("format")).lower()
    if question_format not in QUESTION_FORMATS:
        question_format = infer_question_format(question_text, marks)
    family_id = _clean_string(raw.get("family_id")) or None
    mapping_input: dict[str, Any]
    if isinstance(raw.get("mapping"), Mapping):
        mapping_input = dict(raw["mapping"])
    else:
        mapping_input = {
            key: raw.get(key)
            for key in (
                "mapping_status", "lecture_id", "unit_id", "concept_ids",
                "mapping_evidence", "unresolved_reason",
            )
            if key in raw
        }
        if "mapping_evidence" in mapping_input:
            mapping_input["evidence"] = mapping_input.pop("mapping_evidence")
    return {
        "question_id": question_id,
        "source_id": source_id,
        "source_name": str(source["source_name"]),
        "source_role": role,
        "source_locator": locator,
        "locator_status": locator_status,
        "formal_year": year,
        "question_text": question_text,
        "question_format": question_format,
        "explicit_marks": marks,
        "family_id": family_id,
        "mapping": _normalise_mapping(mapping_input),
    }


def extract_question_records(sources: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Extract conservative line-level question records from source text fields.

    Only formal, mock/specimen, and worksheet sources are extracted. Lecture
    material and mark schemes remain mapping/evaluation evidence and therefore
    cannot accidentally add occurrences.
    """

    normalised_sources = [_normalise_source(source, index) for index, source in enumerate(sources, 1)]
    by_id = {source["source_id"]: source for source in normalised_sources}
    records: list[dict[str, Any]] = []
    next_id = 1
    for raw, source in zip(sources, normalised_sources):
        if source["source_role"] not in OCCURRENCE_ROLES:
            continue
        text = str(raw.get("text") or raw.get("content") or "")
        for line_number, line in enumerate(text.splitlines(), 1):
            clean = _clean_string(line)
            if not clean or ("?" not in clean and not QUESTION_START.match(clean)):
                continue
            locator = f"{source['source_locator']}; line {line_number}"
            record = _normalise_question(
                {
                    "question_id": f"question-{next_id:04d}",
                    "source_id": source["source_id"],
                    "source_locator": locator,
                    "locator_status": source["locator_status"],
                    "question_text": clean,
                },
                next_id,
                by_id,
            )
            records.append(record)
            next_id += 1
    return records


def source_scan_to_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Adapt the repository's shared source-processor result for this builder.

    ``payload`` may be a scan itself or the outer object returned by
    ``extract_sources.py``. Raw fragment text is used only to derive audit
    question records; lecture and mark-scheme fragments never become
    occurrences.
    """

    scan_value = payload.get("scan") if isinstance(payload.get("scan"), Mapping) else payload
    if not isinstance(scan_value, Mapping):
        raise ExamIntelligenceError("Source-processor payload has no scan object")
    documents = scan_value.get("documents")
    fragments = scan_value.get("fragments")
    if not isinstance(documents, list) or not isinstance(fragments, list):
        raise ExamIntelligenceError("Source scan requires documents and fragments lists")

    sources: list[dict[str, Any]] = []
    documents_by_id: dict[str, Mapping[str, Any]] = {}
    for index, document in enumerate(documents, 1):
        if not isinstance(document, Mapping):
            raise ExamIntelligenceError("Each source-scan document must be an object")
        source_id = _clean_string(document.get("source_id") or document.get("id") or f"source-{index:03d}")
        source_name = _clean_string(document.get("source_name") or document.get("name") or source_id)
        role_value = (
            document.get("declared_source_role")
            or document.get("exam_source_role")
            or document.get("source_role")
        )
        role = _normalise_role(role_value)
        formal_year = document.get("formal_year")
        if formal_year in (None, "") and role == FORMAL_ROLE:
            formal_year = _explicit_year_from_name(source_name, document.get("path"))
        source_locator = _clean_string(document.get("path") or document.get("source_locator") or source_name)
        locator_status = _clean_string(document.get("locator_status")).lower()
        if locator_status not in {"complete", "incomplete"}:
            locator_status = "complete" if document.get("path") else "incomplete"
        sources.append(
            {
                "source_id": source_id,
                "source_name": source_name,
                "source_role": role,
                "formal_year": formal_year,
                "source_locator": source_locator,
                "locator_status": locator_status,
            }
        )
        documents_by_id[source_id] = document

    normalised_sources = [_normalise_source(source, index) for index, source in enumerate(sources, 1)]
    sources_by_id = {source["source_id"]: source for source in normalised_sources}
    questions: list[dict[str, Any]] = []
    question_index = 0
    for fragment_index, fragment in enumerate(fragments, 1):
        if not isinstance(fragment, Mapping):
            continue
        source_id = _clean_string(fragment.get("source_id"))
        source = sources_by_id.get(source_id)
        if source is None or source["source_role"] not in OCCURRENCE_ROLES:
            continue
        text = str(fragment.get("text") or "")
        locator_value = fragment.get("locator")
        provenance = fragment.get("provenance")
        if not locator_value and isinstance(provenance, Mapping):
            locator_value = provenance.get("locator")
        base_locator = _clean_string(locator_value or source["source_locator"])
        fragment_id = _clean_string(fragment.get("id") or f"fragment-{fragment_index:04d}")
        for line_number, line in enumerate(text.splitlines(), 1):
            clean = _clean_string(line)
            if not clean or ("?" not in clean and not QUESTION_START.match(clean)):
                continue
            question_index += 1
            mapping = fragment.get("mapping") if isinstance(fragment.get("mapping"), Mapping) else None
            raw_question: dict[str, Any] = {
                "question_id": f"{fragment_id}-q{line_number}",
                "source_id": source_id,
                "source_locator": f"{base_locator}; line {line_number}",
                "locator_status": fragment.get("locator_status") or ("complete" if locator_value else "incomplete"),
                "question_text": clean,
                "family_id": fragment.get("family_id"),
            }
            if mapping is not None:
                raw_question["mapping"] = mapping
            questions.append(_normalise_question(raw_question, question_index, sources_by_id))

    adapted: dict[str, Any] = {
        "course_id": payload.get("course_id"),
        "course_title": payload.get("course_title"),
        "sources": normalised_sources,
        "questions": questions,
    }
    for key in ("families", "allow_heuristic_clustering"):
        if key in payload:
            adapted[key] = payload[key]
    return adapted


def _slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return clean[:48] or "family"


def _question_tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in TOKEN_PATTERN.findall(text)
        if token.lower() not in STOPWORDS and len(token) >= 4
    }


def _similarity_clusters(records: Sequence[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Greedily group only strong lexical matches; every cluster needs review."""

    clusters: list[list[dict[str, Any]]] = []
    signatures: list[set[str]] = []
    for record in sorted(records, key=lambda item: item["question_id"]):
        tokens = _question_tokens(record["question_text"])
        chosen: int | None = None
        chosen_score = 0.0
        for index, signature in enumerate(signatures):
            shared = tokens & signature
            union = tokens | signature
            score = len(shared) / len(union) if union else 0.0
            if len(shared) >= 2 and score >= 0.6 and score > chosen_score:
                chosen = index
                chosen_score = score
        if chosen is None:
            clusters.append([record])
            signatures.append(set(tokens))
        else:
            clusters[chosen].append(record)
            signatures[chosen] |= tokens
    return clusters


def cluster_question_families(
    question_records: list[dict[str, Any]],
    declared_families: Sequence[Mapping[str, Any]] | None = None,
    *,
    allow_heuristic_clustering: bool = False,
) -> list[dict[str, Any]]:
    """Assign each question to one auditable family.

    Explicit family declarations win, followed by explicit concept mappings.
    Unmapped questions remain singleton families unless the caller explicitly
    enables transparent, manual-review lexical clustering.
    """

    declared_families = declared_families or []
    records_by_id = {record["question_id"]: record for record in question_records}
    memberships: dict[str, dict[str, Any]] = {}
    owner: dict[str, str] = {}

    for index, raw in enumerate(declared_families, 1):
        family_id = _clean_string(raw.get("family_id") or raw.get("id") or f"family-{index:03d}")
        title = _clean_string(raw.get("title") or raw.get("label") or family_id)
        description = _clean_string(raw.get("description"))
        member_ids = _unique_strings(raw.get("member_question_ids") or raw.get("question_ids"))
        if family_id in memberships:
            raise ExamIntelligenceError(f"Duplicate family_id {family_id!r}")
        memberships[family_id] = {
            "family_id": family_id,
            "title": title,
            "description": description,
            "member_question_ids": [],
            "clustering_method": "explicit_family",
            "manual_review_required": bool(raw.get("manual_review_required", False)),
        }
        for question_id in member_ids:
            if question_id not in records_by_id:
                raise ExamIntelligenceError(
                    f"Family {family_id!r} references unknown question_id {question_id!r}"
                )
            if question_id in owner and owner[question_id] != family_id:
                raise ExamIntelligenceError(f"Question {question_id!r} belongs to multiple families")
            owner[question_id] = family_id
            memberships[family_id]["member_question_ids"].append(question_id)

    for record in question_records:
        family_id = record.get("family_id")
        if not family_id:
            continue
        family_id = str(family_id)
        if record["question_id"] in owner and owner[record["question_id"]] != family_id:
            raise ExamIntelligenceError(
                f"Question {record['question_id']!r} has conflicting family assignments"
            )
        if family_id not in memberships:
            memberships[family_id] = {
                "family_id": family_id,
                "title": family_id.replace("_", " ").replace("-", " ").strip().title(),
                "description": "",
                "member_question_ids": [],
                "clustering_method": "explicit_family",
                "manual_review_required": False,
            }
        if record["question_id"] not in memberships[family_id]["member_question_ids"]:
            memberships[family_id]["member_question_ids"].append(record["question_id"])
        owner[record["question_id"]] = family_id

    unresolved: list[dict[str, Any]] = []
    for record in question_records:
        if record["question_id"] in owner:
            continue
        mapping = record["mapping"]
        concept_ids = mapping.get("concept_ids") or []
        if mapping.get("status") == "resolved" and concept_ids:
            concept_id = str(concept_ids[0])
            family_id = f"concept-{_slug(concept_id)}"
            if family_id not in memberships:
                memberships[family_id] = {
                    "family_id": family_id,
                    "title": concept_id,
                    "description": "Family formed from an explicitly supported concept mapping.",
                    "member_question_ids": [],
                    "clustering_method": "explicit_mapping",
                    "manual_review_required": False,
                }
            memberships[family_id]["member_question_ids"].append(record["question_id"])
            owner[record["question_id"]] = family_id
        else:
            unresolved.append(record)

    clusters = _similarity_clusters(unresolved) if allow_heuristic_clustering else [[item] for item in unresolved]
    for cluster in clusters:
        member_ids = sorted(record["question_id"] for record in cluster)
        digest = hashlib.sha256("\n".join(member_ids).encode("utf-8")).hexdigest()[:10]
        if len(cluster) > 1:
            shared = set.intersection(*(_question_tokens(record["question_text"]) for record in cluster))
            title = "Potential family: " + ", ".join(sorted(shared)[:4])
            method = "deterministic_similarity"
        else:
            title = f"Unresolved question family {member_ids[0]}"
            method = "singleton_unresolved"
        family_id = f"review-{digest}"
        memberships[family_id] = {
            "family_id": family_id,
            "title": title,
            "description": "Family requires manual review before being treated as a confirmed course concept.",
            "member_question_ids": member_ids,
            "clustering_method": method,
            "manual_review_required": True,
        }
        for record in cluster:
            owner[record["question_id"]] = family_id

    empty_ids = [family_id for family_id, family in memberships.items() if not family["member_question_ids"]]
    for family_id in empty_ids:
        del memberships[family_id]
    for family in memberships.values():
        family["member_question_ids"] = sorted(set(family["member_question_ids"]))
        for question_id in family["member_question_ids"]:
            records_by_id[question_id]["family_id"] = family["family_id"]
    return sorted(memberships.values(), key=lambda item: item["family_id"])


def _round_ratio(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 6)


def _tidy_number(value: float) -> int | float:
    rounded = round(value, 6)
    return int(rounded) if float(rounded).is_integer() else rounded


def calculate_family_metrics(
    question_records: Sequence[Mapping[str, Any]],
    formal_year_universe: Sequence[int],
) -> tuple[dict[str, int | float], dict[str, Any]]:
    """Calculate all required metrics for one family's records."""

    universe = sorted(set(int(year) for year in formal_year_universe))
    formal = [record for record in question_records if record.get("source_role") == FORMAL_ROLE]
    auxiliary = [record for record in question_records if record.get("source_role") in AUXILIARY_ROLES]
    occurrences = formal + auxiliary
    formal_years = sorted(
        {
            int(record["formal_year"])
            for record in formal
            if isinstance(record.get("formal_year"), int) and not isinstance(record.get("formal_year"), bool)
        }
    )
    annual_counts = {
        str(year): sum(1 for record in formal if record.get("formal_year") == year)
        for year in universe
    }
    coverage = len(formal_years) / len(universe) if universe else 0.0

    retention = 0.0
    if formal_years and universe:
        tail = [year for year in universe if year >= formal_years[0]]
        if len(tail) >= 2:
            retention = len(set(formal_years) & set(tail)) / len(tail)

    stability = 0.0
    counts = [annual_counts[str(year)] for year in universe]
    if len(counts) >= 2 and sum(counts) > 0:
        mean_count = sum(counts) / len(counts)
        mean_absolute_deviation = sum(abs(count - mean_count) for count in counts) / len(counts)
        stability = 1.0 - (mean_absolute_deviation / mean_count)

    formats = sorted({str(record["question_format"]) for record in occurrences})
    marked = [record for record in occurrences if record.get("explicit_marks") is not None]
    explicit_mark_exposure = sum(float(record["explicit_marks"]) for record in marked)
    mapped = [record for record in occurrences if record.get("mapping", {}).get("status") == "resolved"]
    unresolved = [record for record in occurrences if record.get("mapping", {}).get("status") != "resolved"]
    mapping_coverage = len(mapped) / len(occurrences) if occurrences else 0.0

    metrics: dict[str, int | float] = {
        "formal_occurrence_count": len(formal),
        "distinct_formal_years": len(formal_years),
        "formal_year_coverage": _round_ratio(coverage),
        "auxiliary_occurrence_count": len(auxiliary),
        "format_diversity": len(formats),
        "explicit_mark_exposure": _tidy_number(explicit_mark_exposure),
        "retention": _round_ratio(retention),
        "cross_year_stability": _round_ratio(stability),
        "mapping_coverage": _round_ratio(mapping_coverage),
        "unresolved_mapping_count": len(unresolved),
    }
    evidence = {
        "formal_question_ids": sorted(str(record["question_id"]) for record in formal),
        "formal_years": formal_years,
        "annual_formal_counts": annual_counts,
        "auxiliary_question_ids": sorted(str(record["question_id"]) for record in auxiliary),
        "observed_formats": formats,
        "explicitly_marked_question_ids": sorted(str(record["question_id"]) for record in marked),
        "mapped_question_ids": sorted(str(record["question_id"]) for record in mapped),
        "unresolved_question_ids": sorted(str(record["question_id"]) for record in unresolved),
    }
    return metrics, evidence


def _formal_year_universe(sources: Sequence[Mapping[str, Any]]) -> list[int]:
    years = {
        int(source["formal_year"])
        for source in sources
        if source.get("source_role") == FORMAL_ROLE
        and isinstance(source.get("formal_year"), int)
        and not isinstance(source.get("formal_year"), bool)
    }
    return sorted(years)


def _normalise_input(payload: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if "sources" not in payload and ("scan" in payload or "documents" in payload):
        payload = source_scan_to_payload(payload)
    raw_sources = payload.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise ExamIntelligenceError("Input requires a non-empty sources list")
    sources = [_normalise_source(source, index) for index, source in enumerate(raw_sources, 1)]
    source_ids = [source["source_id"] for source in sources]
    if len(source_ids) != len(set(source_ids)):
        raise ExamIntelligenceError("source_id values must be unique")
    by_id = {source["source_id"]: source for source in sources}

    raw_questions = payload.get("question_records", payload.get("questions"))
    if raw_questions is None:
        questions = extract_question_records(raw_sources)
    else:
        if not isinstance(raw_questions, list):
            raise ExamIntelligenceError("questions must be a list")
        questions = [
            _normalise_question(question, index, by_id)
            for index, question in enumerate(raw_questions, 1)
        ]
    question_ids = [question["question_id"] for question in questions]
    if len(question_ids) != len(set(question_ids)):
        raise ExamIntelligenceError("question_id values must be unique")
    return sources, questions


def build_exam_intelligence_package(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic public/audit exam-intelligence package."""

    if not isinstance(payload, Mapping):
        raise ExamIntelligenceError("Input payload must be a JSON object")
    sources, questions = _normalise_input(payload)
    declared_families = payload.get("families")
    if declared_families is not None and not isinstance(declared_families, list):
        raise ExamIntelligenceError("families must be a list")
    memberships = cluster_question_families(
        questions,
        declared_families,
        allow_heuristic_clustering=bool(payload.get("allow_heuristic_clustering", False)),
    )
    questions_by_id = {question["question_id"]: question for question in questions}
    formal_years = _formal_year_universe(sources)

    public_families: list[dict[str, Any]] = []
    metric_evidence: list[dict[str, Any]] = []
    for family in memberships:
        family_questions = [questions_by_id[item] for item in family["member_question_ids"]]
        metrics, evidence = calculate_family_metrics(family_questions, formal_years)
        public_families.append(
            {
                "family_id": family["family_id"],
                "title": family["title"],
                "description": family["description"],
                **metrics,
            }
        )
        metric_evidence.append({"family_id": family["family_id"], **evidence})

    unresolved = [
        {
            "question_id": question["question_id"],
            "reason": str(question["mapping"]["unresolved_reason"]),
        }
        for question in questions
        if question["source_role"] in OCCURRENCE_ROLES
        and question["mapping"]["status"] == "unresolved"
    ]
    role_counts = {role: 0 for role in SOURCE_ROLES}
    for source in sources:
        role_counts[source["source_role"]] += 1
    formal_sources = [source for source in sources if source["source_role"] == FORMAL_ROLE]
    manual_review = [family for family in memberships if family["manual_review_required"]]
    undated_formal = [source for source in formal_sources if source["formal_year"] is None]
    formal_questions = [question for question in questions if question["source_role"] == FORMAL_ROLE]

    warnings: list[str] = []
    if not formal_sources:
        warnings.append("No formal_past_paper source was supplied; formal recurrence is unavailable.")
    if undated_formal:
        warnings.append(
            f"{len(undated_formal)} formal past-paper source(s) have no explicit year and are excluded from year-based metrics."
        )
    if formal_sources and not formal_questions:
        warnings.append("Formal past-paper sources were supplied, but no examinable formal question was extracted.")
    if unresolved:
        warnings.append(f"{len(unresolved)} formal or auxiliary question mapping(s) remain unresolved.")
    if manual_review:
        warnings.append(f"{len(manual_review)} question family/families require manual review.")

    if not formal_sources:
        status = "needs_material_input"
    elif unresolved or undated_formal or manual_review or not formal_questions:
        status = "completed_with_gaps"
    else:
        status = "completed"

    package = {
        "schema_version": SCHEMA_VERSION,
        "package_type": "exam_intelligence",
        "public": {
            "status": status,
            "course_id": _clean_string(payload.get("course_id")) or None,
            "course_title": _clean_string(payload.get("course_title")) or None,
            "corpus_scope": {
                "source_role_counts": role_counts,
                "formal_years": formal_years,
            },
            "metric_definitions": dict(METRIC_DEFINITIONS),
            "question_families": sorted(public_families, key=lambda item: item["family_id"]),
            "limitations": list(LIMITATIONS),
            "interpretation_guardrails": {
                "formal_recurrence_basis": "formal_past_paper_only",
                "weighting_inference_allowed": False,
                "certain_prediction_allowed": False,
                "composite_score_produced": False,
            },
        },
        "audit": {
            "sources": sources,
            "question_records": sorted(questions, key=lambda item: item["question_id"]),
            "family_memberships": memberships,
            "metric_evidence": sorted(metric_evidence, key=lambda item: item["family_id"]),
            "unresolved_mappings": sorted(unresolved, key=lambda item: item["question_id"]),
            "exclusions": [
                "lecture_material and mark_scheme records are excluded from occurrence metrics.",
                "official_mock_specimen and practice_worksheet records are excluded from formal recurrence.",
            ],
            "warnings": warnings,
        },
    }
    errors = validation_errors(package)
    if errors:
        raise ExamIntelligenceError("Built package failed validation: " + "; ".join(errors))
    validate_with_jsonschema(package, required=False)
    return package


def _walk_fields(value: Any, path: str = "$") -> Iterable[tuple[str, Any, str]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield str(key), child, child_path
            yield from _walk_fields(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_fields(child, f"{path}[{index}]")


def _walk_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _walk_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_strings(child, f"{path}[{index}]")


def _metric_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-6)
    return left == right


def validation_errors(package: Any) -> list[str]:
    """Return deterministic structural and semantic validation errors."""

    errors: list[str] = []
    if not isinstance(package, Mapping):
        return ["Package must be a JSON object"]
    if package.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if package.get("package_type") != "exam_intelligence":
        errors.append("package_type must be exam_intelligence")
    public = package.get("public")
    audit = package.get("audit")
    if not isinstance(public, Mapping):
        errors.append("public must be an object")
        return errors
    if not isinstance(audit, Mapping):
        errors.append("audit must be an object")
        return errors

    guardrails = public.get("interpretation_guardrails")
    expected_guardrails = {
        "formal_recurrence_basis": "formal_past_paper_only",
        "weighting_inference_allowed": False,
        "certain_prediction_allowed": False,
        "composite_score_produced": False,
    }
    if guardrails != expected_guardrails:
        errors.append("interpretation_guardrails must preserve formal-only, non-weighting, non-predictive analysis")
    for key, value, path in _walk_fields(package):
        if key not in ALLOWED_GUARDRAIL_FIELDS and FORBIDDEN_FIELD.search(key):
            errors.append(f"Forbidden weighting, prediction, probability, or composite-score field at {path}")
    for path, value in _walk_strings(public, "$.public"):
        if ASSERTIVE_PREDICTION.search(value):
            errors.append(f"Certain future-question claim at {path}")

    audit_only_keys = {
        "sources", "question_records", "family_memberships", "metric_evidence",
        "unresolved_mappings", "source_locator", "question_text",
    }
    for key, _, path in _walk_fields(public):
        if key in audit_only_keys:
            errors.append(f"Audit-only field leaked into public data at {path}")

    sources = audit.get("sources")
    questions = audit.get("question_records")
    memberships = audit.get("family_memberships")
    metric_evidence = audit.get("metric_evidence")
    if not isinstance(sources, list):
        errors.append("audit.sources must be a list")
        sources = []
    if not isinstance(questions, list):
        errors.append("audit.question_records must be a list")
        questions = []
    if not isinstance(memberships, list):
        errors.append("audit.family_memberships must be a list")
        memberships = []
    if not isinstance(metric_evidence, list):
        errors.append("audit.metric_evidence must be a list")
        metric_evidence = []

    source_map: dict[str, Mapping[str, Any]] = {}
    role_counts = {role: 0 for role in SOURCE_ROLES}
    for source in sources:
        if not isinstance(source, Mapping):
            errors.append("Each source must be an object")
            continue
        source_id = _clean_string(source.get("source_id"))
        try:
            role = _normalise_role(source.get("source_role"))
        except ExamIntelligenceError as exc:
            errors.append(str(exc))
            continue
        if source.get("source_role") != role:
            errors.append(f"Source {source_id!r} must use canonical source_role {role!r}")
        if source_id in source_map:
            errors.append(f"Duplicate source_id {source_id!r}")
        source_map[source_id] = source
        role_counts[role] += 1
        if role != FORMAL_ROLE and source.get("formal_year") is not None:
            errors.append(f"Non-formal source {source_id!r} cannot carry formal_year")

    question_map: dict[str, Mapping[str, Any]] = {}
    for question in questions:
        if not isinstance(question, Mapping):
            errors.append("Each question record must be an object")
            continue
        question_id = _clean_string(question.get("question_id"))
        if question_id in question_map:
            errors.append(f"Duplicate question_id {question_id!r}")
        question_map[question_id] = question
        source_id = _clean_string(question.get("source_id"))
        source = source_map.get(source_id)
        if not source:
            errors.append(f"Question {question_id!r} references unknown source_id {source_id!r}")
        elif question.get("source_role") != source.get("source_role"):
            errors.append(f"Question {question_id!r} source_role differs from its source")
        elif question.get("formal_year") != source.get("formal_year"):
            errors.append(
                f"Question {question_id!r} formal_year differs from its owning source {source_id!r}"
            )
        if question.get("source_role") not in SOURCE_ROLES:
            errors.append(f"Question {question_id!r} has invalid source_role")
        if question.get("source_role") != FORMAL_ROLE and question.get("formal_year") is not None:
            errors.append(f"Non-formal question {question_id!r} cannot carry formal_year")
        if question.get("question_format") not in QUESTION_FORMATS:
            errors.append(f"Question {question_id!r} has invalid question_format")
        mapping = question.get("mapping")
        if not isinstance(mapping, Mapping):
            errors.append(f"Question {question_id!r} mapping must be an object")
            continue
        targets = bool(mapping.get("lecture_id") or mapping.get("unit_id") or mapping.get("concept_ids"))
        if mapping.get("status") == "resolved":
            if not targets:
                errors.append(f"Resolved question {question_id!r} has no course target")
            if not mapping.get("evidence"):
                errors.append(f"Resolved question {question_id!r} has no explicit mapping evidence")
            if mapping.get("unresolved_reason") is not None:
                errors.append(f"Resolved question {question_id!r} cannot have unresolved_reason")
        elif mapping.get("status") == "unresolved":
            if targets:
                errors.append(f"Unresolved question {question_id!r} cannot select a course target")
            if not _clean_string(mapping.get("unresolved_reason")):
                errors.append(f"Unresolved question {question_id!r} needs a reason")
        else:
            errors.append(f"Question {question_id!r} has invalid mapping status")

    owner: dict[str, str] = {}
    family_map: dict[str, Mapping[str, Any]] = {}
    for family in memberships:
        if not isinstance(family, Mapping):
            errors.append("Each family membership must be an object")
            continue
        family_id = _clean_string(family.get("family_id"))
        if family_id in family_map:
            errors.append(f"Duplicate family_id {family_id!r}")
        family_map[family_id] = family
        member_ids = family.get("member_question_ids")
        if not isinstance(member_ids, list) or not member_ids:
            errors.append(f"Family {family_id!r} must have member_question_ids")
            continue
        for question_id in member_ids:
            if question_id not in question_map:
                errors.append(f"Family {family_id!r} references unknown question_id {question_id!r}")
            if question_id in owner and owner[question_id] != family_id:
                errors.append(f"Question {question_id!r} belongs to multiple families")
            owner[str(question_id)] = family_id
    for question_id, question in question_map.items():
        if owner.get(question_id) != question.get("family_id"):
            errors.append(f"Question {question_id!r} family_id does not match audit membership")

    public_families_raw = public.get("question_families")
    if not isinstance(public_families_raw, list):
        errors.append("public.question_families must be a list")
        public_families_raw = []
    for index, family in enumerate(public_families_raw):
        if not isinstance(family, Mapping):
            continue
        for field in ("title", "description"):
            value = family.get(field)
            if not isinstance(value, str):
                continue
            path = f"$.public.question_families[{index}].{field}"
            if FAMILY_WEIGHTING_CLAIM.search(value) or (
                FAMILY_WEIGHTING_TERM.search(value) and FAMILY_ASSESSMENT_CONTEXT.search(value)
            ):
                errors.append(f"Official assessment-weighting claim at {path}")
            if FAMILY_FUTURE_PREDICTION.search(value) or (
                FAMILY_EXPECTATION_CUE.search(value) and FAMILY_FUTURE_CONTEXT.search(value)
            ):
                errors.append(f"Future-question prediction claim at {path}")
    public_families = {
        _clean_string(family.get("family_id")): family
        for family in public_families_raw
        if isinstance(family, Mapping)
    }
    evidence_map = {
        _clean_string(item.get("family_id")): item
        for item in metric_evidence
        if isinstance(item, Mapping)
    }
    if set(public_families) != set(family_map):
        errors.append("Public question families must match audit family memberships")
    if set(evidence_map) != set(family_map):
        errors.append("Metric evidence must match audit family memberships")

    formal_years = _formal_year_universe(sources)
    corpus_scope = public.get("corpus_scope")
    if not isinstance(corpus_scope, Mapping):
        errors.append("public.corpus_scope must be an object")
    else:
        if corpus_scope.get("source_role_counts") != role_counts:
            errors.append("source_role_counts do not match audit sources")
        if corpus_scope.get("formal_years") != formal_years:
            errors.append("corpus formal_years do not match dated formal evidence")

    for family_id, family in family_map.items():
        member_questions = [question_map[item] for item in family.get("member_question_ids", []) if item in question_map]
        recomputed, recomputed_evidence = calculate_family_metrics(member_questions, formal_years)
        public_family = public_families.get(family_id)
        if not public_family:
            continue
        if public_family.get("title") != family.get("title") or public_family.get("description") != family.get("description"):
            errors.append(f"Public family metadata differs from audit for {family_id!r}")
        for metric_name in METRIC_NAMES:
            if not _metric_equal(public_family.get(metric_name), recomputed[metric_name]):
                errors.append(f"Metric {metric_name} does not recompute for family {family_id!r}")
        expected_evidence = {"family_id": family_id, **recomputed_evidence}
        if evidence_map.get(family_id) != expected_evidence:
            errors.append(f"Metric evidence does not recompute for family {family_id!r}")

    formal_source_count = role_counts[FORMAL_ROLE]
    formal_questions = [question for question in questions if question.get("source_role") == FORMAL_ROLE]
    unresolved_occurrences = [
        question
        for question in questions
        if question.get("source_role") in OCCURRENCE_ROLES
        and isinstance(question.get("mapping"), Mapping)
        and question["mapping"].get("status") == "unresolved"
    ]
    undated_formal_sources = [
        source
        for source in sources
        if source.get("source_role") == FORMAL_ROLE and source.get("formal_year") is None
    ]
    review_families = [family for family in memberships if family.get("manual_review_required") is True]
    if formal_source_count == 0:
        expected_status = "needs_material_input"
    elif unresolved_occurrences or undated_formal_sources or review_families or not formal_questions:
        expected_status = "completed_with_gaps"
    else:
        expected_status = "completed"
    if public.get("status") != expected_status:
        errors.append(f"public.status must be {expected_status!r} for the audited evidence state")
    expected_unresolved = sorted(
        (
            {
                "question_id": str(question.get("question_id")),
                "reason": str(question.get("mapping", {}).get("unresolved_reason")),
            }
            for question in unresolved_occurrences
        ),
        key=lambda item: item["question_id"],
    )
    if audit.get("unresolved_mappings") != expected_unresolved:
        errors.append("audit.unresolved_mappings does not match unresolved occurrence records")
    definitions = public.get("metric_definitions")
    if not isinstance(definitions, Mapping) or set(definitions) != set(METRIC_NAMES):
        errors.append("metric_definitions must explain all ten metrics")
    return errors


def validate_with_jsonschema(package: Mapping[str, Any], *, required: bool = False) -> bool:
    """Validate against the self-contained Draft 2020-12 schema when available."""

    try:
        import jsonschema  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        if required:
            raise ExamIntelligenceError("jsonschema is not installed")
        return False
    schema_path = ROOT / "schemas" / "exam_intelligence_package.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        validator = jsonschema.Draft202012Validator(schema)
        validator.check_schema(schema)
        validator.validate(package)
    except jsonschema.exceptions.ValidationError as exc:
        location = ".".join(str(item) for item in exc.absolute_path) or "$"
        raise ExamIntelligenceError(f"JSON Schema validation failed at {location}: {exc.message}") from exc
    except jsonschema.exceptions.SchemaError as exc:
        raise ExamIntelligenceError(f"Invalid exam-intelligence schema: {exc.message}") from exc
    return True


def validate_exam_intelligence_package(package: Any) -> dict[str, Any]:
    errors = validation_errors(package)
    if errors:
        raise ExamIntelligenceError("; ".join(errors))
    jsonschema_used = validate_with_jsonschema(package, required=False)
    return {
        "status": "valid",
        "schema_version": SCHEMA_VERSION,
        "jsonschema_validation": "passed" if jsonschema_used else "not_installed",
        "question_family_count": len(package["public"]["question_families"]),
        "question_record_count": len(package["audit"]["question_records"]),
    }


def _load_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ExamIntelligenceError(f"Could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ExamIntelligenceError(f"Invalid JSON in {path}: {exc}") from exc


def _render_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def self_test() -> None:
    payload = {
        "course_id": "DEMO101",
        "sources": [
            {"source_id": "f20", "source_name": "Paper 2020", "source_role": FORMAL_ROLE, "formal_year": 2020},
            {"source_id": "f21", "source_name": "Paper 2021", "source_role": FORMAL_ROLE, "formal_year": 2021},
            {"source_id": "mock", "source_name": "Specimen", "source_role": "official_mock_specimen"},
            {"source_id": "scheme", "source_name": "Scheme", "source_role": "mark_scheme"},
        ],
        "questions": [
            {
                "question_id": "q1", "source_id": "f20", "question_text": "Explain pathway X. [5 marks]",
                "question_format": "short_answer", "family_id": "pathway-x",
                "mapping": {"status": "resolved", "concept_ids": ["pathway-x"], "evidence": ["Lecture 1 slide 4"]},
            },
            {
                "question_id": "q2", "source_id": "f21", "question_text": "Describe pathway X. [5 marks]",
                "question_format": "short_answer", "family_id": "pathway-x",
                "mapping": {"status": "unresolved", "unresolved_reason": "Course mapping not supplied."},
            },
            {
                "question_id": "q3", "source_id": "mock", "question_text": "State pathway X. [2 marks]",
                "question_format": "short_answer", "family_id": "pathway-x",
                "mapping": {"status": "unresolved", "unresolved_reason": "Course mapping not supplied."},
            },
            {
                "question_id": "q4", "source_id": "scheme", "question_text": "Pathway X marking points.",
                "question_format": "other", "family_id": "pathway-x",
                "mapping": {"status": "unresolved", "unresolved_reason": "Not a question occurrence."},
            },
        ],
    }
    package = build_exam_intelligence_package(payload)
    family = package["public"]["question_families"][0]
    assert family["formal_occurrence_count"] == 2
    assert family["auxiliary_occurrence_count"] == 1
    assert family["explicit_mark_exposure"] == 12
    assert family["mapping_coverage"] == round(1 / 3, 6)
    assert family["unresolved_mapping_count"] == 2
    assert package["public"]["interpretation_guardrails"]["certain_prediction_allowed"] is False
    validate_exam_intelligence_package(package)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "validate", "extract", "self-test"))
    parser.add_argument("--input", help="Input JSON path")
    parser.add_argument("--out", help="Output JSON path; otherwise write to stdout")
    parser.add_argument(
        "--require-jsonschema",
        action="store_true",
        help="Fail validation when the optional jsonschema package is unavailable",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "self-test":
            self_test()
            result: Any = {"status": "ok"}
        else:
            if not args.input:
                parser.error(f"{args.command} requires --input")
            payload = _load_json(args.input)
            if args.command == "build":
                result = build_exam_intelligence_package(payload)
                if args.require_jsonschema:
                    validate_with_jsonschema(result, required=True)
            elif args.command == "validate":
                result = validate_exam_intelligence_package(payload)
                if args.require_jsonschema:
                    validate_with_jsonschema(payload, required=True)
                    result["jsonschema_validation"] = "passed"
            else:
                if not isinstance(payload, Mapping) or not isinstance(payload.get("sources"), list):
                    raise ExamIntelligenceError("extract input requires a JSON object with sources")
                result = {"question_records": extract_question_records(payload["sources"])}
        rendered = _render_json(result)
        if args.out:
            Path(args.out).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except ExamIntelligenceError as exc:
        parser.exit(2, f"error: {exc}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
