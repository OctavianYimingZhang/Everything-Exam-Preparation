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


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def paragraph_xml(text: str, style: str = "Normal", align: str = "both") -> str:
    style_xml = "" if style == "Normal" else f'<w:pStyle w:val="{esc(style)}"/>'
    return (
        "<w:p><w:pPr>"
        f"{style_xml}<w:jc w:val=\"{esc(align)}\"/><w:spacing w:line=\"{LINE_SPACING}\" w:lineRule=\"auto\"/>"
        "</w:pPr><w:r><w:rPr><w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/></w:rPr>"
        f"<w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r></w:p>"
    )


def table_xml(rows: list[list[Any]]) -> str:
    row_xml = []
    for row in rows:
        cells = "".join(f"<w:tc><w:p><w:r><w:rPr><w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/></w:rPr><w:t>{esc(cell)}</w:t></w:r></w:p></w:tc>" for cell in row)
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


def add_text_value(blocks: list[Any], title: str, value: Any) -> None:
    if value in (None, "", [], {}):
        return
    blocks.append((title, "Heading2", "left"))
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                label = item.get("topic") or item.get("heading") or item.get("question") or item.get("label") or "Point"
                text = item.get("explanation") or item.get("paragraph") or item.get("text") or item.get("answer") or json.dumps(item, ensure_ascii=False)
                blocks.append((f"- {label}: {text}", "Normal", "both"))
            else:
                blocks.append((f"- {item}", "Normal", "both"))
    elif isinstance(value, dict):
        for key, val in value.items():
            blocks.append((f"{key}: {val}", "Normal", "both"))
    else:
        blocks.append((str(value), "Normal", "both"))


def blocks_from_plan(plan: dict[str, Any]) -> list[Any]:
    blocks: list[Any] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
    add_text_value(blocks, "Course knowledge map", plan.get("course_knowledge_map"))
    add_text_value(blocks, "Exam habit analysis", plan.get("exam_habit_analysis"))
    for key, heading in [
        ("mcq_preparation", "MCQ preparation"),
        ("short_answer_preparation", "Short-answer preparation"),
        ("long_answer_preparation", "Long-answer preparation"),
        ("essay_preparation", "Essay preparation"),
    ]:
        add_text_value(blocks, heading, plan.get(key))
    for section in plan.get("sections", []) or []:
        blocks.append((section.get("heading", "Section"), "Heading1", "left"))
        for block in section.get("blocks", []) or []:
            if isinstance(block, str):
                blocks.append((block, "Normal", "both"))
                continue
            if block.get("heading"):
                blocks.append((block["heading"], "Heading2", "left"))
            if block.get("text") or block.get("paragraph"):
                blocks.append((block.get("text") or block.get("paragraph"), "Normal", "both"))
            if block.get("points"):
                add_text_value(blocks, "Key points", block.get("points"))
            if block.get("table"):
                table = block["table"]
                rows = table.get("rows", table) if isinstance(table, dict) else table
                if rows:
                    blocks.append({"kind": "table", "rows": rows})
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
        out = generate({"title": "Exam Preparation Notes", "sections": [{"heading": "Topic", "blocks": [{"heading": "Mechanism", "text": "Explain the mechanism."}]}]}, td)
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
