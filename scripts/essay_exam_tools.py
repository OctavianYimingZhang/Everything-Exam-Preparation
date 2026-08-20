#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any

STOPWORDS = {"lecture", "module", "question", "answer", "using", "explain", "describe", "compare", "evaluate", "discuss", "material", "course", "student"}
ONLINE_ASSESSMENT_STATES = {"active", "closed", "unknown"}
PERMISSION_ALLOWED = {True, "allowed", "yes", "permitted", "true"}
PERMISSION_DENIED = {False, "denied", "no", "not_allowed", "not permitted", "false"}
ONLINE_ACTION_ALIASES = {
    "outline": "plan",
    "essay_plan": "plan",
    "paragraph_plan": "plan",
    "evidence_organisation": "evidence_map",
    "evidence_organization": "evidence_map",
    "draft": "complete_draft",
    "full_draft": "complete_draft",
    "submission_ready_draft": "complete_draft",
    "external_source_research": "use_external_sources",
    "online_research": "use_online_materials",
}
ONLINE_ACTION_PERMISSION = {
    "use_lecture_materials": "lecture_materials",
    "use_online_materials": "online_materials",
    "use_uploaded_readings": "uploaded_readings",
    "use_external_sources": "external_sources",
    "complete_draft": "complete_draft",
}
ONLINE_SAFE_ACTIONS = {
    "question_analysis",
    "concept_explanation",
    "permission_neutral_plan",
    "plan",
    "evidence_map",
    "feedback_on_student_work",
}
ONLINE_KNOWN_ACTIONS = ONLINE_SAFE_ACTIONS | set(ONLINE_ACTION_PERMISSION)


def frequent_topics(text: str, limit: int = 6) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or "")
    counts = collections.Counter(w.lower() for w in words if w.lower() not in STOPWORDS)
    return [term for term, _ in counts.most_common(limit)] or ["core module theme"]


def scan_text(source_scan: dict[str, Any] | None) -> str:
    if not source_scan:
        return ""
    return "\n".join(str(frag.get("text", "")) for frag in source_scan.get("fragments", []))


def load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def extra_reading_topics(extra_reading: dict[str, Any] | None) -> list[str]:
    if not extra_reading:
        return []
    topics = []
    for item in extra_reading.get("topic_enrichment", []):
        topic = item.get("lecture_topic")
        if topic:
            topics.append(str(topic))
    if not topics:
        for item in extra_reading.get("lecture_topics", []):
            topics.append(str(item.get("topic") if isinstance(item, dict) else item))
    return topics


def extra_reading_slots(extra_reading: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not extra_reading:
        return []
    essay = extra_reading.get("essay_enrichment", {})
    return essay.get("paragraph_slots", []) or []


def lecture_topics(source_scan: dict[str, Any] | None, limit: int = 12) -> list[dict[str, Any]]:
    text = scan_text(source_scan)
    counts = collections.Counter(
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text)
        if word.lower() not in STOPWORDS
    )
    return [{"topic": topic, "occurrences": count} for topic, count in counts.most_common(limit)]


def generate_extra_reading_queries(topics: list[dict[str, Any]] | list[str], limit: int = 20) -> list[dict[str, str]]:
    queries: list[dict[str, str]] = []
    for item in topics:
        topic = str(item.get("topic") if isinstance(item, dict) else item).strip()
        if not topic:
            continue
        for purpose, suffix in (
            ("mechanism", "mechanism review"),
            ("experimental_evidence", "primary research experiment"),
            ("evaluation", "limitations systematic review"),
        ):
            queries.append({"topic": topic, "purpose": purpose, "query": f"{topic} {suffix}"})
            if len(queries) >= limit:
                return queries
    return queries


def discover_extra_reading(source_scan: dict[str, Any] | None) -> dict[str, Any]:
    source_scan = source_scan or {"documents": [], "fragments": []}
    topics = lecture_topics(source_scan)
    source_records: list[dict[str, Any]] = []
    for document in source_scan.get("documents", []):
        if document.get("source_hint") != "extra_reading_source":
            continue
        fragments = [
            fragment for fragment in source_scan.get("fragments", [])
            if fragment.get("source_id") == document.get("id")
        ]
        text = " ".join(str(fragment.get("text") or "") for fragment in fragments)
        matched = [
            item["topic"] for item in topics
            if item["topic"].casefold() in text.casefold()
        ][:4]
        source_records.append({
            "source_id": document.get("id"),
            "source_name": document.get("name"),
            "matched_topics": matched,
            "locators": [fragment.get("locator") for fragment in fragments[:6]],
        })
    return {
        "schema_version": 3,
        "lecture_topics": topics,
        "supplied_extra_reading": source_records,
        "search_queries": generate_extra_reading_queries(topics),
    }


def build_extra_reading_enrichment(discovery: dict[str, Any]) -> dict[str, Any]:
    sources = discovery.get("supplied_extra_reading") or []
    slots: list[dict[str, Any]] = []
    for topic in discovery.get("lecture_topics", [])[:8]:
        label = str(topic.get("topic") if isinstance(topic, dict) else topic)
        matched_sources = [
            source for source in sources
            if label in (source.get("matched_topics") or [])
        ]
        slots.append({
            "lecture_topic": label,
            "paragraph_role": "Use evidence where it strengthens the claim, mechanism, counterargument, or evaluation.",
            "matched_sources": matched_sources,
        })
    return {
        "schema_version": 3,
        "topic_enrichment": slots,
        "essay_enrichment": {"paragraph_slots": slots},
    }


def normalize_assessment_state(value: Any) -> str:
    if value is True:
        return "active"
    if value is False:
        return "closed"
    state = str(value or "unknown").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "open": "active",
        "live": "active",
        "in_progress": "active",
        "finished": "closed",
        "complete": "closed",
        "completed": "closed",
        "unclear": "unknown",
        "unspecified": "unknown",
    }
    state = aliases.get(state, state)
    return state if state in ONLINE_ASSESSMENT_STATES else "unknown"


