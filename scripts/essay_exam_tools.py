#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any

STOPWORDS = {"lecture", "module", "question", "answer", "using", "explain", "describe", "compare", "evaluate", "discuss", "material", "course", "student"}


def frequent_topics(text: str, limit: int = 6) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or "")
    counts = collections.Counter(w.lower() for w in words if w.lower() not in STOPWORDS)
    return [term for term, _ in counts.most_common(limit)] or ["core module theme"]


def scan_text(source_scan: dict[str, Any] | None) -> str:
    if not source_scan:
        return ""
    return "\n".join(str(frag.get("text", "")) for frag in source_scan.get("fragments", []))


def build_essay_pack(question: str | None = None, readings: str | None = None, source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    text = "\n".join(part for part in [readings or "", scan_text(source_scan)] if part)
    topics = frequent_topics(text)
    essay_questions = []
    for topic in topics[:4]:
        essay_questions.append({
            "module_topic": topic,
            "question": question or f"Discuss how {topic} can be used to explain a major issue in this module.",
            "coverage_use": "Broad question for practising argument structure across the module.",
        })
    paragraphs = []
    for topic in topics[:4]:
        paragraphs.append({
            "topic": topic,
            "paragraph": f"A strong exam paragraph on {topic} should begin with a direct claim, explain the relevant course mechanism or argument, then link the explanation back to the wording of the question.",
        })
    return {
        "schema_version": 2,
        "essay_questions": essay_questions,
        "thesis_options": [f"The strongest answer should treat {topics[0]} as a central organising idea."],
        "exam_ready_paragraphs": paragraphs,
        "example_essay_plan": {
            "introduction": "Define the argument and answer the question directly.",
            "body": [p["topic"] for p in paragraphs],
            "conclusion": "Return to the question and state the final judgement.",
        },
    }


def lint_language(text: str) -> dict[str, Any]:
    suggestions = []
    if len(text.split()) < 120:
        suggestions.append("essay_answer_may_be_too_short")
    if text.count("\n-") > 6:
        suggestions.append("essay_answer_reads_like_list")
    if not re.search(r"\btherefore\b|\bhowever\b|\bconsequently\b|\bthis shows\b", text, re.I):
        suggestions.append("add_more_argument_links")
    return {"status": "ok" if not suggestions else "suggestions", "suggestions": suggestions}


def load_scan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    pack = build_essay_pack(readings="enzyme enzyme potency efficacy argument")
    assert pack["essay_questions"]
    assert lint_language("short")["suggestions"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="generate-plan")
    parser.add_argument("--plan")
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--question")
    parser.add_argument("--readings")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.command == "lint-language":
        text = Path(args.input).read_text(encoding="utf-8", errors="ignore") if args.input else ""
        result = lint_language(text)
    else:
        readings = args.readings or (Path(args.input).read_text(encoding="utf-8", errors="ignore") if args.input else "")
        result = build_essay_pack(args.question, readings, load_scan(args.source_scan))
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    target = args.output or args.out
    if target:
        Path(target).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
