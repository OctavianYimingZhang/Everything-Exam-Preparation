#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import struct
import tempfile
import zipfile
from pathlib import Path
from typing import Any

MARGIN_TWIPS = 1417
LINE_SPACING = 360
EMU_PER_PIXEL = 9525
MAX_IMAGE_WIDTH_EMU = 5_400_000
IMAGE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
IMAGE_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
}

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
    "exam practice",
    "common mcq traps",
    "mcq traps",
    "short-answer templates",
    "short answer templates",
    "long-answer structures",
    "long answer structures",
    "data and calculation questions",
    "practical/data tactics",
    "reliable extra reading",
    "standalone reading list",
}

ADDON_ONLY_FIELDS = {
    "exam_use",
    "mode",
    "mode_specific",
    "mcq",
    "distractor",
    "distractors",
    "wrong_statement",
    "mark_points",
    "answer_structure",
    "example_answer",
    "essay_plan",
    "exam_type_related",
}

RAW_FORMULA_PATTERNS = [
    r"\bpartial\b",
    r"\\partial\b",
    r"\\frac\b",
    r"\\sqrt\b",
    r"\bsqrt\s*\(",
    r"\bsqrt\s*\{",
    r"\bsum_[A-Za-z0-9]+",
    r"\\sum\b",
    r"\bprod_[A-Za-z0-9]+",
    r"\\prod\b",
    r"\bdot\b",
    r"\bcross\b",
    r"->|=>|<->|<=>|⇌|→",
    r"\b[A-Z][a-z]?\d+[A-Za-z0-9+-]*\b",
    r"\[[A-Za-z0-9+-]+\]",
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
    "grad": "∇",
    "infty": "∞",
    "infinity": "∞",
    "pi": "π",
    "Pi": "Π",
    "partial": "∂",
}

ELEMENTS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
}

CODE_LIKE_PATTERNS = [
    r"^\s*(def|class|import|from|return|if|elif|else|for|while|try|except|function|const|let|var)\b",
    r"\b(console\.log|print\(|lambda\b|return\b|async\b|await\b)\b",
    r"(==|!=|===|!==|&&|\|\||\+\+|--|::)",
    r"[{};]\s*$",
]


def xml_escape(value: Any) -> str:
    return html.escape(str(value), quote=False)


def visible_formula(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if looks_code_like(text):
        return re.sub(r"\s+", " ", text)
    text = normalize_latex_like(text)
    text = normalize_common_symbol_tokens(text)
    text = normalize_arrows_and_relations(text)
    text = normalize_derivatives(text)
    text = normalize_named_constants(text)
    text = normalize_large_operators(text)
    text = normalize_vectors(text)
    text = normalize_roots_and_fractions(text)
    text = normalize_chemistry(text)
    text = normalize_variable_indices(text)
    text = normalize_units(text)
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

    text = re.sub(r"\^([A-Za-z0-9+\-=]{1,4})", sup, text)
    text = re.sub(r"_([A-Za-z0-9+\-=()]{1,4})", sub, text)
    return text


def has_raw_formula_tokens(text: str) -> bool:
    return any(re.search(pattern, text, flags=re.I) for pattern in RAW_FORMULA_PATTERNS)


def normalize_public_heading(value: Any) -> str:
    heading = str(value or "").strip().lower()
    heading = re.sub(r"^\d+(?:\.\d+)*[.)]?\s*", "", heading)
    return heading


def looks_code_like(text: str) -> bool:
    stripped = text.strip()
    if "\n" in stripped and any(re.search(pattern, stripped, flags=re.M) for pattern in CODE_LIKE_PATTERNS):
        return True
    return any(re.search(pattern, stripped) for pattern in CODE_LIKE_PATTERNS)


def normalize_latex_like(text: str) -> str:
    text = re.sub(r"\\left|\\right", "", text)
    text = re.sub(r"\\mathrm\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\text\{([^{}]+)\}", r"\1", text)
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    text = re.sub(r"\\sqrt\{([^{}]+)\}", r"√(\1)", text)
    text = re.sub(r"\\vec\{?([A-Za-z])\}?", r"\1⃗", text)
    text = re.sub(r"\\hat\{?([A-Za-z])\}?", r"\1̂", text)
    text = re.sub(r"\\bar\{?([A-Za-z])\}?", r"\1̄", text)
    text = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK_AND_OPERATORS.get(m.group(1), m.group(0)), text)
    text = re.sub(r"_\{([^{}]+)\}", r"_\1", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)
    return text


def normalize_named_constants(text: str) -> str:
    for raw, replacement in GREEK_AND_OPERATORS.items():
        text = re.sub(rf"\b{re.escape(raw)}\b", replacement, text)
    return text


