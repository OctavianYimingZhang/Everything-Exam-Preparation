from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any

MODE_PATTERNS = {
    "MCQ": [r"\b[A-D][).]", r"single best", r"multiple choice", r"\bmcq\b"],
    "Short Answer": [r"\b[1-5]\s*marks?\b", r"short answer", r"define|state|list"],
    "Long Answer": [r"\b(8|10|12|15|20)\s*marks?\b", r"compare|evaluate|explain|discuss"],
    "Practical/Data/Problem": [r"graph|table|calculate|method|control|limitation|data|problem"],
    "Essay": [r"essay|critically|to what extent|argument|thesis"],
}
RISKY_PREDICTION = [r"will ask", r"guaranteed", r"exact question", r"definitely appear", r"certain to"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_questions(text: str) -> list[dict[str, Any]]:
    chunks = re.split(r"\n(?=\s*(?:Q\d+|\d+[).]))", text)
    questions = []
    for i, chunk in enumerate(chunks, 1):
        cleaned = re.sub(r"\s+", " ", chunk).strip()
        if len(cleaned) < 12:
            continue
        questions.append({"id": f"Q{i}", "text": cleaned[:1000], "mode_hint": diagnose_text(cleaned)["detected_mode"]})
    return questions


def diagnose_text(text: str) -> dict[str, Any]:
    scores = {}
    for mode, patterns in MODE_PATTERNS.items():
        scores[mode] = sum(len(re.findall(p, text, flags=re.I)) for p in patterns)
    best_mode = max(scores, key=scores.get) if scores else "Unknown"
    if scores.get(best_mode, 0) == 0:
        best_mode = "Unknown"
    nonzero = [m for m, s in scores.items() if s > 0]
    detected = "Mixed" if len(nonzero) >= 3 and best_mode != "Unknown" else best_mode
    confidence = 0.0 if best_mode == "Unknown" else min(0.95, 0.45 + scores[best_mode] * 0.1)
    return {"detected_mode": detected, "confidence": round(confidence, 2), "scores": scores, "evidence_basis": nonzero}


def diagnose_scan(scan: dict[str, Any]) -> dict[str, Any]:
    text = "\n".join(str(f.get("text", "")) for f in scan.get("fragments", []))
    return diagnose_text(text)


def lint_prediction_text(text: str) -> dict[str, Any]:
    failures = [p for p in RISKY_PREDICTION if re.search(p, text, flags=re.I)]
    return {"status": "fail" if failures else "pass", "failures": failures}


def self_test() -> int:
    text = "Q1. Which option is correct? A. alpha B. beta\nQ2. Calculate the value from the table."
    qs = extract_questions(text)
    assert qs and diagnose_text(text)["detected_mode"] in {"Mixed", "MCQ", "Practical/Data/Problem"}
    assert lint_prediction_text("This theme may be useful.")["status"] == "pass"
    assert lint_prediction_text("The exam will ask this exact question.")["status"] == "fail"
    print("exam_mode_tools self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?")
    parser.add_argument("--input")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.command == "extract-questions":
        if not args.input:
            parser.error("--input is required")
        out = {"questions": extract_questions(read_text(Path(args.input)))}
    elif args.command == "diagnose":
        if args.source_scan:
            out = diagnose_scan(json.loads(Path(args.source_scan).read_text(encoding="utf-8")))
        elif args.input:
            out = diagnose_text(read_text(Path(args.input)))
        else:
            parser.error("--source-scan or --input is required")
    elif args.command == "lint-prediction":
        if not args.input:
            parser.error("--input is required")
        out = lint_prediction_text(read_text(Path(args.input)))
    else:
        parser.error("command must be extract-questions, diagnose, or lint-prediction")
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