def permission_state(value: Any) -> str:
    if not isinstance(value, (str, bool)):
        return "unknown"
    normalized = value.strip().lower() if isinstance(value, str) else value
    if normalized in PERMISSION_ALLOWED:
        return "allowed"
    if normalized in PERMISSION_DENIED:
        return "denied"
    return "unknown"


def normalize_requested_actions(value: Any) -> list[str]:
    if value in (None, "", []):
        return ["plan"]
    raw_actions = value if isinstance(value, list) else [value]
    actions: list[str] = []
    for raw in raw_actions:
        action = str(raw or "").strip().lower().replace("-", "_").replace(" ", "_")
        action = ONLINE_ACTION_ALIASES.get(action, action)
        if action and action not in actions:
            actions.append(action)
    return actions or ["plan"]


def online_essay_permission_status(
    permissions: dict[str, Any] | None,
    assessment_state: str | None = None,
    requested_actions: list[str] | str | None = None,
) -> dict[str, Any]:
    """Resolve Online Essay actions from lifecycle state and action-specific permissions."""
    permissions = permissions or {}
    state = normalize_assessment_state(
        assessment_state
        if assessment_state is not None
        else permissions.get("assessment_state", permissions.get("assessment_status"))
    )
    actions = normalize_requested_actions(
        requested_actions
        if requested_actions is not None
        else permissions.get("requested_actions", permissions.get("requested_action"))
    )
    source_keys = ("lecture_materials", "online_materials", "uploaded_readings", "external_sources")
    allowed_sources = [key for key in source_keys if permission_state(permissions.get(key)) == "allowed"]
    allowed_actions = sorted(ONLINE_SAFE_ACTIONS - {"plan", "evidence_map"})
    blocked_actions: list[dict[str, str]] = []
    gaps: list[dict[str, str]] = []
    advisories: list[dict[str, str]] = []
    action_conditions: dict[str, str] = {}

    if state == "closed":
        for action in actions:
            if action not in ONLINE_KNOWN_ACTIONS:
                blocked_actions.append({"action": action, "reason": "unsupported_or_unclassified_action"})
                continue
            if action not in allowed_actions:
                allowed_actions.append(action)
            action_conditions[action] = "post_assessment_support_only"
        if "complete_draft" in actions:
            action_conditions["complete_draft"] = "post_assessment_model_answer_not_live_submission_support"
        status = "restricted" if blocked_actions else "ready"
    elif state == "unknown":
        unknown_state_notice = {
            "code": "unknown_assessment_state",
            "field": "assessment_state",
            "detail": "Confirm whether the Online Essay assessment is active or closed before restricted support.",
        }
        for action in actions:
            if action in ONLINE_SAFE_ACTIONS:
                if action not in allowed_actions:
                    allowed_actions.append(action)
                action_conditions[action] = "permission_neutral_until_assessment_state_is_confirmed"
            else:
                blocked_actions.append({
                    "action": action,
                    "reason": "assessment_state_unknown",
                })
        if blocked_actions:
            gaps.append(unknown_state_notice)
            status = "needs_clarification"
        else:
            advisories.append(unknown_state_notice)
            status = "ready"
    else:
        for action in actions:
            if action == "complete_draft":
                blocked_actions.append({
                    "action": action,
                    "reason": "active_assessed_complete_draft_out_of_scope",
                })
                action_conditions[action] = "closed_past_assessment_model_answers_only"
                continue
            permission_key = ONLINE_ACTION_PERMISSION.get(action)
            if permission_key is None:
                if action in ONLINE_SAFE_ACTIONS:
                    if action not in allowed_actions:
                        allowed_actions.append(action)
                    action_conditions[action] = "permission_neutral_or_feedback_support"
                else:
                    blocked_actions.append({"action": action, "reason": "unsupported_or_unclassified_action"})
                continue
            decision = permission_state(permissions.get(permission_key))
            if decision == "allowed":
                if action not in allowed_actions:
                    allowed_actions.append(action)
                action_conditions[action] = f"explicit_{permission_key}_permission"
                if action == "use_external_sources" and permission_state(permissions.get("citation_expectations")) == "unknown":
                    gaps.append({
                        "code": "unresolved_citation_expectations",
                        "field": "citation_expectations",
                        "detail": "External-source use is allowed, but the required citation practice is unresolved.",
                    })
            elif decision == "denied":
                blocked_actions.append({"action": action, "reason": f"{permission_key}_explicitly_denied"})
            else:
                blocked_actions.append({"action": action, "reason": f"{permission_key}_permission_unresolved"})
                gaps.append({
                    "code": "unresolved_online_essay_permission",
                    "field": permission_key,
                    "detail": f"Confirm {permission_key.replace('_', ' ')} permission for the requested action.",
                })
        status = "needs_clarification" if gaps else ("restricted" if blocked_actions else "ready")

    unresolved = []
    for item in gaps:
        field = item.get("field")
        if field and field not in unresolved:
            unresolved.append(field)
    return {
        "type": "online_essay_permission_state",
        "task_mode": "essay",
        "assessment_state": state,
        "status": status,
        "gaps": gaps,
        "advisories": advisories,
        "degraded": status != "ready",
        "requested_actions": actions,
        "allowed_actions": sorted(set(allowed_actions)),
        "blocked_actions": blocked_actions,
        "action_conditions": action_conditions,
        "unresolved": unresolved,
        "allowed_sources": allowed_sources,
        "complete_draft": "denied_by_scope" if state == "active" else permission_state(permissions.get("complete_draft")),
        "public_scope": "exam_preparation_and_closed_past_assessment_only",
    }


