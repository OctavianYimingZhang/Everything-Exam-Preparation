#!/usr/bin/env python3
"""Lint public student-facing text for knowledge-surface purity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None  # type: ignore

from knowledge_only_rendering_rules import (
    forbidden_advisory_heading_hits,
    forbidden_advisory_phrase_hits,
    forbidden_non_knowledge_hits,
    repeated_template_label_hits,
)


def iter_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(
            child
            for child in path.rglob("*")
            if child.is_file() and child.suffix.lower() in {".docx", ".md", ".txt"}
        )
    return []


def read_visible_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        if Document is None:
            raise RuntimeError("python-docx is required to lint DOCX files")
        doc = Document(path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip())
    return path.read_text(encoding="utf-8", errors="ignore")


def lint_text(text: str, *, reference: str = "<text>") -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for phrase in forbidden_advisory_phrase_hits(text):
        failures.append({"type": "forbidden_advisory_phrase", "reference": reference, "phrase": phrase})
    for heading in forbidden_advisory_heading_hits(text):
        failures.append({"type": "forbidden_advisory_heading", "reference": reference, "heading": heading})
    for category in forbidden_non_knowledge_hits(text):
        failures.append({"type": "forbidden_non_knowledge_surface", "reference": reference, "category": category})
    for label in repeated_template_label_hits(text):
        failures.append({"type": "repeated_rigid_template_label", "reference": reference, "label": label})
    return failures


def lint_paths(paths: list[Path]) -> dict[str, Any]:
    files: list[Path] = []
    for path in paths:
        files.extend(iter_files(path))
    failures: list[dict[str, Any]] = []
    if not files:
        failures.append({"type": "no_supported_files", "paths": [str(path) for path in paths]})
    for file_path in files:
        try:
            failures.extend(lint_text(read_visible_text(file_path), reference=str(file_path)))
        except Exception as exc:
            failures.append({"type": "read_error", "reference": str(file_path), "error": str(exc)})
    return {"status": "pass" if not failures else "fail", "counts": {"files": len(files)}, "failures": failures}


def self_test() -> dict[str, Any]:
    raw_bullets = [f"• copied slide bullet {idx}" for idx in range(1, 24)]
    bad_text = "\n".join(
        [
            "Course Knowledge Map",
            "Core knowledge spans Lecture 1 slides.pptx; Lecture 2 slides.pptx; Module 3.pdf; Module 4.pptm; Module 5.pptx; Module 6.pdf; Module 7.pptx; Module 8.pptx.",
            "Unit Attendance: download the SEAtS app and scan the QR code.",
            "To make the most of the live session, join Mentimeter.",
            "Meet the Staff: Unit Coordinator, Tel: 0161 000 0000, Location: Some Building, lecturer@example.ac.uk.",
            "English explanations extracted from the shared ChatGPT page",
            "This slide shows the opposite side of the body.",
            "Definition: one",
            "Definition: two",
            "Definition: three",
            "Definition: four",
            "Graph logic: a graph wrapper rather than knowledge.",
            "Graph logic: another wrapper.",
            "Graph logic: another wrapper.",
            "Graph logic: another wrapper.",
            "Components: PCR tubes, thermocycler, tips and gel kit.",
            "Workflow: DNA extraction -> PCR -> digest -> gel.",
            "Exclusion logic: antibodies and microscope are not needed.",
            "Binding logic: resin is charged.",
            "Protein charge: the protein is positive.",
            "Elution mechanism: salt elutes the protein.",
            "Formula: Resin-COOH ⇌ Resin-COO- + H+.",
            "Logic: pH below pKa favours protonation.",
            *raw_bullets,
        ]
    )
    good_text = (
        "The crossed extensor reflex activates contralateral extensors and inhibits contralateral flexors, "
        "allowing the unstimulated limb to support body weight while the stimulated limb withdraws."
    )
    bad_failures = lint_text(bad_text, reference="bad_fixture")
    good_failures = lint_text(good_text, reference="good_fixture")
    failure_labels = {failure.get("label") for failure in bad_failures}
    failure_categories = {failure.get("category") for failure in bad_failures}
    failures: list[dict[str, Any]] = []
    if not bad_failures:
        failures.append({"type": "self_test_bad_fixture_not_rejected"})
    if "colon_fragment_label_density" not in failure_labels:
        failures.append({"type": "self_test_colon_fragment_fixture_not_rejected", "failures": bad_failures})
    if "raw_slide_bullet_dump" not in failure_labels:
        failures.append({"type": "self_test_raw_bullet_fixture_not_rejected", "failures": bad_failures})
    for category in ["admin_logistics_noise", "admin_contact_noise", "course_map_file_title_dump"]:
        if category not in failure_categories:
            failures.append({"type": f"self_test_{category}_not_rejected", "failures": bad_failures})
    if good_failures:
        failures.append({"type": "self_test_good_fixture_rejected", "failures": good_failures})
    return {
        "status": "pass" if not failures else "fail",
        "bad_fixture_failures": bad_failures,
        "good_fixture_failures": good_failures,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = self_test() if args.self_test else lint_paths(args.paths)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
