#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
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
        "complete_draft": permission_state(permissions.get("complete_draft")),
    }


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
        extra_detail = slot.get("extra_reading_detail") or slot.get("paragraph_role") or "Use Extra Reading where it strengthens the paragraph."
        paragraphs.append({
            "topic": topic,
            "paragraph": f"A strong exam paragraph on {topic} should begin with a direct claim, explain the relevant lecture mechanism, add extra reading evidence, analyse why that evidence strengthens the argument, and link back to the question.",
            "extra_reading_slot": {
                "role": slot.get("paragraph_role", "extra reading evidence and analysis"),
                "detail": extra_detail,
            },
        })

    return {
        "schema_version": 3,
        "essay_questions": essay_questions,
        "thesis_options": [f"The strongest answer should treat {topics[0]} as a central organising idea and use Extra Reading to deepen the mechanism or evidence."],
        "exam_ready_paragraphs": paragraphs,
        "extra_reading_paragraph_slots": slots,
        "example_essay_plan": {
            "introduction": "Define the argument and answer the question directly.",
            "body": [p["topic"] for p in paragraphs],
            "extra_reading_use": "Place Extra Reading in selected body paragraphs as mechanism depth, molecular evidence, experimental support, counterargument, or evaluation.",
            "conclusion": "Return to the question and state the final judgement.",
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
    assert active_draft_unknown["status"] == "needs_clarification"
    assert active_draft_unknown["gaps"][0]["field"] == "complete_draft"
    active_draft_denied = online_essay_permission_status(
        {"assessment_state": "active", "complete_draft": "denied"},
        requested_actions=["complete_draft"],
    )
    assert active_draft_denied["status"] == "restricted"
    assert active_draft_denied["blocked_actions"][0]["reason"] == "complete_draft_explicitly_denied"
    active_draft_allowed = online_essay_permission_status(
        {"assessment_state": "active", "complete_draft": "allowed"},
        requested_actions=["complete_draft"],
    )
    assert active_draft_allowed["status"] == "ready"
    assert "complete_draft" in active_draft_allowed["allowed_actions"]
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
