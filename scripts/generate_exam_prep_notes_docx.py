from __future__ import annotations

import argparse
import base64
import html
import json
import re
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
RENDER_MODES = {"kp_list", "compact_table", "mechanism_chain", "image_plus_kp_list", "paragraph"}
LEGACY_TOP_LEVEL_KEYS = {
    "high_yield_exam_map",
    "topics",
    "methods_and_data",
    "confusions",
    "practical_operations",
    "past_paper_emphasis",
    "add_on_sections",
    "revision_checklist",
}
GENERIC_CAPTION_PATTERNS = [
    r"^\s*visual aid for\b",
    r"^\s*source visual\s*$",
    r"^\s*image\d+\s*$",
]


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


def visual_id(visual: dict[str, Any]) -> str:
    return str(visual.get("visual_id") or visual.get("id") or "")


def visual_caption(visual: Any) -> str:
    if isinstance(visual, dict):
        return str(visual.get("caption") or visual.get("media_name") or visual.get("asset_path") or visual.get("path") or "Source visual")
    return str(visual)


def is_generic_caption(caption: str) -> bool:
    return any(re.search(pattern, caption, flags=re.I) for pattern in GENERIC_CAPTION_PATTERNS)


def visual_bytes(visual: Any) -> tuple[bytes, str] | None:
    if not isinstance(visual, dict):
        path = Path(str(visual))
        if path.exists() and path.suffix.lower() in IMAGE_CONTENT_TYPES:
            return path.read_bytes(), path.suffix.lower()
        return None
    direct = visual.get("asset_path") or visual.get("image_path") or visual.get("path")
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


def visual_size(visual: Any) -> tuple[float, float]:
    width = MAX_IMAGE_WIDTH_INCHES
    height = 2.1
    if isinstance(visual, dict):
        placement = visual.get("placement") or {}
        width = min(float(placement.get("max_width_inches") or visual.get("max_width_inches") or width), MAX_IMAGE_WIDTH_INCHES)
        height = float(placement.get("height_inches") or visual.get("height_inches") or max(0.6, width * 0.56))
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
                raise ValueError(f"visual_asset_missing:{caption}")
            data, ext = resolved
            rid = f"rIdImage{image_index}"
            name = f"image{image_index}{ext}"
            width, height = visual_size(visual)
            body_parts.append(drawing(rid, caption, image_index, width, height))
            body_parts.append(paragraph(caption, "Normal", "center"))
            media_parts.append((f"word/media/{name}", ext, data, IMAGE_CONTENT_TYPES[ext]))
            rel_parts.append(
                f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>'
            )
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
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:pPr><w:jc w:val="left"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:color w:val="000000"/></w:rPr></w:style>
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


