#!/usr/bin/env python3
"""Validate the shared PublicLectureNotesPlan used by ordinary notes routes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from public_lecture_notes_renderer import load_plan, validate_public_lecture_notes_plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--route", choices=["exam_prep_notes_docx", "knowledge_walkthrough_docx"], default="exam_prep_notes_docx")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    failures = validate_public_lecture_notes_plan(load_plan(args.plan), args.route)
    result = {"pass": not failures, "failures": failures}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
