#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import html
import json
import re
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
PAST_PAPER_WORDS = {"past paper", "mock paper", "official exam", "exam paper", "final examination", "final exam", "paper"}
PRACTICE_ONLY_WORDS = {"practice material", "practice questions", "worksheet", "problem sheet", "revision questions"}


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


def combined_source_text(source: dict[str, Any], frag: dict[str, Any] | None = None) -> str:
    fields = [
        source.get("name"),
        source.get("path"),
        source.get("source_hint"),
        source.get("category"),
    ]
    if frag:
        fields.extend([frag.get("source_name"), frag.get("locator"), frag.get("category")])
    return " ".join(str(field or "") for field in fields).lower()


def is_past_or_mock_source(source: dict[str, Any], frag: dict[str, Any] | None = None) -> bool:
    signals = source.get("question_signals", {}) or {}
    if signals.get("has_past_paper") or signals.get("has_mock_paper") or signals.get("has_official_exam_paper"):
        return True
    source_text = combined_source_text(source, frag)
    if any(word in source_text for word in PAST_PAPER_WORDS):
        return not any(word in source_text for word in PRACTICE_ONLY_WORDS if word != "paper")
    return False


def source_year(record: dict[str, Any]) -> str:
    text = " ".join(str(record.get(key) or "") for key in ("source_name", "locator", "question"))
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return match.group(0) if match else ""


def paper_key(record: dict[str, Any]) -> str:
    year = source_year(record)
    source_name = re.sub(r"\s+", " ", str(record.get("source_name") or "paper")).strip().lower()
    return f"{year}:{source_name}" if year else source_name


def past_paper_question_records_from_scan(scan: dict[str, Any], modes: set[str] | None = None) -> list[dict[str, Any]]:
    docs = {doc.get("id"): doc for doc in scan.get("documents", [])}
    records: list[dict[str, Any]] = []
    for source_order, frag in enumerate(scan.get("fragments", []), 1):
        source = docs.get(frag.get("source_id"), {})
        if not is_past_or_mock_source(source, frag):
            continue
        for record in question_records_from_text(
            str(frag.get("text") or ""),
            source_name=str(frag.get("source_name") or source.get("name") or "source"),
            source_order=source_order,
            locator=str(frag.get("locator") or ""),
            source_id=str(frag.get("source_id") or ""),
        ):
            record["provenance"] = fragment_provenance(frag, source)
            if modes and record.get("mode") not in modes:
                continue
            record["source_year"] = source_year(record)
            record["paper_key"] = paper_key(record)
            records.append(record)
    records.sort(key=lambda item: (item["source_order"], item["question_order"], item.get("subquestion_order") or 0))
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


def direct_exam_demand_signature(record: dict[str, Any]) -> str:
    demand = record.get("question_demand") or []
    if demand:
        return "+".join(str(item).lower() for item in demand[:2])
    mode = str(record.get("mode") or "")
    if mode == "MCQ":
        return "recognize"
    if mode == "Short Answer":
        return "state"
    return "identify"


def first_relevant_sentence(text: str, terms: set[str]) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text or "").strip())
    for sentence in sentences:
        lower = sentence.lower()
        if terms and any(term.lower() in lower for term in terms):
            return sentence[:420].strip()
    return (sentences[0] if sentences else "").strip()[:420]


def normalize_knowledge_title(label: str, terms: set[str]) -> str:
    label = re.sub(r"\s+", " ", label or "").strip()
    if label:
        return label
    if terms:
        return ", ".join(sorted(terms)[:5]).title()
    return "Exam knowledge point"


