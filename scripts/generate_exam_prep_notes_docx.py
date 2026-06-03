#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

OUTPUT_NAME = "Exam_Preparation_Notes.docx"
MARGIN_TWIPS = 1417
LINE_SPACING = 360

SECTION_ORDER = [
    ("course_overview", "Course Overview"),
    ("course_knowledge_map", "Course Knowledge Map"),
    ("exam_habit_analysis", "Exam Pattern and Examiner Habits"),
    ("high_yield_topics", "High-Yield Topics"),
    ("mcq_preparation", "MCQ Preparation"),
    ("short_answer_preparation", "Short-Answer Preparation"),
    ("long_answer_preparation", "Long-Answer Preparation"),
    ("practical_data_preparation", "Practical/Data/Problem Preparation"),
    ("essay_preparation", "Essay Preparation"),
    ("revision_checklist", "Final Revision Checklist"),
]

FIELD_LABELS = {
    "tested_point": "Tested point",
    "how_it_appears": "How it appears in MCQ",
    "correct_reasoning": "Correct reasoning",
    "plausible_wrong_statement": "Plausible wrong statement",
    "why_wrong": "Why it is wrong",
    "definition": "Definition",
    "mark_points": "Mark points",
    "explain_sentence": "Explain sentence",
    "example_answer": "Example answer",
    "question": "Question",
    "examiner_wants": "What the examiner wants",
    "relevant_knowledge": "Relevant knowledge",
    "answer_structure": "Answer structure",
    "why_this_answer_works": "Why this answer works",
    "task": "Task",
    "method_aim": "Method aim",
    "readout": "Readout",
    "control": "Control",
    "calculation_or_interpretation": "Calculation or interpretation",
    "limitation": "Limitation",
    "exam_conclusion": "Exam conclusion",
    "module_theme": "Module theme",
    "broad_essay_question": "Broad essay question",
    "thesis_options": "Thesis options",
    "paragraph_plan": "Paragraph plan",
    "example_essay_paragraph": "Example essay paragraph",
    "why_it_matters": "Why it matters",
    "how_it_is_tested": "How it is tested",
    "how_to_answer": "How to answer",
    "core_explanation": "Core explanation",
    "exam_use": "Exam use",
    "common_question_style": "Common question style",
    "example_answer_move": "Example answer move",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def paragraph_xml(text: str, style: str = "Normal", align: str = "both") -> str:
    style_xml = "" if style == "Normal" else f'<w:pStyle w:val="{esc(style)}"/>'
    bold_start = "<w:b/>" if style in {"Title", "Heading1", "Heading2"} else ""
    size = {"Title": "32", "Heading1": "26", "Heading2": "23"}.get(style, "22")
    return (
        "<w:p><w:pPr>"
        f"{style_xml}<w:jc w:val=\"{esc(align)}\"/><w:spacing w:line=\"{LINE_SPACING}\" w:lineRule=\"auto\"/>"
        "</w:pPr><w:r><w:rPr>"
        f"<w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/>{bold_start}<w:sz w:val=\"{size}\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"
    )


def table_xml(rows: list[list[Any]]) -> str:
    row_xml = []
    for row in rows:
        cells = "".join(
            "<w:tc><w:p><w:pPr><w:spacing w:line=\"360\" w:lineRule=\"auto\"/></w:pPr>"
            "<w:r><w:rPr><w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/><w:sz w:val=\"20\"/></w:rPr>"
            f"<w:t>{esc(cell)}</w:t></w:r></w:p></w:tc>"
            for cell in row
        )
        row_xml.append(f"<w:tr>{cells}</w:tr>")
    return "<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/><w:tblBorders><w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/><w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/><w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/></w:tblBorders></w:tblPr>" + "".join(row_xml) + "</w:tbl>"


def document_xml(blocks: list[Any]) -> str:
    body = []
    for block in blocks:
        if isinstance(block, dict) and block.get("kind") == "table":
            body.append(table_xml(block.get("rows", [])))
        else:
            text, style, align = block
            body.append(paragraph_xml(text, style, align))
    sect = f"<w:sectPr><w:pgMar w:top=\"{MARGIN_TWIPS}\" w:right=\"{MARGIN_TWIPS}\" w:bottom=\"{MARGIN_TWIPS}\" w:left=\"{MARGIN_TWIPS}\" w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/></w:sectPr>"
    return "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\"><w:body>" + "".join(body) + sect + "</w:body></w:document>"


def write_minimal_docx(path: Path, blocks: list[Any]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"><Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/><Default Extension=\"xml\" ContentType=\"application/xml\"/><Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/></Types>")
        zf.writestr("_rels/.rels", "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"><Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/></Relationships>")
        zf.writestr("word/_rels/document.xml.rels", "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\"/>")
        zf.writestr("word/document.xml", document_xml(blocks))


def label_for(key: str) -> str:
    return FIELD_LABELS.get(key, key.replace("_", " ").title())


def normalise_rows(table: Any) -> list[list[Any]]:
    if isinstance(table, dict):
        headers = table.get("headers") or []
        rows = table.get("rows") or []
        if headers:
            return [headers] + rows
        return rows
    if isinstance(table, list):
        return table
    return [[table]]


def add_value(blocks: list[Any], value: Any, bullet: bool = False) -> None:
    if value in (None, "", [], {}):
        return
    if isinstance(value, str):
        prefix = "- " if bullet else ""
        blocks.append((prefix + value, "Normal", "both"))
        return
    if isinstance(value, list):
        for item in value:
            add_value(blocks, item, bullet=True)
        return
    if isinstance(value, dict):
        if value.get("kind") == "table" or value.get("table"):
            rows = normalise_rows(value.get("rows") if value.get("kind") == "table" else value.get("table"))
            blocks.append({"kind": "table", "rows": rows})
            return
        heading = value.get("heading") or value.get("topic") or value.get("module_theme") or value.get("question")
        if heading:
            blocks.append((str(heading), "Heading2", "left"))
        for key, val in value.items():
            if key in {"heading", "topic"} or val in (None, "", [], {}):
                continue
            if key == "table":
                blocks.append({"kind": "table", "rows": normalise_rows(val)})
            elif key in {"points", "mark_points", "thesis_options", "paragraph_plan"} and isinstance(val, list):
                blocks.append((label_for(key), "Heading2", "left"))
                for point in val:
                    add_value(blocks, point, bullet=True)
            elif isinstance(val, list):
                blocks.append((label_for(key), "Heading2", "left"))
                for item in val:
                    add_value(blocks, item, bullet=True)
            elif isinstance(val, dict):
                blocks.append((label_for(key), "Heading2", "left"))
                add_value(blocks, val)
            else:
                blocks.append((f"{label_for(key)}: {val}", "Normal", "both"))
        return
    blocks.append((str(value), "Normal", "both"))


def add_named_section(blocks: list[Any], heading: str, value: Any) -> None:
    if value in (None, "", [], {}):
        return
    blocks.append((heading, "Heading1", "left"))
    add_value(blocks, value)


def add_sections(blocks: list[Any], sections: Any) -> None:
    if not sections:
        return
    if isinstance(sections, dict):
        sections = [sections]
    for section in sections:
        if isinstance(section, str):
            blocks.append((section, "Heading1", "left"))
            continue
        heading = section.get("heading") or section.get("title") or "Topic-by-Topic Exam Preparation Notes"
        blocks.append((heading, "Heading1", "left"))
        content = section.get("blocks") or section.get("content") or section.get("points") or []
        add_value(blocks, content)


def blocks_from_plan(plan: dict[str, Any]) -> list[Any]:
    blocks: list[Any] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
    for key, heading in SECTION_ORDER:
        add_named_section(blocks, heading, plan.get(key))
    add_sections(blocks, plan.get("sections"))
    if len(blocks) == 1:
        blocks.append(("Add course and practice material to generate exam preparation notes.", "Normal", "both"))
    return blocks


def generate(plan: dict[str, Any], output_dir: str | Path = ".") -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out = output_dir / OUTPUT_NAME
    write_minimal_docx(out, blocks_from_plan(plan))
    return out


def self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        out = generate({"title": "Exam Preparation Notes", "course_overview": "This course covers exam preparation.", "mcq_preparation": [{"tested_point": "Potency", "correct_reasoning": "Compare EC50."}]}, td)
        assert out.exists()
        with zipfile.ZipFile(out) as zf:
            assert "word/document.xml" in zf.namelist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan")
    parser.add_argument("--out", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8")) if args.plan else {"title": "Exam Preparation Notes"}
    print(generate(plan, args.out))


if __name__ == "__main__":
    main()