ESSAY_VIEW_SCHEMA_VERSION = 1
ESSAY_SEGMENT_ANNOTATIONS = {"thesis", "claim", "evidence", "analysis", "limitation", "synthesis"}
ESSAY_REQUIRED_ANNOTATIONS = ESSAY_SEGMENT_ANNOTATIONS | {"paragraph_function", "adaptation_notes"}
PAST_PAPER_SOURCE_USES = {"scope", "emphasis", "question_scope", "question_emphasis"}
QUANTITATIVE_CLAIM_PATTERN = re.compile(
    r"(?:\b\d+(?:\.\d+)?\s*(?:percent(?:age)?|fold|times|mV|V|mM|uM|nM|mg|kg|ug|"
    r"mL|Hz|min|hours?|seconds?|degrees?\s*C)\b|\b\d+(?:\.\d+)?\s*%|"
    r"\bp\s*(?:<|>|=|<=|>=)\s*0?\.\d+\b)",
    re.IGNORECASE,
)
EMPIRICAL_RESULT_CUE = re.compile(
    r"\b(?:experiment(?:al)?|study|studies|trial|dataset|data|reported|observed|"
    r"measured|demonstrated|found)\b",
    re.IGNORECASE,
)
EVIDENCE_TOKEN_STOPWORDS = {
    "about", "after", "against", "also", "because", "before", "between", "course",
    "despite", "during", "evidence", "from", "into", "material", "reported", "result",
    "showed", "source", "study", "such", "that", "their", "therefore", "these", "this",
    "through", "using", "were", "which", "while", "with",
}


def _explicit_assessment_state(payload: dict[str, Any]) -> tuple[bool, Any, dict[str, Any]]:
    permissions = payload.get("permissions") if isinstance(payload.get("permissions"), dict) else {}
    for key in ("assessment_state", "assessment_status"):
        if key in payload:
            return True, payload.get(key), permissions
        if key in permissions:
            return True, permissions.get(key), permissions
    return False, None, permissions


def _essay_view_lifecycle_refusal(payload: dict[str, Any]) -> dict[str, Any] | None:
    explicit, state_value, permissions = _explicit_assessment_state(payload)
    if not explicit:
        return None
    state = normalize_assessment_state(state_value)
    if state == "closed":
        return None
    gate = online_essay_permission_status(
        permissions,
        assessment_state=state,
        requested_actions=["complete_draft"],
    )
    return {
        "schema_version": ESSAY_VIEW_SCHEMA_VERSION,
        "task_mode": "example_essay",
        "document_kind": "example_essay_views",
        "status": gate["status"],
        "assessment_state": state,
        "views_generated": False,
        "blocked_actions": gate["blocked_actions"],
        "gaps": gate["gaps"],
        "reason": (
            "active_assessed_complete_draft_out_of_scope"
            if state == "active"
            else "assessment_state_unknown"
        ),
    }


def _essay_text_list(value: Any) -> list[str]:
    if value in (None, "", []):
        return []
    values = value if isinstance(value, list) else [value]
    return [re.sub(r"\s+", " ", str(item or "")).strip() for item in values if str(item or "").strip()]


