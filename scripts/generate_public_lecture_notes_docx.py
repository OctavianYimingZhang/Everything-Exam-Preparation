#!/usr/bin/env python3
"""Generate the public lecture-notes DOCX for exam-prep notes or source-order walkthrough routes."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from public_lecture_notes_renderer import load_plan, sample_plan, write_public_lecture_notes_docx

ROUTE_DEFAULTS = {
    "exam_prep_notes_docx": ("exam_prep_notes_internal_qa", "exam_prep_notes_manifest.json"),
    "knowledge_walkthrough_docx": ("knowledge_walkthrough_internal_qa", "knowledge_walkthrough_manifest.json"),
}



def self_test() -> dict[str, object]:
    import tempfile
    with tempfile.TemporaryDirectory(prefix="public_lecture_notes_generator_selftest_") as tmp:
        root = Path(tmp)
        result = write_public_lecture_notes_docx(sample_plan("exam_prep_notes_docx"), "exam_prep_notes_docx", root / "out", root / "qa", True, "manifest.json")
        docx_exists = (root / "out" / "Lecture_Knowledge_Walkthrough.docx").exists()
    failures = []
    if result.get("status") != "pass":
        failures.append({"type": "render_status_not_pass", "result": result})
    if not docx_exists:
        failures.append({"type": "docx_missing"})
    return {"pass": not failures, "result": result, "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--route", choices=sorted(ROUTE_DEFAULTS), default="exam_prep_notes_docx")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--qa-dir", type=Path)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--deliverable-only", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    if not args.plan or not args.output_dir:
        print(json.dumps({"status": "fail", "qa_flags": ["missing_plan_output_dir_or_self_test"]}, indent=2))
        return 1

    qa_name, manifest_name = ROUTE_DEFAULTS[args.route]
    output_dir = args.output_dir
    qa_dir = args.qa_dir or (output_dir if not args.deliverable_only else output_dir.parent / qa_name)
    if args.clean:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        if qa_dir.exists() and qa_dir != output_dir:
            shutil.rmtree(qa_dir)
    result = write_public_lecture_notes_docx(load_plan(args.plan), args.route, output_dir, qa_dir, args.strict, manifest_name)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") in {"pass", "warn"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
