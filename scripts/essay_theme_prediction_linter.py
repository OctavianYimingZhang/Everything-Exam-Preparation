#!/usr/bin/env python3
"""Check essay/problem-essay prediction language stays theme-level."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_PATHS = [Path("SKILL.md"), Path("README.md"), Path("references")]

def exact_phrase(*parts: str, ignore_case: bool = False) -> re.Pattern[str]:
    flags = re.I if ignore_case else 0
    return re.compile(r"\b" + re.escape("".join(parts)) + r"\b", flags)


BANNED_PATTERNS = [
    ("predicted_practice_essay_questions", exact_phrase("predicted practice essay ", "questions", ignore_case=True)),
    ("practice_essay_questions_default", exact_phrase("practice essay ", "questions", ignore_case=True)),
    ("predicted_essay_question_header", exact_phrase("Predicted Essay ", "Question")),
    ("old_essay_predicted_questions_sheet", exact_phrase("Essay_Predicted_", "Questions")),
    ("old_essay_theme_field_name", exact_phrase("essay_question_", "candidates")),
    ("predicted_questions_alone", exact_phrase("predicted questions ", "alone", ignore_case=True)),
    ("all_predicted_questions_label", exact_phrase("Label all predicted ", "questions")),
]

REQUIRED_PATTERNS = [
    ("skill_predicted_essay_theme", Path("SKILL.md"), re.compile(r"\bPredicted essay theme\b")),
    ("question_type_theme_schema", Path("references/exam_mode_and_addons_protocol.md"), re.compile(r"\bEssayThemePrediction\b")),
    ("scoring_theme_result", Path("references/exam_mode_and_addons_protocol.md"), re.compile(r"\bEssayProblemThemeResult\b")),
    ("excel_theme_header", Path("references/runtime_qa_release_protocol.md"), re.compile(r"\bPredicted Essay Theme / Scope / Practice Angle\b")),
]


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file() and item.suffix.lower() in {".md", ".txt"})
    return sorted(files, key=lambda item: str(item).lower())


def scan_banned(paths: list[Path]) -> list[dict[str, str]]:
    hits = []
    for path in iter_files(paths):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in BANNED_PATTERNS:
            match = pattern.search(text)
            if match:
                hits.append({"file": str(path), "pattern": name, "match": match.group(0)})
    return hits


def scan_required(root: Path) -> list[dict[str, str]]:
    missing = []
    for name, rel_path, pattern in REQUIRED_PATTERNS:
        path = root / rel_path
        text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        if not pattern.search(text):
            missing.append({"file": str(rel_path), "pattern": name})
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint essay/problem-essay prediction language.")
    parser.add_argument("paths", nargs="*", type=Path, default=DEFAULT_PATHS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    banned_hits = scan_banned(args.paths)
    missing_required = scan_required(Path("."))
    result = {
        "pass": not banned_hits and not missing_required,
        "banned_hits": banned_hits,
        "missing_required": missing_required,
    }
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
