#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any

BOOK_HEADINGS = [
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
PAPER_HEADINGS = ["doi", "pmid", "journal", "reference", "references", "source", "sources"]
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


def extract_book_mentions(scan: dict[str, Any], lecture_topics: list[str]) -> list[dict[str, Any]]:
    mentions: list[dict[str, Any]] = []
    docs = document_lookup(scan)
    for frag in scan.get("fragments", []):
        text = str(frag.get("text") or "")
        hint = str(frag.get("source_hint") or frag.get("category") or "")
        source = docs.get(str(frag.get("source_id")), {})
        lower = text.lower()
        if hint == "extra_reading_book":
            mentions.append({
                "kind": "book",
                "title": source.get("name") or frag.get("source_name") or "Uploaded book material",
                "author_or_editor": "",
                "chapter_or_section": "",
                "mentioned_in": f"{frag.get('source_name')} {frag.get('locator')}",
                "linked_lecture_topics": topic_overlap(text, lecture_topics),
                "snippet": re.sub(r"\s+", " ", text)[:350],
            })
            continue
        if hint == "knowledge_material" and any(marker in lower for marker in BOOK_HEADINGS):
            mentions.append({
                "kind": "book",
                "title": nearby_snippet(text, "book") if "book" in lower else nearby_snippet(text, "reading"),
                "author_or_editor": "",
                "chapter_or_section": nearby_snippet(text, "chapter") if "chapter" in lower else "",
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


def extract_paper_mentions(scan: dict[str, Any], lecture_topics: list[str]) -> list[dict[str, Any]]:
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
        has_paper_marker = doi or pmid or author_year or any(marker in lower for marker in PAPER_HEADINGS)
        if hint == "extra_reading_paper" or (hint == "knowledge_material" and has_paper_marker):
            year = YEAR_RE.search(text)
            mentions.append({
                "kind": "academic_paper",
                "title": source.get("name") if hint == "extra_reading_paper" else nearby_snippet(text, "doi") if doi else nearby_snippet(text, "reference"),
                "authors": author_year.group(0) if author_year else "",
                "year": year.group(0) if year else "",
                "journal": nearby_snippet(text, "journal") if "journal" in lower else "",
                "doi_or_url": doi.group(0) if doi else pmid.group(0) if pmid else "",
                "evidence_type": infer_evidence_type(text),
                "linked_lecture_topics": topic_overlap(text, lecture_topics),
                "use_in_notes": "Add mechanism detail, molecular evidence, experimental evidence, or research support to the linked topic.",
                "mentioned_in": f"{frag.get('source_name')} {frag.get('locator')}",
                "snippet": re.sub(r"\s+", " ", text)[:350],
            })
    return mentions


def lecture_topics(scan: dict[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    text = fragment_text(scan, {"knowledge_material"}) or fragment_text(scan)
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
    return {
        "schema_version": 2,
        "book_mentions": extract_book_mentions(scan, topic_names),
        "paper_mentions": extract_paper_mentions(scan, topic_names),
        "lecture_topics": topics,
        "search_queries": generate_queries(topics),
    }


def topic_enrichment(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    topics = [item["topic"] if isinstance(item, dict) else str(item) for item in discovery.get("lecture_topics", [])]
    for topic in topics:
        book_hits = [m for m in discovery.get("book_mentions", []) if topic in m.get("linked_lecture_topics", [])]
        paper_hits = [m for m in discovery.get("paper_mentions", []) if topic in m.get("linked_lecture_topics", [])]
        records.append({
            "lecture_topic": topic,
            "core_lecture_explanation": f"Explain the lecture material on {topic} in exam-focused language.",
            "book_enrichment": [m.get("snippet") or m.get("title") for m in book_hits],
            "paper_enrichment": [m.get("snippet") or m.get("title") for m in paper_hits],
            "molecular_or_mechanism_detail": [f"Use extra reading to add molecular or mechanism detail for {topic}."] if book_hits or paper_hits else [],
            "experimental_evidence_support": [m.get("use_in_notes", "Use the paper as experimental evidence support.") for m in paper_hits],
            "exam_use": f"Use the enriched {topic} material to improve explanations, essay paragraphs, and answer depth.",
        })
    return records


def essay_enrichment(enrichment: list[dict[str, Any]]) -> dict[str, Any]:
    slots = []
    for item in enrichment[:6]:
        topic = item.get("lecture_topic", "topic")
        detail = " ".join((item.get("book_enrichment") or item.get("paper_enrichment") or item.get("molecular_or_mechanism_detail") or [""])[:1])
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
        "book_mentions": discovery.get("book_mentions", []),
        "paper_mentions": discovery.get("paper_mentions", []),
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
            "documents": [{"id": "S1", "name": "Lecture 1", "source_hint": "knowledge_material"}],
            "fragments": [{"source_id": "S1", "source_name": "Lecture 1", "source_hint": "knowledge_material", "locator": "chunk 1", "text": "Recommended reading: Molecular Biology textbook Chapter 2. DOI 10.1000/test shows receptor mechanism results."}],
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
