#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Any

MODE_PATTERNS = {
    "MCQ": [r"\b[A-D][).]", r"multiple choice", r"single best", r"\bmcq\b", r"which of the following", r"true/false"],
    "Short Answer": [r"short answer", r"\b[1-6]\s*marks?\b", r"\bdefine\b", r"\bstate\b", r"\blist\b", r"\boutline\b"],
    "Long Answer": [r"\b(7|8|9|10|12|15|20|25|30)\s*marks?\b", r"\bexplain\b", r"\bcompare\b", r"\bevaluate\b", r"\bdiscuss\b", r"\bjustify\b"],
    "Essay": [r"essay", r"critically", r"to what extent", r"argument", r"thesis", r"in-campus"],
}

COMMAND_VERBS = ["define", "state", "list", "outline", "describe", "explain", "compare", "evaluate", "discuss", "calculate", "interpret", "justify", "criticise", "critically"]
STOPWORDS = {"which", "there", "their", "about", "using", "answer", "question", "marks", "following", "explain", "describe", "compare", "evaluate", "discuss"}


def extract_questions(text: str) -> list[str]:
    questions: list[str] = []
    for line in (text or "").splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if not clean:
            continue
        if "?" in clean or re.match(r"^(Q\d+|\d+[).]|[a-z][)])\s+", clean, re.I):
            questions.append(clean[:1000])
    return questions


def score_modes(text: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    for mode, patterns in MODE_PATTERNS.items():
        scores[mode] = sum(len(re.findall(pattern, text or "", flags=re.I)) for pattern in patterns)
    return scores


def detected_mode(scores: dict[str, int]) -> str:
    positive = [(mode, score) for mode, score in scores.items() if score > 0]
    if not positive:
        return "Unknown"
    positive.sort(key=lambda item: item[1], reverse=True)
    if len(positive) > 1 and positive[1][1] >= max(1, positive[0][1] // 2):
        return "Mixed"
    return positive[0][0]


def command_counts(text: str) -> dict[str, int]:
    lower = (text or "").lower()
    return {verb: len(re.findall(r"\b" + re.escape(verb) + r"\b", lower)) for verb in COMMAND_VERBS if re.search(r"\b" + re.escape(verb) + r"\b", lower)}


def mark_values(text: str) -> list[str]:
    return sorted(set(re.findall(r"\b\d+\s*marks?\b", text or "", flags=re.I)), key=lambda s: int(re.search(r"\d+", s).group()))


def frequent_terms(text: str, limit: int = 20) -> list[dict[str, Any]]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or "")
    counts = collections.Counter(w.lower() for w in words if w.lower() not in STOPWORDS)
    return [{"term": term, "count": count} for term, count in counts.most_common(limit)]


def analyze_text(text: str) -> dict[str, Any]:
    scores = score_modes(text)
    questions = extract_questions(text)
    return {
        "schema_version": 2,
        "detected_mode": detected_mode(scores),
        "mode_scores": scores,
        "question_count": len(questions),
        "questions": questions,
        "examiner_habits": {
            "command_verbs": command_counts(text),
            "mark_values": mark_values(text),
            "frequent_terms": frequent_terms(text),
            "question_forms": [q[:180] for q in questions[:20]],
        },
    }


def text_from_scan(scan: dict[str, Any]) -> str:
    wanted = {"practice_material", "marking_material"}
    parts = [frag.get("text", "") for frag in scan.get("fragments", []) if frag.get("category") in wanted]
    if not parts:
        parts = [frag.get("text", "") for frag in scan.get("fragments", [])]
    return "\n".join(str(p) for p in parts)


def load_input(path: str | None, source_scan: str | None) -> str:
    if source_scan:
        return text_from_scan(json.loads(Path(source_scan).read_text(encoding="utf-8")))
    if path:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    return ""


def self_test() -> None:
    text = "1. Which of the following is correct? A) x B) y\n2. Explain the mechanism. 10 marks"
    result = analyze_text(text)
    assert result["detected_mode"] in {"Mixed", "MCQ", "Long Answer"}
    assert result["question_count"] == 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="diagnose")
    parser.add_argument("--input")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = load_input(args.input, args.source_scan)
    if args.command == "extract-questions":
        result: Any = {"questions": extract_questions(text)}
    else:
        result = analyze_text(text)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
