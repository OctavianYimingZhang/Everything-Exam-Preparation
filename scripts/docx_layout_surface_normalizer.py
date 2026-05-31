#!/usr/bin/env python3
"""Normalise public notes DOCX layout after rendering-plan generation.

This post-processor enforces the notes/walkthrough layout surface:
- body text justified;
- titles, lecture headings and subheadings left aligned;
- images centered;
- default text line spacing 1.5;
- images scaled to the available content area while preserving aspect ratio.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from docx import Document  # type: ignore
    from docx.enum.text import WD_ALIGN_PARAGRAPH  # type: ignore
    from docx.oxml.ns import qn  # type: ignore
    from docx.shared import Cm, Pt, RGBColor  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"python-docx is required: {exc}")

EMU_PER_CM = 360000


def set_run_defaults(run, *, font_name: str = "Arial", font_size_pt: float | None = None) -> None:
    run.font.name = font_name
    if font_size_pt is not None:
        run.font.size = Pt(font_size_pt)
    run.font.color.rgb = RGBColor(0, 0, 0)
    if run._element.rPr is not None:
        run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)


def paragraph_has_image(paragraph) -> bool:
    return bool(paragraph._p.xpath(".//w:drawing"))


def paragraph_is_heading(paragraph, visible_index: int) -> bool:
    text = paragraph.text.strip()
    style_name = str(getattr(paragraph.style, "name", "") or "").lower()
    if visible_index == 1:
        return True
    if any(marker in style_name for marker in ["title", "heading", "subheading", "lecture"]):
        return True
    if text.startswith("Lecture:"):
        return True
    if len(text) <= 130 and text and not text.endswith(".") and any(run.bold for run in paragraph.runs):
        return True
    return False


def scale_inline_shapes(doc: Document, max_width_cm: float, max_height_cm: float) -> int:
    max_width = int(max_width_cm * EMU_PER_CM)
    max_height = int(max_height_cm * EMU_PER_CM)
    changed = 0
    for shape in doc.inline_shapes:
        width = int(shape.width)
        height = int(shape.height)
        if width <= 0 or height <= 0:
            continue
        scale = min(max_width / width, max_height / height, 1.0)
        if scale < 0.999:
            shape.width = int(width * scale)
            shape.height = int(height * scale)
            changed += 1
    return changed


def normalise_docx(
    input_path: Path,
    output_path: Path,
    *,
    margin_cm: float = 2.0,
    line_spacing: float = 1.5,
    body_font_pt: float = 10.5,
    max_image_width_cm: float = 15.0,
    max_image_height_cm: float = 8.0,
) -> dict[str, int | str]:
    doc = Document(input_path)
    section = doc.sections[0]
    section.top_margin = Cm(margin_cm)
    section.bottom_margin = Cm(margin_cm)
    section.left_margin = Cm(margin_cm)
    section.right_margin = Cm(margin_cm)

    for style_name in ["Normal", "Body Text"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "Arial"
            style.font.size = Pt(body_font_pt)
            style.font.color.rgb = RGBColor(0, 0, 0)
            style.paragraph_format.line_spacing = line_spacing
            if style._element.rPr is not None:
                style._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")

    changed_images = scale_inline_shapes(doc, max_image_width_cm, max_image_height_cm)

    visible_index = 0
    image_paragraphs = 0
    body_paragraphs = 0
    heading_paragraphs = 0
    for paragraph in doc.paragraphs:
        if not paragraph.text.strip() and not paragraph_has_image(paragraph):
            continue
        visible_index += 1
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(3)
        if paragraph_has_image(paragraph):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.line_spacing = 1.0
            image_paragraphs += 1
        elif paragraph_is_heading(paragraph, visible_index):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            paragraph.paragraph_format.line_spacing = line_spacing
            heading_paragraphs += 1
        else:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph.paragraph_format.line_spacing = line_spacing
            body_paragraphs += 1
        for run in paragraph.runs:
            if run.text:
                set_run_defaults(run, font_size_pt=body_font_pt if paragraph.style.name == "Normal" else None)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return {
        "status": "pass",
        "input": str(input_path),
        "output": str(output_path),
        "body_paragraphs": body_paragraphs,
        "heading_paragraphs": heading_paragraphs,
        "image_paragraphs": image_paragraphs,
        "scaled_images": changed_images,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--margin-cm", type=float, default=2.0)
    parser.add_argument("--line-spacing", type=float, default=1.5)
    parser.add_argument("--body-font-pt", type=float, default=10.5)
    parser.add_argument("--max-image-width-cm", type=float, default=15.0)
    parser.add_argument("--max-image-height-cm", type=float, default=8.0)
    args = parser.parse_args()
    result = normalise_docx(
        args.input,
        args.output,
        margin_cm=args.margin_cm,
        line_spacing=args.line_spacing,
        body_font_pt=args.body_font_pt,
        max_image_width_cm=args.max_image_width_cm,
        max_image_height_cm=args.max_image_height_cm,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
