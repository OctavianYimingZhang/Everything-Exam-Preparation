#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

TEXT_SUFFIXES = {".txt", ".md", ".json", ".yaml", ".yml", ".csv"}
MEDIA_PREFIXES = {".docx": "word/media/", ".pptx": "ppt/media/"}

MARKING_KEYWORDS = ["mark scheme", "markscheme", "answer key", "answers", "solution", "solutions", "examiner feedback"]
PRACTICE_KEYWORDS = ["past paper", "practice", "question paper", "exam paper", "mcq", "sba", "short answer", "essay", "problem sheet", "calculate"]
STYLE_KEYWORDS = ["model answer", "example answer", "style", "sample essay"]
BOOK_KEYWORDS = ["textbook", "book", "chapter", "edition", "publisher", "recommended reading", "further reading"]
PAPER_KEYWORDS = ["doi", "pmid", "journal", "abstract", "methods", "results", "et al", "primary research", "recent research"]
KNOWLEDGE_KEYWORDS = ["lecture", "slides", "notes", "module", "handbook", "practical", "lab", "seminar", "reading"]
AUTHOR_YEAR_RE = re.compile(r"\b[A-Z][A-Za-z\-]+\s+et\s+al\.?\s*\(?\d{4}\)?|\b[A-Z][A-Za-z\-]+\s*\(\d{4}\)")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
PMID_RE = re.compile(r"\bPMID\s*:?\s*\d+", re.I)

KNOWLEDGE_SIGNAL_PATTERNS: dict[str, list[str]] = {
    "heading_or_topic_boundary": [
        r"^\s*(lecture|topic|section|unit|part|chapter)\b",
        r"^\s*\d+(\.\d+)*\s+[A-Z]",
        r"^\s*[A-Z][A-Za-z0-9 ,:/()\-]{8,80}$",
    ],
    "learning_objective": [
        r"\blearning objectives?\b",
        r"\bby the end\b",
        r"\byou should be able to\b",
        r"\bunderstand\b",
    ],
    "definition": [r"\bis defined as\b", r"\brefers to\b", r"\bmeans\b", r"\bdefinition\b"],
    "mechanism": [r"\bmechanism\b", r"\bpathway\b", r"\bcauses?\b", r"\bleads? to\b", r"\bactivates?\b", r"\binhibits?\b", r"\btherefore\b"],
    "method": [r"\bmethod\b", r"\bprotocol\b", r"\bassay\b", r"\bmeasure\b", r"\bstep\b", r"\bcontrol\b", r"\breadout\b"],
    "comparison": [r"\bcompare\b", r"\bcontrast\b", r"\bversus\b", r"\bwhereas\b", r"\bdifferent from\b", r"\bsimilar to\b"],
    "calculation": [r"\bcalculate\b", r"\bequation\b", r"\bformula\b", r"\brate\b", r"\bEC50\b", r"\bIC50\b", r"=\s*"],
    "data_interpretation": [r"\bgraph\b", r"\bfigure\b", r"\btable\b", r"\bdata\b", r"\btrend\b", r"\binterpret\b"],
    "evidence": [r"\bevidence\b", r"\bresults?\b", r"\bfinding\b", r"\bshown by\b", r"\bdemonstrates?\b", r"\bdoi\b", r"\bpmid\b"],
    "application": [r"\bapplication\b", r"\bclinical\b", r"\bcase\b", r"\bused to\b", r"\bexam\b", r"\banswer\b"],
    "explanatory_example": [r"\bfor example\b", r"\be\.g\.\b", r"\bexample\b", r"\bcase study\b"],
}

ROLE_BY_SIGNAL: dict[str, str] = {
    "heading_or_topic_boundary": "knowledge_unit_boundary",
    "learning_objective": "coverage_target",
    "definition": "concept",
    "mechanism": "mechanism",
    "method": "method",
    "comparison": "comparison",
    "calculation": "calculation",
    "data_interpretation": "data_interpretation",
    "evidence": "evidence",
    "application": "exam_application",
    "explanatory_example": "explanatory_example",
}


def has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def knowledge_signals(text: str) -> list[str]:
    signals: list[str] = []
    for signal, patterns in KNOWLEDGE_SIGNAL_PATTERNS.items():
        if any(re.search(pattern, text or "", flags=re.I | re.M) for pattern in patterns):
            signals.append(signal)
    term_count = len(re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or ""))
    if term_count >= 35:
        signals.append("term_density")
    return unique(signals)


