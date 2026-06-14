#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
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


def question_mode(question: str) -> str:
    scores = score_modes(question)
    mode = detected_mode(scores)
    return "Short Answer" if mode == "Unknown" and re.search(r"\bdefine\b|\bstate\b|\blist\b", question, flags=re.I) else mode


def question_terms(questions: list[str]) -> list[dict[str, Any]]:
    return frequent_terms("\n".join(questions))


def command_verbs_in_text(text: str) -> list[str]:
    lower = (text or "").lower()
    return [verb for verb in COMMAND_VERBS if re.search(r"\b" + re.escape(verb) + r"\b", lower)]


def has_practical_worked_signal(text: str) -> bool:
    lower = (text or "").lower()
    return any(re.search(r"\b" + re.escape(word) + r"\b", lower) for word in PRACTICAL_WORKED_WORDS)


def question_records_from_text(text: str, source_name: str = "input", source_order: int = 0, locator: str = "text", source_id: str = "") -> list[dict[str, Any]]:
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
            "practical_worked_signal": has_practical_worked_signal(question),
        })
    return records


def question_records_from_scan(scan: dict[str, Any]) -> list[dict[str, Any]]:
    docs = {doc.get("id"): doc for doc in scan.get("documents", [])}
    records: list[dict[str, Any]] = []
    for source_order, frag in enumerate(scan.get("fragments", []), 1):
        source = docs.get(frag.get("source_id"), {})
        category = frag.get("category") or source.get("category")
        question_flags = source.get("question_signals", {})
        if category not in {"practice_material", "marking_material"} and not question_flags.get("has_questions"):
            continue
        records.extend(question_records_from_text(
            str(frag.get("text") or ""),
            source_name=str(frag.get("source_name") or source.get("name") or "source"),
            source_order=source_order,
            locator=str(frag.get("locator") or ""),
            source_id=str(frag.get("source_id") or ""),
        ))
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="diagnose")
    parser.add_argument("--input")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = load_input(args.input, args.source_scan)
    if args.command == "extract-questions":
        result: Any = {"questions": extract_questions(text)}
    elif args.command == "build-addon":
        result = build_exam_type_addon(load_json(args.source_scan) if args.source_scan else None, text)
    elif args.command == "build-practical-worked-solutions":
        result = build_practical_worked_solutions(load_json(args.source_scan) if args.source_scan else None, text)
    else:
        result = analyze_text(text)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
