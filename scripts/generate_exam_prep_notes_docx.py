#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

MARGIN_TWIPS = 1417
LINE_SPACING = 360

INTERNAL_PUBLIC_HEADINGS = {
    "source and extraction limits",
    "source inventory",
    "coverage calibration",
    "examples retained in the notes plan",
    "final revision checklist",
    "workflow plan",
    "qa",
    "quality assurance",
    "subagent result",
    "extraction limits",
}

RAW_FORMULA_PATTERNS = [
    r"\bpartial\b",
    r"\bsqrt\s*\(",
    r"\bsum_[A-Za-z0-9]+",
    r"\bdot\b",
    r"\bcross\b",
]

SUPERSCRIPT = str.maketrans(
    {
        "0": "⁰",
        "1": "¹",
        "2": "²",
        "3": "³",
        "4": "⁴",
        "5": "⁵",
        "6": "⁶",
        "7": "⁷",
        "8": "⁸",
        "9": "⁹",
        "+": "⁺",
        "-": "⁻",
        "=": "⁼",
        "(": "⁽",
        ")": "⁾",
        "n": "ⁿ",
    }
)
SUBSCRIPT = str.maketrans(
    {
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
        "+": "₊",
        "-": "₋",
        "=": "₌",
        "(": "₍",
        ")": "₎",
        "a": "ₐ",
        "e": "ₑ",
        "h": "ₕ",
        "i": "ᵢ",
        "j": "ⱼ",
        "k": "ₖ",
        "l": "ₗ",
        "m": "ₘ",
        "n": "ₙ",
        "o": "ₒ",
        "p": "ₚ",
        "r": "ᵣ",
        "s": "ₛ",
        "t": "ₜ",
        "u": "ᵤ",
        "v": "ᵥ",
        "x": "ₓ",
        "y": "ᵧ",
    }
)

GREEK_AND_OPERATORS = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "Delta": "Δ",
    "epsilon": "ε",
    "theta": "θ",
    "lambda": "λ",
    "mu": "μ",
    "rho": "ρ",
    "sigma": "σ",
    "tau": "τ",
    "phi": "φ",
    "omega": "ω",
    "Omega": "Ω",
    "hbar": "ℏ",
    "nabla": "∇",
}