def _normalise_annotation(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    annotations: list[str] = []
    aliases = {
        "counterargument": "limitation",
        "evaluation": "analysis",
        "link": "synthesis",
        "topic_sentence": "claim",
    }
    for raw in values:
        label = str(raw or "").strip().lower().replace("-", "_").replace(" ", "_")
        label = aliases.get(label, label)
        if label in ESSAY_SEGMENT_ANNOTATIONS and label not in annotations:
            annotations.append(label)
    return annotations


def _normalise_source_refs(value: Any) -> list[dict[str, str]]:
    values = value if isinstance(value, list) else ([value] if value not in (None, "") else [])
    refs: list[dict[str, str]] = []
    for raw in values:
        if isinstance(raw, str):
            ref = {"source_id": raw, "usage": "course_fact", "locator": ""}
        elif isinstance(raw, dict):
            ref = {
                "source_id": str(raw.get("source_id") or raw.get("id") or "").strip(),
                "source_name": str(raw.get("source_name") or raw.get("name") or "").strip(),
                "usage": str(raw.get("usage") or raw.get("role") or "course_fact").strip().lower().replace(" ", "_"),
                "locator": str(raw.get("locator") or "").strip(),
            }
        else:
            continue
        if ref.get("source_id") or ref.get("source_name"):
            refs.append(ref)
    return refs


def _segment_from_value(raw: Any, block_id: str, index: int, role: str = "") -> dict[str, Any] | None:
    if isinstance(raw, str):
        data: dict[str, Any] = {"text": raw, "annotations": [role] if role else []}
    elif isinstance(raw, dict):
        data = raw
    else:
        return None
    text = re.sub(r"\s+", " ", str(data.get("text") or data.get("content") or "")).strip()
    if not text:
        return None
    annotations = _normalise_annotation(data.get("annotations") or data.get("annotation") or data.get("role") or role)
    segment = {
        "segment_id": str(data.get("segment_id") or data.get("id") or f"{block_id}-S{index}"),
        "text": text,
        "annotations": annotations,
        "source_refs": _normalise_source_refs(data.get("source_refs") or data.get("sources")),
    }
    for field in ("citation", "doi", "reported_result"):
        if data.get(field):
            segment[field] = re.sub(r"\s+", " ", str(data[field])).strip()
    return segment


def normalise_essay_body(payload: dict[str, Any]) -> dict[str, Any]:
    """Create the one canonical body from which both public views are projected."""
    if not isinstance(payload, dict):
        raise TypeError("essay view payload must be an object")
    raw_body = payload.get("canonical_body") or payload.get("body") or payload.get("paragraphs")
    if isinstance(raw_body, dict):
        raw_blocks = raw_body.get("blocks") or raw_body.get("paragraphs")
    else:
        raw_blocks = raw_body
    if not isinstance(raw_blocks, list) or not raw_blocks:
        raise ValueError("essay views require a non-empty canonical body")
    blocks: list[dict[str, Any]] = []
    for block_index, raw_block in enumerate(raw_blocks, 1):
        if isinstance(raw_block, str):
            raw_block = {"text": raw_block}
        if not isinstance(raw_block, dict):
            raise TypeError("each canonical essay block must be an object or string")
        block_id = str(raw_block.get("block_id") or raw_block.get("id") or f"P{block_index}")
        raw_segments = raw_block.get("segments")
        segments: list[dict[str, Any]] = []
        if isinstance(raw_segments, list):
            for segment_index, raw_segment in enumerate(raw_segments, 1):
                segment = _segment_from_value(raw_segment, block_id, segment_index)
                if segment:
                    segments.append(segment)
        else:
            for role in ("thesis", "claim", "evidence", "analysis", "limitation", "synthesis"):
                for value in raw_block.get(role, []) if isinstance(raw_block.get(role), list) else ([raw_block.get(role)] if raw_block.get(role) else []):
                    segment = _segment_from_value(value, block_id, len(segments) + 1, role)
                    if segment:
                        segments.append(segment)
            if not segments and raw_block.get("text"):
                segment = _segment_from_value(raw_block, block_id, 1)
                if segment:
                    segments.append(segment)
        if not segments:
            raise ValueError(f"canonical essay block {block_id} has no text")
        blocks.append({
            "block_id": block_id,
            "paragraph_function": re.sub(r"\s+", " ", str(raw_block.get("paragraph_function") or raw_block.get("function") or "")).strip(),
            "adaptation_notes": _essay_text_list(raw_block.get("adaptation_notes")),
            "segments": segments,
        })
    return {
        "title": re.sub(r"\s+", " ", str(payload.get("title") or "Example Essay")).strip(),
        "question": re.sub(r"\s+", " ", str(payload.get("question") or "")).strip(),
        "blocks": blocks,
    }


def normalize_essay_body(payload: dict[str, Any]) -> dict[str, Any]:
    return normalise_essay_body(payload)


def _block_text(block: dict[str, Any]) -> str:
    return " ".join(str(segment.get("text") or "").strip() for segment in block.get("segments", []) if segment.get("text")).strip()


def _essay_body_text(body: dict[str, Any]) -> str:
    return "\n\n".join(_block_text(block) for block in body.get("blocks", []))


def _body_digest(body: dict[str, Any]) -> str:
    return hashlib.sha256(_essay_body_text(body).encode("utf-8")).hexdigest()


def _render_annotated_paragraphs(paragraphs: Any) -> str:
    if not isinstance(paragraphs, list):
        return ""
    rendered: list[str] = []
    for paragraph in paragraphs:
        if not isinstance(paragraph, dict):
            continue
        rendered.append(f"[Paragraph function: {paragraph.get('paragraph_function') or 'unmarked'}]")
        segments = paragraph.get("segments") if isinstance(paragraph.get("segments"), list) else []
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            raw_annotations = segment.get("annotations")
            annotations = raw_annotations if isinstance(raw_annotations, list) else []
            rendered.append(
                f"[{', '.join(str(annotation) for annotation in annotations) or 'unmarked'}] "
                f"{segment.get('text') or ''}"
            )
        adaptation_notes = paragraph.get("adaptation_notes")
        if isinstance(adaptation_notes, list) and adaptation_notes:
            rendered.append("[Adaptation notes: " + "; ".join(str(note) for note in adaptation_notes) + "]")
        rendered.append("")
    return "\n".join(rendered).strip()


def _paragraph_annotation_metadata(paragraphs: Any) -> list[Any]:
    if not isinstance(paragraphs, list):
        return []
    fields = ("block_id", "paragraph_function", "adaptation_notes")
    return [
        {field: paragraph[field] for field in fields if field in paragraph}
        if isinstance(paragraph, dict)
        else None
        for paragraph in paragraphs
    ]


def _segment_annotation_metadata(paragraphs: Any) -> list[Any]:
    if not isinstance(paragraphs, list):
        return []
    projection: list[Any] = []
    for paragraph in paragraphs:
        if not isinstance(paragraph, dict) or not isinstance(paragraph.get("segments"), list):
            projection.append(None)
            continue
        projection.append([
            {key: value for key, value in segment.items() if key != "text"}
            if isinstance(segment, dict)
            else None
            for segment in paragraph["segments"]
        ])
    return projection


def render_clean_essay(body: dict[str, Any]) -> dict[str, Any]:
    paragraphs = [{"block_id": block["block_id"], "text": _block_text(block)} for block in body.get("blocks", [])]
    projected = {"blocks": [{"segments": [{"text": paragraph["text"]}]} for paragraph in paragraphs]}
    return {
        "view": "clean",
        "title": body.get("title"),
        "question": body.get("question"),
        "paragraphs": paragraphs,
        "rendered_text": "\n\n".join(paragraph["text"] for paragraph in paragraphs),
        "body_sha256": _body_digest(projected),
    }


def render_annotated_essay(body: dict[str, Any]) -> dict[str, Any]:
    paragraphs = []
    for block in body.get("blocks", []):
        paragraph = {
            "block_id": block["block_id"],
            "paragraph_function": block.get("paragraph_function"),
            "adaptation_notes": block.get("adaptation_notes", []),
            "segments": block.get("segments", []),
        }
        paragraphs.append(paragraph)
    projected = {"blocks": [{"segments": [{"text": segment.get("text") or ""} for segment in block.get("segments", [])]} for block in paragraphs]}
    return {
        "view": "annotated_teaching",
        "title": body.get("title"),
        "question": body.get("question"),
        "paragraphs": paragraphs,
        "rendered_text": _render_annotated_paragraphs(paragraphs),
        "body_sha256": _body_digest(projected),
    }


def _is_past_paper_source(document: dict[str, Any]) -> bool:
    signals = document.get("question_signals") if isinstance(document.get("question_signals"), dict) else {}
    if signals.get("has_past_paper") or signals.get("has_mock_paper") or signals.get("has_official_exam_paper"):
        return True
    source_roles = {
        str(document.get(field) or "").casefold()
        for field in ("exam_source_role", "declared_source_role", "source_role", "source_type", "category", "source_hint")
    }
    name = str(document.get("name") or document.get("path") or "").casefold()
    paper_roles = {
        "formal_past_paper", "past_paper", "mock_paper", "specimen_paper",
        "official_mock_specimen", "official_mock_or_specimen",
    }
    return bool(source_roles & paper_roles) or bool(re.search(r"\bpast[ -]?paper\b|\bmock[ -]?paper\b|\bexam[ -]?paper\b", name))


def _normalise_locator(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().casefold()


def _fragment_locator_keys(fragment: dict[str, Any]) -> set[str]:
    values: list[Any] = [fragment.get("locator")]
    provenance = fragment.get("provenance") if isinstance(fragment.get("provenance"), dict) else {}
    values.append(provenance.get("locator"))
    for key, prefix in (
        ("page_number", "page"),
        ("slide_number", "slide"),
        ("paragraph_start", "paragraph"),
        ("time_offset_seconds", "timestamp"),
    ):
        value = fragment.get(key, provenance.get(key))
        if value not in (None, ""):
            values.append(f"{prefix} {value}")
    if fragment.get("heading_path"):
        heading_path = fragment["heading_path"]
        values.append(" > ".join(str(item) for item in heading_path) if isinstance(heading_path, list) else heading_path)
    if fragment.get("time_range") or provenance.get("time_range"):
        values.append(fragment.get("time_range") or provenance.get("time_range"))
    return {normalised for value in values if (normalised := _normalise_locator(value))}


def _canonical_evidence_text(value: Any) -> str:
    text = str(value or "").casefold().replace("μ", "u").replace("µ", "u")
    text = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"\1 percent", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _value_in_fragment_texts(value: str, fragment_texts: list[str]) -> bool:
    raw = re.sub(r"\s+", " ", value).strip().casefold()
    canonical = _canonical_evidence_text(value)
    for fragment_text in fragment_texts:
        compact_fragment = re.sub(r"\s+", " ", fragment_text).strip().casefold()
        if raw and raw in compact_fragment:
            return True
        if canonical and canonical in _canonical_evidence_text(fragment_text):
            return True
    return False


def _evidence_tokens(value: str) -> set[str]:
    tokens: set[str] = set()
    for raw in re.findall(r"[A-Za-z][A-Za-z-]{2,}", value.casefold()):
        if raw in EVIDENCE_TOKEN_STOPWORDS:
            continue
        token = raw
        if token.endswith("ing") and len(token) > 6:
            token = token[:-3]
        elif token.endswith("ed") and len(token) > 5:
            token = token[:-2]
        elif token.endswith("es") and len(token) > 5:
            token = token[:-2]
        elif token.endswith("s") and len(token) > 4:
            token = token[:-1]
        elif token.endswith("e") and len(token) > 4:
            token = token[:-1]
        if token:
            tokens.add(token)
    return tokens


def _result_sentence_supported(sentence: str, fragment_texts: list[str]) -> bool:
    if _value_in_fragment_texts(sentence, fragment_texts):
        return True
    claim_tokens = _evidence_tokens(sentence)
    if len(claim_tokens) < 3:
        return False
    for fragment_text in fragment_texts:
        overlap = claim_tokens & _evidence_tokens(fragment_text)
        if len(overlap) >= 3 and len(overlap) / len(claim_tokens) >= 0.55:
            return True
    return False


def audit_essay_sources(body: dict[str, Any], source_scan: dict[str, Any] | None) -> dict[str, Any]:
    source_scan = source_scan or {"documents": [], "fragments": []}
    documents = source_scan.get("documents", [])
    fragments = [fragment for fragment in source_scan.get("fragments", []) if isinstance(fragment, dict)]
    by_id = {str(document.get("id") or document.get("source_id") or ""): document for document in documents}
    by_name = {str(document.get("name") or "").casefold(): document for document in documents if document.get("name")}
    fragments_by_source: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for fragment in fragments:
        source_id = str(fragment.get("source_id") or "")
        source_name = str(fragment.get("source_name") or "").casefold()
        if source_id:
            fragments_by_source[source_id].append(fragment)
        if source_name:
            fragments_by_source[source_name].append(fragment)
    issues: list[dict[str, str]] = []
    course_source_ids: set[str] = set()
    past_paper_source_ids: set[str] = set()
    for block in body.get("blocks", []):
        for segment in block.get("segments", []):
            resolved_non_past = False
            factual_fragment_texts: list[str] = []
            for ref in segment.get("source_refs", []):
                source_id = str(ref.get("source_id") or "")
                source_name = str(ref.get("source_name") or "")
                document = by_id.get(source_id) or by_name.get(source_name.casefold())
                if not document:
                    issues.append({
                        "code": "unknown_source_reference",
                        "block_id": str(block.get("block_id") or ""),
                        "segment_id": str(segment.get("segment_id") or ""),
                        "source": source_id or source_name,
                    })
                    continue
                resolved_id = str(document.get("id") or document.get("source_id") or source_id or source_name)
                candidate_fragments = list(fragments_by_source.get(resolved_id, []))
                if not candidate_fragments and source_name:
                    candidate_fragments = list(fragments_by_source.get(source_name.casefold(), []))
                requested_locator = _normalise_locator(ref.get("locator"))
                if requested_locator:
                    resolved_fragments = [
                        fragment
                        for fragment in candidate_fragments
                        if requested_locator in _fragment_locator_keys(fragment)
                    ]
                else:
                    resolved_fragments = candidate_fragments if len(candidate_fragments) == 1 else []
                if not resolved_fragments:
                    issues.append({
                        "code": "unresolved_source_locator",
                        "block_id": str(block.get("block_id") or ""),
                        "segment_id": str(segment.get("segment_id") or ""),
                        "source": resolved_id,
                        "locator": str(ref.get("locator") or ""),
                    })
                    continue
                is_past_paper = _is_past_paper_source(document)
                if is_past_paper:
                    past_paper_source_ids.add(resolved_id)
                    if str(ref.get("usage") or "") not in PAST_PAPER_SOURCE_USES:
                        issues.append({
                            "code": "past_paper_used_as_factual_evidence",
                            "block_id": str(block.get("block_id") or ""),
                            "segment_id": str(segment.get("segment_id") or ""),
                            "source": resolved_id,
                        })
                else:
                    resolved_non_past = True
                    course_source_ids.add(resolved_id)
                    factual_fragment_texts.extend(str(fragment.get("text") or "") for fragment in resolved_fragments)
            if "evidence" in set(segment.get("annotations") or []) and not resolved_non_past:
                issues.append({
                    "code": "evidence_without_course_source",
                    "block_id": str(block.get("block_id") or ""),
                    "segment_id": str(segment.get("segment_id") or ""),
                })
            verification_values = []
            for field in ("citation", "doi", "reported_result"):
                if segment.get(field):
                    verification_values.append((field, str(segment[field])))
            for doi in re.findall(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", str(segment.get("text") or ""), flags=re.I):
                verification_values.append(("doi", doi.rstrip(".,;:)")))
            for citation in re.findall(r"\b[A-Z][A-Za-z'’-]+(?:\s+(?:et\s+al\.|and\s+[A-Z][A-Za-z'’-]+))?,\s*(?:19|20)\d{2}\b", str(segment.get("text") or "")):
                verification_values.append(("citation", citation))
            for field, value in verification_values:
                if not _value_in_fragment_texts(value, factual_fragment_texts):
                    issues.append({
                        "code": f"unverified_{field}",
                        "block_id": str(block.get("block_id") or ""),
                        "segment_id": str(segment.get("segment_id") or ""),
                        "value": value,
                    })
            segment_text = str(segment.get("text") or "")
            for quantitative_value in QUANTITATIVE_CLAIM_PATTERN.findall(segment_text):
                if not _value_in_fragment_texts(quantitative_value, factual_fragment_texts):
                    issues.append({
                        "code": "unsupported_quantitative_claim",
                        "block_id": str(block.get("block_id") or ""),
                        "segment_id": str(segment.get("segment_id") or ""),
                        "value": quantitative_value,
                    })
            result_sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", segment_text)
                if EMPIRICAL_RESULT_CUE.search(sentence)
            ]
            for sentence in result_sentences:
                if not _result_sentence_supported(sentence, factual_fragment_texts):
                    issues.append({
                        "code": "unsupported_result_claim",
                        "block_id": str(block.get("block_id") or ""),
                        "segment_id": str(segment.get("segment_id") or ""),
                        "value": sentence,
                    })
    unique_issues: list[dict[str, str]] = []
    seen = set()
    for issue in issues:
        key = json.dumps(issue, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)
    return {
        "status": "grounded" if not unique_issues else "needs_review",
        "issues": unique_issues,
        "course_source_ids": sorted(course_source_ids),
        "past_paper_source_ids": sorted(past_paper_source_ids),
        "past_paper_use": "question_scope_and_emphasis_only",
        "fabricated_citations_added": False,
    }


def validate_essay_views(package: dict[str, Any]) -> dict[str, Any]:
    body = package.get("canonical_body") or {}
    clean = package.get("views", {}).get("clean") or {}
    annotated = package.get("views", {}).get("annotated") or {}
    canonical_blocks = body.get("blocks", [])
    annotated_paragraphs = annotated.get("paragraphs", [])
    canonical_digest = _body_digest(body)
    clean_text = "\n\n".join(str(paragraph.get("text") or "") for paragraph in clean.get("paragraphs", []))
    annotated_text = "\n\n".join(
        " ".join(str(segment.get("text") or "") for segment in paragraph.get("segments", []))
        for paragraph in annotated_paragraphs
    )
    clean_digest = hashlib.sha256(clean_text.encode("utf-8")).hexdigest()
    annotated_digest = hashlib.sha256(annotated_text.encode("utf-8")).hexdigest()
    declared_digests_match = (
        str(clean.get("body_sha256") or "") == clean_digest
        and str(annotated.get("body_sha256") or "") == annotated_digest
    )
    paragraph_metadata_matches = (
        _paragraph_annotation_metadata(canonical_blocks)
        == _paragraph_annotation_metadata(annotated_paragraphs)
    )
    segment_metadata_matches = (
        _segment_annotation_metadata(canonical_blocks)
        == _segment_annotation_metadata(annotated_paragraphs)
    )
    annotated_metadata_matches = paragraph_metadata_matches and segment_metadata_matches
    annotated_rendered_text_matches = (
        str(annotated.get("rendered_text") or "")
        == _render_annotated_paragraphs(annotated_paragraphs)
    )
    annotation_types: set[str] = set()
    for paragraph in annotated_paragraphs:
        if not isinstance(paragraph, dict):
            continue
        if paragraph.get("paragraph_function"):
            annotation_types.add("paragraph_function")
        if paragraph.get("adaptation_notes"):
            annotation_types.add("adaptation_notes")
        segments = paragraph.get("segments") if isinstance(paragraph.get("segments"), list) else []
        for segment in segments:
            if not isinstance(segment, dict):
                continue
            annotations = segment.get("annotations")
            if isinstance(annotations, list):
                annotation_types.update(str(annotation) for annotation in annotations)
    missing = sorted(ESSAY_REQUIRED_ANNOTATIONS - annotation_types)
    shared_body = canonical_digest == clean_digest == annotated_digest and declared_digests_match
    annotation_coverage_complete = not missing
    return {
        "valid": (
            shared_body
            and annotation_coverage_complete
            and annotated_metadata_matches
            and annotated_rendered_text_matches
        ),
        "shared_body": shared_body,
        "canonical_body_sha256": canonical_digest,
        "clean_body_sha256": clean_digest,
        "annotated_body_sha256": annotated_digest,
        "annotated_paragraph_metadata_matches_canonical": paragraph_metadata_matches,
        "annotated_segment_metadata_matches_canonical": segment_metadata_matches,
        "annotated_metadata_matches_canonical": annotated_metadata_matches,
        "annotated_rendered_text_matches_metadata": annotated_rendered_text_matches,
        "annotation_types_present": sorted(annotation_types),
        "missing_annotation_types": missing,
        "annotation_coverage_complete": annotation_coverage_complete,
    }


def build_essay_views(payload: dict[str, Any], source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    refusal = _essay_view_lifecycle_refusal(payload)
    if refusal:
        return refusal
    body = normalise_essay_body(payload)
    package = {
        "schema_version": ESSAY_VIEW_SCHEMA_VERSION,
        "task_mode": "example_essay",
        "document_kind": "example_essay_views",
        "canonical_body": body,
        "views": {
            "clean": render_clean_essay(body),
            "annotated": render_annotated_essay(body),
        },
        "source_policy": {
            "course_sources": "primary_basis_for_course_facts_and_scope",
            "past_papers": "question_scope_and_emphasis_only",
            "external_evidence": "use_only_when_supplied_and_verifiable",
            "invented_citations_results_or_dois": "prohibited",
        },
        "source_audit": audit_essay_sources(body, source_scan),
    }
    package["view_integrity"] = validate_essay_views(package)
    package["status"] = (
        "ready"
        if package["view_integrity"]["shared_body"]
        and package["view_integrity"]["annotation_coverage_complete"]
        and package["view_integrity"]["annotated_metadata_matches_canonical"]
        and package["view_integrity"]["annotated_rendered_text_matches_metadata"]
        and package["source_audit"]["status"] == "grounded"
        else "needs_review"
    )
    return package


def build_example_essay_views(payload: dict[str, Any], source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_essay_views(payload, source_scan)


def build_essay_pack(
    question: str | None = None,
    readings: str | None = None,
    source_scan: dict[str, Any] | None = None,
    extra_reading: dict[str, Any] | None = None,
) -> dict[str, Any]:
    text = "\n".join(part for part in [readings or "", scan_text(source_scan)] if part)
    topics = frequent_topics(text)
    extra_topics = extra_reading_topics(extra_reading)
    combined_topics = []
    for topic in topics + extra_topics:
        if topic and topic not in combined_topics:
            combined_topics.append(topic)
    topics = combined_topics or ["core module theme"]

    essay_questions = []
    for topic in topics[:4]:
        essay_questions.append({
            "module_topic": topic,
            "question": question or f"Discuss how {topic} can be used to explain a major issue in this module.",
            "coverage_use": "Broad question for practising argument structure across the module.",
        })

    slots = extra_reading_slots(extra_reading)
    paragraphs = []
    for idx, topic in enumerate(topics[:4]):
        slot = slots[idx] if idx < len(slots) else {}
        extra_detail = slot.get("extra_reading_detail") or slot.get("paragraph_role") or "No external evidence is added unless the source is supplied and verifiable."
        paragraphs.append({
            "topic": topic,
            "paragraph": f"A strong exam paragraph on {topic} should begin with a direct claim, explain the relevant course mechanism, use only supplied source-grounded evidence, analyse how that evidence affects the argument, and link back to the question.",
            "extra_reading_slot": {
                "role": slot.get("paragraph_role", "supplied and verified external evidence only"),
                "detail": extra_detail,
            },
        })

    return {
        "schema_version": 3,
        "essay_questions": essay_questions,
        "thesis_options": [f"The strongest answer should treat {topics[0]} as a central organising idea and ground its mechanism and factual scope in the supplied course sources."],
        "exam_ready_paragraphs": paragraphs,
        "extra_reading_paragraph_slots": slots,
        "example_essay_plan": {
            "introduction": "Define the argument and answer the question directly.",
            "body": [p["topic"] for p in paragraphs],
            "extra_reading_use": "Use external evidence only when it was supplied and its identity and claim support can be verified; never invent a citation, DOI, or result.",
            "conclusion": "Return to the question and state the final judgement.",
        },
        "source_policy": {
            "course_sources": "primary_basis_for_course_facts_and_scope",
            "past_papers": "question_scope_and_emphasis_only",
        },
    }


def lint_language(text: str) -> dict[str, Any]:
    suggestions = []
    if len(text.split()) < 120:
        suggestions.append("essay_answer_may_be_too_short")
    if text.count("\n-") > 6:
        suggestions.append("essay_answer_reads_like_list")
    if not re.search(r"\btherefore\b|\bhowever\b|\bconsequently\b|\bthis shows\b", text, re.I):
        suggestions.append("add_more_argument_links")
    return {"status": "ok" if not suggestions else "suggestions", "suggestions": suggestions}


def self_test() -> None:
    pack = build_essay_pack(readings="enzyme enzyme potency efficacy argument", extra_reading={"essay_enrichment": {"paragraph_slots": [{"topic": "enzyme", "extra_reading_detail": "primary research evidence"}]}})
    assert pack["essay_questions"]
    assert lint_language("short")["suggestions"]
    scan = {
        "documents": [{"id": "S1", "name": "Review.pdf", "source_hint": "extra_reading_source"}],
        "fragments": [{"source_id": "S1", "locator": "page 1", "text": "Receptor signalling mechanism and experimental evidence."}],
    }
    discovery = discover_extra_reading(scan)
    assert discovery["supplied_extra_reading"][0]["source_name"] == "Review.pdf"
    assert build_extra_reading_enrichment(discovery)["essay_enrichment"]["paragraph_slots"]
    active_plan = online_essay_permission_status(
        {"assessment_state": "active"},
        requested_actions=["plan"],
    )
    assert active_plan["status"] == "ready"
    assert "plan" in active_plan["allowed_actions"]
    assert not active_plan["gaps"]
    active_draft_unknown = online_essay_permission_status(
        {"assessment_state": "active"},
        requested_actions=["complete_draft"],
    )
    assert active_draft_unknown["status"] == "restricted"
    assert active_draft_unknown["blocked_actions"][0]["reason"] == "active_assessed_complete_draft_out_of_scope"
    active_draft_denied = online_essay_permission_status(
        {"assessment_state": "active", "complete_draft": "denied"},
        requested_actions=["complete_draft"],
    )
    assert active_draft_denied["status"] == "restricted"
    assert active_draft_denied["blocked_actions"][0]["reason"] == "active_assessed_complete_draft_out_of_scope"
    active_draft_allowed = online_essay_permission_status(
        {"assessment_state": "active", "complete_draft": "allowed"},
        requested_actions=["complete_draft"],
    )
    assert active_draft_allowed["status"] == "restricted"
    assert "complete_draft" not in active_draft_allowed["allowed_actions"]
    assert active_draft_allowed["complete_draft"] == "denied_by_scope"
    closed_draft = online_essay_permission_status(
        {"assessment_state": "closed"},
        requested_actions=["complete_draft"],
    )
    assert closed_draft["status"] == "ready"
    assert closed_draft["action_conditions"]["complete_draft"].startswith("post_assessment")
    closed_unknown_action = online_essay_permission_status(
        {"assessment_state": "closed"},
        requested_actions=["unsupported_action"],
    )
    assert closed_unknown_action["status"] == "restricted"
    assert "unsupported_action" not in closed_unknown_action["allowed_actions"]
    assert closed_unknown_action["blocked_actions"][0]["reason"] == "unsupported_or_unclassified_action"
    unknown_draft = online_essay_permission_status(
        {},
        requested_actions=["complete_draft"],
    )
    assert unknown_draft["assessment_state"] == "unknown"
    assert unknown_draft["status"] == "needs_clarification"
    assert unknown_draft["blocked_actions"][0]["reason"] == "assessment_state_unknown"
    unknown_plan = online_essay_permission_status({}, requested_actions=["plan"])
    assert unknown_plan["status"] == "ready"
    assert unknown_plan["gaps"] == []
    assert unknown_plan["advisories"][0]["field"] == "assessment_state"
    external_without_citation_rule = online_essay_permission_status(
        {"assessment_state": "active", "external_sources": "allowed"},
        requested_actions=["use_external_sources"],
    )
    assert external_without_citation_rule["status"] == "needs_clarification"
    assert external_without_citation_rule["gaps"][0]["field"] == "citation_expectations"
    view_scan = {
        "documents": [
            {"id": "L1", "name": "Lecture 1.pdf", "category": "knowledge_material"},
            {"id": "P1", "name": "Past Paper 2025.pdf", "source_type": "formal_past_paper"},
        ],
        "fragments": [
            {"source_id": "L1", "text": "Selective permeability and ion gradients determine membrane potential."},
            {"source_id": "P1", "text": "Discuss how selective permeability shapes membrane potential."},
        ],
    }
    view_payload = {
        "title": "Membrane Potential",
        "question": "Discuss how selective permeability shapes membrane potential.",
        "canonical_body": {"blocks": [{
            "block_id": "P1",
            "paragraph_function": "introduce the answer and establish the judgement",
            "adaptation_notes": ["Narrow the mechanism if the exam question specifies one ion."],
            "segments": [
                {"text": "Selective permeability is the central organising mechanism.", "annotation": "thesis", "source_refs": [{"source_id": "P1", "usage": "scope"}]},
                {"text": "The membrane is more permeable to some ions than others.", "annotation": "claim", "source_refs": ["L1"]},
                {"text": "Course material links ion gradients and selective permeability to membrane potential.", "annotation": "evidence", "source_refs": ["L1"]},
                {"text": "This means diffusion and charge separation must be analysed together.", "annotation": "analysis"},
                {"text": "The explanation is limited if changing permeability over time is ignored.", "annotation": "limitation", "source_refs": ["L1"]},
                {"text": "Therefore the final judgement depends on both the gradient and relative permeability.", "annotation": "synthesis", "source_refs": ["L1"]},
            ],
        }]},
    }
    views = build_essay_views(view_payload, view_scan)
    assert views["status"] == "ready"
    assert views["view_integrity"]["shared_body"]
    assert views["view_integrity"]["annotation_coverage_complete"]
    assert views["source_audit"]["past_paper_use"] == "question_scope_and_emphasis_only"
    assert views["views"]["clean"]["body_sha256"] == views["views"]["annotated"]["body_sha256"]
    bad_payload = json.loads(json.dumps(view_payload))
    bad_payload["canonical_body"]["blocks"][0]["segments"][2]["source_refs"] = [{"source_id": "P1", "usage": "course_fact"}]
    bad_payload["canonical_body"]["blocks"][0]["segments"][2]["text"] += " (Fictional, 2026; 10.1234/not-real)."
    bad_views = build_essay_views(bad_payload, view_scan)
    issue_codes = {item["code"] for item in bad_views["source_audit"]["issues"]}
    assert "past_paper_used_as_factual_evidence" in issue_codes
    assert "unverified_doi" in issue_codes
    assert "unverified_citation" in issue_codes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="generate-plan")
    parser.add_argument("--plan")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--source-scan")
    parser.add_argument("--extra-reading")
    parser.add_argument("--out")
    parser.add_argument("--question")
    parser.add_argument("--readings")
    parser.add_argument("--permissions")
    parser.add_argument("--assessment-state", choices=("active", "closed", "unknown"))
    parser.add_argument("--requested-action", action="append")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.command == "lint-language":
        text = Path(args.input).read_text(encoding="utf-8", errors="ignore") if args.input else ""
        result = lint_language(text)
    elif args.command == "build-essay-views":
        payload = load_json(args.input)
        if not isinstance(payload, dict):
            parser.error("build-essay-views requires --input")
        result = build_essay_views(payload, load_json(args.source_scan))
    elif args.command == "discover-extra-reading":
        result = discover_extra_reading(load_json(args.source_scan))
    elif args.command == "enrich-extra-reading":
        discovery = load_json(args.input)
        if not isinstance(discovery, dict):
            parser.error("enrich-extra-reading requires --input")
        result = build_extra_reading_enrichment(discovery)
    elif args.command == "check-online-permissions":
        result = online_essay_permission_status(
            load_json(args.permissions),
            assessment_state=args.assessment_state,
            requested_actions=args.requested_action,
        )
    else:
        readings = args.readings or (Path(args.input).read_text(encoding="utf-8", errors="ignore") if args.input else "")
        result = build_essay_pack(args.question, readings, load_json(args.source_scan), load_json(args.extra_reading))
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    target = args.output or args.out
    if target:
        Path(target).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
