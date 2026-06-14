#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any

BACKGROUND_SOURCE_MARKERS = [
    "extra reading recommendation",
    "recommended reading",
    "further reading",
    "source",
    "sources",
    "references",
    "textbook",
    "book",
    "chapter",
]
RESEARCH_SOURCE_MARKERS = ["doi", "pmid", "journal", "reference", "references", "source", "sources"]
STOPWORDS = {
    "lecture", "module", "course", "student", "question", "answer", "material", "using", "these", "those", "there", "their",
    "which", "about", "should", "would", "could", "because", "chapter", "source", "references", "reading", "abstract",
    "methods", "results", "discussion", "figure", "table", "study", "paper", "book", "textbook",
}
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
PMID_RE = re.compile(r"\bPMID\s*:?\s*\d+", re.I)
AUTHOR_YEAR_RE = re.compile(r"\b[A-Z][A-Za-z\-]+\s+et\s+al\.?\s*\(?\d{4}\)?|\b[A-Z][A-Za-z\-]+\s*\(\d{4}\)")
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def load_scan(path: str | None) -> dict[str, Any]:
    if not path:
        return {"documents": [], "fragments": []}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fragment_text(scan: dict[str, Any], hints: set[str] | None = None) -> str:
    parts = []
    for frag in scan.get("fragments", []):
        hint = str(frag.get("source_hint") or frag.get("category") or "")
        if hints is None or hint in hints:
            parts.append(str(frag.get("text") or ""))
    return "\n".join(parts)


def course_signal_text(scan: dict[str, Any]) -> str:
    signal_roles = {
        "concept",
        "mechanism",
        "method",
        "comparison",
        "calculation",
        "data_interpretation",
        "evidence",
        "exam_application",
        "dense_academic_content",
        "coverage_target",
    }
    parts = []
    for frag in scan.get("fragments", []):
        roles = set(frag.get("knowledge_roles", []) or [])
        signals = set(frag.get("knowledge_signals", []) or [])
        if roles & signal_roles or signals:
            parts.append(str(frag.get("text") or ""))
    return "\n".join(parts) or fragment_text(scan)


def words(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-]{4,}", text or "") if w.lower() not in STOPWORDS]


def frequent_topics(text: str, limit: int = 12) -> list[str]:
    counts = collections.Counter(words(text))
    return [term for term, _ in counts.most_common(limit)]


