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


def has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_source(path: str | Path, text: str = "") -> str:
    name = Path(path).name.lower().replace("_", " ").replace("-", " ")
    sample = (text or "")[:6000].lower().replace("_", " ").replace("-", " ")
    haystack = name + "\n" + sample
    lecture_named = any(word in name for word in ["lecture", "slides", "notes", "module"])

    if DOI_RE.search(text or "") or PMID_RE.search(text or "") or AUTHOR_YEAR_RE.search(text or ""):
        return "extra_reading_paper"
    if has_any(name, ["paper", "article", "journal", "doi", "pmid"]):
        return "extra_reading_paper"
    if has_any(sample, PAPER_KEYWORDS) and not lecture_named:
        return "extra_reading_paper"
    if has_any(name, ["textbook", "book", "chapter"]):
        return "extra_reading_book"
    if has_any(sample, BOOK_KEYWORDS) and not lecture_named:
        return "extra_reading_book"
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
            for idx, name in enumerate(n for n in zf.namelist() if n.startswith(prefix) and not n.endswith("/"), 1):
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
        documents.append({
            "id": source_id,
            "path": str(path),
            "name": path.name,
            "source_hint": hint,
            "category": hint,
            "text_chars": len(text),
            "extraction_notes": notes,
        })
        extraction_notes.extend(f"{source_id}:{note}" for note in notes)
        for frag_idx, chunk in enumerate(chunk_text(text), 1):
            fragments.append({
                "id": f"{source_id}_F{frag_idx}",
                "source_id": source_id,
                "source_name": path.name,
                "source_hint": hint,
                "category": hint,
                "locator": f"chunk {frag_idx}",
                "text": chunk,
            })
        if visual_mode != "none":
            visuals.extend(extract_media(path, source_id, Path(asset_dir)))
    hints: dict[str, int] = {}
    for doc in documents:
        hints[doc["source_hint"]] = hints.get(doc["source_hint"], 0) + 1
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
            "extraction_notes": extraction_notes,
        },
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "Lecture_1_notes.md"
        p2 = Path(td) / "Past_Paper_MCQ.txt"
        p3 = Path(td) / "Academic_Paper.txt"
        p1.write_text("Lecture notes on enzymes and dose response.", encoding="utf-8")
        p2.write_text("1. Which statement is correct? A) One B) Two", encoding="utf-8")
        p3.write_text("Abstract Methods Results DOI 10.1000/test", encoding="utf-8")
        scan = build_scan([str(p1), str(p2), str(p3)], asset_dir=str(Path(td) / "assets"))
        assert scan["summary"]["source_count"] == 3
        assert scan["fragments"]
        assert any(doc["source_hint"] == "extra_reading_paper" for doc in scan["documents"])


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
