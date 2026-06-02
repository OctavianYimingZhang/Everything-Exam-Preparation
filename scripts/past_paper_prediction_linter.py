#!/usr/bin/env python3
"""Validate past-paper prediction records and hard-failure language."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


PRECISE_PROBABILITY = re.compile(r"\b\d{2}\.\d+%\b")
EXACT_CLAIM = re.compile(r"\b(this exact question will appear|guaranteed|certainly appear|will definitely appear)\b", re.I)
ALL_POSSIBLE = re.compile(r"\ball possible questions\b", re.I)
OFFICIAL_ANSWER = re.compile(r"\bofficial answer\b", re.I)

REQUIRED_QUESTION_FIELDS = {
    "source_file",
    "target_group_key",
    "year",
    "paper_id",
    "section",
    "question_no",
    "raw_stem",
    "marks",
    "question_type",
    "command_verbs",
    "input_format",
    "negative_marking",
    "candidate_options",
    "extracted_confidence",
    "review_flag",
}

REQUIRED_ARCHETYPE_FIELDS = {
    "archetype_id",
    "target_group_key",
    "current_regime_key",
    "question_family",
    "recurrent_operation",
    "slot_grammar",
    "mark_scheme_skeleton",
    "compatible_kp_families",
    "seen_in",
    "confidence",
    "student_output_action",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(collect_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(collect_text(item) for item in value)
    return ""


def lint_language(payload: Any) -> list[dict[str, Any]]:
    text = collect_text(payload)
    failures = []
    if EXACT_CLAIM.search(text):
        failures.append({"type": "exact_future_question_claim", "phrase": EXACT_CLAIM.search(text).group(0)})
    if PRECISE_PROBABILITY.search(text):
        failures.append({"type": "fabricated_precise_probability", "phrase": PRECISE_PROBABILITY.search(text).group(0)})
    if ALL_POSSIBLE.search(text) and "slot_grammar" not in text:
        failures.append({"type": "unbounded_all_possible_questions"})
    return failures


def lint_question_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for index, record in enumerate(records, start=1):
        missing = sorted(REQUIRED_QUESTION_FIELDS - set(record))
        if missing:
            failures.append({"type": "question_record_missing_fields", "index": index, "missing": missing})
        if record.get("question_type") == "mcq_single_best" and not record.get("candidate_options", {}).get("count"):
            failures.append({"type": "mcq_record_missing_options", "index": index})
        if OFFICIAL_ANSWER.search(collect_text(record)) and not record.get("answer_key_present"):
            failures.append({"type": "official_answer_without_answer_key", "index": index})
    return failures


def lint_archetypes(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures = []
    for index, record in enumerate(records, start=1):
        missing = sorted(REQUIRED_ARCHETYPE_FIELDS - set(record))
        if missing:
            failures.append({"type": "archetype_missing_fields", "index": index, "missing": missing})
        if not record.get("slot_grammar"):
            failures.append({"type": "archetype_missing_slot_grammar", "index": index})
        if str(record.get("confidence")) not in {"High", "Medium", "Low"}:
            failures.append({"type": "archetype_invalid_confidence", "index": index, "confidence": record.get("confidence")})
    return failures


def lint_payload(payload: dict[str, Any]) -> dict[str, Any]:
    failures = lint_language(payload)
    if isinstance(payload.get("questions"), list):
        failures.extend(lint_question_records(payload["questions"]))
    if isinstance(payload.get("archetypes"), list):
        failures.extend(lint_archetypes(payload["archetypes"]))
    if isinstance(payload.get("prediction_objects"), list):
        for index, item in enumerate(payload["prediction_objects"], start=1):
            if item.get("confidence_band") not in {"High", "Medium", "Low"}:
                failures.append({"type": "prediction_missing_confidence_band", "index": index})
            if item.get("exact_question_wording_claimed") is True:
                failures.append({"type": "prediction_claims_exact_wording", "index": index})
    return {"pass": not failures, "failures": failures}



def self_test() -> dict[str, Any]:
    valid_question = {
        "source_file": "inline_paper.txt",
        "target_group_key": "inline_self_test",
        "year": "2025",
        "paper_id": "inline_paper",
        "section": "A",
        "question_no": "1",
        "raw_stem": "Explain competitive inhibition. [5]",
        "marks": 5,
        "question_type": "short_answer_explain",
        "command_verbs": ["explain"],
        "input_format": {"text_only": True},
        "negative_marking": {"present": False},
        "candidate_options": {"count": 0, "option_texts": []},
        "extracted_confidence": "High",
        "review_flag": [],
        "answer_key_present": False,
    }
    valid_archetype = {
        "archetype_id": "ARCH001",
        "target_group_key": "inline_self_test",
        "current_regime_key": "current_regime",
        "question_family": "short_answer_explain",
        "recurrent_operation": {"command_verbs": ["explain"]},
        "slot_grammar": {"slot_types": ["knowledge_point"], "bounded": True},
        "mark_scheme_skeleton": ["claim", "mechanism"],
        "compatible_kp_families": [],
        "seen_in": [{"year": "2025", "question_no": "1"}],
        "confidence": "Low",
        "student_output_action": "build_bounded_variant_space_and_mark_schema",
    }
    good = lint_payload({"questions": [valid_question], "archetypes": [valid_archetype], "prediction_objects": [{"confidence_band": "Low", "exact_question_wording_claimed": False}]})
    bad = lint_payload({"summary": "This exact question will appear with 87.5% confidence.", "prediction_objects": [{"confidence_band": "Certain", "exact_question_wording_claimed": True}]})
    failures = []
    if not good.get("pass"):
        failures.append({"type": "valid_payload_rejected", "good": good})
    if bad.get("pass"):
        failures.append({"type": "bad_payload_accepted", "bad": bad})
    return {"pass": not failures, "good": good, "bad": bad, "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate past-paper prediction outputs.")
    parser.add_argument("--input", action="append", type=Path, default=[])
    parser.add_argument("--suite", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1

    reports = []
    overall_pass = True
    for path in args.input + args.suite:
        try:
            payload = load_json(path)
            report = lint_payload(payload)
        except Exception as exc:
            report = {"pass": False, "failures": [{"type": "read_error", "error": str(exc)}]}
        report.update({"path": str(path)})
        reports.append(report)
        overall_pass = overall_pass and bool(report["pass"])

    if not reports:
        reports.append({"path": None, "pass": False, "failures": [{"type": "no_inputs"}]})
        overall_pass = False

    result = {"pass": overall_pass, "reports": reports}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