def annotated_recurrence_records(records: list[dict[str, Any]], units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for record in records:
        match = match_question_to_knowledge_unit(record, units)
        if not match:
            continue
        unit = match["unit"]
        shared_terms = set(match.get("shared_terms") or [])
        if len(shared_terms) < 2:
            continue
        annotated.append({
            "record": record,
            "unit": unit,
            "shared_terms": shared_terms,
            "direct_exam_demand": direct_exam_demand_signature(record),
            "answer_operation_type": record.get("answer_operation_type") or answer_operation_type(str(record.get("question") or ""), str(record.get("mode") or "")),
            "question_pattern": record.get("question_pattern") or question_pattern(str(record.get("question") or ""), str(record.get("mode") or "")),
            "paper_key": record.get("paper_key") or paper_key(record),
            "source_year": record.get("source_year") or source_year(record),
            "mode": record.get("mode"),
        })
    return annotated


def compatible_recurrence_record(cluster: dict[str, Any], item: dict[str, Any]) -> bool:
    if cluster["unit"]["id"] != item["unit"]["id"]:
        return False
    if cluster["direct_exam_demand"] != item["direct_exam_demand"]:
        return False
    if cluster["answer_operation_type"] != item["answer_operation_type"]:
        return False
    return len(set(cluster["terms"]) & set(item["shared_terms"])) >= 2


def cluster_recurrent_exam_points(records: list[dict[str, Any]], units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    for item in annotated_recurrence_records(records, units):
        target: dict[str, Any] | None = None
        for cluster in clusters:
            if compatible_recurrence_record(cluster, item):
                target = cluster
                break
        if target is None:
            target = {
                "unit": item["unit"],
                "lecture_order": item["unit"]["lecture_order"],
                "direct_exam_demand": item["direct_exam_demand"],
                "answer_operation_type": item["answer_operation_type"],
                "question_patterns": set(),
                "terms": set(item["shared_terms"]),
                "records": [],
                "paper_keys": set(),
                "modes": set(),
            }
            clusters.append(target)
        target["records"].append(item["record"])
        target["terms"].update(item["shared_terms"])
        target["paper_keys"].add(item["paper_key"])
        target["modes"].add(item["mode"])
        target["question_patterns"].add(item["question_pattern"])
    recurrent = []
    for cluster in clusters:
        paper_count = len(cluster["paper_keys"])
        if paper_count < 2:
            continue
        level = "strong_recurrent" if paper_count >= 3 or {"MCQ", "Short Answer"} <= set(cluster["modes"]) else "recurrent"
        if len(cluster["question_patterns"]) == 1 and paper_count >= 2:
            level = "recurrent_question_form" if level == "recurrent" else level
        cluster["recurrence_level"] = level
        recurrent.append(cluster)
    recurrent.sort(key=lambda item: (item["lecture_order"], str(item["unit"].get("label") or "")))
    return recurrent


def exam_needed_knowledge_content(cluster: dict[str, Any]) -> str:
    unit = cluster["unit"]
    terms = set(cluster.get("terms") or [])
    title = normalize_knowledge_title(str(unit.get("label") or ""), terms)
    sentence = first_relevant_sentence(str(unit.get("text") or ""), terms)
    if sentence and title.lower() not in sentence.lower():
        return f"{title}: {sentence}"
    return sentence or title


def exam_scope_text(cluster: dict[str, Any]) -> str:
    terms = sorted(set(cluster.get("terms") or []))[:8]
    if not terms:
        return ""
    return "Exam scope: " + ", ".join(terms) + "."


def build_recurrence_sections(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sections: list[dict[str, Any]] = []
    by_lecture: dict[int, list[dict[str, Any]]] = {}
    for cluster in clusters:
        by_lecture.setdefault(int(cluster["lecture_order"]), []).append(cluster)
    for lecture_order in sorted(by_lecture):
        clusters_for_lecture = by_lecture[lecture_order]
        source_name = str(clusters_for_lecture[0]["unit"].get("source_name") or f"Lecture {lecture_order}")
        heading = f"Lecture {lecture_order}: {source_name}"
        blocks = []
        for idx, cluster in enumerate(clusters_for_lecture, 1):
            title = normalize_knowledge_title(str(cluster["unit"].get("label") or ""), set(cluster.get("terms") or []))
            block = {
                "render_mode": "exam_knowledge_point",
                "title": f"{idx}. {title}",
                "content": exam_needed_knowledge_content(cluster),
            }
            scope = exam_scope_text(cluster)
            if scope:
                block["exam_scope"] = scope
            blocks.append(block)
        sections.append({"heading": heading, "blocks": blocks})
    return sections


def build_mcq_saq_recurrence_report(scan: dict[str, Any], route: str = "mixed") -> dict[str, Any]:
    mode_map = {
        "mcq": {"MCQ", "Mixed"},
        "short_answer": {"Short Answer", "Mixed"},
        "mixed": {"MCQ", "Short Answer", "Mixed"},
    }
    modes = mode_map.get(route, mode_map["mixed"])
    records = past_paper_question_records_from_scan(scan, modes=modes)
    units = lecture_knowledge_units_from_scan(scan)
    clusters = cluster_recurrent_exam_points(records, units)
    title_map = {
        "mcq": "MCQ High-Frequency Knowledge Points",
        "short_answer": "Short Answer High-Frequency Knowledge Points",
        "mixed": "MCQ and Short Answer High-Frequency Knowledge Points",
    }
    kind_map = {
        "mcq": "mcq_exam_type_related_addon",
        "short_answer": "short_answer_exam_type_related_addon",
        "mixed": "exam_type_related_addon_docx",
    }
    return {
        "schema_version": 2,
        "document_kind": kind_map.get(route, kind_map["mixed"]),
        "result_only": True,
        "default_language": "English",
        "title": title_map.get(route, title_map["mixed"]),
        "sections": build_recurrence_sections(clusters),
        "_internal_recurrence": [
            {
                "recurrence_level": cluster["recurrence_level"],
                "lecture_order": cluster["lecture_order"],
                "knowledge_unit": cluster["unit"].get("label"),
                "paper_count": len(cluster["paper_keys"]),
                "question_count": len(cluster["records"]),
                "terms": sorted(cluster["terms"]),
                "direct_exam_demand": cluster["direct_exam_demand"],
                "answer_operation_type": cluster["answer_operation_type"],
                "question_patterns": sorted(cluster["question_patterns"]),
            }
            for cluster in clusters
        ],
    }


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

    recurrence_scan = {
        "documents": [
            {"id": "RL1", "name": "Lecture 1 Membranes", "category": "knowledge_material"},
            {"id": "RL2", "name": "Lecture 2 Enzymes", "category": "knowledge_material"},
            {"id": "RP1", "name": "Physiology Past Paper 2022", "category": "practice_material", "question_signals": {"has_questions": True, "has_past_paper": True}},
            {"id": "RP2", "name": "Physiology Mock Paper 2023", "category": "practice_material", "question_signals": {"has_questions": True, "has_mock_paper": True}},
            {"id": "RPR", "name": "Physiology Practice Material", "category": "practice_material", "question_signals": {"has_questions": True}},
        ],
        "fragments": [
            {
                "source_id": "RL1",
                "source_name": "Lecture 1 Membranes",
                "category": "knowledge_material",
                "locator": "slide 3",
                "text": "Resting membrane potential depends on potassium permeability, sodium permeability, and relative ion permeability.",
                "knowledge_unit_candidates": [{"label": "Resting membrane potential and relative permeability"}],
            },
            {
                "source_id": "RL2",
                "source_name": "Lecture 2 Enzymes",
                "category": "knowledge_material",
                "locator": "slide 9",
                "text": "Enzyme velocity depends on substrate concentration and Michaelis constant.",
                "knowledge_unit_candidates": [{"label": "Enzyme velocity and substrate concentration"}],
            },
            {
                "source_id": "RP1",
                "source_name": "Physiology Past Paper 2022",
                "category": "practice_material",
                "locator": "page 1",
                "page_number": 1,
                "provenance": {"source_name": "Physiology Past Paper 2022", "locator": "page 1", "page_number": 1},
                "text": "1. Which of the following describes resting membrane potential and potassium permeability?",
            },
            {
                "source_id": "RP2",
                "source_name": "Physiology Mock Paper 2023",
                "category": "practice_material",
                "locator": "page 1",
                "text": "1. Which of the following describes resting membrane potential and potassium permeability?\n2. (a) State how resting membrane potential depends on potassium permeability. (b) State how resting membrane potential depends on sodium permeability.",
            },
            {
                "source_id": "RPR",
                "source_name": "Physiology Practice Material",
                "category": "practice_material",
                "locator": "worksheet",
                "text": "1. Which of the following describes enzyme velocity and substrate concentration?",
            },
        ],
    }
    past_records = past_paper_question_records_from_scan(recurrence_scan)
    assert all("Practice Material" not in str(record.get("source_name")) for record in past_records)
    assert next(record for record in past_records if record.get("source_name") == "Physiology Past Paper 2022")["provenance"]["page_number"] == 1
    saq_records = past_paper_question_records_from_scan(recurrence_scan, modes={"Short Answer", "Mixed"})
    assert len([record for record in saq_records if record.get("subquestion_order")]) == 2
    mcq_report = build_mcq_saq_recurrence_report(recurrence_scan, "mcq")
    assert mcq_report["document_kind"] == "mcq_exam_type_related_addon"
    assert mcq_report["default_language"] == "English"
    assert mcq_report["sections"]
    rendered_public = json.dumps({"sections": mcq_report["sections"]}, ensure_ascii=False)
    assert "Resting membrane potential and relative permeability" in rendered_public
    assert "enzyme velocity" not in rendered_public.lower()
    assert "source_name" not in rendered_public
    assert "locator" not in rendered_public
    assert "score" not in rendered_public
    assert "frequency" not in rendered_public
    assert mcq_report["_internal_recurrence"][0]["recurrence_level"] in {"recurrent", "recurrent_question_form", "strong_recurrent"}
    assert mcq_report["_internal_recurrence"][0]["paper_count"] == 2
    with tempfile.TemporaryDirectory() as tmpdir:
        out_docx = Path(tmpdir) / "organized_questions.docx"
        write_organized_questions_docx(out_docx, organized)
        assert out_docx.exists() and out_docx.stat().st_size > 0
        with zipfile.ZipFile(out_docx) as zf:
            assert "word/document.xml" in zf.namelist()
            xml = zf.read("word/document.xml").decode("utf-8")
            assert "Describe sodium conductance" in xml
            assert "final answer" not in xml.lower()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="diagnose")
    parser.add_argument("--input")
    parser.add_argument("--source-scan")
    parser.add_argument("--question")
    parser.add_argument("--out")
    parser.add_argument("--out-docx")
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
    elif args.command == "build-mcq-report":
        if not scan:
            parser.error("build-mcq-report requires --source-scan")
        result = build_mcq_saq_recurrence_report(scan, "mcq")
    elif args.command == "build-short-answer-report":
        if not scan:
            parser.error("build-short-answer-report requires --source-scan")
        result = build_mcq_saq_recurrence_report(scan, "short_answer")
    elif args.command == "build-mcq-saq-report":
        if not scan:
            parser.error("build-mcq-saq-report requires --source-scan")
        result = build_mcq_saq_recurrence_report(scan, "mixed")
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
    else:
        result = analyze_text(text)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