def xml_escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def visible_formula(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(
        r"\bpartial\s+([A-Za-z0-9_{}]+)\s*/\s*partial\s+([A-Za-z0-9_{}]+)",
        r"∂\1/∂\2",
        text,
    )
    text = re.sub(
        r"\bpartial\s*/\s*partial\s+([A-Za-z0-9_{}]+)",
        r"∂/∂\1",
        text,
    )
    text = re.sub(r"\bsqrt\s*\(([^()]+)\)", r"√(\1)", text)
    text = re.sub(r"\bsum_ij\b", "∑ᵢⱼ", text)
    text = re.sub(r"\bsum_i\b", "∑ᵢ", text)
    text = re.sub(r"\bsum_j\b", "∑ⱼ", text)
    text = re.sub(r"\bint\b", "∫", text)
    text = re.sub(r"\bdot\b", "·", text)
    text = re.sub(r"\bcross\b", "×", text)
    for raw, replacement in GREEK_AND_OPERATORS.items():
        text = re.sub(rf"\b{re.escape(raw)}\b", replacement, text)
    text = re.sub(r"\*\*", "^", text)
    text = re.sub(r"\s+", " ", text)

    def sup(match: re.Match[str]) -> str:
        token = match.group(1)
        return token.translate(SUPERSCRIPT) if len(token) <= 4 else "^" + token

    def sub(match: re.Match[str]) -> str:
        token = match.group(1)
        return token.translate(SUBSCRIPT) if len(token) <= 4 else "_" + token

    text = re.sub(r"\^([A-Za-z0-9+\-=()]{1,4})", sup, text)
    text = re.sub(r"_([A-Za-z0-9+\-=()]{1,4})", sub, text)
    return text


def has_raw_formula_tokens(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in RAW_FORMULA_PATTERNS)


def paragraph_xml(text: str, style: str = "Normal", align: str = "both") -> str:
    style_xml = "" if style == "Normal" else f'<w:pStyle w:val="{xml_escape(style)}"/>'
    bold = "<w:b/>" if style in {"Title", "Heading1", "Heading2"} else ""
    size = {"Title": "32", "Heading1": "26", "Heading2": "23", "Formula": "24"}.get(style, "22")
    return (
        "<w:p><w:pPr>"
        f"{style_xml}<w:jc w:val=\"{xml_escape(align)}\"/><w:spacing w:line=\"{LINE_SPACING}\" w:lineRule=\"auto\"/>"
        "</w:pPr><w:r><w:rPr>"
        f"<w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/>{bold}<w:sz w:val=\"{size}\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{xml_escape(text)}</w:t></w:r></w:p>"
    )


def formula_xml(formula: str) -> str:
    formula = visible_formula(formula)
    return (
        f'<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr>'
        "<m:oMathPara><m:oMath><m:r><m:rPr><m:nor/></m:rPr>"
        f"<m:t>{xml_escape(formula)}</m:t>"
        "</m:r></m:oMath></m:oMathPara></w:p>"
    )


def table_cell_xml(text: Any) -> str:
    value = visible_formula(text) if has_raw_formula_tokens(str(text)) else str(text)
    return (
        "<w:tc>"
        '<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>'
        '<w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="20"/></w:rPr>'
        f"<w:t>{xml_escape(value)}</w:t></w:r></w:p>"
        "</w:tc>"
    )


def table_xml(rows: list[list[Any]]) -> str:
    rendered_rows = []
    for row in rows:
        cells = row if isinstance(row, list) else [row]
        rendered_rows.append("<w:tr>" + "".join(table_cell_xml(cell) for cell in cells) + "</w:tr>")
    return (
        "<w:tbl><w:tblPr><w:tblW w:w=\"0\" w:type=\"auto\"/>"
        "<w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"4\"/><w:left w:val=\"single\" w:sz=\"4\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"4\"/><w:right w:val=\"single\" w:sz=\"4\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"4\"/><w:insideV w:val=\"single\" w:sz=\"4\"/>"
        "</w:tblBorders></w:tblPr>"
        + "".join(rendered_rows)
        + "</w:tbl>"
    )


def document_xml(blocks: list[Any]) -> str:
    body = []
    for block in blocks:
        if isinstance(block, dict) and block.get("kind") == "table":
            body.append(table_xml(block.get("rows", [])))
        elif isinstance(block, dict) and block.get("kind") == "formula":
            body.append(formula_xml(str(block.get("formula") or "")))
        else:
            text, style, align = block
            body.append(paragraph_xml(text, style, align))
    sect = (
        f'<w:sectPr><w:pgMar w:top="{MARGIN_TWIPS}" w:right="{MARGIN_TWIPS}" '
        f'w:bottom="{MARGIN_TWIPS}" w:left="{MARGIN_TWIPS}" w:header="720" '
        'w:footer="720" w:gutter="0"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
        "<w:body>"
        + "".join(body)
        + sect
        + "</w:body></w:document>"
    )


def styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
        '</w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:jc w:val="both"/>'
        f'<w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/>'
        '<w:pPr><w:jc w:val="both"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
        '<w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
        '<w:pPr><w:jc w:val="left"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>'
        '<w:pPr><w:jc w:val="left"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr></w:style>'
        "</w:styles>"
    )


