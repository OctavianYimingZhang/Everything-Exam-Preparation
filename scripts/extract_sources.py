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
    ("previous_generated_output", ["exam preparation notes", "high-yield exam map", "final quick revision checklist"]),
    ("generated_output", ["source map", "qa flag", "internal manifest", "route narration"]),
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
MEDIA_PREFIXES = {"docx": "word/media/", "pptx": "ppt/media/"}
EXAM_NOTES_FACTUAL_ROLES = {"lecture_slides", "lecture_notes", "official_course_notes", "practical_material", "data_problem_material", "extra_reading"}
EXAM_NOTES_EMPHASIS_ROLES = {"past_paper", "mark_scheme", "answer_key"}
EXAM_NOTES_STYLE_ROLES = {"example_answer", "user_draft", "style_reference", "previous_generated_output", "generated_output"}
PRACTICE_MARKING_AUTHORITY_ROLES = {"mark_scheme", "answer_key"}
PRACTICE_MARKING_QUESTION_ROLES = {"past_paper", "practical_material", "data_problem_material"}

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
    return "unknown"


def decision_for_route(doc: SourceDoc, route: str) -> dict[str, Any]:
    role = doc.role
    if route == "exam_prep_notes":
        if not doc.readable and not doc.visuals:
            scope = "needs_confirmation"
            reason = "Source is unreadable or unsupported, so it cannot support notes content."
        elif role in EXAM_NOTES_FACTUAL_ROLES:
            scope = "factual_course_content"
            reason = "Role can support course concepts, methods, limitations, and explanations for exam notes."
        elif role in EXAM_NOTES_EMPHASIS_ROLES:
            scope = "exam_emphasis"
            reason = "Role can shape exam emphasis and answer operations, but does not create course facts."
        elif role == "source_visual":
            scope = "visual_candidate_only"
            reason = "Visuals can be selected only by block ownership in the notes plan."
        elif role in EXAM_NOTES_STYLE_ROLES:
            scope = "style_only"
            reason = "Role can inform layout or comparison only; it cannot supply factual course claims."
        else:
            scope = "needs_confirmation"
            reason = "Role is ambiguous for factual notes and must be clarified before factual use."
    elif route == "practice_marking":
        if role in PRACTICE_MARKING_AUTHORITY_ROLES:
            scope = "marking_authority"
            reason = "Role can provide marking criteria or expected answer operations."
        elif role in PRACTICE_MARKING_QUESTION_ROLES:
            scope = "question_source"
            reason = "Role can provide question context or problem material for marking."
        elif role in EXAM_NOTES_FACTUAL_ROLES:
            scope = "factual_course_content"
            reason = "Role can support lecture or knowledge-point mapping for feedback."
        elif role in {"user_draft", "student_answer_script"}:
            scope = "student_answer"
            reason = "Role can be assessed against supplied course and marking sources."
        else:
            scope = "needs_confirmation"
            reason = "Role is ambiguous for practice marking and must be clarified before use."
    else:
        scope = "ignored"
        reason = "No route-specific use is defined for this source."
    return {
        "decision_id": f"{doc.id}:{route}",
        "source_id": doc.id,
        "route": route,
        "declared_role": role,
        "inferred_role": role,
        "evidence_scope": scope,
        "reason": reason,
    }


def route_use_for_doc(doc: SourceDoc) -> dict[str, dict[str, str]]:
    return {
        route: {
            "evidence_scope": decision["evidence_scope"],
            "reason": decision["reason"],
        }
        for route in ["exam_prep_notes", "practice_marking"]
        for decision in [decision_for_route(doc, route)]
    }


def exam_notes_scope(source_scan: dict[str, Any], source_id: str) -> str | None:
    for decision in source_scan.get("source_decisions", []):
        if decision.get("route") == "exam_prep_notes" and decision.get("source_id") == source_id:
            return str(decision.get("evidence_scope") or "")
    return None


def media_candidate(
    *,
    source_id: str,
    path: Path,
    media_name: str,
    index: int,
    asset_dir: Path | None,
    visual_mode: str,
) -> dict[str, Any]:
    asset_path = ""
    if asset_dir and visual_mode in {"embedded_media", "both"}:
        asset_path = str(asset_dir / source_id / Path(media_name).name)
    item: dict[str, Any] = {
        "visual_id": f"{source_id}_V{index}",
        "id": f"{source_id}_V{index}",
        "source_id": source_id,
        "visual_kind": "source_embedded_image",
        "selection_state": "candidate",
        "source_path": str(path),
        "media_name": media_name,
        "caption": Path(media_name).stem.replace("_", " "),
        "source_locator": {"media_name": media_name},
        "candidate_reason": "Extracted source image candidate from source media.",
    }
    if asset_path:
        item["asset_path"] = asset_path
    return item


def export_media_asset(zf: zipfile.ZipFile, media_name: str, source_id: str, asset_dir: Path | None, visual_mode: str) -> None:
    if not asset_dir or visual_mode not in {"embedded_media", "both"}:
        return
    out = asset_dir / source_id / Path(media_name).name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(zf.read(media_name))


def extract_docx_text(path: Path, source_id: str, asset_dir: Path | None = None, visual_mode: str = "metadata_only") -> tuple[str, list[dict[str, Any]]]:
    visuals: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        chunks = []
        for name in zf.namelist():
            if name.startswith("word/") and name.endswith(".xml"):
                raw = zf.read(name).decode("utf-8", errors="ignore")
                chunks.extend(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw))
            if name.startswith(MEDIA_PREFIXES["docx"]):
                export_media_asset(zf, name, source_id, asset_dir, visual_mode)
                visuals.append(
                    media_candidate(
                        source_id=source_id,
                        path=path,
                        media_name=name,
                        index=len(visuals) + 1,
                        asset_dir=asset_dir,
                        visual_mode=visual_mode,
                    )
                )
        return html.unescape("\n".join(chunks)), visuals


