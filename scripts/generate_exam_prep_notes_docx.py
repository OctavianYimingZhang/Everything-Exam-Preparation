#!/usr/bin/env python3
"""Generate default lecture-first public exam-prep notes."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from public_lecture_notes_renderer import load_plan, write_public_lecture_notes_docx


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--deliverable-only", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir
    qa_dir = args.qa_dir or (output_dir if not args.deliverable_only else output_dir.parent / "exam_prep_notes_internal_qa")
    if args.clean:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        if qa_dir.exists() and qa_dir != output_dir:
            shutil.rmtree(qa_dir)

    result = write_public_lecture_notes_docx(
        load_plan(args.plan),
        "exam_prep_notes_docx",
        output_dir,
        qa_dir,
        args.strict,
        "exam_prep_notes_manifest.json",
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
