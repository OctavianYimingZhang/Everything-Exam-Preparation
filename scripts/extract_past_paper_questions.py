#!/usr/bin/env python3
"""Extract conservative question-level records from readable past-paper text."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None


QUESTION_START = re.compile(r"^\s*(?:Question|Q)\s*(\d+)(?:\s*[\.:)-]\s*|\s+)(.*)$", re.I)
SECTION_RE = re.compile(r"^\s*Section\s+([A-Z])\b", re.I)
MARKS_RE = re.compile(r"\[(\d+)\]|\((\d+)\s*marks?\)", re.I)
YEAR_RE = re.compile(r"(?<!\d)(20\d{2}|19\d{2})(?!\d)")
OPTION_RE = re.compile(r"^\s*([A-D])[\).:]\s+(.+)$", re.I)
COMMAND_VERBS = [
    "define",
    "list",
    "name",
    "state",
    "identify",
    "describe",
    "explain",
    "compare",
    "contrast",
    "calculate",
    "draw",
    "label",
    "discuss",
    "evaluate",
    "design",
    "interpret",
    "justify",
    "predict",
]


def read_text(path: Path) -> tuple[str, list[str]]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        return path.read_text(encoding="utf-8", errors="replace"), []
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(data, ensure_ascii=False, indent=2), []
    if suffix == ".pdf":
        if fitz is not None:
            try:
                doc = fitz.open(path)
                return "\n".join(page.get_text("text") for page in doc), []
            except Exception:
                pass
        if PdfReader is not None:
            try:
                reader = PdfReader(str(path))
                return "\n".join(page.extract_text() or "" for page in reader.pages), []
            except Exception as exc:
                return "", [f"pdf_read_error:{type(exc).__name__}"]
    return "", [f"unsupported_extension:{suffix or '[none]'}"]


def iter_files(inputs: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in inputs:
        if path.is_dir():
            files.extend(item for item in path.rglob("*") if item.is_file())
        else:
            files.append(path)
    return sorted(files, key=lambda item: str(item).lower())


def year_from_path(path: Path, text: str) -> str | None:
    for haystack in [path.name, text[:1000]]:
        match = YEAR_RE.search(haystack)
        if match:
            return match.group(1)
    return None


def negative_marking(text: str) -> dict[str, Any]:
    lower = text.lower()
    present = "negative marking" in lower or "deduct" in lower or "penalty" in lower
    correct_value = None
    wrong_value = None
    unanswered_value = 0
    if re.search(r"\+?1\b", text) and re.search(r"-\s*1\s*/\s*3|-1/3", text):
        correct_value = 1
        wrong_value = -1 / 3
    elif re.search(r"\+1\s*/\s*3|\+1/3|correct[^.\n]{0,40}1\s*/\s*3", text, re.I) and re.search(r"-\s*1\b", text):
        correct_value = 1 / 3
        wrong_value = -1
    return {
        "present": present,
        "correct_value": correct_value,
        "wrong_value": wrong_value,
        "unanswered_value": unanswered_value,
    }


def split_questions(text: str) -> list[dict[str, Any]]:
    records = []
    current: dict[str, Any] | None = None
    section = None
    for line in text.splitlines():
        section_match = SECTION_RE.match(line)
        if section_match:
            section = section_match.group(1).upper()
            continue
        question_match = QUESTION_START.match(line)
        if question_match:
            if current:
                records.append(current)
            current = {
                "question_no": question_match.group(1),
                "section": section,
                "lines": [question_match.group(2).strip()] if question_match.group(2).strip() else [],
            }
            continue
        if current is not None:
            current["lines"].append(line.rstrip())
    if current:
        records.append(current)
    return records


def command_verbs(stem: str) -> list[str]:
    hits = []
    lower = stem.lower()
    for verb in COMMAND_VERBS:
        if re.search(rf"\b{re.escape(verb)}\b", lower):
            hits.append(verb)
    return hits


def option_texts(stem: str) -> list[str]:
    options = []
    for line in stem.splitlines():
        match = OPTION_RE.match(line)
        if match:
            options.append(f"{match.group(1).upper()}. {match.group(2).strip()}")
    return options


def input_format(stem: str) -> dict[str, bool]:
    lower = stem.lower()
    return {
        "text_only": not any(token in lower for token in ["graph", "table", "figure", "calculate", "diagram", "structure", "scenario", "case"]),
        "graph": "graph" in lower,
        "table": "table" in lower,
        "figure": "figure" in lower or "diagram" in lower,
        "structure": "structure" in lower,
        "calculation": "calculate" in lower or "calculation" in lower,
        "scenario": "scenario" in lower or "case" in lower or "patient" in lower,
    }


def infer_question_type(stem: str, options: list[str], marks: int | None) -> str:
    lower = stem.lower()
    verbs = command_verbs(stem)
    formats = input_format(stem)
    if options or "multiple choice" in lower or "choose one" in lower:
        return "mcq_single_best"
    if "true or false" in lower or "mark each statement" in lower:
        return "mcq_multiple_true_false"
    if "____" in stem or "fill" in lower or "missing word" in lower:
        return "fill_blank"
    if formats["graph"] or formats["table"] or formats["calculation"]:
        return "data_problem"
    if "project" in lower or ("design" in verbs and ("experiment" in lower or "method" in lower or "assay" in lower)):
        return "long_answer_project"
    if "essay" in lower or "discuss" in verbs or "evaluate" in verbs:
        return "essay_theory"
    if "compare" in verbs or "contrast" in verbs:
        return "short_answer_compare"
    if "explain" in verbs or "describe" in verbs:
        return "short_answer_explain" if not marks or marks < 15 else "long_answer_project"
    if "define" in verbs:
        return "short_answer_define"
    if "list" in verbs or "name" in verbs or "state" in verbs:
        return "short_answer_list"
    return "mixed_or_uncertain"


def marks_from_stem(stem: str) -> int | None:
    matches = MARKS_RE.findall(stem)
    if not matches:
        return None
    value = next((left or right for left, right in matches if left or right), None)
    return int(value) if value else None


def confidence_for(raw_stem: str, question_type: str, marks: int | None) -> str:
    if question_type == "mixed_or_uncertain":
        return "Low"
    if not raw_stem.strip() or marks is None:
        return "Medium"
    return "High"


def question_record(path: Path, target_group_key: str, paper_id: str, year: str | None, section_default: str | None, raw: dict[str, Any], file_negative: dict[str, Any]) -> dict[str, Any]:
    stem = "\n".join(line for line in raw["lines"] if line.strip()).strip()
    options = option_texts(stem)
    marks = marks_from_stem(stem)
    qtype = infer_question_type(stem, options, marks)
    section = raw.get("section") or section_default or "unknown"
    confidence = confidence_for(stem, qtype, marks)
    review_flags = []
    if marks is None:
        review_flags.append("marks_not_detected")
    if qtype == "mixed_or_uncertain":
        review_flags.append("question_type_uncertain")
    if not stem:
        review_flags.append("empty_stem")
    return {
        "source_file": str(path),
        "target_group_key": target_group_key,
        "year": year,
        "paper_id": paper_id,
        "section": section,
        "question_no": raw["question_no"],
        "subquestion_no": None,
        "raw_stem": stem[:1500],
        "marks": marks,
        "answer_rule": None,
        "answer_all": None,
        "answer_one": None,
        "choose_n": None,
        "question_type": qtype,
        "command_verbs": command_verbs(stem),
        "input_format": input_format(stem),
        "negative_marking": file_negative,
        "candidate_options": {"count": len(options), "option_texts": options},
        "extracted_confidence": confidence,
        "review_flag": review_flags,
        "answer_key_present": False,
    }


def family_key(record: dict[str, Any]) -> str:
    qtype = record.get("question_type") or "unknown"
    verbs = "-".join(record.get("command_verbs") or ["no_verb"])
    formats = record.get("input_format", {})
    active_formats = "-".join(key for key, value in formats.items() if value and key != "text_only") or "text"
    return f"{qtype}:{verbs}:{active_formats}"


def build_archetypes(records: list[dict[str, Any]], current_regime_key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[family_key(record)].append(record)

    archetypes = []
    for index, (key, items) in enumerate(sorted(grouped.items()), start=1):
        question_type, verbs, active_formats = key.split(":", 2)
        confidence = "High" if len(items) >= 3 else "Medium" if len(items) == 2 else "Low"
        archetypes.append(
            {
                "archetype_id": f"ARCH{index:03d}",
                "target_group_key": items[0]["target_group_key"],
                "current_regime_key": current_regime_key,
                "question_family": question_type,
                "recurrent_operation": {
                    "command_verbs": [] if verbs == "no_verb" else verbs.split("-"),
                    "input_format": active_formats,
                    "expected_answer_shape": question_type,
                },
                "slot_grammar": {
                    "slot_types": ["knowledge_point", "example", "representation"],
                    "source": "question_family_plus_input_format",
                    "bounded": True,
                },
                "mark_scheme_skeleton": ["claim_or_term", "mechanism_or_operation", "evidence_or_example", "limitation_if_relevant"],
                "compatible_kp_families": [],
                "seen_in": [
                    {
                        "year": item.get("year"),
                        "question_no": item.get("question_no"),
                        "section": item.get("section"),
                    }
                    for item in items
                ],
                "contradicted_by": [],
                "saturation": "unknown",
                "confidence": confidence,
                "student_output_action": output_action_for(question_type),
            }
        )
    return archetypes


def output_action_for(question_type: str) -> str:
    if question_type.startswith("mcq"):
        return "build_discriminator_trap_table_and_scoring_policy"
    if question_type == "fill_blank":
        return "build_term_bank_and_cloze_variants"
    if question_type.startswith("short_answer"):
        return "build_bounded_variant_space_and_mark_schema"
    if question_type in {"data_problem", "practical_protocol"}:
        return "build_input_operation_inference_limitation_follow_up"
    if question_type == "long_answer_project":
        return "build_method_block_library"
    if question_type.startswith("essay"):
        return "build_essay_coverage_plan"
    return "manual_review"


def prediction_objects(archetypes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outputs = []
    for archetype in archetypes:
        outputs.append(
            {
                "archetype_id": archetype["archetype_id"],
                "student_label": "High-priority prep target" if archetype["confidence"] == "High" else "Prep target",
                "prediction_object": "question_family",
                "exact_question_wording_claimed": False,
                "confidence_band": archetype["confidence"],
                "student_prep_action": archetype["student_output_action"],
                "uncertainty": "Exact filler is uncertain; prepare the compatible answer form and source-linked knowledge points.",
            }
        )
    return outputs


def process_file(path: Path, target_group_key: str) -> tuple[list[dict[str, Any]], list[str]]:
    text, qa_flags = read_text(path)
    if not text.strip():
        return [], qa_flags or ["empty_or_unreadable"]
    year = year_from_path(path, text)
    paper_id = path.stem
    file_negative = negative_marking(text)
    raw_questions = split_questions(text)
    records = [
        question_record(path, target_group_key, paper_id, year, None, raw, file_negative)
        for raw in raw_questions
    ]
    if not raw_questions:
        qa_flags.append("no_question_boundaries_detected")
    return records, qa_flags



def self_test() -> dict[str, Any]:
    import tempfile
    with tempfile.TemporaryDirectory(prefix="past_paper_questions_selftest_") as tmp:
        paper = Path(tmp) / "sample_paper_2025.txt"
        paper.write_text(
            "Negative marking: +1 for correct, -1/3 for wrong.\n"
            "Section A\n"
            "Question 1. Choose one answer.\nA. Enzyme inhibition\nB. Membrane potential\n[1]\n"
            "Question 2. Explain how competitive inhibition changes Km. [5]\n",
            encoding="utf-8",
        )
        questions, flags = process_file(paper, "inline_self_test")
    archetypes = build_archetypes(questions, "current_regime")
    qtypes = {item.get("question_type") for item in questions}
    failures = []
    if flags:
        failures.append({"type": "unexpected_flags", "flags": flags})
    if len(questions) != 2:
        failures.append({"type": "wrong_question_count", "questions": len(questions)})
    if "mcq_single_best" not in qtypes or "short_answer_explain" not in qtypes:
        failures.append({"type": "question_types_not_detected", "question_types": sorted(qtypes)})
    if not questions or not questions[0].get("negative_marking", {}).get("present"):
        failures.append({"type": "negative_marking_not_detected"})
    if not archetypes:
        failures.append({"type": "archetypes_not_built"})
    return {"pass": not failures, "question_types": sorted(qtypes), "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description="Extract question-level past-paper records.")
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--target-group-key")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--current-regime-key", default="current_regime")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1
    if not args.inputs or not args.target_group_key or not args.output_dir:
        print(json.dumps({"status": "fail", "error": "missing_inputs_target_group_output_dir_or_self_test"}, indent=2))
        return 1

    questions: list[dict[str, Any]] = []
    qa_flags: list[dict[str, str]] = []
    for path in iter_files(args.inputs):
        file_questions, file_flags = process_file(path, args.target_group_key)
        questions.extend(file_questions)
        for flag in file_flags:
            qa_flags.append({"source_file": str(path), "type": flag})

    archetypes = build_archetypes(questions, args.current_regime_key)
    result = {
        "status": "ok" if questions else "review_required",
        "questions": questions,
        "archetypes": archetypes,
        "prediction_objects": prediction_objects(archetypes),
        "qa_flags": qa_flags,
        "counts": {
            "questions": len(questions),
            "archetypes": len(archetypes),
            "qa_flags": len(qa_flags),
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "past_paper_questions.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (args.output_dir / "archetype_registry.json").write_text(json.dumps({"archetypes": archetypes}, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "questions": len(questions), "archetypes": len(archetypes), "output": str(args.output_dir)}, indent=2))
    return 0 if questions else 1


if __name__ == "__main__":
    raise SystemExit(main())