def extract_pptx_text(path: Path, source_id: str, asset_dir: Path | None = None, visual_mode: str = "metadata_only") -> tuple[str, list[dict[str, Any]]]:
    visuals: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        chunks = []
        for name in zf.namelist():
            if name.startswith("ppt/slides/") and name.endswith(".xml"):
                raw = zf.read(name).decode("utf-8", errors="ignore")
                chunks.extend(re.findall(r"<a:t>(.*?)</a:t>", raw))
            if name.startswith(MEDIA_PREFIXES["pptx"]):
                export_media_asset(zf, name, source_id, asset_dir, visual_mode)
                visuals.append(
                    media_candidate(
                        source_id=source_id,
                        path=path,
                        media_name=name,
                        index=len(visuals) + 1,
                        asset_dir=asset_dir,
                        visual_mode=visual_mode,
                    )
                )
        return html.unescape("\n".join(chunks)), visuals


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def read_source(path: Path, idx: int, asset_dir: Path | None = None, visual_mode: str = "metadata_only") -> SourceDoc:
    suffix = path.suffix.lower()
    source_id = f"S{idx}"
    gaps: list[str] = []
    visuals: list[dict[str, Any]] = []
    text = ""
    try:
        if suffix in TEXT_SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".docx":
            text, visuals = extract_docx_text(path, source_id, asset_dir, visual_mode)
        elif suffix == ".pptx":
            text, visuals = extract_pptx_text(path, source_id, asset_dir, visual_mode)
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
    return SourceDoc(source_id, str(path), role, readable, text, visuals, gaps)


def fragment_text(doc: SourceDoc) -> list[dict[str, Any]]:
    parts = [p.strip() for p in re.split(r"\n\s*\n|(?<=[.!?])\s+", doc.text) if p.strip()]
    notes_scope = decision_for_route(doc, "exam_prep_notes")["evidence_scope"]
    return [
        {"id": f"{doc.id}_F{i+1}", "source_id": doc.id, "role": doc.role, "evidence_scope": notes_scope, "text": part[:1200]}
        for i, part in enumerate(parts[:200])
    ]


def build_scan(paths: list[Path], asset_dir: Path | None = None, visual_mode: str = "metadata_only") -> dict[str, Any]:
    docs = [read_source(path, i + 1, asset_dir, visual_mode) for i, path in enumerate(paths)]
    fragments = [frag for doc in docs for frag in fragment_text(doc)]
    decisions = [decision_for_route(doc, route) for doc in docs for route in ["exam_prep_notes", "practice_marking"]]
    visuals: list[dict[str, Any]] = []
    for doc in docs:
        for visual in doc.visuals:
            item = dict(visual)
            item["source_id"] = doc.id
            item.setdefault("visual_kind", "source_embedded_image")
            item.setdefault("selection_state", "candidate")
            item.setdefault("caption", f"Source figure candidate {doc.id}")
            item.setdefault("source_locator", {"media_name": item.get("media_name", "")})
            visuals.append(item)
    return {
        "documents": [{"id": d.id, "path": d.path, "role": d.role, "route_use": route_use_for_doc(d), "readable": d.readable} for d in docs],
        "source_decisions": decisions,
        "fragments": fragments,
        "visual_source_references": visuals,
        "unsupported_gaps": [{"source_id": d.id, "gap": gap} for d in docs for gap in d.gaps],
        "source_roles": sorted({d.role for d in docs}),
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "lecture_notes.txt"
        p.write_text("Enzyme kinetics graph interpretation. Practical controls and limitations.", encoding="utf-8")
        scan = build_scan([p])
        assert scan["documents"][0]["role"] in {"lecture_notes", "practical_material", "data_problem_material"}
        assert any(d["route"] == "exam_prep_notes" and d["evidence_scope"] == "factual_course_content" for d in scan["source_decisions"])
        assert scan["fragments"]
        pptx = Path(td) / "lecture_slides.pptx"
        with zipfile.ZipFile(pptx, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("ppt/slides/slide1.xml", "<a:t>Graph interpretation slide</a:t>")
            zf.writestr("ppt/media/image1.png", b"\x89PNG\r\n\x1a\n")
        asset_dir = Path(td) / "assets"
        visual_scan = build_scan([pptx], asset_dir=asset_dir, visual_mode="embedded_media")
        visual = visual_scan["visual_source_references"][0]
        assert visual["selection_state"] == "candidate"
        assert "placement" not in visual
        assert Path(visual["asset_path"]).exists()
        generated = Path(td) / "previous.txt"
        generated.write_text("Exam Preparation Notes\nHigh-yield exam map\nFinal quick revision checklist", encoding="utf-8")
        out = build_scan([generated])
        assert out["source_decisions"][0]["evidence_scope"] == "style_only"
    print("extract_sources self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="*")
    parser.add_argument("--out")
    parser.add_argument("--asset-dir", default=".skill_assets")
    parser.add_argument("--visual-mode", choices=["metadata_only", "embedded_media", "slide_snapshots", "both"], default="embedded_media")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    paths = [Path(p) for p in args.inputs]
    scan = build_scan(paths, Path(args.asset_dir), args.visual_mode)
    text = json.dumps(scan, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