def plan_visuals(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    visuals = {}
    for visual in plan.get("visuals", []):
        if isinstance(visual, dict) and visual_id(visual):
            visuals[visual_id(visual)] = visual
    return visuals


def validate_plan_contract(plan: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    legacy = sorted(LEGACY_TOP_LEVEL_KEYS.intersection(plan))
    if legacy:
        failures.append(f"legacy_top_level_keys:{','.join(legacy)}")
    for key in ["title", "ordering", "visual_policy", "sections"]:
        if key not in plan:
            failures.append(f"missing_required:{key}")
    if plan.get("visual_policy") not in {"block_level_only", "text_only_with_skip_reason"}:
        failures.append("invalid_visual_policy")

    visual_map = plan_visuals(plan)
    block_ids: set[str] = set()
    referenced_visuals: set[str] = set()
    visual_references: dict[str, set[str]] = {}
    sections = plan.get("sections", [])
    if not isinstance(sections, list) or not sections:
        failures.append("sections_required")
        sections = []
    for section_index, section in enumerate(sections, start=1):
        if not isinstance(section, dict):
            failures.append(f"section_not_object:{section_index}")
            continue
        if not section.get("section_id"):
            failures.append(f"section_missing_id:{section_index}")
        if not section.get("heading"):
            failures.append(f"section_missing_heading:{section_index}")
        blocks = section.get("blocks")
        if not isinstance(blocks, list) or not blocks:
            failures.append(f"section_missing_blocks:{section.get('section_id', section_index)}")
            continue
        for block_index, block in enumerate(blocks, start=1):
            if not isinstance(block, dict):
                failures.append(f"block_not_object:{section_index}.{block_index}")
                continue
            block_id = str(block.get("block_id") or "")
            if not block_id:
                failures.append(f"block_missing_id:{section_index}.{block_index}")
            elif block_id in block_ids:
                failures.append(f"duplicate_block_id:{block_id}")
            else:
                block_ids.add(block_id)
            mode = block.get("render_mode")
            if mode not in RENDER_MODES:
                failures.append(f"invalid_render_mode:{block_id or section_index}")
            if not block.get("heading"):
                failures.append(f"block_missing_heading:{block_id or section_index}")
            if not block.get("source_ids"):
                failures.append(f"block_missing_source_ids:{block_id or section_index}")
            if mode == "paragraph" and not block.get("paragraph"):
                failures.append(f"paragraph_missing_text:{block_id}")
            if mode == "kp_list" and not block.get("points"):
                failures.append(f"kp_list_missing_points:{block_id}")
            if mode == "compact_table" and not block.get("table"):
                failures.append(f"compact_table_missing_table:{block_id}")
            if mode == "mechanism_chain" and not block.get("chain"):
                failures.append(f"mechanism_chain_missing_chain:{block_id}")
            if mode == "image_plus_kp_list" and (not block.get("visual_ids") or not block.get("points")):
                failures.append(f"image_plus_kp_list_missing_visual_or_points:{block_id}")
            for vid in block.get("visual_ids", []) or []:
                vid_text = str(vid)
                referenced_visuals.add(vid_text)
                visual_references.setdefault(vid_text, set()).add(block_id)
                if vid_text not in visual_map:
                    failures.append(f"missing_visual_spec:{vid}")

    for vid, visual in visual_map.items():
        caption = visual_caption(visual)
        placement = visual.get("placement") or {}
        after_block_id = str(placement.get("after_block_id") or "")
        if visual.get("is_decorative"):
            failures.append(f"decorative_visual_selected:{vid}")
        if is_generic_caption(caption):
            failures.append(f"generic_visual_caption:{vid}")
        if not visual.get("use_reason"):
            failures.append(f"visual_missing_use_reason:{vid}")
        if after_block_id not in block_ids:
            failures.append(f"visual_without_block_ownership:{vid}")
        if vid in visual_references and after_block_id not in visual_references[vid]:
            failures.append(f"visual_placement_mismatch:{vid}")
    unreferenced = sorted(set(visual_map) - referenced_visuals)
    if unreferenced:
        failures.append(f"unreferenced_visuals:{','.join(unreferenced)}")
    if plan.get("visual_policy") == "text_only_with_skip_reason" and visual_map:
        failures.append("text_only_plan_has_visuals")
    if plan.get("visual_policy") == "text_only_with_skip_reason" and not (plan.get("visual_decisions") or {}).get("skip_reason"):
        failures.append("text_only_plan_missing_skip_reason")
    return failures


def render_visuals_for_block(block: dict[str, Any], visual_map: dict[str, dict[str, Any]]) -> list[Any]:
    rendered = []
    for vid in block.get("visual_ids", []) or []:
        visual = visual_map[str(vid)]
        rendered.append({"kind": "image", "visual": visual})
    return rendered


def add_points(blocks: list[Any], points: list[Any], limit: int = 16) -> None:
    for point in points[:limit]:
        blocks.append((f"- {point}", "Normal", "both"))


def add_table(blocks: list[Any], rows: list[Any]) -> None:
    for row in rows[:28]:
        cells = row if isinstance(row, list) else [row]
        blocks.append((" | ".join(str(cell) for cell in cells), "Normal", "both"))


def build_docx_blocks(plan: dict[str, Any]) -> list[Any]:
    failures = validate_plan_contract(plan)
    if failures:
        raise ValueError("invalid_exam_prep_notes_plan:" + ";".join(failures))

    visual_map = plan_visuals(plan)
    blocks: list[Any] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
    for section in plan["sections"]:
        blocks.append((str(section["heading"]), "Heading1", "left"))
        for block in section["blocks"]:
            blocks.append((str(block["heading"]), "Heading2", "left"))
            paragraph_text = block.get("paragraph")
            if paragraph_text:
                blocks.append((str(paragraph_text), "Normal", "both"))
            mode = block["render_mode"]
            if mode == "image_plus_kp_list":
                blocks.extend(render_visuals_for_block(block, visual_map))
                add_points(blocks, block.get("points", []), 12)
            elif mode == "kp_list":
                add_points(blocks, block.get("points", []))
                blocks.extend(render_visuals_for_block(block, visual_map))
            elif mode == "compact_table":
                add_table(blocks, block.get("table", []))
                blocks.extend(render_visuals_for_block(block, visual_map))
            elif mode == "mechanism_chain":
                blocks.append((" -> ".join(str(step) for step in block.get("chain", [])), "Normal", "both"))
                blocks.extend(render_visuals_for_block(block, visual_map))
    return blocks


def generate(plan: dict[str, Any], output_dir: Path) -> Path:
    out = output_dir / OUTPUT_NAME
    write_minimal_docx(out, build_docx_blocks(plan))
    return out


def sample_strict_plan(image_path: Path) -> dict[str, Any]:
    return {
        "title": "Exam Preparation Notes",
        "ordering": "exam_emphasis_first",
        "visual_policy": "block_level_only",
        "visual_decisions": {"selected_visual_ids": ["V1"]},
        "visuals": [
            {
                "visual_id": "V1",
                "asset_path": str(image_path),
                "visual_kind": "source_image",
                "caption": "Reaction curve showing early rate estimation",
                "use_reason": "The graph explains why the initial slope is used before substrate depletion.",
                "placement": {"after_block_id": "B1", "max_width_inches": 1.0, "height_inches": 1.0},
                "is_decorative": False,
            }
        ],
        "sections": [
            {
                "section_id": "S1",
                "heading": "Core concepts",
                "blocks": [
                    {
                        "block_id": "B1",
                        "heading": "Enzyme rate",
                        "render_mode": "image_plus_kp_list",
                        "source_ids": ["SRC1"],
                        "paragraph": "Initial slope estimates early reaction rate before substrate depletion.",
                        "points": ["Axes define the measured readout.", "A later plateau can reflect substrate depletion rather than initial velocity."],
                        "visual_ids": ["V1"],
                    }
                ],
            }
        ],
    }


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        image_path = Path(td) / "visual.png"
        image_path.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lzU2VwAAAABJRU5ErkJggg=="))
        out = generate(sample_strict_plan(image_path), Path(td))
        assert out.name == OUTPUT_NAME and out.exists()
        with zipfile.ZipFile(out) as zf:
            doc = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            assert "word/document.xml" in zf.namelist()
            assert any(name.startswith("word/media/") for name in zf.namelist())
            assert "Visual aids" not in doc
        try:
            generate({"title": "Exam Preparation Notes", "topics": ["legacy"]}, Path(td))
        except ValueError as exc:
            assert "legacy_top_level_keys" in str(exc)
        else:
            raise AssertionError("legacy plan was accepted")
        bad_plan = sample_strict_plan(image_path)
        bad_plan["visuals"][0]["caption"] = "Visual aid for enzyme rate"
        assert "generic_visual_caption" in ";".join(validate_plan_contract(bad_plan))
        mismatch_plan = sample_strict_plan(image_path)
        mismatch_plan["visuals"][0]["placement"]["after_block_id"] = "B2"
        assert "visual_placement_mismatch" in ";".join(validate_plan_contract(mismatch_plan))
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
