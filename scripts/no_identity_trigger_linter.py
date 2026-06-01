#!/usr/bin/env python3
"""Detect legacy target-identity strings in production Skill files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_PATHS = ["SKILL.md", "README.md", "agents", "references", "scripts", "schemas"]
IGNORE_DIRS = {".git", "__pycache__", ".venv", "benchmarks", "tests"}
LEGACY_WORD = "un" + "it"

OLD_HELPER = LEGACY_WORD + "_grouper"
LEGACY_LABEL_PATTERN = re.compile(rf"\b{LEGACY_WORD}\s*(?:#?\d+|[=-]\s*['\"]?[\w-]+)", re.I)
COURSE_PREFIX = "B" + "IOL"
PRIVATE_SCHOOL = "School of " + "Biological"
PRIVATE_INSTITUTION = "University of " + "Manchester"
LEGACY_TOPICS = [
    "Mot" + "or " + "Systems",
    "Developmental " + "Bio" + "logy",
    "Genome " + "Bio" + "logy",
    "Proteins and " + "Enz" + "ymes",
]

BASE_PATTERNS = [
    ("course_code_branch", re.compile(rf"\b{COURSE_PREFIX}\d{{5}}[A-Z]?\b", re.I)),
    ("private_course_name", re.compile(re.escape(PRIVATE_SCHOOL) + "|" + re.escape(PRIVATE_INSTITUTION), re.I)),
    ("legacy_topic_identity", re.compile(r"\b(" + "|".join(re.escape(topic) for topic in LEGACY_TOPICS) + r")\b", re.I)),
    ("old_helper_name", re.compile(rf"\b{OLD_HELPER}\b", re.I)),
]


def iter_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            files.append(path)
        else:
            for item in path.rglob("*"):
                if item.is_file() and not any(part in IGNORE_DIRS for part in item.parts):
                    files.append(item)
    return sorted(files, key=lambda item: str(item).lower())


def scan_file(path: Path, patterns: list[tuple[str, re.Pattern[str]]], scan_path: bool) -> list[dict]:
    hits = []
    haystacks = []
    if scan_path:
        haystacks.append(("path", str(path)))
    try:
        haystacks.append(("text", path.read_text(encoding="utf-8", errors="ignore")))
    except Exception:
        return hits
    for location, text in haystacks:
        for name, pattern in patterns:
            for match in pattern.finditer(text):
                hits.append({"file": str(path), "location": location, "pattern": name, "match": match.group(0)})
                break
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan production files for identity-trigger strings.")
    parser.add_argument("paths", nargs="*", type=Path, default=[Path(path) for path in DEFAULT_PATHS])
    parser.add_argument("--forbid-legacy-label", action="store_true", help="Also forbid the legacy source-set label word as a standalone word.")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-path-scan", action="store_true")
    args = parser.parse_args()

    patterns = list(BASE_PATTERNS)
    if args.forbid_legacy_label:
        patterns.append(("legacy_source_set_label", LEGACY_LABEL_PATTERN))

    hits = []
    for path in iter_files(args.paths):
        hits.extend(scan_file(path, patterns, scan_path=not args.no_path_scan))

    result = {"pass": not hits, "hits": hits}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