def write_minimal_docx(path: Path, blocks: list[Any]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            "</Types>",
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>",
        )
        zf.writestr("word/_rels/document.xml.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        zf.writestr("word/document.xml", document_xml(blocks))
        zf.writestr("word/styles.xml", styles_xml())


def table_rows(block: dict[str, Any]) -> list[list[Any]]:
    table = block.get("table") or {}
    if isinstance(table, dict):
        headers = table.get("headers") or block.get("headers") or []
        rows = table.get("rows") or block.get("rows") or []
        return ([headers] if headers else []) + rows
    rows = block.get("rows") or []
    return rows if isinstance(rows, list) else []


def add_text(blocks: list[Any], text: Any, bullet: bool = False) -> None:
    if text in (None, "", [], {}):
        return
    if isinstance(text, list):
        for item in text:
            add_text(blocks, item, bullet=True)
        return
    if isinstance(text, dict):
        label = text.get("label") or text.get("heading") or text.get("term")
        explanation = text.get("explanation") or text.get("text") or text.get("definition")
        exam_use = text.get("exam_use")
        parts = []
        if label:
            parts.append(str(label))
        if explanation:
            parts.append(str(explanation))
        if exam_use:
            parts.append(f"Exam use: {exam_use}")
        add_text(blocks, " - ".join(parts) if parts else json.dumps(text, ensure_ascii=False), bullet=bullet)
        return
    prefix = "• " if bullet else ""
    blocks.append((prefix + str(text), "Normal", "both"))


def render_block(blocks: list[Any], block: dict[str, Any]) -> None:
    heading = block.get("heading") or block.get("title")
    if heading:
        blocks.append((str(heading), "Heading2", "left"))
    mode = block.get("render_mode") or block.get("kind") or "paragraph"
    if mode == "formula_block":
        formula = block.get("formula") or block.get("expression") or block.get("text")
        blocks.append({"kind": "formula", "formula": formula})
        add_text(blocks, block.get("symbols"))
        add_text(blocks, block.get("assumptions"))
        add_text(blocks, block.get("use") or block.get("exam_use") or block.get("explanation"))
    elif mode == "compact_table":
        rows = table_rows(block)
        if rows:
            blocks.append({"kind": "table", "rows": rows})
    elif mode in {"kp_list", "image_plus_kp_list"}:
        add_text(blocks, block.get("points") or block.get("key_points") or block.get("content"), bullet=True)
    elif mode == "mechanism_chain":
        steps = block.get("steps") or block.get("chain") or block.get("points") or []
        for idx, step in enumerate(steps, 1):
            add_text(blocks, f"{idx}. {step}")
    else:
        add_text(blocks, block.get("text") or block.get("paragraph") or block.get("content") or block.get("explanation"))


def validate_plan_contract(plan: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for section in plan.get("sections", []) or []:
        heading = str(section.get("heading") or section.get("title") or "").strip().lower()
        if heading in INTERNAL_PUBLIC_HEADINGS:
            failures.append(f"internal_public_heading:{heading}")
        for block in section.get("blocks", []) or []:
            if not isinstance(block, dict):
                continue
            block_heading = str(block.get("heading") or block.get("title") or "").strip().lower()
            if block_heading in INTERNAL_PUBLIC_HEADINGS:
                failures.append(f"internal_public_heading:{block_heading}")
            if block.get("render_mode") == "formula_block" and not visible_formula(block.get("formula") or block.get("expression") or block.get("text")):
                failures.append("empty_formula_block")
    return failures


def blocks_from_plan(plan: dict[str, Any]) -> list[Any]:
    failures = validate_plan_contract(plan)
    if failures:
        raise ValueError(";".join(failures))
    blocks: list[Any] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
    for section in plan.get("sections", []) or []:
        heading = section.get("heading") or section.get("title")
        if heading:
            blocks.append((str(heading), "Heading1", "left"))
        for block in section.get("blocks", []) or []:
            if isinstance(block, dict):
                render_block(blocks, block)
            else:
                add_text(blocks, block)
    if len(blocks) == 1:
        blocks.append(("No knowledge content was supplied.", "Normal", "both"))
    return blocks


def safe_docx_name(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        raw = "notes"
    raw = Path(raw).name
    if raw.lower().endswith(".docx"):
        raw = raw[:-5]
    slug = re.sub(r"[^A-Za-z0-9._ -]+", " ", raw).strip()
    slug = re.sub(r"\s+", "_", slug).strip("._- ")
    if not slug:
        slug = "notes"
    return f"{slug}.docx"


def output_path(plan: dict[str, Any], output_target: str | Path = ".") -> Path:
    target = Path(output_target)
    if target.suffix.lower() == ".docx":
        return target
    name_source = (
        plan.get("output_name")
        or plan.get("filename")
        or plan.get("file_name")
        or plan.get("document_name")
        or plan.get("source_name")
        or plan.get("title")
    )
    return target / safe_docx_name(name_source)


def generate(plan: dict[str, Any], output_target: str | Path = ".") -> Path:
    out = output_path(plan, output_target)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_minimal_docx(out, blocks_from_plan(plan))
    return out


def self_test() -> None:
    plan = {
        "title": "Exam Preparation Notes",
        "output_name": "custom_notes.docx",
        "sections": [
            {
                "heading": "Charge conservation",
                "blocks": [
                    {
                        "render_mode": "paragraph",
                        "heading": "Meaning",
                        "text": "Charge conservation links local charge accumulation to current flow.",
                    },
                    {
                        "render_mode": "formula_block",
                        "heading": "Continuity equation",
                        "formula": "partial rho/partial t + nabla dot J = 0",
                        "symbols": ["ρ is charge density.", "J is current density."],
                        "use": "Use it to test whether a current field changes charge density.",
                    },
                ],
            }
        ],
    }
    with tempfile.TemporaryDirectory() as td:
        out = generate(plan, td)
        assert out.name == "custom_notes.docx"
        with zipfile.ZipFile(out) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            assert "word/document.xml" in zf.namelist()
            assert "∂ρ/∂t + ∇ · J = 0" in raw
            assert "partial" not in raw
            assert "Coverage Calibration" not in raw
        generated = generate({"title": "Charge Conservation Notes", "sections": [{"heading": "Meaning", "blocks": ["Charge is locally conserved."]}]}, td)
        assert generated.name == "Charge_Conservation_Notes.docx"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan")
    parser.add_argument("--out", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8")) if args.plan else {"title": "Exam Preparation Notes", "sections": []}
    print(generate(plan, args.out))


if __name__ == "__main__":
    main()
