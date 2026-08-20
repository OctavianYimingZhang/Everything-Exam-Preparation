#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import html
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

MODE_PATTERNS = {
    "MCQ": [r"\b[A-D][).]", r"multiple choice", r"single best", r"\bmcq\b", r"which of the following", r"true/false"],
    "Short Answer": [r"short answer", r"\b[1-6]\s*marks?\b", r"\bdefine\b", r"\bstate\b", r"\blist\b", r"\boutline\b"],
    "Long Answer": [r"\b(7|8|9|10|12|15|20|25|30)\s*marks?\b", r"\bexplain\b", r"\bcompare\b", r"\bevaluate\b", r"\bdiscuss\b", r"\bjustify\b"],
    "Practical/Data/Problem": [r"\bpractical\b", r"\bdata\b", r"\bproblem\b", r"\bcalculate\b", r"\binterpret\b", r"\bcontrol\b", r"\breadout\b", r"\bgraph\b", r"\btable\b"],
    "Essay": [r"essay", r"critically", r"to what extent", r"argument", r"thesis", r"in-campus"],
}

COMMAND_VERBS = ["define", "state", "list", "outline", "describe", "explain", "compare", "evaluate", "discuss", "calculate", "interpret", "justify", "criticise", "critically"]
STOPWORDS = {"which", "there", "their", "about", "using", "answer", "question", "marks", "following", "explain", "describe", "compare", "evaluate", "discuss", "calculate", "interpret"}
PRACTICAL_WORKED_WORDS = {"calculate", "derive", "show", "estimate", "prove", "data", "problem", "interpret", "graph", "table", "fit", "plot", "uncertainty", "error", "unit"}


def extract_questions(text: str) -> list[str]:
    questions: list[str] = []
    for line in (text or "").splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if not clean:
            continue
        if "?" in clean or re.match(r"^(Q\d+|\d+[).]|[a-z][)])\s+", clean, re.I):
            questions.append(clean)
    return questions


def split_saq_subquestions(question: str) -> list[str]:
    clean = re.sub(r"\s+", " ", question or "").strip()
    if not clean:
        return []
    markers = list(re.finditer(r"(?<![A-Za-z])(?:\([a-z]\)|[a-z]\)|\([ivx]{1,4}\)|[ivx]{1,4}\))\s+", clean))
    if len(markers) < 2:
        return [clean]
    prefix = clean[:markers[0].start()].strip()
    parts: list[str] = []
    for idx, marker in enumerate(markers):
        end = markers[idx + 1].start() if idx + 1 < len(markers) else len(clean)
        part = clean[marker.start():end].strip()
        if not part:
            continue
        parts.append(f"{prefix} {part}".strip() if prefix else part)
    return parts or [clean]


def question_mode(question: str) -> str:
    scores = score_modes(question)
    mode = detected_mode(scores)
    return "Short Answer" if mode == "Unknown" and re.search(r"\bdefine\b|\bstate\b|\blist\b", question, flags=re.I) else mode


def question_terms(questions: list[str]) -> list[dict[str, Any]]:
    return frequent_terms("\n".join(questions))


def command_verbs_in_text(text: str) -> list[str]:
    lower = (text or "").lower()
    return [verb for verb in COMMAND_VERBS if re.search(r"\b" + re.escape(verb) + r"\b", lower)]


def answer_operation_type(text: str, mode: str = "") -> str:
    lower = (text or "").lower()
    if re.search(r"\bdefine\b|\bwhat is\b|\bwhat are\b", lower):
        return "definition"
    if re.search(r"\bcompare\b|\bdifference\b|\bversus\b|\bvs\b|\bwhich.*different", lower):
        return "comparison"
    if re.search(r"\bexplain\b|\bwhy\b|\bmechanism\b|\bhow\b", lower):
        return "mechanism"
    if re.search(r"\bcalculate\b|\bderive\b|\bestimate\b|\bsolve\b", lower):
        return "calculation"
    if re.search(r"\bidentify\b|\bstate\b|\blist\b|\bwhich of the following\b|\bsingle best\b", lower):
        return "recognition"
    if mode == "MCQ":
        return "recognition"
    if mode == "Short Answer":
        return "short_answer_recall"
    return "knowledge_application"


def question_pattern(text: str, mode: str = "") -> str:
    lower = (text or "").lower()
    if mode == "MCQ" or re.search(r"\bwhich of the following\b|\bsingle best\b|\btrue/false\b", lower):
        if re.search(r"\bexcept\b|\bnot\b|\bincorrect\b|\bfalse\b", lower):
            return "mcq_negative_discrimination"
        return "mcq_positive_recognition"
    if re.search(r"\b\d+\s*marks?\b", lower):
        return "saq_marked_prompt"
    if re.search(r"\bdefine\b", lower):
        return "saq_definition"
    if re.search(r"\blist\b|\bstate\b", lower):
        return "saq_list_or_state"
    return "open_prompt"


def has_practical_worked_signal(text: str) -> bool:
    lower = (text or "").lower()
    return any(re.search(r"\b" + re.escape(word) + r"\b", lower) for word in PRACTICAL_WORKED_WORDS)


def question_records_from_text(text: str, source_name: str = "input", source_order: int = 0, locator: str = "text", source_id: str = "") -> list[dict[str, Any]]:
    records = []
    order = 0
    for extracted in extract_questions(text):
        parts = split_saq_subquestions(extracted)
        for part_index, question in enumerate(parts, 1):
            order += 1
            mode = question_mode(question)
            subpart = part_index if len(parts) > 1 else None
            records.append({
                "source_order": source_order,
                "source_id": source_id,
                "source_name": source_name,
                "locator": locator,
                "question_order": order,
                "subquestion_order": subpart,
                "mode": mode,
                "question": question,
                "question_demand": command_verbs_in_text(question),
                "knowledge_terms": [item["term"] for item in question_terms([question])],
                "answer_operation_type": answer_operation_type(question, mode),
                "question_pattern": question_pattern(question, mode),
                "practical_worked_signal": has_practical_worked_signal(question),
            })
    return records


def legacy_question_records_from_text(text: str, source_name: str = "input", source_order: int = 0, locator: str = "text", source_id: str = "") -> list[dict[str, Any]]:
    records = []
    for idx, question in enumerate(extract_questions(text), 1):
        mode = question_mode(question)
        records.append({
            "source_order": source_order,
            "source_id": source_id,
            "source_name": source_name,
            "locator": locator,
            "question_order": idx,
            "mode": mode,
            "question": question,
            "question_demand": command_verbs_in_text(question),
            "knowledge_terms": [item["term"] for item in question_terms([question])],
            "answer_operation_type": answer_operation_type(question, mode),
            "question_pattern": question_pattern(question, mode),
            "practical_worked_signal": has_practical_worked_signal(question),
        })
    return records


