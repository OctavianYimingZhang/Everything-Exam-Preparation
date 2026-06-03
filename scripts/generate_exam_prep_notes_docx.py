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
LISTABLE_REASONS = {
    "source_numbered_list",
    "source_bulleted_list",
    "past_paper_list_question",
    "criteria_set",
    "taxonomy_or_contrast",
    "short_answer_mark_points",
    "definition_group",
}
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


def table_cell_xml(text: Any) -> str:
    return (
        "<w:tc>"
        '<w:tcPr><w:tcW w:w="2400" w:type="dxa"/></w:tcPr>'
        '<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>'
        '<w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="000000"/></w:rPr>'
        f"<w:t>{xml_escape(text)}</w:t></w:r></w:p>"
        "</w:tc>"
    )


def table_rows(table: dict[str, Any]) -> list[Any]:
    return [table["headers"]] + table["rows"]


def table_xml(rows: list[Any]) -> str:
    row_parts = []
    for row in rows[:28]:
        cells = row if isinstance(row, list) else [row]
        row_parts.append("<w:tr>" + "".join(table_cell_xml(cell) for cell in cells[:8]) + "</w:tr>")
    return (
        "<w:tbl>"
        "<w:tblPr>"
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>'
        "</w:tblBorders>"
        "</w:tblPr>"
        + "".join(row_parts)
        + "</w:tbl>"
    )


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
        elif isinstance(block, dict) and block.get("kind") == "table":
            body_parts.append(table_xml(block.get("rows") or []))
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


def source_decision_scopes(source_scan: dict[str, Any] | None) -> dict[str, str]:
    if not source_scan:
        return {}
    return {
        str(decision.get("source_id")): str(decision.get("evidence_scope"))
        for decision in source_scan.get("source_decisions", [])
        if decision.get("route") == "exam_prep_notes"
    }


def allowed_source_scope_for_block(block: dict[str, Any]) -> set[str]:
    if block.get("evidence_scope") == "exam_emphasis":
        return {"exam_emphasis"}
    return {"factual_course_content"}


def validate_source_scopes(block: dict[str, Any], scopes: dict[str, str], failures: list[str]) -> None:
    if not scopes:
        return
    allowed = allowed_source_scope_for_block(block)
    block_id = str(block.get("block_id") or "unknown")
    for source_id in block.get("source_ids", []) or []:
        scope = scopes.get(str(source_id))
        if not scope:
            failures.append(f"source_without_route_decision:{block_id}:{source_id}")
        elif scope == "needs_confirmation":
            failures.append(f"unconfirmed_source_in_notes:{block_id}:{source_id}")
        elif scope not in allowed:
            failures.append(f"source_scope_not_allowed:{block_id}:{source_id}:{scope}")


def word_count(text: Any) -> int:
    return len(re.findall(r"\w+", str(text)))


def validate_points(block: dict[str, Any], failures: list[str]) -> None:
    block_id = str(block.get("block_id") or "unknown")
    points = block.get("points")
    if not isinstance(points, list) or not points:
        failures.append(f"points_required:{block_id}")
        return
    for index, point in enumerate(points, start=1):
        if not isinstance(point, dict):
            failures.append(f"legacy_string_point_not_allowed:{block_id}:{index}")
            continue
        if not str(point.get("label") or "").strip():
            failures.append(f"point_missing_label:{block_id}:{index}")
        explanation = str(point.get("explanation") or "").strip()
        if word_count(explanation) < 5:
            failures.append(f"point_explanation_too_short:{block_id}:{point.get('label', index)}")


def validate_table(block: dict[str, Any], failures: list[str]) -> None:
    block_id = str(block.get("block_id") or "unknown")
    table = block.get("table")
    if isinstance(table, list):
        failures.append(f"legacy_array_table_not_allowed:{block_id}")
        return
    if not isinstance(table, dict):
        failures.append(f"compact_table_missing_table:{block_id}")
        return
    headers = table.get("headers")
    rows = table.get("rows")
    if not isinstance(headers, list) or not headers:
        failures.append(f"compact_table_missing_headers:{block_id}")
    if not isinstance(rows, list) or not rows:
        failures.append(f"compact_table_missing_rows:{block_id}")


