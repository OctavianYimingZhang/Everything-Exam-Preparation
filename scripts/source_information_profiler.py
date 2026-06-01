#!/usr/bin/env python3
"""Estimate information-bearing pages/slides before source-scale budgeting."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except Exception:  # pragma: no cover
        PdfReader = None  # type: ignore


WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_'/.-]*")
EQUATION_RE = re.compile(r"(?:=|->|<->|[A-Za-z]\d|pH|pKa|logP|EC50|IC50|K[dm]|Vmax|Km)")
PLAN_RE = re.compile(
    r"\b(?:lecture\s+plan|outline|overview|today'?s\s+lecture|learning\s+outcomes?|objectives?|reading|assessment|timetable|housekeeping)\b",
    re.I,
)
COVER_RE = re.compile(r"\b(?:lecture|course|module|unit|welcome|introduction)\b", re.I)
SCIENCE_SIGNAL_RE = re.compile(
    r"\b(?:gene|protein|enzyme|receptor|pathway|assay|cell|drug|dose|metabolism|sequence|rna|dna|pcr|clinical|plant|hormone|mutation|trial|disease)\b",
    re.I,
)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def slide_number(path: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", path)
    return int(match.group(1)) if match else 0


def xml_text(root: ET.Element) -> str:
    return " ".join(node.text or "" for node in root.iter() if node.tag.endswith("}t") and node.text)


def count_tags(root: ET.Element, suffix: str) -> int:
    return sum(1 for node in root.iter() if node.tag.endswith(suffix))


def parse_xml(data: bytes) -> ET.Element:
    return ET.fromstring(data)


def classify_page(index: int, text: str, note_text: str, metrics: dict[str, Any]) -> tuple[str, bool, float, str]:
    all_text = " ".join([text, note_text]).strip()
    word_count = len(words(all_text))
    science_signal = bool(SCIENCE_SIGNAL_RE.search(all_text))
    visual_count = int(metrics.get("picture_count", 0)) + int(metrics.get("graphic_frame_count", 0))

    if word_count == 0 and visual_count == 0:
        return "blank", False, 0.0, "no_text_or_visual_content"
    if index == 1 and word_count <= 25 and COVER_RE.search(all_text) and len(words(note_text)) <= 10 and visual_count <= 1:
        return "cover", False, 0.0, "cover_or_title_page"
    if word_count <= 10 and visual_count > 0 and not science_signal:
        return "video_or_media_placeholder", False, 0.0, "media_placeholder_without_teachable_text"
    if PLAN_RE.search(all_text) and word_count <= 100 and metrics.get("equation_like_count", 0) == 0 and visual_count <= 1:
        return "lecture_plan_or_admin", False, 0.0, "plan_admin_or_learning_outcome_without_teachable_content"

    base = min(2.0, len(words(text)) / 90.0)
    notes = min(1.0, len(words(note_text)) / 140.0)
    structure = min(0.8, metrics.get("paragraph_count", 0) / 10.0)
    visuals = min(1.2, visual_count * 0.25 + metrics.get("table_count", 0) * 0.4)
    equations = min(0.8, metrics.get("equation_like_count", 0) * 0.2)
    signal = 0.4 if science_signal else 0.0
    score = round(max(0.25, base + notes + structure + visuals + equations + signal), 2)
    if score < 0.75:
        band = "light_context"
    elif score < 1.75:
        band = "knowledge_standard"
    else:
        band = "knowledge_dense"
    return band, True, score, "teachable_source_content"


def profile_pptx(path: Path) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        slide_names = sorted([name for name in names if re.search(r"ppt/slides/slide\d+\.xml$", name)], key=slide_number)
        for slide_name in slide_names:
            index = slide_number(slide_name)
            root = parse_xml(zf.read(slide_name))
            text = xml_text(root)
            note_name = f"ppt/notesSlides/notesSlide{index}.xml"
            note_text = xml_text(parse_xml(zf.read(note_name))) if note_name in names else ""
            metrics = {
                "word_count": len(words(text)),
                "speaker_note_word_count": len(words(note_text)),
                "paragraph_count": count_tags(root, "}p"),
                "picture_count": count_tags(root, "}pic"),
                "graphic_frame_count": count_tags(root, "}graphicFrame"),
                "table_count": count_tags(root, "}tbl"),
                "equation_like_count": len(EQUATION_RE.findall(" ".join([text, note_text]))),
            }
            category, informative, score, reason = classify_page(index, text, note_text, metrics)
            pages.append(
                {
                    "page_index": index,
                    "page_kind": "slide",
                    "category": category,
                    "informative": informative,
                    "information_score": score,
                    "exclusion_reason": None if informative else reason,
                    **metrics,
                }
            )
    return {"source_path": str(path), "source_type": "pptx", "pages": pages}


def profile_pdf(path: Path) -> dict[str, Any]:
    if PdfReader is None:
        return {"source_path": str(path), "source_type": "pdf", "pages": [], "error": "pdf_reader_unavailable"}
    reader = PdfReader(str(path))
    pages: list[dict[str, Any]] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        metrics = {
            "word_count": len(words(text)),
            "speaker_note_word_count": 0,
            "paragraph_count": len([part for part in text.splitlines() if part.strip()]),
            "picture_count": 0,
            "graphic_frame_count": 0,
            "table_count": 0,
            "equation_like_count": len(EQUATION_RE.findall(text)),
        }
        category, informative, score, reason = classify_page(index, text, "", metrics)
        pages.append(
            {
                "page_index": index,
                "page_kind": "page",
                "category": category,
                "informative": informative,
                "information_score": score,
                "exclusion_reason": None if informative else reason,
                **metrics,
            }
        )
    return {"source_path": str(path), "source_type": "pdf", "pages": pages}


def profile_path(path: Path) -> list[dict[str, Any]]:
    files = sorted(item for item in path.rglob("*") if item.is_file()) if path.is_dir() else [path]
    profiles: list[dict[str, Any]] = []
    for file_path in files:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            try:
                profiles.append(profile_pdf(file_path))
            except Exception as exc:
                profiles.append({"source_path": str(file_path), "source_type": "pdf", "pages": [], "error": str(exc)})
        elif suffix in {".pptx", ".pptm"} or zipfile.is_zipfile(file_path):
            try:
                profiles.append(profile_pptx(file_path))
            except Exception as exc:
                profiles.append({"source_path": str(file_path), "source_type": "unknown", "pages": [], "error": str(exc)})
    return profiles


def summarize(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    pages = [page for profile in profiles for page in profile.get("pages", [])]
    informative = [page for page in pages if page.get("informative")]
    mass = round(sum(float(page.get("information_score") or 0) for page in informative), 2)
    return {
        "source_files_profiled": len([profile for profile in profiles if profile.get("pages")]),
        "raw_pages_or_slides": len(pages),
        "informative_page_count": len(informative),
        "non_informative_page_count": len(pages) - len(informative),
        "information_mass_units": mass,
        "average_information_score": round(mass / len(informative), 2) if informative else 0,
        "profile_status": "measured" if pages else "missing_readable_pages",
    }


def self_test() -> dict[str, Any]:
    ns = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'

    def slide_xml(text: str, extra: str = "") -> str:
        return f'<p:sld {ns}><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>{extra}</p:spTree></p:cSld></p:sld>'

    with tempfile.TemporaryDirectory(prefix="source_information_profile_") as tmp:
        pptx = Path(tmp) / "fixture.pptx"
        with zipfile.ZipFile(pptx, "w") as zf:
            zf.writestr("ppt/slides/slide1.xml", slide_xml("Course introduction lecture"))
            zf.writestr("ppt/slides/slide2.xml", slide_xml("Lecture plan and reading"))
            zf.writestr(
                "ppt/slides/slide3.xml",
                slide_xml("PCR amplification uses primers, DNA polymerase, denaturation, annealing and extension to amplify a defined DNA sequence."),
            )
            zf.writestr("ppt/slides/slide4.xml", slide_xml("", "<p:pic/>"))
        profiles = profile_path(pptx)
    summary = summarize(profiles)
    failures = []
    if summary["raw_pages_or_slides"] != 4:
        failures.append({"type": "raw_count_wrong", "summary": summary})
    if summary["informative_page_count"] != 1:
        failures.append({"type": "informative_count_wrong", "summary": summary})
    return {"pass": not failures, "summary": summary, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    else:
        profiles = [profile for path in args.paths for profile in profile_path(path)]
        result = {"summary": summarize(profiles), "files": profiles}
    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("pass", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
