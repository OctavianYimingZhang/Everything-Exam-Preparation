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


def xml_escape(text: str) -> str:
    return html.escape(str(text), quote=False)


def paragraph(text: str, style: str = "Normal", align: str = "both") -> str:
    text = xml_escape(text)
    return (
        '<w:p><w:pPr>'
        f'<w:pStyle w:val="{style}"/><w:jc w:val="{align}"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/>'
        '</w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="000000"/></w:rPr>'
        f'<w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
    )


def write_minimal_docx(path: Path, blocks: list[tuple[str, str, str]]) -> None:
    body = "".join(paragraph(text, style, align) for text, style, align in blocks)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr><w:pgMar w:top="{MARGIN_TWIPS}" w:right="{MARGIN_TWIPS}" w:bottom="{MARGIN_TWIPS}" w:left="{MARGIN_TWIPS}" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>"""
    styles = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="000000"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:jc w:val="both"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:jc w:val="both"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="000000"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:jc w:val="center"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:color w:val="000000"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:jc w:val="left"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:color w:val="000000"/></w:rPr></w:style>
</w:styles>"""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", styles)


def plan_to_blocks(plan: dict[str, Any]) -> list[tuple[str, str, str]]:
    blocks: list[tuple[str, str, str]] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
    sections = [
        ("High-yield exam map", plan.get("high_yield_exam_map", [])),
        ("Core concepts by source/topic", plan.get("topics", [])),
        ("Mechanisms, methods, calculations, and data interpretation", plan.get("methods_and_data", [])),
        ("Common confusions and contrasts", plan.get("confusions", [])),
        ("Practical/data/problem operations", plan.get("practical_operations", [])),
        ("Past-paper emphasis map", plan.get("past_paper_emphasis", [])),
        ("Exam-mode add-on", plan.get("add_on_sections", [])),
        ("Final quick revision checklist", plan.get("revision_checklist", [])),
    ]
    for heading, value in sections:
        if not value:
            continue
        blocks.append((heading, "Heading1", "left"))
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, dict):
                line = item.get("heading") or item.get("title") or item.get("concept") or "Point"
                detail = item.get("explanation") or item.get("detail") or item.get("content") or ""
                blocks.append((f"{line}: {detail}" if detail else str(line), "Normal", "both"))
                for bullet in item.get("bullets", [])[:12]:
                    blocks.append((f"- {bullet}", "Normal", "both"))
            else:
                blocks.append((f"- {item}", "Normal", "both"))
    visuals = plan.get("visuals", [])
    if visuals:
        blocks.append(("Visual aids", "Heading1", "left"))
        for visual in visuals[:12]:
            caption = visual.get("caption") if isinstance(visual, dict) else str(visual)
            blocks.append((f"Visual: {caption}", "Normal", "both"))
    if len(blocks) == 1:
        blocks.extend([
            ("High-yield exam map", "Heading1", "left"),
            ("Use supplied course sources to build source-backed concepts, methods, calculations, and exam operations.", "Normal", "both"),
            ("Final quick revision checklist", "Heading1", "left"),
            ("- Rehearse definitions, mechanisms, method steps, graph interpretation, limitations, and answer structures.", "Normal", "both"),
        ])
    return blocks


def generate(plan: dict[str, Any], output_dir: Path) -> Path:
    out = output_dir / OUTPUT_NAME
    write_minimal_docx(out, plan_to_blocks(plan))
    return out


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        plan = {"title": "Exam Preparation Notes", "topics": [{"heading": "Enzyme rate", "explanation": "Initial slope estimates early reaction rate before substrate depletion.", "bullets": ["Axes define the measured readout."]}], "revision_checklist": ["Practise graph interpretation."]}
        out = generate(plan, Path(td))
        assert out.name == OUTPUT_NAME and out.exists()
        with zipfile.ZipFile(out) as zf:
            assert "word/document.xml" in zf.namelist()
    print("generate_exam_prep_notes_docx self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan")
    parser.add_argument("--out", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.plan:
        parser.error("--plan is required")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    path = generate(plan, Path(args.out))
    print(path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