def validate_plan_contract(plan: dict[str, Any], source_scan: dict[str, Any] | None = None) -> list[str]:
    failures: list[str] = []
    legacy = sorted(LEGACY_TOP_LEVEL_KEYS.intersection(plan))
    if legacy:
        failures.append(f"legacy_top_level_keys:{','.join(legacy)}")
    for key in ["title", "ordering", "visual_policy", "sections"]:
        if key not in plan:
            failures.append(f"missing_required:{key}")
    if plan.get("visual_policy") not in {"auto_source_visuals", "user_requested_text_only"}:
        failures.append("invalid_visual_policy")
    visual_decisions = plan.get("visual_decisions") or {}
    for key in ["candidate_count", "selected_count", "user_requested_text_only"]:
        if key not in visual_decisions:
            failures.append(f"visual_decisions_missing:{key}")
    selected_visual_ids = visual_decisions.get("selected_visual_ids") or []
    candidate_count = int(visual_decisions.get("candidate_count") or 0)
    selected_count = int(visual_decisions.get("selected_count") or 0)
    rejected_visuals = visual_decisions.get("rejected_visuals") or []
    if selected_count != len(selected_visual_ids):
        failures.append("selected_visual_count_mismatch")
    if plan.get("visual_policy") == "auto_source_visuals":
        if visual_decisions.get("user_requested_text_only"):
            failures.append("auto_visuals_marked_text_only")
        if candidate_count > 0 and selected_count == 0 and len(rejected_visuals) < candidate_count:
            failures.append("auto_visual_candidates_unresolved")
    if plan.get("visual_policy") == "user_requested_text_only":
        if not visual_decisions.get("user_requested_text_only"):
            failures.append("text_only_without_user_request")
        if selected_count or plan.get("visuals"):
            failures.append("text_only_plan_has_visuals")

    visual_map = plan_visuals(plan)
    source_scopes = source_decision_scopes(source_scan)
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
            reason = block.get("listability_reason")
            if not reason:
                failures.append(f"missing_listability_reason:{block_id or section_index}")
            if reason in LISTABLE_REASONS and mode not in {"kp_list", "compact_table", "image_plus_kp_list"}:
                failures.append(f"listable_block_wrong_render_mode:{block_id}:{reason}:{mode}")
            if not block.get("heading"):
                failures.append(f"block_missing_heading:{block_id or section_index}")
            if not block.get("source_ids"):
                failures.append(f"block_missing_source_ids:{block_id or section_index}")
            validate_source_scopes(block, source_scopes, failures)
            if mode == "paragraph" and not block.get("paragraph"):
                failures.append(f"paragraph_missing_text:{block_id}")
            if mode == "kp_list":
                validate_points(block, failures)
            if mode == "compact_table":
                validate_table(block, failures)
            if mode == "mechanism_chain" and not block.get("chain"):
                failures.append(f"mechanism_chain_missing_chain:{block_id}")
            if mode == "image_plus_kp_list" and (not block.get("visual_ids") or not block.get("points")):
                failures.append(f"image_plus_kp_list_missing_visual_or_points:{block_id}")
            if mode == "image_plus_kp_list":
                validate_points(block, failures)
            if mode != "image_plus_kp_list" and block.get("visual_ids"):
                failures.append(f"visual_ids_require_image_plus_kp_list:{block_id}")
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
        if visual.get("selection_state") != "selected":
            failures.append(f"visual_not_selected:{vid}")
        if visual.get("is_decorative"):
            failures.append(f"decorative_visual_selected:{vid}")
        if is_generic_caption(caption):
            failures.append(f"generic_visual_caption:{vid}")
        if not visual.get("use_reason"):
            failures.append(f"visual_missing_use_reason:{vid}")
        if visual.get("visual_kind") == "generated_schematic" and not visual.get("asset_path"):
            failures.append(f"generated_schematic_missing_asset_path:{vid}")
        if after_block_id not in block_ids:
            failures.append(f"visual_without_block_ownership:{vid}")
        if vid in visual_references and after_block_id not in visual_references[vid]:
            failures.append(f"visual_placement_mismatch:{vid}")
    unreferenced = sorted(set(visual_map) - referenced_visuals)
    if unreferenced:
        failures.append(f"unreferenced_visuals:{','.join(unreferenced)}")
    return failures


def render_visuals_for_block(block: dict[str, Any], visual_map: dict[str, dict[str, Any]]) -> list[Any]:
    rendered = []
    for vid in block.get("visual_ids", []) or []:
        visual = visual_map[str(vid)]
        rendered.append({"kind": "image", "visual": visual})
    return rendered


def point_text(point: Any) -> str:
    if not isinstance(point, dict):
        raise ValueError("legacy_string_point_not_allowed")
    label = str(point["label"]).strip()
    explanation = str(point["explanation"]).strip()
    text = f"{label} - {explanation}"
    exam_use = str(point.get("exam_use") or "").strip()
    limitation = str(point.get("limitation") or "").strip()
    if exam_use:
        text += f"; exam use: {exam_use}"
    if limitation:
        text += f"; limitation: {limitation}"
    return text


def add_points(blocks: list[Any], points: list[Any], limit: int = 16) -> None:
    for point in points[:limit]:
        blocks.append((f"- {point_text(point)}", "Normal", "both"))


def add_table(blocks: list[Any], table: dict[str, Any]) -> None:
    blocks.append({"kind": "table", "rows": table_rows(table)})


def build_docx_blocks(plan: dict[str, Any], source_scan: dict[str, Any] | None = None) -> list[Any]:
    failures = validate_plan_contract(plan, source_scan)
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
            elif mode == "compact_table":
                add_table(blocks, block["table"])
            elif mode == "mechanism_chain":
                blocks.append((" -> ".join(str(step) for step in block.get("chain", [])), "Normal", "both"))
    return blocks