def normalize_arrows_and_relations(text: str) -> str:
    replacements = [
        (r"<=>", "⇌"),
        (r"<->", "↔"),
        (r"-->", "→"),
        (r"->", "→"),
        (r"=>", "⇒"),
        (r"<-", "←"),
        (r"\\rightleftharpoons", "⇌"),
        (r"\\leftrightarrow", "↔"),
        (r"\\rightarrow", "→"),
        (r"\\to\b", "→"),
        (r"\\leftarrow", "←"),
        (r">=", "≥"),
        (r"<=", "≤"),
        (r"!=", "≠"),
        (r"~=", "≈"),
        (r"\\approx", "≈"),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
    return text


def normalize_derivatives(text: str) -> str:
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
    text = re.sub(
        r"\bd\s*\^\s*2\s*([A-Za-z0-9_{}]*)\s*/\s*d\s*([A-Za-z0-9_{}]+)\s*\^\s*2",
        lambda m: f"d²{m.group(1)}/d{m.group(2)}²",
        text,
    )
    text = re.sub(
        r"\bd\s*([A-Za-z0-9_{}]*)\s*/\s*d\s*([A-Za-z0-9_{}]+)",
        lambda m: f"d{m.group(1)}/d{m.group(2)}",
        text,
    )
    return text


def normalize_large_operators(text: str) -> str:
    text = re.sub(r"\\sum|\bsum\b", "∑", text)
    text = re.sub(r"\\prod|\bprod\b", "∏", text)
    text = re.sub(r"\\int|\bint\b", "∫", text)
    text = re.sub(r"∑_ij\b", "∑ᵢⱼ", text)
    text = re.sub(r"∑_i\b", "∑ᵢ", text)
    text = re.sub(r"∑_j\b", "∑ⱼ", text)
    text = re.sub(r"∏_i\b", "∏ᵢ", text)
    return text


def normalize_vectors(text: str) -> str:
    text = re.sub(r"\bvec\s+([A-Za-z])\b", r"\1⃗", text)
    text = re.sub(r"\bhat\s+([A-Za-z])\b", r"\1̂", text)
    text = re.sub(r"\bdot\b", "·", text)
    text = re.sub(r"\bcross\b", "×", text)
    return text


def normalize_roots_and_fractions(text: str) -> str:
    text = re.sub(r"\bsqrt\s*\(([^()]+)\)", r"√(\1)", text)
    text = re.sub(r"\bsqrt\s*\{([^{}]+)\}", r"√(\1)", text)
    return text


def is_element_sequence(token: str) -> bool:
    body = re.sub(r"(\d*[+-]+|\^\d*[+-]+)$", "", token)
    matches = re.findall(r"([A-Z][a-z]?)(\d*)", body)
    if not matches:
        return False
    rebuilt = "".join(el + count for el, count in matches)
    return rebuilt == body and all(el in ELEMENTS for el, _ in matches)


def format_chemical_token(token: str) -> str:
    suffix = ""
    body = token
    charge_match = re.search(r"([+-]+)$", token)
    if charge_match:
        signs = charge_match.group(1)
        prefix = token[: -len(signs)]
        element_counts = re.findall(r"([A-Z][a-z]?)(\d*)", prefix)
        if len(element_counts) == 1 and element_counts[0][1]:
            suffix = element_counts[0][1] + signs
            body = element_counts[0][0]
        else:
            suffix = signs
            body = prefix
    isotope_match = re.match(r"\^(\d+)([A-Z][a-z]?.*)", body)
    isotope = ""
    if isotope_match:
        isotope = isotope_match.group(1).translate(SUPERSCRIPT)
        body = isotope_match.group(2)
    pieces = []
    for element, count in re.findall(r"([A-Z][a-z]?)(\d*)", body):
        pieces.append(element)
        if count:
            pieces.append(count.translate(SUBSCRIPT))
    charge = ""
    if suffix:
        charge = suffix.translate(SUPERSCRIPT)
    return isotope + "".join(pieces) + charge


def normalize_chemistry(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        token = match.group(0)
        return format_chemical_token(token) if is_element_sequence(token) else token

    text = re.sub(r"(?<![A-Za-z0-9])\^[0-9]{1,3}[A-Z][a-z]?(?:[A-Za-z0-9]*)(?:\d*[+-]+)?(?![A-Za-z0-9])", repl, text)
    text = re.sub(r"(?<![A-Za-z0-9])(?:[A-Z][a-z]?\d*){1,}(?:\d*[+-]+)?(?![A-Za-z0-9])", repl, text)
    text = re.sub(r"(?<![A-Za-z0-9])e-(?![A-Za-z0-9])", "e⁻", text)
    text = re.sub(r"\[([A-Za-z][A-Za-z0-9+-]*)\]", lambda m: "[" + normalize_chemistry(m.group(1)) + "]", text)
    text = re.sub(r"\((aq|s|l|g)\)", lambda m: f"({m.group(1)})", text)
    return text


def normalize_common_symbol_tokens(text: str) -> str:
    replacements = {
        "pKa": "pKₐ",
        "pKb": "pKᵦ",
        "Km": "Kₘ",
        "Vmax": "Vₘₐₓ",
        "V_max": "Vₘₐₓ",
        "delta G": "ΔG",
        "Delta G": "ΔG",
        "deltaG": "ΔG",
        "DeltaG": "ΔG",
        "δ G": "ΔG",
        "Δ G": "ΔG",
    }
    for raw, repl in replacements.items():
        text = re.sub(rf"\b{re.escape(raw)}\b", repl, text)
    return text


def normalize_variable_indices(text: str) -> str:
    return re.sub(
        r"(?<![A-Za-z])([A-Za-zα-ωΑ-Ω])(\d+)\b",
        lambda m: f"{m.group(1)}{m.group(2).translate(SUBSCRIPT)}",
        text,
    )


def normalize_units(text: str) -> str:
    return re.sub(r"\b([A-Za-zμΩ]+)-(\d+)\b", lambda m: f"{m.group(1)}⁻{m.group(2).translate(SUPERSCRIPT)}", text)


def is_addon_document(plan: dict[str, Any]) -> bool:
    kind = str(plan.get("document_kind") or plan.get("kind") or plan.get("output") or "").lower()
    return "addon" in kind or "exam_type_related" in kind or "worked_solutions" in kind


def is_result_only_exam_report(plan: dict[str, Any]) -> bool:
    kind = str(plan.get("document_kind") or plan.get("kind") or plan.get("output") or "").lower()
    if plan.get("result_only") is True:
        return True
    return kind in {"mcq_exam_type_related_addon", "short_answer_exam_type_related_addon"}


def image_extension(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix if suffix in IMAGE_CONTENT_TYPES else ".png"


def image_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        idx = 2
        while idx + 9 < len(data):
            if data[idx] != 0xFF:
                idx += 1
                continue
            marker = data[idx + 1]
            idx += 2
            if marker in {0xD8, 0xD9}:
                continue
            if idx + 2 > len(data):
                break
            size = int.from_bytes(data[idx:idx + 2], "big")
            if marker in {0xC0, 0xC1, 0xC2, 0xC3} and idx + 7 < len(data):
                height = int.from_bytes(data[idx + 3:idx + 5], "big")
                width = int.from_bytes(data[idx + 5:idx + 7], "big")
                return width, height
            idx += size
    return 640, 360


def image_emu_size(path: Path) -> tuple[int, int]:
    width_px, height_px = image_dimensions(path)
    width = max(1, width_px) * EMU_PER_PIXEL
    height = max(1, height_px) * EMU_PER_PIXEL
    if width > MAX_IMAGE_WIDTH_EMU:
        scale = MAX_IMAGE_WIDTH_EMU / width
        width = MAX_IMAGE_WIDTH_EMU
        height = int(height * scale)
    return int(width), int(height)


def paragraph_xml(text: str, style: str = "Normal", align: str = "both") -> str:
    style_xml = "" if style == "Normal" else f'<w:pStyle w:val="{xml_escape(style)}"/>'
    keep_next = "<w:keepNext/>" if style in {"Title", "Heading1", "Heading2"} else ""
    bold = "<w:b/>" if style in {"Title", "Heading1", "Heading2"} else ""
    italic = "<w:i/>" if style == "Caption" else ""
    size = {"Title": "32", "Heading1": "26", "Heading2": "23", "Caption": "18", "Formula": "24"}.get(style, "21")
    color = "000000"
    return (
        "<w:p><w:pPr>"
        f"{style_xml}{keep_next}<w:jc w:val=\"{xml_escape(align)}\"/><w:spacing w:line=\"{LINE_SPACING}\" w:lineRule=\"auto\"/>"
        "</w:pPr><w:r><w:rPr>"
        f"<w:rFonts w:ascii=\"Arial\" w:hAnsi=\"Arial\"/>{bold}{italic}<w:color w:val=\"{color}\"/><w:sz w:val=\"{size}\"/>"
        "</w:rPr>"
        f"<w:t xml:space=\"preserve\">{xml_escape(text)}</w:t></w:r></w:p>"
    )


def formula_xml(formula: str) -> str:
    formula = visible_formula(formula)
    return (
        f'<w:p><w:pPr><w:jc w:val="center"/><w:shd w:fill="F6F7F8"/>'
        f'<w:spacing w:line="{LINE_SPACING}" w:lineRule="auto"/></w:pPr>'
        "<m:oMathPara><m:oMath><m:r><m:rPr><m:nor/></m:rPr>"
        f"<m:t>{xml_escape(formula)}</m:t>"
        "</m:r></m:oMath></m:oMathPara></w:p>"
    )


def table_cell_xml(text: Any, header: bool = False) -> str:
    value = visible_formula(text) if has_raw_formula_tokens(str(text)) else str(text)
    shading = '<w:shd w:fill="E9EEF3"/>' if header else ""
    bold = "<w:b/>" if header else ""
    return (
        "<w:tc>"
        f'<w:tcPr>{shading}</w:tcPr>'
        '<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>'
        f'<w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>{bold}<w:color w:val="000000"/><w:sz w:val="20"/></w:rPr>'
        f"<w:t>{xml_escape(value)}</w:t></w:r></w:p>"
        "</w:tc>"
    )


def table_xml(rows: list[list[Any]]) -> str:
    rendered_rows = []
    for idx, row in enumerate(rows):
        cells = row if isinstance(row, list) else [row]
        row_properties = "<w:trPr><w:cantSplit/>" + ("<w:tblHeader/>" if idx == 0 else "") + "</w:trPr>"
        rendered_rows.append(
            "<w:tr>"
            + row_properties
            + "".join(table_cell_xml(cell, header=(idx == 0)) for cell in cells)
            + "</w:tr>"
        )
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


def image_xml(block: dict[str, Any]) -> str:
    rid = block.get("rid")
    if not rid:
        return ""
    cx = int(block.get("cx") or 0)
    cy = int(block.get("cy") or 0)
    doc_id = int(block.get("doc_id") or 1)
    alt = xml_escape(block.get("alt_text") or block.get("caption") or "Academic source visual")
    return (
        '<w:p><w:pPr><w:jc w:val="center"/><w:spacing w:line="240" w:lineRule="auto"/></w:pPr><w:r><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:docPr id="{doc_id}" name="Source visual {doc_id}" descr="{alt}"/>'
        '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        '<pic:pic><pic:nvPicPr>'
        f'<pic:cNvPr id="{doc_id}" name="Source visual {doc_id}"/><pic:cNvPicPr/>'
        '</pic:nvPicPr><pic:blipFill>'
        f'<a:blip r:embed="{xml_escape(rid)}"/><a:stretch><a:fillRect/></a:stretch>'
        '</pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        '</pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline>'
        '</w:drawing></w:r></w:p>'
    )


def document_xml(blocks: list[Any]) -> str:
    body = []
    for block in blocks:
        if isinstance(block, dict) and block.get("kind") == "table":
            body.append(table_xml(block.get("rows", [])))
        elif isinstance(block, dict) and block.get("kind") == "formula":
            body.append(formula_xml(str(block.get("formula") or "")))
        elif isinstance(block, dict) and block.get("kind") == "image":
            body.append(image_xml(block))
        elif isinstance(block, dict) and block.get("kind") == "page_break":
            body.append('<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        else:
            text, style, align = block
            body.append(paragraph_xml(text, style, align))
    sect = (
        f'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="{MARGIN_TWIPS}" w:right="{MARGIN_TWIPS}" '
        f'w:bottom="{MARGIN_TWIPS}" w:left="{MARGIN_TWIPS}" w:header="720" '
        'w:footer="720" w:gutter="0"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
        'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
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
        '<w:pPr><w:jc w:val="both"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
        '<w:color w:val="000000"/><w:sz w:val="21"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>'
        '<w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
        '<w:color w:val="000000"/><w:sz w:val="32"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>'
        '<w:pPr><w:jc w:val="left"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
        '<w:color w:val="000000"/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>'
        '<w:pPr><w:jc w:val="left"/></w:pPr><w:rPr><w:b/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
        '<w:color w:val="000000"/><w:sz w:val="23"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="Caption"/>'
        '<w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:i/><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>'
        '<w:color w:val="000000"/><w:sz w:val="18"/></w:rPr></w:style>'
        "</w:styles>"
    )


def prepare_media_blocks(blocks: list[Any]) -> tuple[list[Any], list[dict[str, Any]]]:
    prepared: list[Any] = []
    media: list[dict[str, Any]] = []
    for block in blocks:
        if not (isinstance(block, dict) and block.get("kind") == "image"):
            prepared.append(block)
            continue
        image_path = Path(str(block.get("path") or block.get("asset_path") or ""))
        if not is_renderable_image_path(image_path):
            continue
        ext = image_extension(image_path)
        idx = len(media) + 1
        rid = f"rId{idx}"
        media_name = f"image{idx}{ext}"
        cx, cy = image_emu_size(image_path)
        prepared_block = dict(block)
        prepared_block.update({"rid": rid, "media_name": media_name, "cx": cx, "cy": cy, "doc_id": idx})
        prepared.append(prepared_block)
        media.append({
            "rid": rid,
            "source_path": image_path,
            "media_name": media_name,
            "content_type": IMAGE_CONTENT_TYPES[ext],
        })
    return prepared, media


def document_rels_xml(media: list[dict[str, Any]]) -> str:
    relationships = [
        f'<Relationship Id="{xml_escape(item["rid"])}" Type="{IMAGE_REL_TYPE}" Target="media/{xml_escape(item["media_name"])}"/>'
        for item in media
    ]
    relationships.append(
        '<Relationship Id="rIdStyles" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
        'Target="styles.xml"/>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?><Relationships '
        'xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(relationships)
        + "</Relationships>"
    )


def content_types_xml(media: list[dict[str, Any]]) -> str:
    defaults = [
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
    ]
    seen_ext: set[str] = set()
    for item in media:
        ext = Path(str(item["media_name"])).suffix.lower().lstrip(".")
        if ext and ext not in seen_ext:
            seen_ext.add(ext)
            defaults.append(f'<Default Extension="{xml_escape(ext)}" ContentType="{xml_escape(item["content_type"])}"/>')
    return (
        '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        + "".join(defaults)
        + '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        + '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        + "</Types>"
    )


def write_minimal_docx(path: Path, blocks: list[Any]) -> None:
    prepared_blocks, media = prepare_media_blocks(blocks)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(media))
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>",
        )
        zf.writestr("word/_rels/document.xml.rels", document_rels_xml(media))
        zf.writestr("word/document.xml", document_xml(prepared_blocks))
        zf.writestr("word/styles.xml", styles_xml())
        for item in media:
            zf.write(item["source_path"], f'word/media/{item["media_name"]}')


def table_rows(block: dict[str, Any]) -> list[list[Any]]:
    table = block.get("table") or {}
    if isinstance(table, dict):
        headers = table.get("headers") or block.get("headers") or []
        rows = table.get("rows") or block.get("rows") or []
        return ([headers] if headers else []) + rows
    rows = block.get("rows") or []
    return rows if isinstance(rows, list) else []


ADDON_FIELD_ORDER = [
    "mode",
    "source",
    "source_name",
    "locator",
    "question",
    "source_question",
    "options",
    "mark_value",
    "high_frequency_knowledge_points",
    "question_demand",
    "repeated_knowledge_target",
    "expected_answer_focus",
    "analysis_prediction",
    "example_answer",
    "worked_solution",
    "answer_structure",
    "mark_points",
    "verification",
]


def label_from_key(key: str) -> str:
    return key.replace("_", " ").title()


def add_text(blocks: list[Any], text: Any, bullet: bool = False, include_addon: bool = False, result_only: bool = False) -> None:
    if text in (None, "", [], {}):
        return
    if isinstance(text, list):
        for item in text:
            add_text(blocks, item, bullet=True, include_addon=include_addon, result_only=result_only)
        return
    if isinstance(text, dict):
        if result_only:
            primary = text.get("content") or text.get("text") or text.get("paragraph")
            if primary:
                add_text(blocks, primary, bullet=bullet, include_addon=include_addon, result_only=result_only)
            scope = text.get("exam_scope")
            if scope:
                add_text(blocks, scope, include_addon=include_addon, result_only=result_only)
            return
        if include_addon:
            rendered_any = False
            ordered = [key for key in ADDON_FIELD_ORDER if key in text] + [key for key in text if key not in ADDON_FIELD_ORDER]
            for key in ordered:
                value = text.get(key)
                rendered = inline_text(value, include_addon=True)
                if rendered:
                    blocks.append((f"{label_from_key(key)}: {rendered}", "Normal", "both"))
                    rendered_any = True
            if rendered_any:
                return
        label = text.get("label") or text.get("heading") or text.get("term")
        explanation = text.get("explanation") or text.get("text") or text.get("definition")
        knowledge_use = text.get("knowledge_use") or text.get("application_context") or text.get("use")
        parts = []
        if label:
            parts.append(str(label))
        if explanation:
            parts.append(str(explanation))
        if knowledge_use:
            parts.append(str(knowledge_use))
        if parts:
            add_text(blocks, " - ".join(parts), bullet=bullet, include_addon=include_addon, result_only=result_only)
        else:
            filtered = {k: v for k, v in text.items() if k not in ADDON_ONLY_FIELDS}
            if filtered:
                add_text(blocks, json.dumps(filtered, ensure_ascii=False), bullet=bullet, include_addon=include_addon, result_only=result_only)
        return
    prefix = "• " if bullet else ""
    blocks.append((prefix + str(text), "Normal", "both"))


def inline_text(value: Any, include_addon: bool = False) -> str:
    if value in (None, "", [], {}):
        return ""
    if isinstance(value, dict):
        if include_addon:
            parts = []
            ordered = [key for key in ADDON_FIELD_ORDER if key in value] + [key for key in value if key not in ADDON_FIELD_ORDER]
            for key in ordered:
                rendered = inline_text(value.get(key), include_addon=True)
                if rendered:
                    parts.append(f"{label_from_key(key)}: {rendered}")
            return "; ".join(parts)
        label = value.get("label") or value.get("heading") or value.get("term")
        explanation = value.get("explanation") or value.get("text") or value.get("definition")
        knowledge_use = value.get("knowledge_use") or value.get("application_context") or value.get("use")
        parts = []
        if label:
            parts.append(str(label))
        if explanation:
            parts.append(str(explanation))
        if knowledge_use:
            parts.append(str(knowledge_use))
        if parts:
            return " - ".join(parts)
        filtered = {k: v for k, v in value.items() if k not in ADDON_ONLY_FIELDS}
        return json.dumps(filtered, ensure_ascii=False) if filtered else ""
    if isinstance(value, list):
        return "; ".join(item for item in (inline_text(item, include_addon=include_addon) for item in value) if item)
    return str(value)


def readable_step_text(value: Any, include_addon: bool = False) -> str:
    text = inline_text(value, include_addon=include_addon)
    technical = has_raw_formula_tokens(text) or bool(re.search(r"=|\b[A-Za-zμΩ]+-\d+\b|∝|≈|≤|≥", text))
    return visible_formula(text) if technical else text


def image_path_from_block(block: dict[str, Any]) -> str:
    return str(block.get("asset_path") or block.get("image_path") or block.get("path") or "")


def has_supported_image_signature(path: Path) -> bool:
    data = path.read_bytes()[:12]
    suffix = path.suffix.lower()
    if suffix == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8")
    if suffix == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a"))
    return False


def is_renderable_image_path(path: str | Path) -> bool:
    image_path = Path(str(path or ""))
    if not image_path.exists() or image_path.suffix.lower() not in IMAGE_CONTENT_TYPES:
        return False
    try:
        if not has_supported_image_signature(image_path):
            return False
        width, height = image_dimensions(image_path)
    except Exception:
        return False
    return width > 0 and height > 0


def add_labeled_field(blocks: list[Any], label: str, value: Any, include_addon: bool = False) -> None:
    if value in (None, "", [], {}):
        return
    if isinstance(value, list):
        blocks.append((f"{label}:", "Normal", "both"))
        for item in value:
            add_text(blocks, readable_step_text(item, include_addon=include_addon), bullet=True, include_addon=include_addon)
        return
    rendered = readable_step_text(value, include_addon=include_addon)
    if rendered:
        blocks.append((f"{label}: {rendered}", "Normal", "both"))


def render_worked_example(blocks: list[Any], block: dict[str, Any], include_addon: bool = False) -> None:
    add_labeled_field(blocks, "Question", block.get("question"), include_addon=include_addon)
    add_labeled_field(blocks, "Givens", block.get("givens"), include_addon=include_addon)
    add_labeled_field(blocks, "Target", block.get("target"), include_addon=include_addon)
    add_labeled_field(blocks, "Method", block.get("method"), include_addon=include_addon)
    steps = block.get("steps") or block.get("worked_solution") or []
    if steps:
        blocks.append(("Step-by-step solution:", "Normal", "both"))
        for idx, step in enumerate(steps, 1):
            rendered = readable_step_text(step, include_addon=include_addon)
            if rendered:
                add_text(blocks, f"{idx}. {rendered}", include_addon=include_addon)
    add_labeled_field(blocks, "Final answer", block.get("final_answer"), include_addon=include_addon)
    add_labeled_field(blocks, "Assumptions", block.get("assumptions"), include_addon=include_addon)
    add_labeled_field(blocks, "Unit check", block.get("unit_check"), include_addon=include_addon)
    add_labeled_field(blocks, "Interpretation", block.get("interpretation"), include_addon=include_addon)
    add_labeled_field(blocks, "Verification", block.get("verification"), include_addon=include_addon)


def render_block(blocks: list[Any], block: dict[str, Any], include_addon: bool = False, result_only: bool = False) -> None:
    heading = block.get("heading") or block.get("title")
    if heading:
        blocks.append((str(heading), "Heading2", "left"))
    mode = block.get("render_mode") or block.get("kind") or "paragraph"
    if mode == "exam_knowledge_point":
        add_text(blocks, block.get("content") or block.get("text") or block.get("paragraph"), include_addon=include_addon, result_only=result_only)
        add_text(blocks, block.get("exam_scope"), include_addon=include_addon, result_only=result_only)
    elif mode == "formula_block":
        formula = block.get("formula") or block.get("expression") or block.get("text")
        blocks.append({"kind": "formula", "formula": formula})
        add_text(blocks, block.get("symbols"), include_addon=include_addon, result_only=result_only)
        add_text(blocks, block.get("assumptions"), include_addon=include_addon, result_only=result_only)
        add_text(blocks, block.get("use") or block.get("knowledge_use") or block.get("application_context") or block.get("explanation"), include_addon=include_addon, result_only=result_only)
    elif mode == "compact_table":
        rows = table_rows(block)
        if rows:
            blocks.append({"kind": "table", "rows": rows})
    elif mode == "worked_example":
        render_worked_example(blocks, block, include_addon=include_addon)
    elif mode == "image_plus_kp_list":
        image_path = image_path_from_block(block)
        caption = block.get("caption") or block.get("source_locator") or block.get("locator")
        if is_renderable_image_path(image_path):
            blocks.append({
                "kind": "image",
                "path": image_path,
                "caption": caption,
                "alt_text": block.get("alt_text") or caption or heading or "Academic source visual",
            })
        if caption and is_renderable_image_path(image_path):
            blocks.append((str(caption), "Caption", "center"))
        add_text(blocks, block.get("points") or block.get("key_points") or block.get("content"), bullet=True, include_addon=include_addon, result_only=result_only)
    elif mode == "kp_list":
        add_text(blocks, block.get("points") or block.get("key_points") or block.get("content"), bullet=True, include_addon=include_addon, result_only=result_only)
    elif mode == "mechanism_chain":
        steps = block.get("steps") or block.get("chain") or block.get("points") or []
        for idx, step in enumerate(steps, 1):
            rendered_step = inline_text(step, include_addon=include_addon)
            if rendered_step:
                add_text(blocks, f"{idx}. {rendered_step}", include_addon=include_addon, result_only=result_only)
    else:
        primary = block.get("text") or block.get("paragraph") or block.get("content") or block.get("explanation")
        if primary in (None, "", [], {}) and include_addon and not result_only:
            primary = {k: v for k, v in block.items() if k not in {"render_mode", "kind", "heading", "title"}}
        add_text(blocks, primary, include_addon=include_addon, result_only=result_only)


def validate_plan_contract(plan: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if is_addon_document(plan):
        return failures
    for section in plan.get("sections", []) or []:
        heading = normalize_public_heading(section.get("heading") or section.get("title"))
        if heading in INTERNAL_PUBLIC_HEADINGS:
            failures.append(f"internal_public_heading:{heading}")
        for block in section.get("blocks", []) or []:
            if not isinstance(block, dict):
                continue
            block_heading = normalize_public_heading(block.get("heading") or block.get("title"))
            if block_heading in INTERNAL_PUBLIC_HEADINGS:
                failures.append(f"internal_public_heading:{block_heading}")
            if block.get("render_mode") == "formula_block" and not visible_formula(block.get("formula") or block.get("expression") or block.get("text")):
                failures.append("empty_formula_block")
    return failures


def blocks_from_plan(plan: dict[str, Any]) -> list[Any]:
    failures = validate_plan_contract(plan)
    if failures:
        raise ValueError(";".join(failures))
    include_addon = is_addon_document(plan)
    result_only = is_result_only_exam_report(plan)
    blocks: list[Any] = [(plan.get("title") or "Exam Preparation Notes", "Title", "center")]
    for section in plan.get("sections", []) or []:
        if section.get("page_break_before"):
            blocks.append({"kind": "page_break"})
        heading = section.get("heading") or section.get("title")
        if heading:
            blocks.append((str(heading), "Heading1", "left"))
        for block in section.get("blocks", []) or []:
            if isinstance(block, dict):
                render_block(blocks, block, include_addon=include_addon, result_only=result_only)
            else:
                add_text(blocks, block, include_addon=include_addon, result_only=result_only)
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
    assert visible_formula("partial rho/partial t + nabla dot J = 0") == "∂ρ/∂t + ∇ · J = 0"
    assert visible_formula("sum_i x_i^2 + sqrt(y^2)") == "∑ᵢ xᵢ² + √(y²)"
    assert visible_formula("d^2x/dt^2 = -omega^2 x") == "d²x/dt² = -ω² x"
    assert visible_formula("HCO3- + H+ <=> CO2 + H2O") == "HCO₃⁻ + H⁺ ⇌ CO₂ + H₂O"
    assert visible_formula("Km = (k-1 + k2)/k1; Vmax = kcat[E]") == "Kₘ = (k⁻¹ + k₂)/k₁; Vₘₐₓ = kcat[E]"
    assert visible_formula("if (x[i] != y[j]) return x_i;") == "if (x[i] != y[j]) return x_i;"
    with tempfile.TemporaryDirectory() as td:
        image_path = Path(td) / "source_visual.png"
        image_path.write_bytes(base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVR42mP8z8BQz0AEYBxVSFUBABJ4AwnfrWm6AAAAAElFTkSuQmCC"
        ))
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
                            "exam_use": "This should not render in Notes.",
                        },
                        {
                            "render_mode": "worked_example",
                            "heading": "Worked calculation example",
                            "question": "Given E = 2 V/m and H = 3 A/m, calculate the Poynting magnitude.",
                            "givens": ["E = 2 V/m", "H = 3 A/m"],
                            "target": "S",
                            "method": "Use S = E cross H for perpendicular fields.",
                            "steps": [
                                "Write the magnitude relation S = EH.",
                                "Substitute S = 2*3 = 6 W m-2.",
                            ],
                            "final_answer": "S = 6 W m-2",
                            "assumptions": ["E and H are perpendicular."],
                            "unit_check": "V/m times A/m = W m-2.",
                            "interpretation": "The result is the electromagnetic power flow per unit area.",
                            "verification": "Checked against supplied formula path.",
                        },
                        {
                            "render_mode": "worked_example",
                            "heading": "Second worked calculation example",
                            "question": "Given a second calculation, show that numbering restarts.",
                            "steps": [
                                "Second example first step.",
                                "Second example second step.",
                            ],
                            "final_answer": "Numbering restarts at 1.",
                        },
                        {
                            "render_mode": "image_plus_kp_list",
                            "heading": "Source visual",
                            "asset_path": str(image_path),
                            "caption": "Figure 1. Academic source visual.",
                            "key_points": ["The visual is tied to the knowledge unit."],
                        },
                        {
                            "render_mode": "image_plus_kp_list",
                            "heading": "Missing source visual",
                            "asset_path": str(Path(td) / "missing_visual.png"),
                            "caption": "Figure 2. Missing source visual.",
                            "key_points": ["The explanation remains without embedding a missing asset."],
                        },
                        {
                            "render_mode": "compact_table",
                            "heading": "Comparison",
                            "table": {
                                "headers": ["Quantity", "Meaning"],
                                "rows": [["ρ", "charge density"]],
                            },
                        },
                        {
                            "render_mode": "paragraph",
                            "heading": "Add-on field filter",
                            "content": {"label": "Conceptual point", "text": "This renders.", "exam_use": "This does not render."},
                        },
                        {
                            "render_mode": "mechanism_chain",
                            "heading": "Carrier creation",
                            "steps": [
                                {"label": "Substitute impurity", "text": "A higher-valence atom replaces a lattice atom."},
                                {"label": "Create mobile carrier", "text": "Thermal excitation promotes the weakly bound carrier."},
                            ],
                        },
                    ],
                }
            ],
        }
        out = generate(plan, td)
        assert out.name == "custom_notes.docx"
        with zipfile.ZipFile(out) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            rels = zf.read("word/_rels/document.xml.rels").decode("utf-8", errors="ignore")
            assert "word/document.xml" in zf.namelist()
            assert "word/media/image1.png" in zf.namelist()
            assert 'Target="media/image1.png"' in rels
            assert "Figure 1. Academic source visual." in raw
            assert "Question: Given E = 2 V/m and H = 3 A/m, calculate the Poynting magnitude." in raw
            assert "Step-by-step solution:" in raw
            assert "1. Write the magnitude relation S = EH." in raw
            assert "1. Second example first step." in raw
            assert "3. Second example first step." not in raw
            assert "S = 2*3 = 6 W m⁻²" in raw
            assert "Final answer: S = 6 W m⁻²" in raw
            assert "Unit check: V/m times A/m = W m⁻²." in raw
            assert "w:drawing" in raw
            assert "Figure 2. Missing source visual." not in raw
            assert "w:numPr" not in raw
            assert 'w:shd w:fill="F6F7F8"' in raw
            assert 'w:shd w:fill="E9EEF3"' in raw
            assert "∂ρ/∂t + ∇ · J = 0" in raw
            assert "partial" not in raw
            assert "This should not render" not in raw
            assert "This does not render" not in raw
            assert "Exam use:" not in raw
            assert "Coverage Calibration" not in raw
            assert "{'label'" not in raw
            assert "Substitute impurity - A higher-valence atom replaces a lattice atom." in raw
        generated = generate({"title": "Charge Conservation Notes", "sections": [{"heading": "Meaning", "blocks": ["Charge is locally conserved."]}]}, td)
        assert generated.name == "Charge_Conservation_Notes.docx"
        try:
            generate({"title": "Bad Notes", "sections": [{"heading": "18. Exam Practice", "blocks": ["MCQ trap."]}]}, td)
        except ValueError as exc:
            assert "internal_public_heading:exam practice" in str(exc)
        else:
            raise AssertionError("Exam Type Related add-on heading rendered inside Notes")
        addon = generate(
            {
                "title": "Exam Type Related Add-on",
                "document_kind": "exam_type_related_addon",
                "sections": [
                    {
                        "heading": "Long Answer",
                        "blocks": [
                            {
                                "question": "Explain the mechanism of charge conservation.",
                                "example_answer": "Charge conservation means local accumulation is balanced by current flow.",
                                "analysis_prediction": {"question_demand": "explain", "expected_answer_focus": "mechanism"},
                            }
                        ],
                    }
                ],
            },
            td,
        )
        with zipfile.ZipFile(addon) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            assert "Example Answer: Charge conservation means local accumulation is balanced by current flow." in raw
            assert "Analysis Prediction:" in raw
        result_only = generate(
            {
                "title": "MCQ High-Frequency Knowledge Points",
                "document_kind": "mcq_exam_type_related_addon",
                "result_only": True,
                "sections": [
                    {
                        "heading": "Lecture 2: Membrane physiology",
                        "blocks": [
                            {
                                "render_mode": "exam_knowledge_point",
                                "title": "1. Resting membrane potential and relative permeability",
                                "content": "Resting membrane potential is determined by relative ion permeability, so high potassium permeability pulls the value closer to E_K.",
                                "exam_scope": "Exam scope: relative permeability, potassium, resting membrane potential.",
                                "source_name": "Past Paper 2024",
                                "locator": "page 4",
                                "score": 10,
                                "frequency": 3,
                                "verification": {"status": "internal"},
                                "debug": "internal matching data",
                            }
                        ],
                    }
                ],
                "_internal_recurrence": [{"source": "Past Paper 2024", "calculation": "hidden"}],
            },
            td,
        )
        with zipfile.ZipFile(result_only) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            assert "Resting membrane potential is determined by relative ion permeability" in raw
            assert "Exam scope: relative permeability, potassium, resting membrane potential." in raw
            assert "Past Paper 2024" not in raw
            assert "Source Name:" not in raw
            assert "Locator:" not in raw
            assert "Score:" not in raw
            assert "Frequency:" not in raw
            assert "Verification:" not in raw
            assert "debug" not in raw.lower()
            assert "calculation" not in raw.lower()
        practical = generate(
            {
                "title": "Practical Worked Solutions",
                "document_kind": "practical_worked_solutions_docx",
                "sections": [
                    {
                        "heading": "Practical calculations",
                        "blocks": [
                            {
                                "render_mode": "worked_example",
                                "question": "Calculate the gradient from the data table.",
                                "steps": ["Use gradient = delta y / delta x.", "Substitute the table values."],
                                "final_answer": "gradient = delta y / delta x",
                                "verification": {"status": "solution evidence matched"},
                            }
                        ],
                    }
                ],
            },
            td,
        )
        with zipfile.ZipFile(practical) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
            assert "Practical Worked Solutions" in raw
            assert "Verification: Status: solution evidence matched" in raw


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
