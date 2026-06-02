from __future__ import annotations

import argparse
import html
import json
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROLE_KEYWORDS = [
    ("mark_scheme", ["mark scheme", "markscheme"]),
    ("answer_key", ["answer key", "answers"]),
    ("past_paper", ["past paper", "exam paper", "question paper", "mcq", "short answer", "essay"]),
    ("practical_material", ["practical", "protocol", "lab", "experiment", "controls"]),
    ("data_problem_material", ["data", "graph", "table", "calculate", "problem"]),
    ("extra_reading", ["reading", "chapter", "paper", "article"]),
    ("style_reference", ["style", "example answer", "model answer"]),
    ("lecture_slides", ["slides", "lecture"]),
    ("lecture_notes", ["notes"]),
]

TEXT_SUFFIXES = {".txt", ".md", ".csv", ".json", ".yaml", ".yml"}

@dataclass
class SourceDoc:
    id: str
    path: str
    role: str
    readable: bool
    text: str
    visuals: list[dict[str, Any]]
    gaps: list[str]


def classify_source(path: Path, text: str = "") -> str:
    haystack = f"{path.name} {text[:2000]}".lower()
    for role, keys in ROLE_KEYWORDS:
        if any(k in haystack for k in keys):
            return role
    if path.suffix.lower() in {".pptx", ".ppt"}:
        return "lecture_slides"
    if path.suffix.lower() in {".docx", ".pdf"}:
        return "official_course_notes"
    return "lecture_notes"


def extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        chunks = []
        for name in zf.namelist():
            if name.startswith("word/") and name.endswith(".xml"):
                raw = zf.read(name).decode("utf-8", errors="ignore")
                chunks.extend(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw))
        return html.unescape("\n".join(chunks))


def extract_pptx_text(path: Path) -> tuple[str, list[dict[str, Any]]]:
    visuals = []
    with zipfile.ZipFile(path) as zf:
        chunks = []
        for name in zf.namelist():
            if name.startswith("ppt/slides/") and name.endswith(".xml"):
                raw = zf.read(name).decode("utf-8", errors="ignore")
                chunks.extend(re.findall(r"<a:t>(.*?)</a:t>", raw))
            if name.startswith("ppt/media/"):
                visuals.append({"source_path": str(path), "media_name": name, "role": "source_visual"})
        return html.unescape("\n".join(chunks)), visuals


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def read_source(path: Path, idx: int) -> SourceDoc:
    suffix = path.suffix.lower()
    gaps: list[str] = []
    visuals: list[dict[str, Any]] = []
    text = ""
    try:
        if suffix in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".docx":
            text = extract_docx_text(path)
        elif suffix == ".pptx":
            text, visuals = extract_pptx_text(path)
        elif suffix == ".pdf":
            text = extract_pdf_text(path)
            if not text:
                gaps.append("pdf_text_extraction_unavailable")
        else:
            gaps.append("unsupported_file_type")
    except Exception as exc:
        gaps.append(f"read_error:{type(exc).__name__}")
    role = classify_source(path, text)
    readable = bool(text.strip())
    if not readable and not gaps:
        gaps.append("no_readable_text")
    return SourceDoc(f"S{idx}", str(path), role, readable, text, visuals, gaps)


def fragment_text(doc: SourceDoc) -> list[dict[str, Any]]:
    parts = [p.strip() for p in re.split(r"\n\s*\n|(?<=[.!?])\s+", doc.text) if p.strip()]
    return [
        {"id": f"{doc.id}_F{i+1}", "source_id": doc.id, "role": doc.role, "text": part[:1200]}
        for i, part in enumerate(parts[:200])
    ]


def build_scan(paths: list[Path]) -> dict[str, Any]:
    docs = [read_source(path, i + 1) for i, path in enumerate(paths)]
    fragments = [frag for doc in docs for frag in fragment_text(doc)]
    return {
        "documents": [{"id": d.id, "path": d.path, "role": d.role, "readable": d.readable} for d in docs],
        "fragments": fragments,
        "visual_source_references": [v for d in docs for v in d.visuals],
        "unsupported_gaps": [{"source_id": d.id, "gap": gap} for d in docs for gap in d.gaps],
        "source_roles": sorted({d.role for d in docs}),
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "lecture_notes.txt"
        p.write_text("Enzyme kinetics graph interpretation. Practical controls and limitations.", encoding="utf-8")
        scan = build_scan([p])
        assert scan["documents"][0]["role"] in {"lecture_notes", "practical_material", "data_problem_material"}
        assert scan["fragments"]
    print("extract_sources self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="*")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    paths = [Path(p) for p in args.inputs]
    scan = build_scan(paths)
    text = json.dumps(scan, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
