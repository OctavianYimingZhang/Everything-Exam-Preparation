from __future__ import annotations

import argparse
import html
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from generate_exam_prep_notes_docx import write_minimal_docx

ESSAY_NAME = "Example_Essay.docx"
RISKY_CITATION = re.compile(r"\[[A-Z][A-Za-z]+,\s*\d{4}\]|\([A-Z][A-Za-z]+,\s*\d{4}\)")


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as zf:
            raw = zf.read("word/document.xml").decode("utf-8", errors="ignore")
        return html.unescape("\n".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", raw)))
    return path.read_text(encoding="utf-8", errors="ignore")


def generate(plan: dict[str, Any], out_dir: Path) -> Path:
    blocks = [(plan.get("question") or "Example Essay", "Title", "center")]
    thesis = plan.get("thesis") or "A defensible answer needs a clear thesis, ordered reasoning, supported evidence, and counterargument handling."
    blocks.append((f"Thesis: {thesis}", "Normal", "both"))
    for item in plan.get("argument_blocks", []):
        if isinstance(item, dict):
            blocks.append((item.get("heading", "Argument block"), "Heading1", "left"))
            blocks.append((item.get("content", ""), "Normal", "both"))
        else:
            blocks.append((str(item), "Normal", "both"))
    if plan.get("counterargument"):
        blocks.append(("Counterargument", "Heading1", "left"))
        blocks.append((plan["counterargument"], "Normal", "both"))
    path = out_dir / ESSAY_NAME
    write_minimal_docx(path, blocks)
    return path


def lint_language(text: str) -> dict[str, Any]:
    failures = []
    if len(re.findall(r"\b(firstly|secondly|thirdly)\b", text, flags=re.I)) > 8:
        failures.append("mechanical_listing")
    if "this essay will" in text.lower():
        failures.append("filler_intro")
    return {"status": "fail" if failures else "pass", "failures": failures}


def audit_source(plan: dict[str, Any], output_text: str) -> dict[str, Any]:
    allowed = set(plan.get("resolved_citations", []))
    found = set(RISKY_CITATION.findall(output_text))
    unsupported = sorted(found - allowed)
    return {"status": "fail" if unsupported else "pass", "unsupported_citations": unsupported}


def resolve_citations(source_scan: dict[str, Any]) -> dict[str, Any]:
    text = "\n".join(str(f.get("text", "")) for f in source_scan.get("fragments", []))
    citations = sorted(set(RISKY_CITATION.findall(text)))
    return {"resolved_citations": citations}


def match_extra_reading(question: str, readings: list[dict[str, Any]]) -> dict[str, Any]:
    q_terms = set(re.findall(r"[A-Za-z]{5,}", question.lower()))
    scored = []
    for item in readings:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        score = len(q_terms.intersection(re.findall(r"[A-Za-z]{5,}", text)))
        if score:
            scored.append({"reading": item, "score": score})
    return {"matches": sorted(scored, key=lambda x: x["score"], reverse=True)}


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        path = generate({"question": "Evaluate the method.", "thesis": "The method is useful when controls are explicit.", "argument_blocks": [{"heading": "Evidence", "content": "Controls define interpretation."}]}, Path(td))
        assert path.exists()
        assert lint_language(read_text(path))["status"] == "pass"
        assert audit_source({"resolved_citations": []}, "Unsupported (Smith, 2020)")["status"] == "fail"
    print("essay_exam_tools self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    parser.add_argument("--plan")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--source-scan")
    parser.add_argument("--out", default=".")
    parser.add_argument("--question")
    parser.add_argument("--readings")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.command == "generate":
        if not args.plan:
            parser.error("--plan is required")
        path = generate(json.loads(Path(args.plan).read_text(encoding="utf-8")), Path(args.out))
        print(path)
        return 0
    if args.command == "lint-language":
        if not args.input:
            parser.error("--input is required")
        result = lint_language(read_text(Path(args.input)))
    elif args.command == "audit-source":
        if not args.plan or not args.output:
            parser.error("--plan and --output are required")
        result = audit_source(json.loads(Path(args.plan).read_text(encoding="utf-8")), read_text(Path(args.output)))
    elif args.command == "resolve-citations":
        if not args.source_scan:
            parser.error("--source-scan is required")
        result = resolve_citations(json.loads(Path(args.source_scan).read_text(encoding="utf-8")))
    elif args.command == "match-extra-reading":
        if not args.question or not args.readings:
            parser.error("--question and --readings are required")
        result = match_extra_reading(args.question, json.loads(Path(args.readings).read_text(encoding="utf-8")))
    else:
        parser.error("command must be generate, lint-language, audit-source, resolve-citations, or match-extra-reading")
    print(json.dumps(result, indent=2))
    return 1 if result.get("status") == "fail" else 0

if __name__ == "__main__":
    raise SystemExit(main())