def fragment_provenance(frag: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    nested = frag.get("provenance") if isinstance(frag.get("provenance"), dict) else {}
    return {
        "source_id": nested.get("source_id") or frag.get("source_id") or source.get("id"),
        "source_name": nested.get("source_name") or frag.get("source_name") or source.get("name"),
        "locator": nested.get("locator") or frag.get("locator"),
        "page_number": nested.get("page_number") or frag.get("page_number"),
        "slide_number": nested.get("slide_number") or frag.get("slide_number"),
        "time_offset_seconds": nested.get("time_offset_seconds") or frag.get("time_offset_seconds"),
        "time_range": nested.get("time_range") or frag.get("time_range"),
    }


def question_records_from_scan(scan: dict[str, Any]) -> list[dict[str, Any]]:
    docs = {doc.get("id"): doc for doc in scan.get("documents", [])}
    records: list[dict[str, Any]] = []
    for source_order, frag in enumerate(scan.get("fragments", []), 1):
        source = docs.get(frag.get("source_id"), {})
        category = frag.get("category") or source.get("category")
        question_flags = source.get("question_signals", {})
        if category not in {"practice_material", "marking_material"} and not question_flags.get("has_questions"):
            continue
        fragment_records = question_records_from_text(
            str(frag.get("text") or ""),
            source_name=str(frag.get("source_name") or source.get("name") or "source"),
            source_order=source_order,
            locator=str(frag.get("locator") or ""),
            source_id=str(frag.get("source_id") or ""),
        )
        provenance = fragment_provenance(frag, source)
        for record in fragment_records:
            record["provenance"] = provenance
        records.extend(fragment_records)
    records.sort(key=lambda item: (item["source_order"], item["question_order"]))
    return records


def group_by_source_order(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    by_key: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for record in records:
        key = (int(record.get("source_order") or 0), str(record.get("source_name") or "source"))
        by_key.setdefault(key, []).append(record)
    for (source_order, source_name), items in sorted(by_key.items()):
        groups.append({"lecture_order": source_order, "source_name": source_name, "questions": items})
    return groups


def long_answer_analysis_predictions(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for record in records:
        if record.get("mode") not in {"Long Answer", "Practical/Data/Problem", "Mixed"}:
            continue
        terms = record.get("knowledge_terms") or []
        demand = record.get("question_demand") or []
        out.append({
            "question": record.get("question"),
            "source_name": record.get("source_name"),
            "locator": record.get("locator"),
            "question_demand": demand,
            "repeated_knowledge_target": terms,
            "expected_answer_focus": ", ".join(demand + terms).strip(", "),
            "example_answer": "Define the central concept, explain the relevant mechanism, method, calculation, or data interpretation, and state the academic conclusion demanded by the question.",
        })
    return out


def solution_fragments_from_scan(scan: dict[str, Any]) -> list[dict[str, Any]]:
    docs = {doc.get("id"): doc for doc in scan.get("documents", [])}
    fragments = []
    for frag in scan.get("fragments", []):
        source = docs.get(frag.get("source_id"), {})
        category = frag.get("category") or source.get("category")
        signals = source.get("question_signals", {}) or {}
        if category == "marking_material" or signals.get("has_solution_evidence"):
            fragments.append(frag)
    return fragments


def term_set(text: str) -> set[str]:
    return {item["term"] for item in frequent_terms(text)}


def solution_match_score(question: str, fragment_text: str) -> int:
    q_terms = term_set(question)
    f_terms = term_set(fragment_text)
    overlap = len(q_terms & f_terms)
    formula_bonus = len(re.findall(r"=|∝|≈|\btherefore\b|\bhence\b", fragment_text, flags=re.I))
    return overlap + formula_bonus


def match_solution_fragment(record: dict[str, Any], solution_fragments: list[dict[str, Any]]) -> dict[str, Any] | None:
    scored = []
    for fragment in solution_fragments:
        score = solution_match_score(str(record.get("question") or ""), str(fragment.get("text") or ""))
        same_source = str(record.get("source_name") or "").split(".")[0].lower() in str(fragment.get("source_name") or "").lower()
        if same_source:
            score += 1
        if score > 0:
            scored.append((score, fragment))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def solution_steps_from_text(text: str) -> list[str]:
    steps = []
    for line in (text or "").splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if clean and not re.match(r"^PX\d+|^THE UNIVERSITY|^Time Allowed", clean, flags=re.I):
            steps.append(clean)
    return steps


def practical_worked_records_from_scan(scan: dict[str, Any]) -> list[dict[str, Any]]:
    docs = {doc.get("id"): doc for doc in scan.get("documents", [])}
    solution_fragments = solution_fragments_from_scan(scan)
    out = []
    for record in question_records_from_scan(scan):
        source = docs.get(record.get("source_id"), {})
        if (source.get("category") or source.get("source_hint")) == "marking_material":
            continue
        is_practical_source = bool(source.get("question_signals", {}).get("has_practical_worked_questions"))
        source_name = str(source.get("name") or record.get("source_name") or "").lower()
        is_practical_source = is_practical_source or any(word in source_name for word in ["practical", "lab", "experiment", "worksheet"])
        if not (record.get("practical_worked_signal") or is_practical_source):
            continue
        matched = match_solution_fragment(record, solution_fragments)
        steps = solution_steps_from_text(str(matched.get("text") or "")) if matched else [
            "Identify the given quantities and the target quantity from the question.",
            "Choose the course relationship that connects the givens to the target.",
            "Substitute the quantities symbolically before evaluating or simplifying.",
            "State the final expression or numerical result with units where applicable.",
        ]
        out.append({
            "render_mode": "worked_example",
            "source_name": record.get("source_name"),
            "locator": record.get("locator"),
            "question": record.get("question"),
            "givens": [],
            "target": "",
            "method": "Use the relevant course equation, derivation, data interpretation, or approximation indicated by the question.",
            "steps": steps,
            "final_answer": "",
            "assumptions": [],
            "unit_check": "",
            "interpretation": "State what the calculated or derived result means in the context of the practical problem.",
            "verification": {
                "status": "solution evidence matched" if matched else "solution evidence not found",
                "source": matched.get("source_name") if matched else "",
                "locator": matched.get("locator") if matched else "",
            },
        })
    return out


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


def frequent_terms(text: str, limit: int | None = None) -> list[dict[str, Any]]:
    words = re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or "")
    counts = collections.Counter(w.lower() for w in words if w.lower() not in STOPWORDS)
    items = counts.most_common(limit) if limit else counts.most_common()
    return [{"term": term, "count": count} for term, count in items]


def analyze_text(text: str) -> dict[str, Any]:
    scores = score_modes(text)
    records = question_records_from_text(text)
    questions = [record["question"] for record in records]
    return {
        "schema_version": 2,
        "detected_mode": detected_mode(scores),
        "mode_scores": scores,
        "question_count": len(questions),
        "questions": questions,
        "question_groups_by_lecture_order": group_by_source_order(records),
        "question_only_high_frequency_knowledge_points": question_terms(questions),
        "long_answer_analysis_prediction": long_answer_analysis_predictions(records),
        "practical_worked_solution_questions": [record for record in records if record.get("practical_worked_signal")],
        "examiner_habits": {
            "command_verbs": command_counts(text),
            "mark_values": mark_values(text),
            "frequent_terms": question_terms(questions),
            "question_forms": questions,
        },
    }


def build_exam_type_addon(scan: dict[str, Any] | None = None, text: str = "") -> dict[str, Any]:
    records = question_records_from_scan(scan or {}) if scan else question_records_from_text(text)
    mcq_short = [record for record in records if record.get("mode") in {"MCQ", "Short Answer", "Mixed"}]
    return {
        "schema_version": 2,
        "document_kind": "exam_type_related_addon",
        "question_groups_by_lecture_order": group_by_source_order(records),
        "mcq_short_answer_questions": mcq_short,
        "question_only_high_frequency_knowledge_points": question_terms([record["question"] for record in records]),
        "long_answer_practical_data_problem": long_answer_analysis_predictions(records),
    }


def build_practical_worked_solutions(scan: dict[str, Any] | None = None, text: str = "") -> dict[str, Any]:
    if scan:
        blocks = practical_worked_records_from_scan(scan)
    else:
        blocks = [
            {
                "render_mode": "worked_example",
                "question": record.get("question"),
                "method": "Use the relevant course equation, derivation, data interpretation, or approximation indicated by the question.",
                "steps": [
                    "Identify the given quantities and the target quantity from the question.",
                    "Choose the course relationship that connects the givens to the target.",
                    "Substitute the quantities symbolically before evaluating or simplifying.",
                    "State the final expression or numerical result with units where applicable.",
                ],
                "interpretation": "State what the result means in the context of the problem.",
                "verification": {"status": "solution evidence not found"},
            }
            for record in question_records_from_text(text)
            if record.get("practical_worked_signal")
        ]
    return {
        "schema_version": 2,
        "document_kind": "practical_worked_solutions_docx",
        "title": "Detailed Worked Solutions",
        "sections": [{"heading": "Detailed Worked Solutions", "blocks": blocks}],
    }


def terms_from_text(text: str) -> set[str]:
    return {item["term"] for item in frequent_terms(text)}


def lecture_knowledge_units_from_scan(scan: dict[str, Any]) -> list[dict[str, Any]]:
    docs = {doc.get("id"): doc for doc in scan.get("documents", [])}
    units: list[dict[str, Any]] = []
    for idx, frag in enumerate(scan.get("fragments", []), 1):
        source = docs.get(frag.get("source_id"), {})
        category = frag.get("category") or source.get("category") or source.get("source_hint")
        if category != "knowledge_material":
            continue
        text = str(frag.get("text") or "")
        candidates = frag.get("knowledge_unit_candidates", []) or []
        if candidates:
            label = str(candidates[-1].get("label") or candidates[-1].get("signal") or "")
        else:
            label = str(frag.get("source_name") or source.get("name") or f"Lecture unit {idx}")
        units.append({
            "id": f"KU{idx}",
            "lecture_order": idx,
            "source_id": frag.get("source_id"),
            "source_name": frag.get("source_name") or source.get("name") or "lecture source",
            "locator": frag.get("locator") or "",
            "label": label[:180],
            "text": text,
            "terms": sorted(terms_from_text(text)),
            "knowledge_signals": frag.get("knowledge_signals", []),
            "knowledge_roles": frag.get("knowledge_roles", []),
        })
    return units


def record_term_set(record: dict[str, Any]) -> set[str]:
    return set(record.get("knowledge_terms") or []) | terms_from_text(str(record.get("question") or ""))


def matching_knowledge_units(record: dict[str, Any], units: list[dict[str, Any]], min_overlap: int = 2) -> list[dict[str, Any]]:
    q_terms = record_term_set(record)
    matches: list[dict[str, Any]] = []
    for unit in units:
        unit_terms = set(unit.get("terms") or [])
        overlap = sorted(q_terms & unit_terms)
        if len(overlap) < min_overlap:
            continue
        demand_bonus = len(set(record.get("question_demand") or []) & terms_from_text(str(unit.get("text") or "")))
        matches.append({
            "unit": unit,
            "shared_terms": overlap,
            "score": len(overlap) * 10 + demand_bonus,
        })
    matches.sort(key=lambda item: (item["score"], item["unit"]["lecture_order"]), reverse=True)
    return matches


def match_question_to_knowledge_unit(record: dict[str, Any], units: list[dict[str, Any]]) -> dict[str, Any] | None:
    matches = matching_knowledge_units(record, units)
    return matches[0] if matches else None


def target_question_record(question: str) -> dict[str, Any]:
    records = question_records_from_text(question, source_name="target_question", source_order=0, locator="user question")
    if records:
        return records[0]
    return {
        "source_order": 0,
        "source_id": "",
        "source_name": "target_question",
        "locator": "user question",
        "question_order": 1,
        "mode": question_mode(question),
        "question": question,
        "question_demand": command_verbs_in_text(question),
        "knowledge_terms": [item["term"] for item in question_terms([question])],
        "practical_worked_signal": has_practical_worked_signal(question),
    }


def strict_same_knowledge_point_questions(question: str, scan: dict[str, Any]) -> dict[str, Any]:
    units = lecture_knowledge_units_from_scan(scan)
    target = target_question_record(question)
    target_match = match_question_to_knowledge_unit(target, units)
    if not target_match:
        return {
            "match_status": "no_strict_knowledge_unit_match",
            "target_question": question,
            "matched_knowledge_unit": None,
            "same_knowledge_point_questions": [],
        }
    target_unit = target_match["unit"]
    target_terms = set(target_match["shared_terms"])
    required_shared_terms = max(2, min(4, (len(target_terms) + 1) // 2))
    matches = []
    for record in question_records_from_scan(scan):
        candidate_question = str(record.get("question") or "")
        if re.sub(r"\s+", " ", candidate_question).strip().lower() == re.sub(r"\s+", " ", question).strip().lower():
            continue
        candidate_match = match_question_to_knowledge_unit(record, units)
        if not candidate_match:
            continue
        if candidate_match["unit"]["id"] != target_unit["id"]:
            continue
        shared_with_target = sorted(target_terms & set(candidate_match["shared_terms"]))
        if len(shared_with_target) < required_shared_terms:
            continue
        matches.append({
            "source_name": record.get("source_name"),
            "locator": record.get("locator"),
            "question_order": record.get("question_order"),
            "mode": record.get("mode"),
            "question": candidate_question,
            "matched_knowledge_unit": target_unit,
            "shared_terms": shared_with_target,
        })
    return {
        "match_status": "strict_match" if matches else "no_other_strict_same_point_question_found",
        "target_question": question,
        "matched_knowledge_unit": target_unit,
        "target_shared_terms": sorted(target_terms),
        "same_knowledge_point_questions": matches,
    }


def build_question_solver_pack(question: str, scan: dict[str, Any]) -> dict[str, Any]:
    target = target_question_record(question)
    same_point = strict_same_knowledge_point_questions(question, scan)
    unit = same_point.get("matched_knowledge_unit") or {}
    return {
        "schema_version": 2,
        "document_kind": "question_solution_report",
        "target_question": question,
        "question_analysis": {
            "mode": target.get("mode"),
            "question_demand": target.get("question_demand"),
            "knowledge_terms": target.get("knowledge_terms"),
        },
        "matching_knowledge": {
            "status": same_point.get("match_status"),
            "unit_label": unit.get("label"),
            "source_name": unit.get("source_name"),
            "locator": unit.get("locator"),
            "knowledge_excerpt": re.sub(r"\s+", " ", str(unit.get("text") or ""))[:700],
            "shared_terms": same_point.get("target_shared_terms", []),
        },
        "solution_guidance": [
            "Identify the command verb and the exact knowledge being tested.",
            "State the matched course knowledge before attempting the answer.",
            "Apply the matched knowledge to each part of the question and keep the answer source-grounded.",
        ],
        "strict_same_knowledge_point_questions": same_point.get("same_knowledge_point_questions", []),
        "transfer_practice_prompt": "Try the strict same-knowledge-point questions without looking back at the explanation, then check whether the same knowledge unit answers each one.",
    }


def organize_questions_by_lecture_order(scan: dict[str, Any]) -> dict[str, Any]:
    units = lecture_knowledge_units_from_scan(scan)
    grouped: dict[tuple[int, str, str], list[dict[str, Any]]] = {}
    unmatched: list[dict[str, Any]] = []
    for record in question_records_from_scan(scan):
        matches = matching_knowledge_units(record, units)
        if not matches:
            unmatched.append(record)
            continue
        latest = max(matches, key=lambda item: item["unit"]["lecture_order"])
        unit = latest["unit"]
        key = (int(unit["lecture_order"]), str(unit["source_name"]), str(unit["label"]))
        grouped.setdefault(key, []).append({
            "question": record.get("question"),
            "source_name": record.get("source_name"),
            "locator": record.get("locator"),
            "question_order": record.get("question_order"),
            "matched_knowledge_unit": unit,
            "shared_terms": latest.get("shared_terms", []),
        })
    sections = []
    for (lecture_order, source_name, label), questions in sorted(grouped.items(), key=lambda item: item[0][0]):
        sections.append({
            "lecture_order": lecture_order,
            "source_name": source_name,
            "knowledge_unit": label,
            "questions": questions,
        })
    if unmatched:
        sections.append({
            "lecture_order": None,
            "source_name": "Unmatched",
            "knowledge_unit": "Unmatched questions",
            "questions": [{
                "question": item.get("question"),
                "source_name": item.get("source_name"),
                "locator": item.get("locator"),
                "question_order": item.get("question_order"),
            } for item in unmatched],
        })
    return {
        "schema_version": 2,
        "document_kind": "organized_questions_docx",
        "title": "Past Paper and Practice Questions by Lecture Order",
        "question_count": sum(len(section["questions"]) for section in sections),
        "sections": sections,
    }


def docx_paragraph(text: str, style: str = "") -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    escaped = html.escape(text or "")
    return f"<w:p>{style_xml}<w:r><w:t xml:space=\"preserve\">{escaped}</w:t></w:r></w:p>"


def write_organized_questions_docx(path: Path, organized: dict[str, Any]) -> None:
    paragraphs = [docx_paragraph(str(organized.get("title") or "Organized Questions"), "Title")]
    for section in organized.get("sections", []):
        heading = section.get("knowledge_unit") or "Questions"
        if section.get("lecture_order") is not None:
            heading = f"Lecture order {section['lecture_order']}: {heading}"
        paragraphs.append(docx_paragraph(str(heading), "Heading1"))
        for idx, item in enumerate(section.get("questions", []), 1):
            provenance = f"[{item.get('source_name') or 'source'}; {item.get('locator') or 'locator unavailable'}; original order {item.get('question_order') or idx}]"
            paragraphs.append(docx_paragraph(f"{idx}. {item.get('question') or ''}"))
            paragraphs.append(docx_paragraph(provenance))
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(paragraphs)}<w:sectPr/></w:body></w:document>"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        zf.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        zf.writestr("word/document.xml", document_xml)


SOLUTION_BOOK_SCHEMA_VERSION = 1


def _text_items(value: Any) -> list[str]:
    if value in (None, "", []):
        return []
    values = value if isinstance(value, list) else [value]
    result: list[str] = []
    for item in values:
        if isinstance(item, dict):
            text = item.get("text") or item.get("content") or item.get("detail")
        else:
            text = item
        clean = re.sub(r"\s+", " ", str(text or "")).strip()
        if clean:
            result.append(clean)
    return result


def _normalise_solution_subparts(value: Any) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Keep subparts as locators and lift any supplied mini-answer into one question-level chain."""
    subparts: list[dict[str, str]] = []
    lifted_reasoning: list[dict[str, str]] = []
    for index, raw in enumerate(value if isinstance(value, list) else [], 1):
        if isinstance(raw, str):
            match = re.match(r"^\s*(\([a-z0-9ivx]+\)|[a-z0-9ivx]+[.)])\s*(.*)$", raw, flags=re.I)
            label = match.group(1) if match else f"({chr(96 + min(index, 26))})"
            prompt = match.group(2) if match else raw
            item: dict[str, Any] = {"label": label, "prompt": prompt}
        elif isinstance(raw, dict):
            item = raw
            label = str(item.get("label") or item.get("subpart") or f"({chr(96 + min(index, 26))})").strip()
            prompt = str(item.get("prompt") or item.get("question") or item.get("text") or "").strip()
        else:
            continue
        subparts.append({"label": label, "prompt": re.sub(r"\s+", " ", prompt).strip()})
        for field in ("reasoning", "worked_solution", "answer", "final_answer"):
            for text in _text_items(item.get(field)):
                lifted_reasoning.append({"locator": label, "text": text})
    return subparts, lifted_reasoning


def _normalise_reasoning_chain(value: Any) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    values = value if isinstance(value, list) else ([value] if value not in (None, "") else [])
    for raw in values:
        if isinstance(raw, dict):
            text = raw.get("text") or raw.get("content") or raw.get("reasoning") or raw.get("step")
            locator = raw.get("locator") or raw.get("subpart") or raw.get("applies_to") or ""
        else:
            text = raw
            locator = ""
        clean = re.sub(r"\s+", " ", str(text or "")).strip()
        if clean:
            result.append({"locator": re.sub(r"\s+", " ", str(locator or "")).strip(), "text": clean})
    return result


def _normalise_solution_table(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    headers = [re.sub(r"\s+", " ", str(value or "")).strip() for value in raw.get("headers", [])]
    rows: list[list[str]] = []
    for row in raw.get("rows", []) if isinstance(raw.get("rows"), list) else []:
        values = row if isinstance(row, list) else list(row.values()) if isinstance(row, dict) else [row]
        rows.append([re.sub(r"\s+", " ", str(value or "")).strip() for value in values])
    if not headers and rows:
        headers = [f"Column {index + 1}" for index in range(max(len(row) for row in rows))]
    if not headers:
        return None
    width = len(headers)
    rows = [(row + [""] * width)[:width] for row in rows]
    return {
        "title": re.sub(r"\s+", " ", str(raw.get("title") or "")).strip(),
        "headers": headers,
        "rows": rows,
    }


def _solution_source_evidence(payload: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    """Index the shared source scan so a displayed source reference cannot self-authenticate."""
    scan = payload.get("source_scan") if isinstance(payload.get("source_scan"), dict) else {}
    documents = scan.get("documents") if isinstance(scan.get("documents"), list) else []
    fragments = scan.get("fragments") if isinstance(scan.get("fragments"), list) else []
    sources: dict[str, dict[str, Any]] = {}
    source_ids: set[str] = set()
    for document in documents:
        if not isinstance(document, dict):
            continue
        source_id = str(document.get("id") or document.get("source_id") or "").strip()
        source_name = str(document.get("name") or document.get("source_name") or "").strip()
        if source_id:
            source_ids.add(source_id)
            sources[f"id:{source_id}"] = document
        if source_name:
            sources[f"name:{source_name.casefold()}"] = document
    locators: dict[str, set[str]] = {source_id: set() for source_id in source_ids}
    for fragment in fragments:
        if not isinstance(fragment, dict):
            continue
        source_id = str(fragment.get("source_id") or "").strip()
        locator = str(fragment.get("locator") or "").strip()
        if source_id in locators and locator:
            locators[source_id].add(locator)
    return sources, locators


def _validate_solution_source_refs(
    refs: list[Any],
    sources: dict[str, dict[str, Any]],
    locators: dict[str, set[str]],
    question_id: str,
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for index, ref in enumerate(refs, 1):
        if not isinstance(ref, dict):
            issues.append({
                "code": "unverifiable_source_reference",
                "question_id": question_id,
                "source_ref": str(index),
            })
            continue
        source_id = str(ref.get("source_id") or "").strip()
        source_name = str(ref.get("source_name") or "").strip()
        document = sources.get(f"id:{source_id}") if source_id else None
        if document is None and source_name:
            document = sources.get(f"name:{source_name.casefold()}")
        if document is None:
            issues.append({
                "code": "unknown_source_reference",
                "question_id": question_id,
                "source_ref": source_id or source_name or str(index),
            })
            continue
        resolved_id = str(document.get("id") or document.get("source_id") or "").strip()
        locator = str(ref.get("locator") or "").strip()
        if not locator:
            issues.append({
                "code": "missing_source_locator",
                "question_id": question_id,
                "source_ref": resolved_id or source_name,
            })
        elif locator not in locators.get(resolved_id, set()):
            issues.append({
                "code": "unresolved_source_locator",
                "question_id": question_id,
                "source_ref": resolved_id or source_name,
            })
    return issues


def normalise_solution_book(payload: dict[str, Any]) -> dict[str, Any]:
    """Build the public solution-book model without splitting answers into subpart units."""
    if not isinstance(payload, dict):
        raise TypeError("solution book payload must be an object")
    raw_groups = payload.get("question_groups") or payload.get("groups")
    if not raw_groups and isinstance(payload.get("questions"), list):
        raw_groups = [{"group_id": "G1", "questions": payload["questions"], "general_approach": payload.get("general_approach")}]
    if not isinstance(raw_groups, list) or not raw_groups:
        raise ValueError("solution book requires at least one question group")

    groups: list[dict[str, Any]] = []
    issues: list[dict[str, str]] = []
    source_evidence, source_locators = _solution_source_evidence(payload)
    seen_question_ids: set[str] = set()
    public_answer_units: list[str] = []
    for group_index, raw_group in enumerate(raw_groups, 1):
        if not isinstance(raw_group, dict):
            raise TypeError("each question group must be an object")
        group_id = re.sub(r"\s+", "-", str(raw_group.get("group_id") or f"G{group_index}").strip())
        raw_questions = raw_group.get("questions")
        if not isinstance(raw_questions, list) or not raw_questions:
            raise ValueError(f"question group {group_id} requires at least one major question")
        questions: list[dict[str, Any]] = []
        group_approach = _text_items(raw_group.get("general_approach"))
        for question_index, raw_question in enumerate(raw_questions, 1):
            if not isinstance(raw_question, dict):
                raw_question = {"question": str(raw_question)}
            question_id = re.sub(
                r"\s+",
                "-",
                str(raw_question.get("question_id") or raw_question.get("id") or f"Q{group_index}.{question_index}").strip(),
            )
            if question_id in seen_question_ids:
                raise ValueError(f"duplicate major question id: {question_id}")
            seen_question_ids.add(question_id)
            public_answer_units.append(question_id)
            prompt = re.sub(
                r"\s+",
                " ",
                str(raw_question.get("question") or raw_question.get("prompt") or raw_question.get("question_text") or ""),
            ).strip()
            if not prompt:
                issues.append({"code": "missing_major_question_prompt", "question_id": question_id})
            subparts, lifted_reasoning = _normalise_solution_subparts(raw_question.get("subparts"))
            reasoning = _normalise_reasoning_chain(
                raw_question.get("reasoning_chain")
                or raw_question.get("worked_solution")
                or raw_question.get("reasoning")
                or raw_question.get("answer")
            )
            reasoning.extend(lifted_reasoning)
            if not reasoning:
                issues.append({"code": "missing_reasoning_chain", "question_id": question_id})
            final_answer = re.sub(
                r"\s+",
                " ",
                str(raw_question.get("final_answer") or raw_question.get("result") or ""),
            ).strip()
            tables = [table for table in (_normalise_solution_table(item) for item in raw_question.get("tables", []) or []) if table]
            formulas = _text_items(raw_question.get("formulas") or raw_question.get("equations"))
            source_refs = raw_question.get("source_refs") if isinstance(raw_question.get("source_refs"), list) else []
            if source_refs:
                issues.extend(_validate_solution_source_refs(
                    source_refs,
                    source_evidence,
                    source_locators,
                    question_id,
                ))
            questions.append({
                "question_id": question_id,
                "question": prompt,
                "subparts": subparts,
                "reasoning_chain": reasoning,
                "formulas": formulas,
                "tables": tables,
                "final_answer": final_answer,
                "source_refs": source_refs,
            })
            for item in _text_items(raw_question.get("general_approach")):
                if item not in group_approach:
                    group_approach.append(item)
        if len(questions) > 1 and not group_approach:
            issues.append({"code": "missing_general_approach_for_question_group", "group_id": group_id})
        groups.append({
            "group_id": group_id,
            "group_title": re.sub(r"\s+", " ", str(raw_group.get("group_title") or raw_group.get("title") or f"Question group {group_index}")).strip(),
            "questions": questions,
            "general_approach": group_approach,
        })

    title = re.sub(r"\s+", " ", str(payload.get("title") or "Solution Book")).strip()
    reference_payload = [
        {
            "question_id": question["question_id"],
            "source_refs": question.get("source_refs") or [],
        }
        for group in groups
        for question in group["questions"]
        if question.get("source_refs")
    ]
    source_issue_codes = {
        "unverifiable_source_reference", "unknown_source_reference",
        "missing_source_locator", "unresolved_source_locator",
    }
    source_reference_validation = {
        "reference_count": sum(len(item["source_refs"]) for item in reference_payload),
        "reference_sha256": hashlib.sha256(json.dumps(
            reference_payload,
            sort_keys=True,
            ensure_ascii=False,
            default=str,
            separators=(",", ":"),
        ).encode("utf-8")).hexdigest(),
        "verified": not any(issue.get("code") in source_issue_codes for issue in issues),
    }
    book = {
        "schema_version": SOLUTION_BOOK_SCHEMA_VERSION,
        "task_mode": "solution_book",
        "document_kind": "solution_book",
        "title": title,
        "language": str(payload.get("language") or "English"),
        "question_groups": groups,
        "public_answer_unit": "major_question",
        "public_answer_units": public_answer_units,
        "subpart_policy": "locator_only",
        "general_approach_policy": "once_after_each_question_group",
        "source_reference_validation": source_reference_validation,
        "qa": {
            "status": "ready" if not issues else "incomplete",
            "issues": issues,
            "major_question_count": len(public_answer_units),
            "group_count": len(groups),
        },
    }
    return book


def _as_solution_book(payload: dict[str, Any]) -> dict[str, Any]:
    if (
        isinstance(payload, dict)
        and payload.get("task_mode") == "solution_book"
        and payload.get("document_kind") == "solution_book"
        and isinstance(payload.get("qa"), dict)
    ):
        return payload
    return normalise_solution_book(payload)


def solution_book_invariants(book: dict[str, Any]) -> dict[str, bool]:
    groups = book.get("question_groups") if isinstance(book.get("question_groups"), list) else []
    questions = [
        question
        for group in groups if isinstance(group, dict)
        for question in (group.get("questions") or []) if isinstance(question, dict)
    ]
    issue_codes = {
        str(issue.get("code") or "")
        for issue in (book.get("qa") or {}).get("issues", [])
        if isinstance(issue, dict)
    }
    source_issue_codes = {
        "unverifiable_source_reference", "unknown_source_reference",
        "missing_source_locator", "unresolved_source_locator",
    }
    reference_payload = [
        {
            "question_id": question.get("question_id"),
            "source_refs": question.get("source_refs") or [],
        }
        for question in questions
        if question.get("source_refs")
    ]
    declared_source_validation = book.get("source_reference_validation")
    if not isinstance(declared_source_validation, dict):
        declared_source_validation = {}
    reference_count = sum(len(item["source_refs"]) for item in reference_payload)
    reference_sha256 = hashlib.sha256(json.dumps(
        reference_payload,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")).hexdigest()
    source_references_verified = (
        declared_source_validation.get("verified") is True
        and declared_source_validation.get("reference_count") == reference_count
        and declared_source_validation.get("reference_sha256") == reference_sha256
        and not bool(issue_codes & source_issue_codes)
    )
    return {
        "subparts_are_locator_only": all(
            set(subpart) <= {"label", "prompt"}
            for question in questions
            for subpart in (question.get("subparts") or [])
            if isinstance(subpart, dict)
        ),
        "continuous_question_level_reasoning": bool(questions) and all(
            bool(question.get("reasoning_chain")) for question in questions
        ),
        "general_approach_after_group": all(
            not any(question.get("general_approach") for question in (group.get("questions") or []))
            for group in groups if isinstance(group, dict)
        ),
        "specific_answers_preserved": bool(questions) and all(
            bool(question.get("question")) and bool(question.get("reasoning_chain"))
            for question in questions
        ),
        "source_references_verified": source_references_verified,
    }


def build_solution_book(payload: dict[str, Any]) -> dict[str, Any]:
    """Public alias for callers selecting task_mode=solution_book."""
    return normalise_solution_book(payload)


def _w_run(text: str, *, bold: bool = False, italic: bool = False, size: int | None = None) -> str:
    properties = []
    if bold:
        properties.append("<w:b/>")
    if italic:
        properties.append("<w:i/>")
    if size:
        properties.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(properties)}</w:rPr>" if properties else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{html.escape(text or "")}</w:t></w:r>'


def _w_para(
    text: str,
    *,
    style: str = "",
    keep_next: bool = False,
    keep_lines: bool = False,
    indent: int = 0,
    bold_prefix: str = "",
    italic: bool = False,
) -> str:
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if keep_next:
        ppr.append("<w:keepNext/>")
    if keep_lines:
        ppr.append("<w:keepLines/>")
    ppr.append("<w:widowControl/>")
    if indent:
        ppr.append(f'<w:ind w:left="{indent}"/>')
    runs = ""
    remainder = text
    if bold_prefix and text.startswith(bold_prefix):
        runs += _w_run(bold_prefix, bold=True)
        remainder = text[len(bold_prefix):]
    runs += _w_run(remainder, italic=italic)
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{runs}</w:p>"


def _w_cell(text: str, *, fill: str = "", bold: bool = False) -> str:
    shading = f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>' if fill else ""
    return (
        "<w:tc><w:tcPr><w:tcW w:w=\"0\" w:type=\"auto\"/>"
        f"{shading}<w:vAlign w:val=\"top\"/></w:tcPr>"
        f"{_w_para(text, keep_lines=True, bold_prefix=text if bold else '')}</w:tc>"
    )


def _w_table(headers: list[str], rows: list[list[str]]) -> str:
    border = '<w:tblBorders><w:top w:val="single" w:sz="4" w:color="AAB2BD"/><w:left w:val="single" w:sz="4" w:color="AAB2BD"/><w:bottom w:val="single" w:sz="4" w:color="AAB2BD"/><w:right w:val="single" w:sz="4" w:color="AAB2BD"/><w:insideH w:val="single" w:sz="4" w:color="D5D8DC"/><w:insideV w:val="single" w:sz="4" w:color="D5D8DC"/></w:tblBorders>'
    table_rows = [
        '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>'
        + "".join(_w_cell(value, fill="EAF2F8", bold=True) for value in headers)
        + "</w:tr>"
    ]
    for row in rows:
        columns = max(1, len(headers))
        approximate_chars_per_line = max(10, 78 // columns)
        estimated_lines = max(
            sum(
                max(1, (len(part) + approximate_chars_per_line - 1) // approximate_chars_per_line)
                for part in str(value).splitlines() or [""]
            )
            for value in row
        ) if row else 1
        row_properties = "<w:cantSplit/>" if estimated_lines <= 36 else ""
        table_rows.append(
            f'<w:tr><w:trPr>{row_properties}</w:trPr>'
            + "".join(_w_cell(value) for value in row)
            + "</w:tr>"
        )
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblLayout w:type="autofit"/>'
        f"{border}<w:tblCellMar><w:top w:w=\"90\" w:type=\"dxa\"/><w:left w:w=\"90\" w:type=\"dxa\"/><w:bottom w:w=\"90\" w:type=\"dxa\"/><w:right w:w=\"90\" w:type=\"dxa\"/></w:tblCellMar></w:tblPr>"
        + "".join(table_rows)
        + "</w:tbl>"
    )


def _w_callout(items: list[str]) -> str:
    border = '<w:tblBorders><w:top w:val="single" w:sz="10" w:color="5D6D7E"/><w:left w:val="single" w:sz="10" w:color="5D6D7E"/><w:bottom w:val="single" w:sz="10" w:color="5D6D7E"/><w:right w:val="single" w:sz="10" w:color="5D6D7E"/><w:insideH w:val="nil"/><w:insideV w:val="nil"/></w:tblBorders>'
    rows = [
        '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
        + _w_cell("General Approach", fill="D6EAF8", bold=True)
        + "</w:tr>"
    ]
    for item in items:
        rows.append('<w:tr><w:trPr><w:cantSplit/></w:trPr>' + _w_cell(item, fill="EBF5FB") + "</w:tr>")
    return (
        '<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblLayout w:type="autofit"/>'
        f"{border}<w:tblCellMar><w:top w:w=\"120\" w:type=\"dxa\"/><w:left w:w=\"160\" w:type=\"dxa\"/><w:bottom w:w=\"120\" w:type=\"dxa\"/><w:right w:w=\"160\" w:type=\"dxa\"/></w:tblCellMar></w:tblPr>"
        + "".join(rows)
        + "</w:tbl>"
    )


def _solution_book_document_xml(book: dict[str, Any]) -> str:
    body = [_w_para(str(book.get("title") or "Solution Book"), style="Title", keep_next=True)]
    for group in book.get("question_groups", []):
        body.append(_w_para(str(group.get("group_title") or "Question group"), style="Heading1", keep_next=True))
        for number, question in enumerate(group.get("questions", []), 1):
            question_id = str(question.get("question_id") or number)
            body.append(_w_para(f"Question {question_id}", style="Heading2", keep_next=True))
            body.append(_w_para(str(question.get("question") or ""), keep_lines=True))
            for subpart in question.get("subparts", []):
                locator = str(subpart.get("label") or "")
                prompt = str(subpart.get("prompt") or "")
                body.append(_w_para(f"{locator} {prompt}".strip(), indent=360, italic=True))
            body.append(_w_para("Worked solution", style="Heading3", keep_next=True))
            for step_index, step in enumerate(question.get("reasoning_chain", []), 1):
                locator = f"[{step.get('locator')}] " if step.get("locator") else ""
                body.append(_w_para(f"{step_index}. {locator}{step.get('text') or ''}", keep_lines=True))
            for formula in question.get("formulas", []):
                body.append(_w_table(["Formula"], [[str(formula)]]))
            for table in question.get("tables", []):
                if table.get("title"):
                    body.append(_w_para(str(table["title"]), style="Heading3", keep_next=True))
                body.append(_w_table(table.get("headers", []), table.get("rows", [])))
            if question.get("final_answer"):
                body.append(_w_para(f"Final answer. {question['final_answer']}", keep_lines=True, bold_prefix="Final answer. "))
            source_refs = question.get("source_refs") or []
            if source_refs:
                rendered_refs = []
                for ref in source_refs:
                    if isinstance(ref, dict):
                        rendered_refs.append("; ".join(str(ref.get(key) or "") for key in ("source_name", "locator") if ref.get(key)))
                    else:
                        rendered_refs.append(str(ref))
                body.append(_w_para("Sources: " + "; ".join(item for item in rendered_refs if item), italic=True))
        if group.get("general_approach"):
            body.append(_w_callout([str(item) for item in group["general_approach"]]))
    section = (
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1417" w:right="1417" w:bottom="1417" w:left="1417" w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="708"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(body)}{section}</w:body></w:document>"
    )


def _solution_book_styles_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:eastAsia="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/></w:rPr></w:rPrDefault>'
        '<w:pPrDefault><w:pPr><w:spacing w:after="140" w:line="276" w:lineRule="auto"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:jc w:val="center"/><w:keepNext/><w:spacing w:before="120" w:after="300"/></w:pPr><w:rPr><w:b/><w:sz w:val="36"/><w:szCs w:val="36"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="280" w:after="140"/></w:pPr><w:rPr><w:b/><w:color w:val="1F4E79"/><w:sz w:val="30"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="220" w:after="100"/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="160" w:after="80"/></w:pPr><w:rPr><w:b/><w:sz w:val="22"/></w:rPr></w:style>'
        '</w:styles>'
    )


def write_solution_book_docx(path: Path, book: dict[str, Any]) -> dict[str, Any]:
    book = _as_solution_book(book)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/></Types>',
        )
        zf.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
        )
        zf.writestr(
            "word/_rels/document.xml.rels",
            '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/></Relationships>',
        )
        zf.writestr("word/document.xml", _solution_book_document_xml(book))
        zf.writestr("word/styles.xml", _solution_book_styles_xml())
        zf.writestr(
            "word/settings.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat><w:doNotAutoCompressPictures/></w:settings>',
        )
    with zipfile.ZipFile(path) as zf:
        corrupt = zf.testzip()
        required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml"}
        missing = sorted(required - set(zf.namelist()))
    if corrupt or missing:
        raise ValueError(f"invalid DOCX package: corrupt={corrupt!r}, missing={missing}")
    return {"zip_valid": True, "required_parts_present": True}


def _pdf_font_file() -> Path | None:
    candidates = (
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    )
    return next((path for path in candidates if path.exists()), None)


class _SolutionBookPDF:
    def __init__(self, fitz_module: Any, title: str):
        self.fitz = fitz_module
        self.document = fitz_module.open()
        self.width, self.height = fitz_module.paper_size("a4")
        self.left = 54.0
        self.right = self.width - 54.0
        self.top = 54.0
        self.bottom = self.height - 54.0
        self.page = None
        self.y = self.top
        self.font_path = _pdf_font_file()
        self.font_name = "SolutionBookFont" if self.font_path else "helv"
        self.font = fitz_module.Font(fontfile=str(self.font_path)) if self.font_path else fitz_module.Font("helv")
        self.audit = {
            "orphan_titles": 0,
            "clipped_blocks": 0,
            "page_breaks": 0,
            "general_approach_callouts": 0,
            "general_approach_box_fragments": 0,
        }
        self.title = title
        self._new_page()

    def _new_page(self) -> None:
        if self.page is not None:
            self.audit["page_breaks"] += 1
        self.page = self.document.new_page(width=self.width, height=self.height)
        if self.font_path:
            self.page.insert_font(fontname=self.font_name, fontfile=str(self.font_path))
        self.y = self.top

    def _line_width(self, text: str, size: float) -> float:
        return float(self.font.text_length(text, fontsize=size))

    def _wrap(self, text: str, width: float, size: float) -> list[str]:
        text = re.sub(r"\s+", " ", str(text or "")).strip()
        if not text:
            return [""]
        lines: list[str] = []
        current = ""
        for word in text.split(" "):
            candidate = word if not current else f"{current} {word}"
            if self._line_width(candidate, size) <= width:
                current = candidate
                continue
            if current:
                lines.append(current)
                current = ""
            while word and self._line_width(word, size) > width:
                cut = max(1, len(word) - 1)
                while cut > 1 and self._line_width(word[:cut], size) > width:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            current = word
        if current:
            lines.append(current)
        return lines or [""]

    def _ensure(self, height: float) -> None:
        if self.y + height > self.bottom:
            self._new_page()

    def add_gap(self, points: float) -> None:
        if self.y + points > self.bottom:
            self._new_page()
        else:
            self.y += points

    def add_heading(self, text: str, *, size: float, level: int) -> None:
        leading = size * 1.25
        lines = self._wrap(text, self.right - self.left, size)
        height = len(lines) * leading + 5
        self._ensure(height + 22)
        color = (0.12, 0.31, 0.47) if level <= 1 else (0.12, 0.12, 0.12)
        for line in lines:
            self.page.insert_text((self.left, self.y + size), line, fontsize=size, fontname=self.font_name, color=color)
            self.y += leading
        self.y += 5

    def add_paragraph(self, text: str, *, size: float = 10.5, indent: float = 0, italic: bool = False) -> None:
        del italic  # Built-in layout uses one embedded face; indentation still distinguishes locator text.
        x = self.left + indent
        leading = size * 1.38
        lines = self._wrap(text, self.right - x, size)
        self._ensure(leading)
        if len(lines) > 1 and self.bottom - self.y < 2 * leading:
            self._new_page()
        index = 0
        while index < len(lines):
            capacity = max(1, int((self.bottom - self.y) // leading))
            remaining = len(lines) - index
            if remaining > capacity and remaining - capacity == 1 and capacity > 1:
                capacity -= 1
            for line in lines[index:index + capacity]:
                self.page.insert_text((x, self.y + size), line, fontsize=size, fontname=self.font_name, color=(0.08, 0.08, 0.08))
                self.y += leading
            index += capacity
            if index < len(lines):
                self._new_page()
        self.y += 4

    def add_box(self, text: str, *, label: str = "", fill: tuple[float, float, float] = (0.94, 0.97, 0.99)) -> int:
        full_text = f"{label}{text}" if label else text
        size = 10.0
        leading = 13.5
        padding = 8.0
        lines = self._wrap(full_text, self.right - self.left - 2 * padding, size)
        index = 0
        box_count = 0
        while index < len(lines):
            max_lines = max(1, int((self.bottom - self.top - 2 * padding) // leading))
            chunk = lines[index:index + max_lines]
            height = len(chunk) * leading + 2 * padding
            self._ensure(height)
            rect = self.fitz.Rect(self.left, self.y, self.right, self.y + height)
            self.page.draw_rect(rect, color=(0.36, 0.43, 0.49), fill=fill, width=0.8)
            box_count += 1
            cursor = self.y + padding
            for line in chunk:
                self.page.insert_text((self.left + padding, cursor + size), line, fontsize=size, fontname=self.font_name, color=(0.08, 0.08, 0.08))
                cursor += leading
            self.y += height + 4
            index += len(chunk)
            if index < len(lines):
                self._new_page()
        return box_count

    def add_table(self, headers: list[str], rows: list[list[str]]) -> None:
        if not headers:
            return
        columns = len(headers)
        column_width = (self.right - self.left) / columns
        size = 8.5
        leading = 11.0
        padding = 4.0

        def wrapped_row(values: list[str]) -> list[list[str]]:
            return [self._wrap(value, column_width - 2 * padding, size) for value in values]

        header_lines = wrapped_row(headers)
        header_line_count = max(len(lines) for lines in header_lines)
        header_height = header_line_count * leading + 2 * padding
        minimum_data_height = leading + 2 * padding if rows else 0
        if self.y + header_height + minimum_data_height > self.bottom:
            self._new_page()

        def draw_cells(
            line_sets: list[list[str]],
            start: int,
            count: int,
            *,
            header: bool = False,
        ) -> None:
            height = count * leading + 2 * padding
            for column, lines in enumerate(line_sets):
                x0 = self.left + column * column_width
                rect = self.fitz.Rect(x0, self.y, x0 + column_width, self.y + height)
                self.page.draw_rect(
                    rect,
                    color=(0.67, 0.70, 0.74),
                    fill=(0.91, 0.95, 0.98) if header else (1, 1, 1),
                    width=0.5,
                )
                cursor = self.y + padding
                for line in lines[start:start + count]:
                    self.page.insert_text(
                        (x0 + padding, cursor + size),
                        line,
                        fontsize=size,
                        fontname=self.font_name,
                        color=(0.08, 0.08, 0.08),
                    )
                    cursor += leading
            self.y += height

        def draw_header() -> None:
            if self.y + header_height > self.bottom:
                self._new_page()
            draw_cells(header_lines, 0, header_line_count, header=True)

        draw_header()
        full_page_data_capacity = max(
            1,
            int((self.bottom - self.top - header_height - 2 * padding) // leading),
        )
        for row in rows:
            row = (row + [""] * columns)[:columns]
            lines = wrapped_row(row)
            row_line_count = max(len(item) for item in lines)
            oversized = row_line_count > full_page_data_capacity
            start = 0
            while start < row_line_count:
                available = int((self.bottom - self.y - 2 * padding) // leading)
                remaining = row_line_count - start
                if available <= 0 or (not oversized and remaining > available):
                    self._new_page()
                    draw_header()
                    available = int((self.bottom - self.y - 2 * padding) // leading)
                chunk_count = min(max(1, available), remaining)
                draw_cells(lines, start, chunk_count)
                start += chunk_count
                if start < row_line_count:
                    self._new_page()
                    draw_header()
        self.y = min(self.bottom, self.y + 6)

    def finish(self, path: Path) -> dict[str, Any]:
        for page_number, page in enumerate(self.document, 1):
            footer = f"{page_number}"
            page.insert_text((self.width / 2 - 3, self.height - 25), footer, fontsize=8, fontname=self.font_name, color=(0.35, 0.35, 0.35))
        self.document.set_metadata({"title": self.title, "subject": "Solution Book", "author": "Everything Exam Preparation"})
        self.document.save(str(path), garbage=4, deflate=True)
        page_count = len(self.document)
        self.document.close()
        return {**self.audit, "page_count": page_count, "pdf_valid": path.read_bytes().startswith(b"%PDF-")}


def write_solution_book_pdf(path: Path, book: dict[str, Any]) -> dict[str, Any]:
    try:
        import fitz
    except ImportError as exc:  # pragma: no cover - dependency contract is checked in packaging.
        raise RuntimeError("PyMuPDF is required to generate a real PDF") from exc
    book = _as_solution_book(book)
    path.parent.mkdir(parents=True, exist_ok=True)
    layout = _SolutionBookPDF(fitz, str(book.get("title") or "Solution Book"))
    layout.add_heading(str(book.get("title") or "Solution Book"), size=20, level=0)
    for group in book.get("question_groups", []):
        layout.add_heading(str(group.get("group_title") or "Question group"), size=15, level=1)
        for number, question in enumerate(group.get("questions", []), 1):
            layout.add_heading(f"Question {question.get('question_id') or number}", size=12.5, level=2)
            layout.add_paragraph(str(question.get("question") or ""))
            for subpart in question.get("subparts", []):
                layout.add_paragraph(f"{subpart.get('label') or ''} {subpart.get('prompt') or ''}".strip(), indent=14, italic=True)
            layout.add_heading("Worked solution", size=11, level=3)
            for step_index, step in enumerate(question.get("reasoning_chain", []), 1):
                locator = f"[{step.get('locator')}] " if step.get("locator") else ""
                layout.add_paragraph(f"{step_index}. {locator}{step.get('text') or ''}")
            for formula in question.get("formulas", []):
                layout.add_box(str(formula), label="Formula: ", fill=(0.96, 0.96, 0.96))
            for table in question.get("tables", []):
                if table.get("title"):
                    layout.add_heading(str(table["title"]), size=10.5, level=3)
                layout.add_table(table.get("headers", []), table.get("rows", []))
            if question.get("final_answer"):
                layout.add_box(str(question["final_answer"]), label="Final answer. ", fill=(0.94, 0.97, 0.94))
            source_refs = question.get("source_refs") or []
            if source_refs:
                refs = []
                for ref in source_refs:
                    if isinstance(ref, dict):
                        refs.append("; ".join(str(ref.get(key) or "") for key in ("source_name", "locator") if ref.get(key)))
                    else:
                        refs.append(str(ref))
                layout.add_paragraph("Sources: " + "; ".join(item for item in refs if item), size=8.5)
        if group.get("general_approach"):
            items = [str(item) for item in group["general_approach"]]
            physical_boxes = layout.add_box(
                " • ".join(items),
                label="General Approach: ",
                fill=(0.86, 0.93, 0.97),
            )
            layout.audit["general_approach_callouts"] = int(
                layout.audit.get("general_approach_callouts", 0)
            ) + 1
            layout.audit["general_approach_box_fragments"] = int(
                layout.audit.get("general_approach_box_fragments", 0)
            ) + physical_boxes
    return layout.finish(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_artifact_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip(".-")
    return stem or "solution-book"


def generate_solution_book_artifacts(
    payload: dict[str, Any],
    output_dir: Path,
    basename: str | None = None,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    book = _as_solution_book(payload)
    stem = _safe_artifact_stem(basename or str(payload.get("basename") or payload.get("title") or "solution-book"))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    docx_path = output_dir / f"{stem}.docx"
    pdf_path = output_dir / f"{stem}.pdf"
    manifest_path = output_dir / f"{stem}.manifest.json"
    targets = (docx_path, pdf_path, manifest_path)
    existing = [str(path) for path in targets if path.exists()]
    if existing and not overwrite:
        raise FileExistsError("solution-book artifacts already exist: " + ", ".join(existing))
    if overwrite:
        for path in targets:
            if path.exists():
                path.unlink()
    docx_qa = write_solution_book_docx(docx_path, book)
    pdf_qa = write_solution_book_pdf(pdf_path, book)
    canonical = json.dumps(book, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    artifacts = [
        {
            "format": "docx",
            "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "path": docx_path.name,
            "size_bytes": docx_path.stat().st_size,
            "sha256": _sha256(docx_path),
        },
        {
            "format": "pdf",
            "media_type": "application/pdf",
            "path": pdf_path.name,
            "size_bytes": pdf_path.stat().st_size,
            "sha256": _sha256(pdf_path),
        },
    ]
    invariants = solution_book_invariants(book)
    invariant_failures = sorted(name for name, passed in invariants.items() if not passed)
    model_issues = list(book.get("qa", {}).get("issues", []))
    model_issues.extend(
        {"code": "failed_solution_book_invariant", "invariant": name}
        for name in invariant_failures
    )
    model_status = (
        "ready"
        if book.get("qa", {}).get("status") == "ready" and not invariant_failures
        else "incomplete"
    )
    manifest = {
        "schema_version": SOLUTION_BOOK_SCHEMA_VERSION,
        "task_mode": "solution_book",
        "artifact_set_id": hashlib.sha256(canonical).hexdigest()[:20],
        "title": book.get("title"),
        "public_answer_unit": "major_question",
        "major_question_ids": book.get("public_answer_units", []),
        "group_count": len(book.get("question_groups", [])),
        "major_question_count": len(book.get("public_answer_units", [])),
        "general_approach_count": sum(1 for group in book.get("question_groups", []) if group.get("general_approach")),
        "invariants": invariants,
        "artifacts": artifacts,
        "validation": {
            "model_status": model_status,
            "model_issues": model_issues,
            "docx": docx_qa,
            "pdf": pdf_qa,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "book": book,
        "manifest": manifest,
        "docx_path": str(docx_path),
        "pdf_path": str(pdf_path),
        "manifest_path": str(manifest_path),
    }


def generate_solution_book_batch(
    payload: dict[str, Any] | list[dict[str, Any]],
    output_dir: Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    books = payload.get("books") if isinstance(payload, dict) else payload
    if not isinstance(books, list) or not books:
        raise ValueError("solution-book batch requires a non-empty books list")
    batch_name = _safe_artifact_stem(str(payload.get("batch_name") or "solution-books")) if isinstance(payload, dict) else "solution-books"
    stems = [_safe_artifact_stem(str(book.get("basename") or book.get("title") or f"solution-book-{index}")) for index, book in enumerate(books, 1)]
    if len(stems) != len(set(stems)):
        raise ValueError("solution-book batch contains duplicate artifact basenames")
    output_dir = Path(output_dir)
    batch_manifest_path = output_dir / f"{batch_name}.batch-manifest.json"
    prospective = [output_dir / f"{stem}{suffix}" for stem in stems for suffix in (".docx", ".pdf", ".manifest.json")]
    prospective.append(batch_manifest_path)
    existing = [str(path) for path in prospective if path.exists()]
    if existing and not overwrite:
        raise FileExistsError("solution-book batch artifacts already exist: " + ", ".join(existing))
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="solution-book-batch-", dir=output_dir.parent) as tmpdir:
        staging = Path(tmpdir)
        staged_results = [
            generate_solution_book_artifacts(book, staging, stems[index], overwrite=False)
            for index, book in enumerate(books)
        ]
        batch_manifest = {
            "schema_version": SOLUTION_BOOK_SCHEMA_VERSION,
            "task_mode": "solution_book",
            "batch": True,
            "book_count": len(staged_results),
            "books": [
                {
                    "artifact_set_id": result["manifest"]["artifact_set_id"],
                    "title": result["manifest"]["title"],
                    "manifest_path": Path(result["manifest_path"]).name,
                    "manifest_sha256": _sha256(Path(result["manifest_path"])),
                }
                for result in staged_results
            ],
        }
        staged_batch_manifest = staging / batch_manifest_path.name
        staged_batch_manifest.write_text(json.dumps(batch_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        output_dir.mkdir(parents=True, exist_ok=True)
        for staged_path in sorted(staging.iterdir()):
            target = output_dir / staged_path.name
            if target.exists() and overwrite:
                target.unlink()
            shutil.move(str(staged_path), str(target))
    return {
        "task_mode": "solution_book",
        "batch": True,
        "book_count": len(books),
        "batch_manifest_path": str(batch_manifest_path),
        "artifact_paths": [str(path) for path in prospective if path != batch_manifest_path] + [str(batch_manifest_path)],
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


def load_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalized_provenance(item: dict[str, Any]) -> dict[str, Any]:
    nested = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    return {
        "source_id": nested.get("source_id") or item.get("source_id"),
        "source_name": nested.get("source_name") or item.get("source_name"),
        "locator": nested.get("locator") or item.get("locator"),
        "page_number": nested.get("page_number") or item.get("page_number"),
        "slide_number": nested.get("slide_number") or item.get("slide_number"),
        "time_offset_seconds": nested.get("time_offset_seconds") or item.get("time_offset_seconds"),
        "time_range": nested.get("time_range") or item.get("time_range"),
    }


def unit_labels(fragment: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for candidate in fragment.get("knowledge_unit_candidates", []) or []:
        if isinstance(candidate, dict) and candidate.get("label"):
            labels.append(str(candidate["label"]).strip())
    for role in fragment.get("knowledge_roles", []) or []:
        label = str(role).strip().replace("_", " ")
        if label:
            labels.append(label)
    if not labels:
        preview = re.sub(r"\s+", " ", str(fragment.get("text") or "")).strip()
        if preview:
            labels.append(preview[:120])
    unique_labels: list[str] = []
    seen: set[str] = set()
    for label in labels:
        key = label.casefold()
        if key not in seen:
            seen.add(key)
            unique_labels.append(label)
    return unique_labels


def build_assessment_blueprint(
    source_fragments: list[dict[str, Any]],
    relevant_memory: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    units: dict[str, dict[str, Any]] = {}
    for fragment in source_fragments:
        provenance = normalized_provenance(fragment)
        for label in unit_labels(fragment):
            record = units.setdefault(label.casefold(), {
                "knowledge_unit": label,
                "source_occurrences": 0,
                "provenance": [],
            })
            record["source_occurrences"] += 1
            if provenance not in record["provenance"]:
                record["provenance"].append(provenance)
    ordered = sorted(units.values(), key=lambda item: (-int(item["source_occurrences"]), str(item["knowledge_unit"])))
    memory_units: list[str] = []
    for memory in relevant_memory or []:
        for key in ("weaknesses", "weakness_history", "knowledge_units"):
            value = memory.get(key)
            if isinstance(value, list):
                for unit in value:
                    label = str(unit.get("knowledge_unit") if isinstance(unit, dict) else unit).strip()
                    if label and label not in memory_units:
                        memory_units.append(label)
    return {
        "type": "assessment_blueprint",
        "coverage_basis": "source_fragment_occurrence",
        "knowledge_units": ordered,
        "student_priority_units": memory_units,
        "provenance_fields": ["source_name", "locator", "page_number", "slide_number", "time_offset_seconds", "time_range"],
    }


NEGATION_CUES = {
    "not",
    "no",
    "never",
    "neither",
    "nor",
    "without",
    "cannot",
    "cant",
    "doesnt",
    "dont",
    "isnt",
    "arent",
    "wasnt",
    "werent",
    "fails",
    "failed",
    "lack",
    "lacks",
    "lacking",
}
EVALUATION_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


def _evaluation_token(value: str) -> str:
    token = value.casefold().replace("’", "'")
    token = re.sub(r"[^a-z0-9]+", "", token)
    if len(token) > 6 and token.endswith("ation"):
        return token[:-5] + "ate"
    if len(token) > 5 and token.endswith("ating"):
        return token[:-3] + "e"
    if len(token) > 5 and token.endswith("ated"):
        return token[:-1]
    if len(token) > 5 and token.endswith("ates"):
        return token[:-1]
    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _evaluation_tokens(value: str, keep_negation: bool = True) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?", value or "")
    tokens = [_evaluation_token(item) for item in raw]
    excluded = EVALUATION_STOPWORDS if keep_negation else EVALUATION_STOPWORDS | NEGATION_CUES | {"only"}
    return [item for item in tokens if item and item not in excluded]


def _answer_clauses(answer: str) -> list[str]:
    clauses = re.split(
        r"(?<=[.!?;])\s+|\b(?:but|however|whereas|although|yet)\b",
        re.sub(r"\s+", " ", answer or "").strip(),
        flags=re.I,
    )
    return [item.strip(" ,;:") for item in clauses if item.strip(" ,;:")]


def _is_negated(tokens: list[str], positions: list[int]) -> bool:
    if not positions:
        return False
    for position in positions:
        start = max(0, position - 2)
        for index in range(start, position):
            token = tokens[index]
            if token == "not" and index + 1 < len(tokens) and tokens[index + 1] == "only":
                continue
            if token in NEGATION_CUES:
                return True
    return False


def _alias_clause_evidence(clause: str, alias: str) -> dict[str, Any]:
    clause_tokens = _evaluation_tokens(clause)
    alias_tokens = _evaluation_tokens(alias, keep_negation=False)
    if not alias_tokens:
        return {"coverage": 0.0, "negated": False, "excerpt": clause}
    positions: list[int] = []
    search_from = 0
    for token in alias_tokens:
        position = next(
            (index for index in range(search_from, len(clause_tokens)) if clause_tokens[index] == token),
            None,
        )
        if position is None:
            continue
        positions.append(position)
        search_from = position + 1
    coverage = len(positions) / len(alias_tokens)
    return {
        "coverage": round(coverage, 4),
        "negated": _is_negated(clause_tokens, positions) if positions else False,
        "excerpt": clause[:360],
    }


def _as_text_list(value: Any) -> list[str]:
    values = value if isinstance(value, list) else ([] if value in (None, "") else [value])
    return [str(item).strip() for item in values if str(item).strip()]


def _concept_definitions(raw: dict[str, Any], label: str) -> list[dict[str, Any]]:
    supplied = raw.get("concepts") or raw.get("required_concepts")
    concepts: list[dict[str, Any]] = []
    if isinstance(supplied, list) and supplied:
        for item in supplied:
            if isinstance(item, dict):
                concept_label = str(item.get("label") or item.get("concept") or item.get("text") or "").strip()
                aliases = _as_text_list(item.get("aliases") or item.get("terms") or item.get("synonyms") or concept_label)
                polarity = str(item.get("expected_polarity") or raw.get("expected_polarity") or "positive").strip().lower()
            else:
                concept_label = str(item).strip()
                aliases = [concept_label] if concept_label else []
                polarity = str(raw.get("expected_polarity") or "positive").strip().lower()
            if aliases:
                concepts.append({
                    "label": concept_label or aliases[0],
                    "aliases": aliases,
                    "expected_polarity": polarity,
                })
    if concepts:
        return concepts
    aliases = _as_text_list(raw.get("terms") or raw.get("aliases") or raw.get("synonyms") or label)
    inferred_negative = any(
        any(token in NEGATION_CUES for token in _evaluation_tokens(alias))
        for alias in aliases
    )
    return [{
        "label": label,
        "aliases": aliases or [label],
        "expected_polarity": str(raw.get("expected_polarity") or ("negative" if inferred_negative else "positive")).strip().lower(),
    }]


def _evaluate_concept(answer: str, concept: dict[str, Any]) -> dict[str, Any]:
    best: dict[str, Any] = {"coverage": 0.0, "negated": False, "excerpt": ""}
    for clause in _answer_clauses(answer):
        for alias in concept.get("aliases") or []:
            evidence = _alias_clause_evidence(clause, str(alias))
            if evidence["coverage"] > best["coverage"]:
                best = evidence
            elif evidence["coverage"] == best["coverage"] == 1.0 and best["negated"] and not evidence["negated"]:
                best = evidence
    expected_negative = str(concept.get("expected_polarity") or "positive").lower() in {"negative", "negated", "false"}
    if best["coverage"] == 1.0:
        if bool(best["negated"]) == expected_negative:
            status = "supported"
        else:
            status = "contradicted"
    elif best["coverage"] >= 0.5:
        status = "partial"
    else:
        status = "missing"
    return {
        "label": concept.get("label"),
        "status": status,
        "coverage": best["coverage"],
        "negated": best["negated"],
        "evidence_excerpt": best["excerpt"],
    }


def _explicit_phrase_hits(answer: str, phrases: Any) -> list[str]:
    hits: list[str] = []
    for phrase in _as_text_list(phrases):
        if any(
            (
                evidence := _alias_clause_evidence(clause, phrase)
            )["coverage"] == 1.0
            and not evidence["negated"]
            for clause in _answer_clauses(answer)
        ):
            hits.append(phrase)
    return hits


def _criterion_mark_value(raw: dict[str, Any]) -> float | None:
    value = raw.get("marks", raw.get("max_marks", raw.get("points")))
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and value >= 0:
        return float(value)
    if isinstance(value, str) and re.fullmatch(r"\d+(?:\.\d+)?", value.strip()):
        return float(value)
    return None


def _criteria_from_payload(payload: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
    rubric = payload.get("rubric") if isinstance(payload.get("rubric"), dict) else {}
    criteria = payload.get("criteria") or payload.get("expected_concepts")
    if not criteria and rubric:
        criteria = rubric.get("criteria") or rubric.get("expected_concepts")
    if not isinstance(criteria, list):
        raise ValueError("criteria must be a list or a rubric containing a criteria list")
    return criteria, rubric


def evaluate_answer(payload: dict[str, Any]) -> dict[str, Any]:
    answer = str(payload.get("student_answer") or "")
    criteria, rubric = _criteria_from_payload(payload)
    results: list[dict[str, Any]] = []
    for raw in criteria:
        if isinstance(raw, dict):
            criterion_id = str(raw.get("criterion_id") or raw.get("id") or raw.get("label") or "criterion")
            label = str(raw.get("label") or raw.get("expected_concept") or raw.get("text") or criterion_id)
            provenance = raw.get("provenance") or []
            criterion = raw
        else:
            criterion_id = re.sub(r"[^a-z0-9]+", "_", str(raw).casefold()).strip("_") or "criterion"
            label = str(raw)
            provenance = []
            criterion = {"label": label, "terms": [label]}
        concept_results = [
            _evaluate_concept(answer, concept)
            for concept in _concept_definitions(criterion, label)
        ]
        contradiction_hits = _explicit_phrase_hits(
            answer,
            criterion.get("contradictions") or criterion.get("contradictory_concepts"),
        )
        incorrect_hits = _explicit_phrase_hits(
            answer,
            criterion.get("incorrect_concepts") or criterion.get("incorrect_terms"),
        )
        supported = [item for item in concept_results if item["status"] == "supported"]
        partial = [item for item in concept_results if item["status"] == "partial"]
        contradicted = [item for item in concept_results if item["status"] == "contradicted"]
        if contradiction_hits or contradicted:
            status = "contradicted"
        elif concept_results and len(supported) == len(concept_results):
            status = "correct"
        elif supported:
            status = "partial"
        elif incorrect_hits:
            status = "incorrect"
        elif partial:
            status = "partial"
        else:
            status = "missing"
        marks = _criterion_mark_value(criterion)
        results.append({
            "criterion_id": criterion_id,
            "label": label,
            "status": status,
            "concepts": concept_results,
            "supported_concepts": [item["label"] for item in supported],
            "partial_concepts": [item["label"] for item in partial],
            "contradicted_concepts": [item["label"] for item in contradicted],
            "incorrect_evidence": incorrect_hits,
            "contradiction_evidence": contradiction_hits,
            "marks_available": int(marks) if marks is not None and marks.is_integer() else marks,
            "provenance": provenance,
        })
    evidenced = sum(item["status"] in {"correct", "partial", "contradicted", "incorrect"} for item in results)
    mark_values = [item.get("marks_available") for item in results]
    marks_supported = bool(results) and all(isinstance(value, (int, float)) for value in mark_values)
    mark_estimate: float | int | None = None
    mark_possible: float | int | None = None
    mark_basis = "unavailable_without_explicit_criterion_marks"
    if marks_supported:
        default_credit = {
            "correct": 1.0,
            "partial": 0.5,
            "incorrect": 0.0,
            "contradicted": 0.0,
            "missing": 0.0,
        }
        rubric_credit = rubric.get("status_credit") if isinstance(rubric.get("status_credit"), dict) else {}
        awarded = 0.0
        possible = 0.0
        for item in results:
            maximum = float(item["marks_available"])
            credit = rubric_credit.get(item["status"], default_credit[item["status"]])
            try:
                credit_value = min(1.0, max(0.0, float(credit)))
            except (TypeError, ValueError):
                credit_value = default_credit[item["status"]]
            estimate = round(maximum * credit_value, 2)
            item["estimated_mark"] = int(estimate) if estimate.is_integer() else estimate
            awarded += estimate
            possible += maximum
        mark_estimate = round(awarded, 2)
        mark_possible = round(possible, 2)
        if float(mark_estimate).is_integer():
            mark_estimate = int(mark_estimate)
        if float(mark_possible).is_integer():
            mark_possible = int(mark_possible)
        mark_basis = (
            "explicit_criterion_marks_and_rubric_status_credit"
            if rubric_credit
            else "explicit_criterion_marks_with_half_credit_for_partial"
        )
    return {
        "type": "answer_evaluation",
        "task_mode": "practice",
        "status": "ready" if results else "blocked",
        "gaps": [] if results else [{"code": "missing_evaluation_criteria", "detail": "No evaluation criteria were supplied."}],
        "degraded": not bool(results),
        "evaluation_basis": "structured_concept_and_negation_evidence",
        "criteria_count": len(results),
        "addressed_count": evidenced,
        "criterion_coverage": round(evidenced / len(results), 4) if results else None,
        "criteria": results,
        "status_counts": dict(collections.Counter(item["status"] for item in results)),
        "strengths": [item["label"] for item in results if item["status"] == "correct"],
        "revision_priorities": [item["label"] for item in results if item["status"] != "correct"],
        "mark_estimate": mark_estimate,
        "mark_possible": mark_possible,
        "mark_estimate_basis": mark_basis,
        "mark_awarded": None,
    }


def build_timed_practice(blueprint: dict[str, Any], duration_minutes: int) -> dict[str, Any]:
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive")
    units = list(blueprint.get("knowledge_units") or [])
    if not units:
        raise ValueError("assessment blueprint has no knowledge units")
    selected = units[: min(len(units), duration_minutes)]
    base, remainder = divmod(duration_minutes, len(selected))
    cursor = 0
    slots: list[dict[str, Any]] = []
    for index, unit in enumerate(selected):
        minutes = base + (1 if index < remainder else 0)
        start = cursor
        cursor += minutes
        slots.append({
            "order": index + 1,
            "knowledge_unit": unit.get("knowledge_unit"),
            "duration_minutes": minutes,
            "time_provenance": {"start_minute": start, "end_minute": cursor},
            "source_provenance": unit.get("provenance") or [],
        })
    return {
        "type": "timed_practice",
        "duration_minutes": duration_minutes,
        "slots": slots,
    }


def self_test() -> None:
    text = "1. Which of the following is correct? A) x B) y\n2. Explain the mechanism. 10 marks\n3. Practical data: calculate the rate from the graph."
    result = analyze_text(text)
    assert result["detected_mode"] in {"Mixed", "MCQ", "Long Answer"}
    assert result["question_count"] == 3
    assert result["question_only_high_frequency_knowledge_points"]
    assert result["long_answer_analysis_prediction"]
    assert result["practical_worked_solution_questions"]
    addon = build_exam_type_addon(text=text)
    assert addon["document_kind"] == "exam_type_related_addon"
    assert addon["mcq_short_answer_questions"]
    scan = {
        "documents": [
            {"id": "S1", "name": "Lecture 1 Practical", "category": "practice_material", "question_signals": {"has_questions": True, "has_practical_worked_questions": True}},
            {"id": "S2", "name": "Lecture 1 Practical Solutions", "category": "marking_material", "question_signals": {"has_solution_evidence": True}},
            {"id": "S3", "name": "Physics Past Paper", "category": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True}},
        ],
        "fragments": [
            {"source_id": "S1", "source_name": "Lecture 1 Practical", "category": "practice_material", "locator": "chunk 1", "text": text},
            {"source_id": "S2", "source_name": "Lecture 1 Practical Solutions", "category": "marking_material", "locator": "chunk 1", "text": "Use gradient = delta y / delta x. Substitute the data values. Therefore the result has units s-1."},
            {"source_id": "S3", "source_name": "Physics Past Paper", "category": "practice_material", "locator": "page 1", "text": "1. Calculate the field strength and show the derivation."},
        ],
    }
    grouped = build_exam_type_addon(scan=scan)["question_groups_by_lecture_order"]
    assert grouped and grouped[0]["source_name"] == "Lecture 1 Practical"
    practical = build_practical_worked_solutions(scan=scan)
    assert practical["document_kind"] == "practical_worked_solutions_docx"
    assert practical["title"] == "Detailed Worked Solutions"
    assert practical["sections"][0]["blocks"]
    assert practical["sections"][0]["blocks"][0]["verification"]["status"] == "solution evidence matched"
    assert any(block.get("source_name") == "Physics Past Paper" for block in practical["sections"][0]["blocks"])
    assert "question_only_high_frequency_knowledge_points" not in practical
    assert "examiner_habits" not in practical

    matching_scan = {
        "documents": [
            {"id": "L1", "name": "Lecture 1 Membranes", "category": "knowledge_material"},
            {"id": "L2", "name": "Lecture 2 Enzymes", "category": "knowledge_material"},
            {"id": "P1", "name": "Past Paper", "category": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True}},
        ],
        "fragments": [
            {
                "source_id": "L1",
                "source_name": "Lecture 1 Membranes",
                "category": "knowledge_material",
                "locator": "slide 4",
                "text": "Membrane potential depends on sodium conductance, potassium conductance, resting gradient, and ion permeability.",
                "knowledge_unit_candidates": [{"label": "Membrane potential and sodium conductance"}],
            },
            {
                "source_id": "L2",
                "source_name": "Lecture 2 Enzymes",
                "category": "knowledge_material",
                "locator": "slide 8",
                "text": "Enzyme kinetics uses substrate concentration, Michaelis constant, reaction velocity, inhibition, and catalytic turnover.",
                "knowledge_unit_candidates": [{"label": "Enzyme kinetics and substrate velocity"}],
            },
            {
                "source_id": "P1",
                "source_name": "Past Paper",
                "category": "practice_material",
                "locator": "page 2",
                "text": "\n".join([
                    "1. Describe sodium conductance and membrane potential gradient in a resting membrane.",
                    "2. Explain substrate concentration and enzyme velocity in Michaelis kinetics.",
                    "3. Explain membrane potential and enzyme kinetics substrate velocity.",
                    "4. Outline sodium channel refractory timing in an action potential.",
                ]),
            },
        ],
    }
    target_question = "Explain how membrane potential depends on sodium conductance and resting gradient."
    target_record = target_question_record(target_question)
    target_match = match_question_to_knowledge_unit(target_record, lecture_knowledge_units_from_scan(matching_scan))
    assert target_match and target_match["unit"]["label"] == "Membrane potential and sodium conductance"
    same_point = strict_same_knowledge_point_questions(target_question, matching_scan)
    returned_questions = [item["question"] for item in same_point["same_knowledge_point_questions"]]
    assert same_point["match_status"] == "strict_match"
    assert any("resting membrane" in question for question in returned_questions)
    assert not any("refractory" in question for question in returned_questions)
    solver_pack = build_question_solver_pack(target_question, matching_scan)
    assert solver_pack["document_kind"] == "question_solution_report"
    assert solver_pack["matching_knowledge"]["unit_label"] == "Membrane potential and sodium conductance"

    organized = organize_questions_by_lecture_order(matching_scan)
    assert organized["document_kind"] == "organized_questions_docx"
    lecture_orders = [section["lecture_order"] for section in organized["sections"] if section["lecture_order"] is not None]
    assert lecture_orders == sorted(lecture_orders)
    latest_section = next(section for section in organized["sections"] if section["knowledge_unit"] == "Enzyme kinetics and substrate velocity")
    assert any("membrane potential and enzyme kinetics" in item["question"] for item in latest_section["questions"])

    with tempfile.TemporaryDirectory() as tmpdir:
        out_docx = Path(tmpdir) / "organized_questions.docx"
        write_organized_questions_docx(out_docx, organized)
        assert out_docx.exists() and out_docx.stat().st_size > 0
        with zipfile.ZipFile(out_docx) as zf:
            assert "word/document.xml" in zf.namelist()
            xml = zf.read("word/document.xml").decode("utf-8")
            assert "Describe sodium conductance" in xml
            assert "final answer" not in xml.lower()
    blueprint = build_assessment_blueprint([{
        "source_id": "S1",
        "source_name": "Lecture 1.pdf",
        "page_number": 4,
        "knowledge_unit_candidates": [{"label": "Signal transduction"}],
        "text": "Signal transduction uses receptor activation.",
    }, {
        "source_id": "S2",
        "source_name": "Lecture 2.pptx",
        "slide_number": 8,
        "knowledge_unit_candidates": [{"label": "Signal transduction"}],
        "text": "Receptor activation continues.",
    }])
    assert blueprint["knowledge_units"][0]["source_occurrences"] == 2
    evaluation = evaluate_answer({
        "student_answer": "Receptor activation initiates the pathway.",
        "criteria": [
            {"label": "Receptor activation", "terms": ["receptor activation"]},
            {"label": "Kinase cascade", "terms": ["kinase cascade"]},
        ],
    })
    assert evaluation["criterion_coverage"] == 0.5
    assert "Kinase cascade" in evaluation["revision_priorities"]
    assert [item["status"] for item in evaluation["criteria"]] == ["correct", "missing"]
    assert evaluation["mark_estimate"] is None
    assert evaluation["mark_awarded"] is None

    semantic_evaluation = evaluate_answer({
        "student_answer": (
            "Activation of the receptor initiates signalling. "
            "Receptor activation does not initiate the kinase cascade. "
            "A phosphatase cascade is the only downstream response. "
            "The revolution example is unrelated."
        ),
        "criteria": [
            {
                "label": "Receptor signalling sequence",
                "concepts": [
                    {"label": "Receptor activation", "aliases": ["receptor activation"]},
                    {"label": "Kinase cascade", "aliases": ["kinase cascade"]},
                ],
                "marks": 4,
            },
            {
                "label": "Activation initiates kinase signalling",
                "terms": ["receptor activation initiates kinase cascade"],
                "marks": 2,
            },
            {
                "label": "Correct downstream enzyme class",
                "terms": ["kinase cascade"],
                "incorrect_concepts": ["phosphatase cascade"],
                "marks": 2,
            },
            {
                "label": "Ion",
                "terms": ["ion"],
                "marks": 1,
            },
        ],
    })
    assert semantic_evaluation["criteria"][0]["status"] == "contradicted"
    assert semantic_evaluation["criteria"][1]["status"] == "contradicted"
    assert semantic_evaluation["criteria"][2]["status"] == "contradicted"
    assert semantic_evaluation["criteria"][3]["status"] == "missing"
    assert semantic_evaluation["mark_estimate"] == 0
    assert semantic_evaluation["mark_possible"] == 9

    incorrect_evaluation = evaluate_answer({
        "student_answer": "The downstream response is a phosphatase cascade.",
        "criteria": [{
            "label": "Kinase cascade",
            "terms": ["kinase cascade"],
            "incorrect_concepts": ["phosphatase cascade"],
        }],
    })
    assert incorrect_evaluation["criteria"][0]["status"] == "incorrect"

    partial_evaluation = evaluate_answer({
        "student_answer": "Receptor activation occurs.",
        "rubric": {
            "criteria": [{
                "label": "Receptor activation and kinase cascade",
                "concepts": ["receptor activation", "kinase cascade"],
                "marks": 4,
            }],
            "status_credit": {"partial": 0.25},
        },
    })
    assert partial_evaluation["criteria"][0]["status"] == "partial"
    assert partial_evaluation["mark_estimate"] == 1
    assert partial_evaluation["mark_estimate_basis"] == "explicit_criterion_marks_and_rubric_status_credit"

    reversed_relation = evaluate_answer({
        "student_answer": "The kinase cascade initiates receptor activation.",
        "criteria": [{
            "label": "Activation initiates kinase signalling",
            "terms": ["receptor activation initiates kinase cascade"],
        }],
    })
    assert reversed_relation["criteria"][0]["status"] != "correct"

    unrelated_negation = evaluate_answer({
        "student_answer": "Receptor activation does not inhibit signalling and initiates the kinase cascade.",
        "criteria": [{
            "label": "Activation initiates kinase signalling",
            "terms": ["receptor activation initiates kinase cascade"],
        }],
    })
    assert unrelated_negation["criteria"][0]["status"] == "correct"
    timed = build_timed_practice(blueprint, 20)
    assert sum(item["duration_minutes"] for item in timed["slots"]) == 20
    solution_payload = {
        "title": "Mechanisms Solution Book",
        "question_groups": [{
            "group_id": "membrane-mechanisms",
            "group_title": "Membrane mechanisms",
            "questions": [{
                "question_id": "Q1",
                "question": "Explain how selective permeability establishes membrane potential.",
                "subparts": [
                    {"label": "(a)", "prompt": "Identify the main gradient."},
                    {"label": "(b)", "prompt": "Explain the electrical consequence."},
                ],
                "reasoning_chain": [
                    {"locator": "(a)", "text": "Start from the concentration gradient and selective potassium permeability."},
                    {"locator": "(b)", "text": "Ion movement separates charge, so the electrical gradient increasingly opposes diffusion."},
                ],
                "formulas": ["Vm = RT/zF ln([K+]out/[K+]in)"],
                "final_answer": "The potential approaches the equilibrium potential of the most permeable ion.",
            }, {
                "question_id": "Q2",
                "question": "Predict the effect of increasing sodium permeability.",
                "reasoning_chain": ["The membrane potential shifts toward the sodium equilibrium potential."],
                "final_answer": "The membrane depolarises.",
            }],
            "general_approach": ["Identify the dominant permeability, then reason toward the relevant equilibrium potential."],
        }],
    }
    solution_book = build_solution_book(solution_payload)
    assert solution_book["task_mode"] == "solution_book"
    assert solution_book["public_answer_units"] == ["Q1", "Q2"]
    assert solution_book["question_groups"][0]["general_approach"]
    with tempfile.TemporaryDirectory() as tmpdir:
        artifacts = generate_solution_book_artifacts(solution_payload, Path(tmpdir), "mechanisms")
        assert Path(artifacts["docx_path"]).exists()
        assert Path(artifacts["pdf_path"]).read_bytes().startswith(b"%PDF-")
        assert Path(artifacts["manifest_path"]).exists()
        assert artifacts["manifest"]["general_approach_count"] == 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="diagnose")
    parser.add_argument("--input")
    parser.add_argument("--source-scan")
    parser.add_argument("--question")
    parser.add_argument("--memory")
    parser.add_argument("--duration-minutes", type=int)
    parser.add_argument("--out")
    parser.add_argument("--out-docx")
    parser.add_argument("--output-dir")
    parser.add_argument("--basename")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    scan = load_json(args.source_scan) if args.source_scan else None
    text = load_input(args.input, args.source_scan)
    if args.command == "extract-questions":
        result: Any = {"questions": extract_questions(text)}
    elif args.command == "build-addon":
        result = build_exam_type_addon(scan, text)
    elif args.command == "build-practical-worked-solutions":
        result = build_practical_worked_solutions(scan, text)
    elif args.command == "solve-question":
        if not args.question:
            parser.error("solve-question requires --question")
        if not scan:
            parser.error("solve-question requires --source-scan")
        result = build_question_solver_pack(args.question, scan)
    elif args.command == "organize-questions":
        if not scan:
            parser.error("organize-questions requires --source-scan")
        result = organize_questions_by_lecture_order(scan)
        if args.out_docx:
            write_organized_questions_docx(Path(args.out_docx), result)
            result["docx_path"] = args.out_docx
    elif args.command == "build-blueprint":
        fragments = (scan or {}).get("fragments") if scan else load_json(args.input)
        if isinstance(fragments, dict):
            fragments = fragments.get("fragments")
        if not isinstance(fragments, list):
            parser.error("build-blueprint requires --source-scan or --input containing fragments")
        memory = load_json(args.memory) if args.memory else None
        result = build_assessment_blueprint(fragments, memory if isinstance(memory, list) else None)
    elif args.command == "evaluate-answer":
        payload = load_json(args.input)
        if not isinstance(payload, dict):
            parser.error("evaluate-answer requires --input")
        result = evaluate_answer(payload)
    elif args.command == "build-timed-practice":
        blueprint = load_json(args.input)
        if not isinstance(blueprint, dict) or not args.duration_minutes:
            parser.error("build-timed-practice requires --input and --duration-minutes")
        result = build_timed_practice(blueprint, args.duration_minutes)
    elif args.command == "build-solution-book":
        payload = load_json(args.input)
        if not isinstance(payload, dict) or not args.output_dir:
            parser.error("build-solution-book requires --input and --output-dir")
        result = generate_solution_book_artifacts(
            payload,
            Path(args.output_dir),
            args.basename,
            overwrite=args.overwrite,
        )
    elif args.command == "build-solution-book-batch":
        payload = load_json(args.input)
        if not isinstance(payload, (dict, list)) or not args.output_dir:
            parser.error("build-solution-book-batch requires --input and --output-dir")
        result = generate_solution_book_batch(payload, Path(args.output_dir), overwrite=args.overwrite)
    else:
        result = analyze_text(text)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