def generate(plan: dict[str, Any], output_dir: Path, source_scan: dict[str, Any] | None = None) -> Path:
    out = output_dir / OUTPUT_NAME
    write_minimal_docx(out, build_docx_blocks(plan, source_scan))
    return out


def sample_strict_plan(image_path: Path) -> dict[str, Any]:
    return {
        "title": "Exam Preparation Notes",
        "ordering": "exam_emphasis_first",
        "visual_policy": "auto_source_visuals",
        "visual_decisions": {"candidate_count": 1, "selected_count": 1, "user_requested_text_only": False, "selected_visual_ids": ["V1"]},
        "visuals": [
            {
                "visual_id": "V1",
                "source_id": "SRC1",
                "selection_state": "selected",
                "asset_path": str(image_path),
                "visual_kind": "source_embedded_image",
                "caption": "Reaction curve showing early rate estimation",
                "use_reason": "The graph explains why the initial slope is used before substrate depletion.",
                "placement": {"after_block_id": "B1", "max_width_inches": 1.0, "height_inches": 1.0},
                "source_locator": {"slide": "1"},
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
                        "listability_reason": "source_bulleted_list",
                        "source_form_signal": "source slide pairs a graph with named interpretation points",
                        "exam_prompt_signal": "graph interpretation answers often need named readout cues",
                        "source_ids": ["SRC1"],
                        "paragraph": "Initial slope estimates early reaction rate before substrate depletion.",
                        "points": [
                            {
                                "label": "Axes",
                                "explanation": "Define the measured readout and the variable being changed."
                            },
                            {
                                "label": "Plateau",
                                "explanation": "Can reflect substrate depletion rather than initial velocity."
                            }
                        ],
                        "visual_ids": ["V1"],
                    },
                    {
                        "block_id": "B2",
                        "heading": "Rate readout table",
                        "render_mode": "compact_table",
                        "listability_reason": "taxonomy_or_contrast",
                        "source_form_signal": "features and exam uses form a two-column contrast",
                        "source_ids": ["SRC1"],
                        "table": {
                            "headers": ["Feature", "Exam use"],
                            "rows": [["Initial slope", "Estimate early rate before depletion"]]
                        },
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
            assert "<w:drawing>" in doc
            assert "<w:tbl>" in doc
            assert "Visual aids" not in doc
        factual_scan = {"source_decisions": [{"source_id": "SRC1", "route": "exam_prep_notes", "evidence_scope": "factual_course_content"}]}
        assert not validate_plan_contract(sample_strict_plan(image_path), factual_scan)
        style_scan = {"source_decisions": [{"source_id": "SRC1", "route": "exam_prep_notes", "evidence_scope": "style_only"}]}
        assert "source_scope_not_allowed" in ";".join(validate_plan_contract(sample_strict_plan(image_path), style_scan))
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
        legacy_points = sample_strict_plan(image_path)
        legacy_points["sections"][0]["blocks"][0]["points"] = ["Axes define the measured readout."]
        assert "legacy_string_point_not_allowed" in ";".join(validate_plan_contract(legacy_points))
        paragraph_listable = sample_strict_plan(image_path)
        paragraph_listable["sections"][0]["blocks"][1]["render_mode"] = "paragraph"
        paragraph_listable["sections"][0]["blocks"][1]["paragraph"] = "The comparison is a set of named criteria."
        paragraph_listable["sections"][0]["blocks"][1].pop("table")
        assert "listable_block_wrong_render_mode" in ";".join(validate_plan_contract(paragraph_listable))
        legacy_table = sample_strict_plan(image_path)
        legacy_table["sections"][0]["blocks"][1]["table"] = [["Feature", "Exam use"]]
        assert "legacy_array_table_not_allowed" in ";".join(validate_plan_contract(legacy_table))
        text_only = sample_strict_plan(image_path)
        text_only["visual_policy"] = "user_requested_text_only"
        text_only["visual_decisions"] = {"candidate_count": 1, "selected_count": 0, "user_requested_text_only": False}
        text_only["visuals"] = []
        text_only["sections"][0]["blocks"][0]["render_mode"] = "kp_list"
        text_only["sections"][0]["blocks"][0].pop("visual_ids")
        assert "text_only_without_user_request" in ";".join(validate_plan_contract(text_only))
        unresolved = sample_strict_plan(image_path)
        unresolved["visual_decisions"] = {"candidate_count": 1, "selected_count": 0, "user_requested_text_only": False}
        unresolved["visuals"] = []
        unresolved["sections"][0]["blocks"][0]["render_mode"] = "kp_list"
        unresolved["sections"][0]["blocks"][0].pop("visual_ids")
        assert "auto_visual_candidates_unresolved" in ";".join(validate_plan_contract(unresolved))
    print("generate_exam_prep_notes_docx self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan")
    parser.add_argument("--source-scan")
    parser.add_argument("--out", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.plan:
        parser.error("--plan is required")
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    source_scan = json.loads(Path(args.source_scan).read_text(encoding="utf-8")) if args.source_scan else None
    path = generate(plan, Path(args.out), source_scan)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
