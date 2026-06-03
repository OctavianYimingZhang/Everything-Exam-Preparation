from __future__ import annotations

import argparse
import base64
import html
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

OUTPUT_NAME = "Exam_Preparation_Notes.docx"
MARGIN_TWIPS = 1417
LINE_SPACING = 360
EMU_PER_INCH = 914400
MAX_IMAGE_WIDTH_INCHES = 3.8
IMAGE_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
}


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


def drawing(rid: str, caption: str, index: int, width_inches: float, height_inches: float) -> str:
    cx = int(width_inches * EMU_PER_INCH)
    cy = int(height_inches * EMU_PER_INCH)
    descr = xml_escape(caption or f"Visual {index}")
    return f"""
<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:r><w:drawing>
  <wp:inline distT="0" distB="0" distL="0" distR="0">
    <wp:extent cx="{cx}" cy="{cy}"/>
    <wp:docPr id="{index}" name="Exam prep visual {index}" descr="{descr}"/>
    <a:graphic>
      <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
        <pic:pic>
          <pic:nvPicPr><pic:cNvPr id="{index}" name="{descr}"/><pic:cNvPicPr/></pic:nvPicPr>
          <pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
          <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
        </pic:pic>
      </a:graphicData>
    </a:graphic>
  </wp:inline>
</w:drawing></w:r></w:p>"""


def visual_bytes(visual: Any) -> tuple[bytes, str] | None:
    if not isinstance(visual, dict):
        path = Path(str(visual))
        if path.exists() and path.suffix.lower() in IMAGE_CONTENT_TYPES:
            return path.read_bytes(), path.suffix.lower()
        return None
    direct = visual.get("image_path") or visual.get("path")
    if direct:
        path = Path(str(direct))
        if path.exists() and path.suffix.lower() in IMAGE_CONTENT_TYPES:
            return path.read_bytes(), path.suffix.lower()
    source_path = visual.get("source_path")
    media_name = visual.get("media_name")
    if source_path and media_name:
        ext = Path(str(media_name)).suffix.lower()
        if ext not in IMAGE_CONTENT_TYPES:
            return None
        with zipfile.ZipFile(Path(str(source_path))) as zf:
            return zf.read(str(media_name)), ext
    return None


def visual_caption(visual: Any) -> str:
    if isinstance(visual, dict):
        return str(visual.get("caption") or visual.get("media_name") or visual.get("path") or "Source visual")
    return str(visual)


def visual_size(visual: Any) -> tuple[float, float]:
    width = MAX_IMAGE_WIDTH_INCHES
    height = 2.1
    if isinstance(visual, dict):
        width = min(float(visual.get("max_width_inches") or width), MAX_IMAGE_WIDTH_INCHES)
        height = float(visual.get("height_inches") or max(0.6, width * 0.56))
    return width, height


def build_body_and_media(blocks: list[Any]) -> tuple[str, list[tuple[str, str, bytes, str]], str]:
    body_parts: list[str] = []
    media_parts: list[tuple[str, str, bytes, str]] = []
    rel_parts: list[str] = []
    image_index = 1
    for block in blocks:
        if isinstance(block, dict) and block.get("kind") == "image":
            visual = block.get("visual", {})
            caption = visual_caption(visual)
            resolved = visual_bytes(visual)
            if not resolved:
                body_parts.append(paragraph(f"Visual: {caption}", "Normal", "both"))
                continue
            data, ext = resolved
            rid = f"rIdImage{image_index}"
            name = f"image{image_index}{ext}"
            width, height = visual_size(visual)
            body_parts.append(drawing(rid, caption, image_index, width, height))
            if caption:
                body_parts.append(paragraph(caption, "Normal", "center"))
            media_parts.append((f"word/media/{name}", ext, data, IMAGE_CONTENT_TYPES[ext]))
            rel_parts.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>')
            image_index += 1
        else:
            text, style, align = block
            body_parts.append(paragraph(text, style, align))
    return "".join(body_parts), media_parts, "".join(rel_parts)


