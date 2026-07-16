#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any

STOPWORDS = {"lecture", "module", "question", "answer", "using", "explain", "describe", "compare", "evaluate", "discuss", "material", "course", "student"}


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


def online_essay_permission_status(permissions: dict[str, Any] | None) -> dict[str, Any]:
    permissions = permissions or {}
    required = ("lecture_materials", "online_materials", "external_sources", "complete_draft")
    unresolved = [key for key in required if permissions.get(key) in (None, "", "unclear")]
    return {
        "status": "ready" if not unresolved else "needs_clarification",
        "unresolved": unresolved,
        "allowed_sources": [
            key for key in ("lecture_materials", "online_materials", "uploaded_readings", "external_sources")
            if permissions.get(key) in (True, "allowed", "yes")
        ],
        "complete_draft": permissions.get("complete_draft"),
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
    assert online_essay_permission_status({"lecture_materials": "allowed"})["status"] == "needs_clarification"


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
        result = online_essay_permission_status(load_json(args.permissions))
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