def nearby_snippet(text: str, term: str, width: int = 220) -> str:
    lower = text.lower()
    idx = lower.find(term.lower())
    if idx < 0:
        return text[:width].strip()
    start = max(0, idx - width // 2)
    end = min(len(text), idx + width // 2)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def topic_overlap(text: str, topics: list[str], limit: int = 4) -> list[str]:
    lower = (text or "").lower()
    matched = [topic for topic in topics if topic.lower() in lower]
    if matched:
        return matched[:limit]
    text_words = set(words(text))
    scored = [(topic, 1 if topic.lower() in text_words else 0) for topic in topics]
    return [topic for topic, score in scored if score][:limit]


def document_lookup(scan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(doc.get("id")): doc for doc in scan.get("documents", [])}


def extract_background_mentions(scan: dict[str, Any], lecture_topics: list[str]) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    docs = document_lookup(scan)
    for frag in scan.get("fragments", []):
        text = str(frag.get("text") or "")
        hint = str(frag.get("source_hint") or frag.get("category") or "")
        source = docs.get(str(frag.get("source_id")), {})
        lower = text.lower()
        if hint == "extra_reading_source" and any(marker in lower for marker in BACKGROUND_SOURCE_MARKERS):
            mentions.append({
                "kind": "extra_reading_source",
                "source_signal": "background_or_textbook_like",
                "title": source.get("name") or frag.get("source_name") or "Uploaded extra reading material",
                "authors_or_editors": "",
                "source_detail": nearby_snippet(text, "chapter") if "chapter" in lower else "",
                "mentioned_in": f"{frag.get('source_name')} {frag.get('locator')}",
                "linked_lecture_topics": topic_overlap(text, lecture_topics),
                "snippet": re.sub(r"\s+", " ", text)[:350],
            })
            continue
        if any(marker in lower for marker in BACKGROUND_SOURCE_MARKERS):
            mentions.append({
                "kind": "extra_reading_source",
                "source_signal": "background_or_textbook_like",
                "title": nearby_snippet(text, "book") if "book" in lower else nearby_snippet(text, "reading"),
                "authors_or_editors": "",
                "source_detail": nearby_snippet(text, "chapter") if "chapter" in lower else "",
                "mentioned_in": f"{frag.get('source_name')} {frag.get('locator')}",
                "linked_lecture_topics": topic_overlap(text, lecture_topics),
                "snippet": re.sub(r"\s+", " ", text)[:350],
            })
    return mentions


def infer_evidence_type(text: str) -> str:
    lower = (text or "").lower()
    if any(term in lower for term in ["mechanism", "pathway", "molecular", "receptor", "protein", "gene"]):
        return "mechanism"
    if any(term in lower for term in ["experiment", "assay", "method", "control", "results"]):
        return "experimental"
    if any(term in lower for term in ["clinical", "patient", "trial", "cohort"]):
        return "clinical"
    return "research"


def extract_research_mentions(scan: dict[str, Any], lecture_topics: list[str]) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    docs = document_lookup(scan)
    for frag in scan.get("fragments", []):
        text = str(frag.get("text") or "")
        hint = str(frag.get("source_hint") or frag.get("category") or "")
        source = docs.get(str(frag.get("source_id")), {})
        lower = text.lower()
        doi = DOI_RE.search(text)
        pmid = PMID_RE.search(text)
        author_year = AUTHOR_YEAR_RE.search(text)
        has_research_marker = doi or pmid or author_year or any(marker in lower for marker in RESEARCH_SOURCE_MARKERS)
        if has_research_marker:
            year = YEAR_RE.search(text)
            mentions.append({
                "kind": "extra_reading_source",
                "source_signal": infer_evidence_type(text),
                "title": source.get("name") if hint == "extra_reading_source" else nearby_snippet(text, "doi") if doi else nearby_snippet(text, "reference"),
                "authors_or_editors": author_year.group(0) if author_year else "",
                "year": year.group(0) if year else "",
                "source_detail": nearby_snippet(text, "journal") if "journal" in lower else "",
                "identifier_or_url": doi.group(0) if doi else pmid.group(0) if pmid else "",
                "evidence_type": infer_evidence_type(text),
                "linked_lecture_topics": topic_overlap(text, lecture_topics),
                "use_in_notes": "Add mechanism detail, molecular evidence, experimental evidence, method support, or research support to the linked topic.",
                "mentioned_in": f"{frag.get('source_name')} {frag.get('locator')}",
                "snippet": re.sub(r"\s+", " ", text)[:350],
            })
    return mentions


def merge_extra_reading_sources(*source_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for group in source_groups:
        for item in group:
            key = (
                str(item.get("title", "")),
                str(item.get("identifier_or_url", "")),
                str(item.get("mentioned_in", "")),
            )
            if key in seen:
                continue
            seen.add(key)
            sources.append(item)
    return sources


def lecture_topics(scan: dict[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    text = course_signal_text(scan)
    topics = frequent_topics(text, limit)
    return [{"topic": topic, "search_seed": topic} for topic in topics]


def generate_queries(topics: list[dict[str, Any]] | list[str], limit: int = 20) -> list[dict[str, str]]:
    topic_names = [item["topic"] if isinstance(item, dict) else str(item) for item in topics]
    queries: list[dict[str, str]] = []
    for topic in topic_names[:limit]:
        queries.extend([
            {"topic": topic, "query": f"{topic} mechanism primary research"},
            {"topic": topic, "query": f"{topic} molecular mechanism experimental evidence"},
            {"topic": topic, "query": f"{topic} recent research academic paper"},
        ])
    return queries[:limit]


def discover(scan: dict[str, Any]) -> dict[str, Any]:
    topics = lecture_topics(scan)
    topic_names = [item["topic"] for item in topics]
    background_sources = extract_background_mentions(scan, topic_names)
    research_sources = extract_research_mentions(scan, topic_names)
    return {
        "schema_version": 2,
        "extra_reading_sources": merge_extra_reading_sources(background_sources, research_sources),
        "lecture_topics": topics,
        "search_queries": generate_queries(topics),
    }


def topic_enrichment(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    topics = [item["topic"] if isinstance(item, dict) else str(item) for item in discovery.get("lecture_topics", [])]
    for topic in topics:
        source_hits = [m for m in discovery.get("extra_reading_sources", []) if topic in m.get("linked_lecture_topics", [])]
        evidence_hits = [m for m in source_hits if m.get("evidence_type") or m.get("identifier_or_url")]
        records.append({
            "lecture_topic": topic,
            "core_lecture_explanation": f"Explain the lecture material on {topic} in student-facing teaching language.",
            "extra_reading_enrichment": [m.get("snippet") or m.get("title") for m in source_hits],
            "background_enrichment": [m.get("snippet") or m.get("title") for m in source_hits if m.get("source_signal") == "background_or_textbook_like"],
            "evidence_enrichment": [m.get("snippet") or m.get("title") for m in evidence_hits],
            "molecular_or_mechanism_detail": [f"Use extra reading to add molecular or mechanism detail for {topic}."] if source_hits else [],
            "experimental_evidence_support": [m.get("use_in_notes", "Use the source as evidence support.") for m in evidence_hits],
            "knowledge_use": f"Use the enriched {topic} material to improve conceptual explanation, mechanism depth, and interpretation.",
        })
    return records


def essay_enrichment(enrichment: list[dict[str, Any]]) -> dict[str, Any]:
    slots = []
    for item in enrichment[:6]:
        topic = item.get("lecture_topic", "topic")
        detail = " ".join((item.get("extra_reading_enrichment") or item.get("molecular_or_mechanism_detail") or [""])[:1])
        slots.append({
            "topic": topic,
            "paragraph_role": "extra reading evidence and analysis",
            "content_target": "Claim from lecture topic, lecture mechanism explanation, extra reading evidence, analysis, link back to the question.",
            "extra_reading_detail": detail,
        })
    return {"extra_reading_blend": "15-30%", "paragraph_slots": slots}


def enrich(discovery: dict[str, Any]) -> dict[str, Any]:
    mapped = topic_enrichment(discovery)
    return {
        "schema_version": 2,
        "extra_reading_sources": discovery.get("extra_reading_sources", []),
        "lecture_topics": discovery.get("lecture_topics", []),
        "search_queries": discovery.get("search_queries", []),
        "topic_enrichment": mapped,
        "essay_enrichment": essay_enrichment(mapped),
    }


def run_command(command: str, source_scan: str | None) -> dict[str, Any]:
    scan = load_scan(source_scan)
    discovered = discover(scan)
    if command == "discover":
        return discovered
    if command == "queries":
        return {"schema_version": 2, "search_queries": discovered["search_queries"]}
    if command == "map":
        return {"schema_version": 2, "topic_enrichment": topic_enrichment(discovered)}
    if command == "enrich":
        return enrich(discovered)
    return enrich(discovered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="all", choices=["discover", "queries", "map", "enrich", "all"])
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        sample = {
            "documents": [{"id": "S1", "name": "Source 1", "source_hint": "knowledge_material"}],
            "fragments": [{"source_id": "S1", "source_name": "Source 1", "source_hint": "knowledge_material", "locator": "chunk 1", "knowledge_signals": ["mechanism", "evidence"], "knowledge_roles": ["mechanism", "evidence"], "text": "Recommended reading: Molecular Biology textbook Chapter 2. DOI 10.1000/test shows receptor mechanism results."}],
        }
        out = enrich(discover(sample))
        assert out["search_queries"]
        assert out["essay_enrichment"]["extra_reading_blend"] == "15-30%"
        return
    result = run_command(args.command, args.source_scan)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