def write_minimal_docx(path: Path, blocks: list[Any]) -> None:
    body, media_parts, image_rels = build_body_and_media(blocks)
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:body>{body}<w:sectPr><w:pgMar w:top="{MARGIN_TWIPS}" w:right="{MARGIN_TWIPS}" w:bottom="{MARGIN_TWIPS}" w:left="{MARGIN_TWIPS}" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>"""
    styles = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="000000"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:jc w:val="both"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:jc w:val="both"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="000000"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:jc w:val="center"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:color w:val="000000"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:jc w:val="left"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:color w:val="000000"/></w:rPr></w:style>
</w:styles>"""
    image_defaults = "".join(f'<Default Extension="{ext.lstrip(".")}" ContentType="{content_type}"/>' for ext, content_type in IMAGE_CONTENT_TYPES.items())
    content_types = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>{image_defaults}<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>"""
    doc_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{image_rels}</Relationships>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
        zf.writestr("word/document.xml", document)
        zf.writestr("word/styles.xml", styles)
        for name, _ext, data, _content_type in media_parts:
            zf.writestr(name, data)


def infer_render_mode(item: dict[str, Any]) -> str:
    if item.get("render_mode"):
        return str(item["render_mode"])
    if item.get("visuals") and item.get("bullets"):
        return "image_plus_kp_list"
    if item.get("table_rows"):
        return "compact_table"
    if item.get("chain"):
        return "mechanism_chain"
    if item.get("bullets"):
        return "kp_list"
    return "paragraph"


def add_notes_item(blocks: list[Any], item: Any) -> None:
    if not isinstance(item, dict):
        blocks.append((f"- {item}", "Normal", "both"))
        return
    heading = item.get("heading") or item.get("title") or item.get("concept")
    detail = item.get("explanation") or item.get("detail") or item.get("content") or ""
    mode = infer_render_mode(item)
    if heading:
        blocks.append((str(heading), "Heading1", "left"))
    if mode == "image_plus_kp_list":
        for visual in item.get("visuals", [])[:3]:
            blocks.append({"kind": "image", "visual": visual})
        if detail:
            blocks.append((str(detail), "Normal", "both"))
        for bullet in item.get("bullets", [])[:12]:
            blocks.append((f"- {bullet}", "Normal", "both"))
    elif mode == "kp_list":
        if detail:
            blocks.append((str(detail), "Normal", "both"))
        for bullet in item.get("bullets", [])[:16]:
            blocks.append((f"- {bullet}", "Normal", "both"))
    elif mode == "compact_table":
        if detail:
            blocks.append((str(detail), "Normal", "both"))
        for row in item.get("table_rows", [])[:24]:
            cells = row if isinstance(row, list) else [row]
            blocks.append((" | ".join(str(cell) for cell in cells), "Normal", "both"))
    elif mode == "mechanism_chain":
        chain = item.get("chain") or []
        if chain:
            blocks.append((" -> ".join(str(step) for step in chain), "Normal", "both"))
        if detail:
            blocks.append((str(detail), "Normal", "both"))
    else:
        if detail:
            blocks.append((str(detail), "Normal", "both"))
        for bullet in item.get("bullets", [])[:8]:
            blocks.append((f"- {bullet}", "Normal", "both"))


def plan_to_blocks(plan: dict[str, Any]) -> list[Any]:
    blocks: list[Any] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
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
            add_notes_item(blocks, item)
    visuals = plan.get("visuals", [])
    if visuals:
        blocks.append(("Visual aids", "Heading1", "left"))
        for visual in visuals[:12]:
            blocks.append({"kind": "image", "visual": visual})
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
        image_path = Path(td) / "visual.png"
        image_path.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lzU2VwAAAABJRU5ErkJggg=="))
        plan = {
            "title": "Exam Preparation Notes",
            "topics": [{
                "heading": "Enzyme rate",
                "render_mode": "image_plus_kp_list",
                "explanation": "Initial slope estimates early reaction rate before substrate depletion.",
                "bullets": ["Axes define the measured readout."],
                "visuals": [{"path": str(image_path), "caption": "Reaction curve", "max_width_inches": 1.0, "height_inches": 1.0}],
            }],
            "revision_checklist": ["Practise graph interpretation."],
        }
        out = generate(plan, Path(td))
        assert out.name == OUTPUT_NAME and out.exists()
        with zipfile.ZipFile(out) as zf:
            assert "word/document.xml" in zf.namelist()
            assert any(name.startswith("word/media/") for name in zf.namelist())
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