def knowledge_roles(signals: list[str]) -> list[str]:
    roles = [ROLE_BY_SIGNAL[signal] for signal in signals if signal in ROLE_BY_SIGNAL]
    if "term_density" in signals:
        roles.append("dense_academic_content")
    return unique(roles)


def knowledge_unit_candidates(text: str, max_items: int = 8) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for line in (text or "").splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if not clean:
            continue
        if any(re.search(pattern, clean, flags=re.I) for pattern in KNOWLEDGE_SIGNAL_PATTERNS["heading_or_topic_boundary"]):
            candidates.append({"signal": "heading_or_topic_boundary", "label": clean[:160]})
        elif re.search(r"\blearning objectives?\b|\bby the end\b|\byou should be able to\b", clean, flags=re.I):
            candidates.append({"signal": "learning_objective", "label": clean[:160]})
        if len(candidates) >= max_items:
            break
    return candidates


def classify_source(path: str | Path, text: str = "") -> str:
    name = Path(path).name.lower().replace("_", " ").replace("-", " ")
    sample = (text or "")[:6000].lower().replace("_", " ").replace("-", " ")
    haystack = name + "\n" + sample
    lecture_named = any(word in name for word in ["lecture", "slides", "notes", "module"])

    if DOI_RE.search(text or "") or PMID_RE.search(text or "") or AUTHOR_YEAR_RE.search(text or ""):
        return "extra_reading_source"
    if has_any(name, ["paper", "article", "journal", "doi", "pmid"]):
        return "extra_reading_source"
    if has_any(sample, PAPER_KEYWORDS) and not lecture_named:
        return "extra_reading_source"
    if has_any(name, ["textbook", "book", "chapter"]):
        return "extra_reading_source"
    if has_any(sample, BOOK_KEYWORDS) and not lecture_named:
        return "extra_reading_source"
    if has_any(haystack, MARKING_KEYWORDS):
        return "marking_material"
    if has_any(haystack, PRACTICE_KEYWORDS):
        return "practice_material"
    if has_any(haystack, STYLE_KEYWORDS):
        return "style_reference"
    if has_any(haystack, KNOWLEDGE_KEYWORDS):
        return "knowledge_material"
    return "other_material"


def clean_xml_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def read_docx_text(path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if name.startswith("word/") and name.endswith(".xml"):
                chunks.append(clean_xml_text(zf.read(name)))
    return "\n".join(chunks).strip()


def read_pptx_text(path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if name.startswith("ppt/slides/") and name.endswith(".xml"):
                chunks.append(clean_xml_text(zf.read(name)))
    return "\n".join(chunks).strip()


def read_pdf_text(path: Path) -> tuple[str, list[str]]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return "", ["pdf_text_not_extracted_by_local_runtime"]
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip(), []


def read_source_text(path: Path) -> tuple[str, list[str]]:
    notes: list[str] = []
    suffix = path.suffix.lower()
    try:
        if suffix in TEXT_SUFFIXES:
            if suffix == ".csv":
                with path.open(newline="", encoding="utf-8", errors="ignore") as f:
                    rows = [" | ".join(row) for row in csv.reader(f)]
                return "\n".join(rows), notes
            return path.read_text(encoding="utf-8", errors="ignore"), notes
        if suffix == ".docx":
            return read_docx_text(path), notes
        if suffix == ".pptx":
            return read_pptx_text(path), notes
        if suffix == ".pdf":
            return read_pdf_text(path)
        return "", ["automatic_text_reader_not_configured_for_this_file_type"]
    except Exception as exc:
        return "", [f"text_extraction_note:{type(exc).__name__}"]


def chunk_text(text: str, max_chars: int = 1400) -> list[str]:
    text = re.sub(r"\r\n?", "\n", text or "").strip()
    if not text:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs or [text]:
        if len(para) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(para), max_chars):
                chunks.append(para[i:i + max_chars].strip())
        elif len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            chunks.append(current.strip())
            current = para
    if current:
        chunks.append(current.strip())
    return chunks


def extract_media(path: Path, source_id: str, asset_dir: Path) -> list[dict[str, Any]]:
    prefix = MEDIA_PREFIXES.get(path.suffix.lower())
    if not prefix:
        return []
    visuals: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as zf:
            media_names = (n for n in zf.namelist() if n.startswith(prefix) and not n.endswith("/"))
            for idx, name in enumerate(media_names, 1):
                asset_dir.mkdir(parents=True, exist_ok=True)
                out = asset_dir / f"{source_id}_{Path(name).name}"
                out.write_bytes(zf.read(name))
                visuals.append({
                    "visual_id": f"{source_id}_V{idx}",
                    "source_id": source_id,
                    "asset_path": str(out),
                    "media_name": Path(name).name,
                    "locator": name,
                })
    except Exception:
        return []
    return visuals


def build_scan(paths: list[str], asset_dir: str = ".skill_assets", visual_mode: str = "embedded_media") -> dict[str, Any]:
    documents: list[dict[str, Any]] = []
    fragments: list[dict[str, Any]] = []
    visuals: list[dict[str, Any]] = []
    extraction_notes: list[str] = []
    for idx, raw in enumerate(paths, 1):
        path = Path(raw)
        source_id = f"S{idx}"
        text, notes = read_source_text(path)
        if not text:
            notes = notes + ["no_text_extracted_automatically"]
        hint = classify_source(path, text)
        doc_signals = knowledge_signals(text)
        doc_roles = knowledge_roles(doc_signals)
        doc_units = knowledge_unit_candidates(text)
        documents.append({
            "id": source_id,
            "path": str(path),
            "name": path.name,
            "source_hint": hint,
            "category": hint,
            "text_chars": len(text),
            "knowledge_signals": doc_signals,
            "knowledge_roles": doc_roles,
            "knowledge_unit_candidates": doc_units,
            "extraction_notes": notes,
        })
        extraction_notes.extend(f"{source_id}:{note}" for note in notes)
        for frag_idx, chunk in enumerate(chunk_text(text), 1):
            frag_signals = knowledge_signals(chunk)
            fragments.append({
                "id": f"{source_id}_F{frag_idx}",
                "source_id": source_id,
                "source_name": path.name,
                "source_hint": hint,
                "category": hint,
                "locator": f"chunk {frag_idx}",
                "text": chunk,
                "knowledge_signals": frag_signals,
                "knowledge_roles": knowledge_roles(frag_signals),
                "knowledge_unit_candidates": knowledge_unit_candidates(chunk),
            })
        if visual_mode != "none":
            visuals.extend(extract_media(path, source_id, Path(asset_dir)))
    hints: dict[str, int] = {}
    signals: dict[str, int] = {}
    roles: dict[str, int] = {}
    for doc in documents:
        hints[doc["source_hint"]] = hints.get(doc["source_hint"], 0) + 1
        for signal in doc.get("knowledge_signals", []):
            signals[signal] = signals.get(signal, 0) + 1
        for role in doc.get("knowledge_roles", []):
            roles[role] = roles.get(role, 0) + 1
    return {
        "schema_version": 2,
        "documents": documents,
        "fragments": fragments,
        "visuals": visuals,
        "summary": {
            "source_count": len(documents),
            "fragment_count": len(fragments),
            "visual_count": len(visuals),
            "source_hints": hints,
            "knowledge_signals": signals,
            "knowledge_roles": roles,
            "knowledge_unit_candidate_count": sum(len(doc.get("knowledge_unit_candidates", [])) for doc in documents),
            "extraction_notes": extraction_notes,
        },
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "source_a.md"
        p2 = Path(td) / "source_b.txt"
        p3 = Path(td) / "source_c.txt"
        p1.write_text("Learning objectives\nDefine enzyme activity.\nThe mechanism leads to dose response changes.\nCompare treated and control results.", encoding="utf-8")
        p2.write_text("1. Which statement is correct? A) One B) Two", encoding="utf-8")
        p3.write_text("Abstract Methods Results DOI 10.1000/test", encoding="utf-8")
        scan = build_scan([str(p1), str(p2), str(p3)], asset_dir=str(Path(td) / "assets"))
        assert scan["summary"]["source_count"] == 3
        assert scan["fragments"]
        assert scan["summary"]["knowledge_signals"]
        assert any("mechanism" in frag["knowledge_roles"] for frag in scan["fragments"])
        assert any(doc["source_hint"] == "extra_reading_source" for doc in scan["documents"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="*")
    parser.add_argument("--out")
    parser.add_argument("--asset-dir", default=".skill_assets")
    parser.add_argument("--visual-mode", default="embedded_media")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = build_scan(args.sources, args.asset_dir, args.visual_mode)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
