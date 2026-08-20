#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import shutil
import tempfile
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

TEXT_SUFFIXES = {".txt", ".md", ".json", ".yaml", ".yml", ".csv", ".vtt", ".srt"}
MEDIA_PREFIXES = {".docx": "word/media/", ".pptx": "ppt/media/"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".heic"}
OFFICE_SUFFIXES = {".pptx", ".pdf", ".docx"}
ARCHIVE_SUFFIXES = {".zip"}
SUPPORTED_INPUT_SUFFIXES = TEXT_SUFFIXES | OFFICE_SUFFIXES | IMAGE_SUFFIXES | ARCHIVE_SUFFIXES
LECTURE_FILENAME_RE = re.compile(r"(?i)(?:^|[\s_\-])L(?:ecture)?\s*(\d{1,3})(?:\b|[\s_\-])")
PPTX_SLIDE_XML_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")

PRACTICE_KEYWORDS = ["past paper", "practice", "question paper", "exam paper", "answer all questions", "time allowed", "mcq", "sba", "short answer", "essay", "problem sheet"]
STYLE_KEYWORDS = ["model answer", "example answer", "style", "sample essay"]
BOOK_KEYWORDS = ["textbook", "book", "chapter", "edition", "publisher", "recommended reading", "further reading"]
PAPER_KEYWORDS = ["doi", "pmid", "journal", "abstract", "methods", "results", "et al", "primary research", "recent research"]
KNOWLEDGE_KEYWORDS = ["lecture", "slides", "notes", "module", "handbook", "practical", "lab", "seminar", "reading"]
VISUAL_KEYWORDS = ["figure", "fig.", "diagram", "graph", "plot", "table", "chart", "pathway", "scheme", "image", "micrograph"]
QUESTION_KEYWORDS = ["?", "which of the following", "define", "state", "list", "outline", "explain", "compare", "evaluate", "discuss", "calculate", "interpret"]
PRACTICAL_QUESTION_KEYWORDS = ["question", "task", "data", "problem", "calculate", "interpret", "graph", "table", "readout", "control"]
PRACTICAL_WORKED_KEYWORDS = ["calculate", "derive", "show", "estimate", "prove", "data", "problem", "interpret", "graph", "table", "fit", "plot", "uncertainty", "error", "unit"]
ADMIN_BOILERPLATE_KEYWORDS = [
    "attendance", "sign in", "password", "office hour", "email", "assessment deadline",
    "housekeeping", "canvas navigation", "canvas operation", "seats", "mentimeter",
    "submission instruction", "submit your", "submission portal", "upload your assignment",
]
EMBEDDED_AI_INSTRUCTION_KEYWORDS = [
    "ignore previous instructions", "ignore all previous instructions", "system prompt",
    "instructions for ai", "instruction for ai", "instructions for chatgpt",
    "as an ai language model", "tell the ai", "do not reveal this prompt",
]
RIGHTS_OR_CREDIT_KEYWORDS = ["copyright", "licensed under", "creative commons", "photo by", "image by", "source:", "credit:"]
READING_REFERENCE_KEYWORDS = ["reading:", "recommended reading", "further reading", "textbook", "edition", "publisher", "kortext", "doi", "pmid"]
LOW_RELEVANCE_CONTEXT_KEYWORDS = ["sustainable development goals", "environmental awareness", "public awareness", "news article", "policy awareness"]
EXAMPLE_KEYWORDS = ["for example", "e.g.", "case study", "example", "photo by", "image by"]
STRUCTURE_SLIDE_KEYWORDS = [
    "learning objective",
    "learning objectives",
    "intended learning outcome",
    "intended learning outcomes",
    "ilo",
    "ilos",
    "agenda",
    "outline",
    "overview",
    "today's lecture",
    "topic",
    "section",
    "part ",
    "summary",
    "conclusion",
    "recap",
    "take home",
    "key points",
]
DECORATIVE_OR_CREDIT_KEYWORDS = RIGHTS_OR_CREDIT_KEYWORDS
CONTINUATION_KEYWORDS = ["continued", "cont.", "same example", "case study continued", "example continued"]
AUTHOR_YEAR_RE = re.compile(r"\b[A-Z][A-Za-z\-]+\s+et\s+al\.?\s*\(?\d{4}\)?|\b[A-Z][A-Za-z\-]+\s*\(\d{4}\)")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
PMID_RE = re.compile(r"\bPMID\s*:?\s*\d+", re.I)
TIMECODE_RE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?[,.]\d{3})\s*-->\s*(?P<end>\d{1,2}:\d{2}(?::\d{2})?[,.]\d{3})"
)

TASK_MODES = {"atlas", "analysis", "notes", "practice", "essay"}
EXAM_FORMAT_PATTERNS: dict[str, list[str]] = {
    "mcq": [r"\bmcq\b", r"\bmultiple choice\b", r"\bsingle best\b", r"\bwhich of the following\b"],
    "short_answer": [r"\bshort answer\b", r"\bdefine\b", r"\bstate\b", r"\blist\b", r"\boutline\b"],
    "long_answer": [r"\blong answer\b", r"\bexplain\b", r"\bcompare\b", r"\bevaluate\b", r"\bdiscuss\b"],
    "essay": [r"\bessay\b", r"\bcritically\b", r"\bto what extent\b", r"\bthesis\b"],
    "practical_data_problem": [r"\bpractical\b", r"\bdata\b", r"\bcalculate\b", r"\binterpret\b", r"\bgraph\b", r"\btable\b"],
}
ASSESSMENT_CATEGORIES = {"practice_material", "marking_material"}
ASSESSMENT_DURATION_RE = re.compile(
    r"\b(?:"
    r"time\s+allowed|"
    r"(?:assessment|exam(?:ination)?|paper)\s+(?:duration|time\s+allowed)|"
    r"(?:assessment|exam(?:ination)?|paper)\s+(?:lasts?|is\s+scheduled\s+for)"
    r")\s*[:\-=]?\s*(\d+(?:\.\d+)?)\s*(hours?|hrs?|minutes?|mins?)\b",
    re.I,
)
ASSESSMENT_MARK_RE = re.compile(r"\b(\d+)\s*marks?\b", re.I)
ASSESSMENT_WEIGHT_RE = re.compile(
    r"\b("
    r"[A-Za-z][A-Za-z0-9 /&()\-]{1,60}?"
    r"(?:component|assessment|exam(?:ination)?|coursework|paper|section(?:\s+[A-Za-z0-9]+)?|part(?:\s+[A-Za-z0-9]+)?)"
    r")\s*(?::|\-|=)\s*(\d{1,3}(?:\.\d+)?)\s*%",
    re.I,
)

KNOWLEDGE_SIGNAL_PATTERNS: dict[str, list[str]] = {
    "heading_or_topic_boundary": [
        r"^\s*(lecture|topic|section|unit|part|chapter)\b",
        r"^\s*\d+(\.\d+)*\s+[A-Z]",
        r"^\s*[A-Z][A-Za-z0-9 ,:/()\-]{8,80}$",
    ],
    "learning_objective": [
        r"\blearning objectives?\b",
        r"\bby the end\b",
        r"\byou should be able to\b",
        r"\bunderstand\b",
    ],
    "definition": [r"\bis defined as\b", r"\brefers to\b", r"\bmeans\b", r"\bdefinition\b"],
    "mechanism": [r"\bmechanism\b", r"\bpathway\b", r"\bcauses?\b", r"\bleads? to\b", r"\bactivates?\b", r"\binhibits?\b", r"\btherefore\b"],
    "method": [r"\bmethod\b", r"\bprotocol\b", r"\bassay\b", r"\bmeasure\b", r"\bstep\b", r"\bcontrol\b", r"\breadout\b"],
    "comparison": [r"\bcompare\b", r"\bcontrast\b", r"\bversus\b", r"\bwhereas\b", r"\bdifferent from\b", r"\bsimilar to\b"],
    "calculation": [r"\bcalculate\b", r"\bequation\b", r"\bformula\b", r"\brate\b", r"\bEC50\b", r"\bIC50\b", r"=\s*"],
    "data_interpretation": [r"\bgraph\b", r"\bfigure\b", r"\btable\b", r"\bdata\b", r"\btrend\b", r"\binterpret\b"],
    "evidence": [r"\bevidence\b", r"\bresults?\b", r"\bfinding\b", r"\bshown by\b", r"\bdemonstrates?\b", r"\bdoi\b", r"\bpmid\b"],
    "application": [r"\bapplication\b", r"\bclinical\b", r"\bcase\b", r"\bused to\b", r"\bexam\b", r"\banswer\b"],
    "explanatory_example": [r"\bfor example\b", r"\be\.g\.\b", r"\bexample\b", r"\bcase study\b"],
}

ROLE_BY_SIGNAL: dict[str, str] = {
    "heading_or_topic_boundary": "knowledge_unit_boundary",
    "learning_objective": "coverage_target",
    "definition": "concept",
    "mechanism": "mechanism",
    "method": "method",
    "comparison": "comparison",
    "calculation": "calculation",
    "data_interpretation": "data_interpretation",
    "evidence": "evidence",
    "application": "exam_application",
    "explanatory_example": "explanatory_example",
}


def has_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def lecture_order_from_path(path: str | Path) -> int | None:
    match = LECTURE_FILENAME_RE.search(Path(path).stem)
    return int(match.group(1)) if match else None


def is_lecture_source(path: str | Path, text: str = "") -> bool:
    name = Path(path).name.lower().replace("_", " ").replace("-", " ")
    sample = (text or "")[:2500].lower().replace("_", " ").replace("-", " ")
    if Path(path).suffix.lower() in {".pptx", ".pdf", ".docx", ".md", ".txt"} and lecture_order_from_path(path) is not None:
        return True
    lecture_markers = [
        "lecture ",
        "learning objectives",
        "intended learning outcomes",
        "ilos",
        "by the end of this session",
        "by the end of today's lecture",
        "module",
        "slides",
    ]
    module_code = bool(re.search(r"\b[A-Z]{2,5}\s*\d{4,6}\b", text or "", flags=re.I))
    return has_any(name + "\n" + sample, lecture_markers) or module_code


def content_triage(text: str) -> str:
    lower = (text or "").lower()
    signals = set(knowledge_signals(text))
    teaching_signals = {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation", "evidence", "application"}
    if has_any(lower, EMBEDDED_AI_INSTRUCTION_KEYWORDS):
        return "embedded_ai_instruction"
    if has_any(lower, ADMIN_BOILERPLATE_KEYWORDS) and not (signals & teaching_signals):
        return "admin_or_boilerplate"
    if has_any(lower, RIGHTS_OR_CREDIT_KEYWORDS) and not (signals & teaching_signals):
        return "rights_or_credit_context"
    if has_any(lower, READING_REFERENCE_KEYWORDS) and not (signals & {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation"}):
        return "reading_reference"
    if has_any(lower, LOW_RELEVANCE_CONTEXT_KEYWORDS) and not (signals & {"definition", "mechanism", "method", "calculation", "data_interpretation"}):
        return "low_exam_relevance_context"
    if has_any(lower, EXAMPLE_KEYWORDS) and not (signals & {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation"}):
        return "supporting_example"
    return "core_lecture_content"


def notes_obligation(content_role: str) -> str:
    if content_role == "core_lecture_content":
        return "must_cover"
    if content_role == "supporting_example":
        return "compress_if_repetitive"
    if content_role in {"admin_or_boilerplate", "embedded_ai_instruction"}:
        return "exclude_if_verified_non_teaching"
    return "review_before_exclusion"


def notes_obligation_for_slide(content_role: str, triage: dict[str, Any]) -> str:
    if triage.get("manual_review_required"):
        return "review_visual_before_final_decision"
    if triage["slide_decision"] == "exclude":
        return "exclude_with_verified_non_teaching_reason"
    if triage["slide_decision"] == "merge_with_previous":
        return "merge_with_previous_unit"
    if not triage["detailed_explanation_allowed"]:
        return "use_for_structure_no_detailed_explanation"
    return notes_obligation(content_role)


def has_visual_signal(text: str) -> bool:
    lower = (text or "").lower()
    return has_any(lower, VISUAL_KEYWORDS)


def has_question_signal(text: str) -> bool:
    lower = (text or "").lower()
    return has_any(lower, QUESTION_KEYWORDS) or bool(re.search(r"\b(Q\d+|\d+[).]|[a-z][)])\s+", text or "", flags=re.I))


def has_marking_signal(name: str, haystack: str) -> bool:
    return (
        has_any(haystack, ["mark scheme", "markscheme", "answer key", "examiner feedback"])
        or has_any(name, ["mark scheme", "markscheme", "answer key", "answers", "solutions"])
    )


def question_signals(path: Path, text: str, source_hint: str) -> dict[str, Any]:
    name = path.name.lower().replace("_", " ").replace("-", " ")
    parent = str(path.parent).lower().replace("_", " ").replace("-", " ")
    lower = (text or "").lower().replace("_", " ").replace("-", " ")
    haystack = name + "\n" + lower
    is_past_paper = (
        "past papers" in parent
        or has_any(haystack, ["past paper", "question paper", "exam paper", "answer all questions"])
        or ("time allowed" in haystack and "examination" in haystack)
    )
    is_practical = has_any(name, ["practical", "lab", "experiment", "worksheet"]) or has_any(haystack, ["practical task", "practical question", "lab practical", "experiment worksheet"])
    has_questions = has_question_signal(text) or (source_hint == "practice_material" and has_question_signal(haystack))
    has_practical_questions = is_practical and has_questions and has_any(haystack, PRACTICAL_QUESTION_KEYWORDS)
    practical_worked_terms = [word for word in PRACTICAL_WORKED_KEYWORDS if word in haystack]
    has_practical_worked_questions = has_questions and bool(practical_worked_terms) and (is_practical or is_past_paper)
    matched = [word for word in QUESTION_KEYWORDS if word != "?" and word in lower]
    return {
        "has_questions": has_questions,
        "has_past_paper": is_past_paper and has_questions,
        "has_practical_questions": has_practical_questions,
        "has_practical_worked_questions": has_practical_worked_questions,
        "matched_question_terms": unique(matched),
        "matched_practical_worked_terms": unique(practical_worked_terms),
        "has_solution_evidence": source_hint == "marking_material" or (not is_past_paper and has_marking_signal(name, haystack)),
    }


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]*", text or ""))


def normalized_text_signature(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def high_text_overlap(text: str, previous_text: str) -> bool:
    current = normalized_text_signature(text)
    previous = normalized_text_signature(previous_text)
    if not current or not previous:
        return False
    if current == previous:
        return True
    current_tokens = set(current.split())
    previous_tokens = set(previous.split())
    if min(len(current_tokens), len(previous_tokens)) < 5:
        return False
    overlap = len(current_tokens & previous_tokens) / max(1, len(current_tokens | previous_tokens))
    return overlap >= 0.85


def knowledge_signals(text: str) -> list[str]:
    signals: list[str] = []
    for signal, patterns in KNOWLEDGE_SIGNAL_PATTERNS.items():
        if any(re.search(pattern, text or "", flags=re.I | re.M) for pattern in patterns):
            signals.append(signal)
    term_count = len(re.findall(r"[A-Za-z][A-Za-z\-]{5,}", text or ""))
    if term_count >= 35:
        signals.append("term_density")
    return unique(signals)


def knowledge_roles(signals: list[str]) -> list[str]:
    roles = [ROLE_BY_SIGNAL[signal] for signal in signals if signal in ROLE_BY_SIGNAL]
    if "term_density" in signals:
        roles.append("dense_academic_content")
    return unique(roles)


def knowledge_unit_candidates(text: str, max_items: int = 8) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for line in (text or "").splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if not clean:
            continue
        if any(re.search(pattern, clean, flags=re.I) for pattern in KNOWLEDGE_SIGNAL_PATTERNS["heading_or_topic_boundary"]):
            candidates.append({"signal": "heading_or_topic_boundary", "label": clean[:160]})
        elif re.search(r"\blearning objectives?\b|\bby the end\b|\byou should be able to\b", clean, flags=re.I):
            candidates.append({"signal": "learning_objective", "label": clean[:160]})
        if len(candidates) >= max_items:
            break
    return candidates


def likely_slide_title(text: str) -> str:
    for line in (text or "").splitlines():
        clean = re.sub(r"\s+", " ", line).strip()
        if clean:
            return clean[:160]
    clean = re.sub(r"\s+", " ", text or "").strip()
    return clean[:160]


def timecode_seconds(value: str) -> float:
    normalized = value.replace(",", ".")
    parts = normalized.split(":")
    if len(parts) == 2:
        minutes, seconds = parts
        return round(int(minutes) * 60 + float(seconds), 3)
    hours, minutes, seconds = parts
    return round(int(hours) * 3600 + int(minutes) * 60 + float(seconds), 3)


def timed_text_units(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() not in {".vtt", ".srt"}:
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    matches = list(TIMECODE_RE.finditer(text))
    units: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]
        lines = [line.strip() for line in body.splitlines() if line.strip() and not line.strip().isdigit()]
        content = re.sub(r"<[^>]+>", " ", " ".join(lines))
        content = re.sub(r"\s+", " ", content).strip()
        if not content:
            continue
        start_seconds = timecode_seconds(match.group("start"))
        end_seconds = timecode_seconds(match.group("end"))
        units.append({
            "locator": f"{match.group('start')} --> {match.group('end')}",
            "time_offset_seconds": start_seconds,
            "time_range": {"start_seconds": start_seconds, "end_seconds": end_seconds},
            "text": content,
        })
    return units


def provenance_record(
    source_id: str,
    source_name: str,
    locator: str | None = None,
    page_number: int | None = None,
    slide_number: int | None = None,
    time_offset_seconds: float | None = None,
    time_range: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "source_name": source_name,
        "locator": locator,
        "page_number": page_number,
        "slide_number": slide_number,
        "time_offset_seconds": time_offset_seconds,
        "time_range": time_range,
    }


def slide_triage(text: str, previous_text: str = "") -> dict[str, Any]:
    clean = re.sub(r"\s+", " ", text or "").strip()
    lower = clean.lower()
    signals = set(knowledge_signals(clean))
    strong_signals = {"definition", "mechanism", "method", "comparison", "calculation", "application"}
    direct_data_signals = {"data_interpretation", "evidence"}
    content_role = content_triage(clean)
    words = word_count(clean)

    if has_any(lower, EMBEDDED_AI_INSTRUCTION_KEYWORDS):
        return {
            "slide_decision": "exclude",
            "notes_role": "untrusted_embedded_instruction",
            "detailed_explanation_allowed": False,
            "manual_review_required": False,
            "triage_reason": "instructions_inside_source_are_not_agent_instructions",
        }
    if not clean or words <= 2:
        return {
            "slide_decision": "use",
            "notes_role": "visual_review_required",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "text_sparse_slide_requires_visual_review",
        }
    if has_any(lower, ADMIN_BOILERPLATE_KEYWORDS) and not (signals & (strong_signals | direct_data_signals)):
        return {
            "slide_decision": "exclude",
            "notes_role": "non_teaching_material",
            "detailed_explanation_allowed": False,
            "manual_review_required": False,
            "triage_reason": "verified_operational_administration_without_teaching_content",
        }
    if has_any(lower, DECORATIVE_OR_CREDIT_KEYWORDS) and (words <= 20 or not (signals & strong_signals)):
        return {
            "slide_decision": "use",
            "notes_role": "visual_review_required",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "rights_or_credit_text_cannot_determine_visual_teaching_content",
        }
    if content_role == "reading_reference":
        return {
            "slide_decision": "use",
            "notes_role": "visual_review_required",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "reference_like_text_requires_visual_review_before_exclusion",
        }
    if content_role == "low_exam_relevance_context" and not (signals & (strong_signals | direct_data_signals)):
        return {
            "slide_decision": "use",
            "notes_role": "visual_review_required",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "context_slide_requires_course_and_visual_review",
        }
    if high_text_overlap(clean, previous_text):
        return {
            "slide_decision": "merge_with_previous",
            "notes_role": "example_or_summary_support",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "duplicate_text_requires_visual_comparison_before_merge",
        }

    title = likely_slide_title(text).lower()
    structure_marker = has_any(title + "\n" + lower[:220], STRUCTURE_SLIDE_KEYWORDS)
    if structure_marker and not (signals & strong_signals) and "data_interpretation" not in signals:
        return {
            "slide_decision": "use",
            "notes_role": "structure_marker",
            "detailed_explanation_allowed": False,
            "manual_review_required": False,
            "triage_reason": "structure_or_learning_outcome_slide_for_topic_order",
        }
    if has_any(lower, CONTINUATION_KEYWORDS) or (content_role == "supporting_example" and previous_text):
        return {
            "slide_decision": "merge_with_previous",
            "notes_role": "example_or_summary_support",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "supporting_example_or_continuation_of_previous_unit",
        }
    if has_visual_signal(clean) and not (signals & (strong_signals | direct_data_signals)):
        return {
            "slide_decision": "merge_with_previous" if previous_text else "use",
            "notes_role": "visual_or_data_support",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "visual_or_data_support_without_standalone_explanation_need",
        }
    if signals & strong_signals:
        return {
            "slide_decision": "use",
            "notes_role": "knowledge_source",
            "detailed_explanation_allowed": True,
            "manual_review_required": False,
            "triage_reason": "substantive_course_knowledge",
        }
    if signals & direct_data_signals:
        detailed = bool(re.search(r"\b(interprets?|trend|shows?|demonstrates?|control|readout|result|conclusion)\b", lower))
        return {
            "slide_decision": "use",
            "notes_role": "visual_or_data_support",
            "detailed_explanation_allowed": detailed,
            "manual_review_required": not detailed,
            "triage_reason": "data_or_evidence_support_for_nearby_knowledge_unit",
        }
    if "learning_objective" in signals or "heading_or_topic_boundary" in signals:
        return {
            "slide_decision": "use",
            "notes_role": "structure_marker",
            "detailed_explanation_allowed": False,
            "manual_review_required": False,
            "triage_reason": "topic_boundary_or_learning_objective",
        }
    if words <= 8:
        return {
            "slide_decision": "use",
            "notes_role": "visual_review_required",
            "detailed_explanation_allowed": False,
            "manual_review_required": True,
            "triage_reason": "short_slide_requires_visual_review_before_exclusion",
        }
    return {
        "slide_decision": "use",
        "notes_role": "example_or_summary_support",
        "detailed_explanation_allowed": False,
        "manual_review_required": False,
        "triage_reason": "context_support_for_notes_structure",
    }


def classify_source(path: str | Path, text: str = "") -> str:
    source_path = Path(path)
    name = source_path.name.lower().replace("_", " ").replace("-", " ")
    parent = str(source_path.parent).lower().replace("_", " ").replace("-", " ")
    sample = (text or "")[:6000].lower().replace("_", " ").replace("-", " ")
    haystack = name + "\n" + sample
    lecture_named = any(word in name for word in ["lecture", "slides", "notes", "module"]) or is_lecture_source(path, text)
    exam_like = has_any(haystack, ["past paper", "question paper", "exam paper", "answer all questions"]) or ("time allowed" in haystack and "examination" in haystack)
    course_like = lecture_named or has_any(sample[:1200], ["notes for", "contents", "chapter", "module"])

    if "past papers" in parent or exam_like or has_any(name, ["problem sheet"]):
        return "practice_material"
    if has_marking_signal(name, haystack) and not exam_like:
        return "marking_material"
    if course_like:
        return "knowledge_material"
    if DOI_RE.search(text or "") or PMID_RE.search(text or "") or AUTHOR_YEAR_RE.search(text or ""):
        return "extra_reading_source"
    if has_any(name, ["paper", "article", "journal", "doi", "pmid"]):
        return "extra_reading_source"
    if has_any(sample, PAPER_KEYWORDS) and not lecture_named:
        return "extra_reading_source"
    if has_any(name, ["textbook", "book", "chapter"]):
        return "extra_reading_source"
    if has_any(sample, BOOK_KEYWORDS) and not lecture_named:
        return "extra_reading_source"
    if has_any(haystack, PRACTICE_KEYWORDS):
        return "practice_material"
    if has_any(haystack, STYLE_KEYWORDS):
        return "style_reference"
    if has_any(haystack, KNOWLEDGE_KEYWORDS):
        return "knowledge_material"
    return "other_material"


def classify_exam_source_role(path: str | Path, text: str, source_hint: str) -> str:
    """Classify assessment evidence without treating every question as a formal paper."""
    source_path = Path(path)
    name = source_path.name.casefold().replace("_", " ").replace("-", " ")
    parent = str(source_path.parent).casefold().replace("_", " ").replace("-", " ")
    sample = (text or "")[:6000].casefold()
    haystack = f"{parent}\n{name}\n{sample}"
    if source_hint == "marking_material" or has_marking_signal(name, haystack):
        return "mark_scheme"
    if has_any(haystack, ["specimen paper", "specimen exam", "official mock", "mock paper", "sample paper"]):
        return "official_mock_specimen"
    practice_markers = [
        "practice exam", "practice paper", "practice question", "worksheet",
        "problem sheet", "question bank", "revision question", "self assessment",
        "self-assessment",
    ]
    practice_directories = {
        "practice", "practice papers", "practice questions", "worksheets",
        "problem sheets", "question banks", "revision questions",
    }
    normalised_parent_parts = {
        part.casefold().replace("_", " ").replace("-", " ")
        for part in source_path.parent.parts
    }
    if has_any(f"{name}\n{sample}", practice_markers) or normalised_parent_parts & practice_directories:
        return "practice_worksheet"
    if (
        "past papers" in parent
        or has_any(haystack, ["past paper", "question paper", "exam paper", "answer all questions"])
        or ("time allowed" in haystack and "examination" in haystack)
    ):
        return "formal_past_paper"
    if source_hint == "practice_material":
        return "practice_worksheet"
    if source_hint == "knowledge_material":
        return "lecture_material"
    return "other"


def clean_xml_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore")
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def clean_pptx_slide_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="ignore")
    runs = re.findall(r"<a:t[^>]*>(.*?)</a:t>", text, flags=re.S)
    if runs:
        cleaned = []
        for run in runs:
            value = html.unescape(re.sub(r"<[^>]+>", " ", run))
            value = re.sub(r"\s+", " ", value).strip()
            if value:
                cleaned.append(value)
        return "\n".join(cleaned).strip()
    return clean_xml_text(raw)


def read_docx_paragraph_units(path: Path) -> list[dict[str, Any]]:
    """Read DOCX body paragraphs with stable paragraph and heading-path locators."""
    word_ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ns = {"w": word_ns}
    with zipfile.ZipFile(path) as zf:
        root = ElementTree.fromstring(zf.read("word/document.xml"))
    units: list[dict[str, Any]] = []
    heading_path: list[str] = []
    paragraph_number = 0
    for paragraph in root.findall(".//w:body//w:p", ns):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", ns)).strip()
        if not text:
            continue
        paragraph_number += 1
        style_node = paragraph.find("./w:pPr/w:pStyle", ns)
        style = ""
        if style_node is not None:
            style = str(style_node.attrib.get(f"{{{word_ns}}}val") or "")
        heading_match = re.match(r"(?i)heading\s*([1-9])", style)
        if heading_match:
            level = int(heading_match.group(1))
            heading_path = heading_path[: level - 1]
            heading_path.append(text)
        path_label = " > ".join(heading_path)
        locator = f"paragraph {paragraph_number}"
        if path_label:
            locator = f"{path_label}; {locator}"
        units.append({
            "paragraph_start": paragraph_number,
            "paragraph_end": paragraph_number,
            "heading_path": list(heading_path),
            "locator": locator,
            "text": text,
            "likely_slide_title": heading_path[-1] if heading_path else "",
        })
    return units


def read_docx_text(path: Path) -> str:
    return "\n".join(item["text"] for item in read_docx_paragraph_units(path)).strip()


def read_image_text(path: Path) -> tuple[str, list[str]]:
    """Use optional local OCR; otherwise retain the image for direct visual review."""
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore

        text = str(pytesseract.image_to_string(Image.open(path)) or "").strip()
        if text:
            return text, ["image_text_extracted_with_local_ocr"]
        return "", ["image_ocr_returned_no_text", "direct_visual_review_required"]
    except Exception:
        return "", ["local_image_ocr_unavailable", "direct_visual_review_required"]


def read_pptx_text(path: Path) -> str:
    return "\n\n".join(item["text"] for item in read_pptx_slide_texts(path) if item["text"]).strip()


def read_pptx_slide_texts(path: Path) -> list[dict[str, Any]]:
    slides: list[dict[str, Any]] = []
    with zipfile.ZipFile(path) as zf:
        slide_names = []
        for name in zf.namelist():
            match = PPTX_SLIDE_XML_RE.fullmatch(name)
            if match:
                slide_names.append((int(match.group(1)), name))
        for slide_number, name in sorted(slide_names):
            text = clean_pptx_slide_text(zf.read(name))
            slides.append({
                "slide_number": slide_number,
                "locator": f"slide {slide_number}",
                "text": text,
                "likely_slide_title": likely_slide_title(text),
            })
    return slides


def read_pdf_text(path: Path) -> tuple[str, list[str]]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return "", ["pdf_text_not_extracted_by_local_runtime"]
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip(), []


def pdf_page_texts(path: Path) -> list[str]:
    try:
        import fitz  # type: ignore
    except Exception:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            return []
        try:
            reader = PdfReader(str(path))
            return [page.extract_text() or "" for page in reader.pages]
        except Exception:
            return []
    try:
        with fitz.open(path) as doc:
            return [page.get_text("text") or "" for page in doc]
    except Exception:
        return []


def slide_like_units(path: Path, page_texts: list[str]) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".pptx":
        return read_pptx_slide_texts(path)
    if path.suffix.lower() == ".pdf" and page_texts:
        return [
            {
                "page_number": idx,
                "locator": f"page {idx}",
                "text": text,
                "likely_slide_title": likely_slide_title(text),
            }
            for idx, text in enumerate(page_texts, 1)
        ]
    if path.suffix.lower() == ".docx":
        return read_docx_paragraph_units(path)
    if path.suffix.lower() in IMAGE_SUFFIXES:
        text, _ = read_image_text(path)
        return [{
            "image_number": 1,
            "locator": "image 1",
            "text": text,
            "likely_slide_title": path.stem,
        }]
    return []


def read_source_text(path: Path) -> tuple[str, list[str]]:
    notes: list[str] = []
    suffix = path.suffix.lower()
    try:
        if suffix in TEXT_SUFFIXES:
            if suffix == ".csv":
                with path.open(newline="", encoding="utf-8", errors="ignore") as f:
                    rows = [" | ".join(row) for row in csv.reader(f)]
                return "\n".join(rows), notes
            return path.read_text(encoding="utf-8", errors="ignore"), notes
        if suffix == ".docx":
            return read_docx_text(path), notes
        if suffix == ".pptx":
            return read_pptx_text(path), notes
        if suffix == ".pdf":
            return read_pdf_text(path)
        if suffix in IMAGE_SUFFIXES:
            return read_image_text(path)
        return "", ["automatic_text_reader_not_configured_for_this_file_type"]
    except Exception as exc:
        return "", [f"text_extraction_note:{type(exc).__name__}"]


def chunk_text(text: str, max_chars: int = 1400) -> list[str]:
    text = re.sub(r"\r\n?", "\n", text or "").strip()
    if not text:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs or [text]:
        if len(para) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            for i in range(0, len(para), max_chars):
                chunks.append(para[i:i + max_chars].strip())
        elif len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).strip()
        else:
            chunks.append(current.strip())
            current = para
    if current:
        chunks.append(current.strip())
    return chunks


def extract_media(path: Path, source_id: str, asset_dir: Path) -> list[dict[str, Any]]:
    prefix = MEDIA_PREFIXES.get(path.suffix.lower())
    if not prefix:
        return []
    visuals: list[dict[str, Any]] = []
    try:
        with zipfile.ZipFile(path) as zf:
            media_names = (n for n in zf.namelist() if n.startswith(prefix) and not n.endswith("/"))
            for idx, name in enumerate(media_names, 1):
                asset_dir.mkdir(parents=True, exist_ok=True)
                out = asset_dir / f"{source_id}_{Path(name).name}"
                out.write_bytes(zf.read(name))
                visuals.append({
                    "visual_id": f"{source_id}_V{idx}",
                    "source_id": source_id,
                    "asset_path": str(out),
                    "media_name": Path(name).name,
                    "package_member": name,
                    "locator": None,
                    "locator_status": "incomplete",
                    "locator_reason": "embedded_media_relationship_not_resolved_to_slide_or_paragraph",
                    "knowledge_status": "incomplete",
                    "manual_review_required": True,
                    "provenance": provenance_record(source_id, path.name),
                })
    except Exception:
        return []
    return visuals


def preserve_direct_image(path: Path, source_id: str, asset_dir: Path) -> dict[str, Any]:
    """Copy an image to the durable task asset directory before archive temp files disappear."""
    asset_dir.mkdir(parents=True, exist_ok=True)
    out = asset_dir / f"{source_id}_{path.name}"
    if path.resolve() != out.resolve():
        shutil.copy2(path, out)
    return {
        "visual_id": f"{source_id}_V1",
        "source_id": source_id,
        "locator": "image 1",
        "locator_status": "complete",
        "asset_path": str(out),
        "media_name": out.name,
        "extraction_method": "direct_image_copy",
    }


def expanded_rect(rect: Any, page_rect: Any, pad: float = 18.0) -> Any:
    rect = rect + (-pad, -pad, pad, pad)
    rect.x0 = max(rect.x0, page_rect.x0)
    rect.y0 = max(rect.y0, page_rect.y0)
    rect.x1 = min(rect.x1, page_rect.x1)
    rect.y1 = min(rect.y1, page_rect.y1)
    return rect


def pdf_visual_rects(page: Any) -> list[Any]:
    try:
        import fitz  # type: ignore
    except Exception:
        return []
    try:
        page_rect = page.rect
        blocks = page.get_text("dict").get("blocks", [])
        image_rects = [fitz.Rect(block["bbox"]) for block in blocks if block.get("type") == 1 and block.get("bbox")]
        text_blocks = [block for block in blocks if block.get("type") == 0 and block.get("bbox")]
        caption_rects = [
            fitz.Rect(block["bbox"])
            for block in text_blocks
            if re.search(r"(?i)\b(fig(?:ure)?\.?\s*\d+|table\s*\d+|diagram|graph|plot|scheme)\b", block_text(block))
        ]
        drawing_rects = []
        for drawing in getattr(page, "get_drawings", lambda: [])():
            rect = drawing.get("rect")
            if rect:
                drawing_rects.append(fitz.Rect(rect))

        linked_rects: list[Any] = []
        for caption in caption_rects:
            window_top = max(page_rect.y0, caption.y0 - max(180.0, page_rect.height * 0.35))
            candidates = [
                rect for rect in image_rects + drawing_rects
                if rect.y0 >= window_top
                and rect.y1 <= caption.y0 + 12.0
                and horizontal_overlap(rect, caption) > 0
                and rect_area(rect) > 12.0
            ]
            if candidates:
                linked_rects.append(union_rects(candidates))

        return unique_rects(linked_rects + image_rects, page_rect)
    except Exception:
        return []


def block_text(block: dict[str, Any]) -> str:
    lines = []
    for line in block.get("lines", []) or []:
        for span in line.get("spans", []) or []:
            lines.append(str(span.get("text") or ""))
    return " ".join(lines)


def rect_area(rect: Any) -> float:
    return max(0.0, float(rect.x1 - rect.x0)) * max(0.0, float(rect.y1 - rect.y0))


def horizontal_overlap(a: Any, b: Any) -> float:
    return max(0.0, min(float(a.x1), float(b.x1)) - max(float(a.x0), float(b.x0)))


def union_rects(rects: list[Any]) -> Any:
    rect = rects[0]
    for item in rects[1:]:
        rect = rect | item
    return rect


def unique_rects(rects: list[Any], page_rect: Any) -> list[Any]:
    out = []
    seen: set[tuple[int, int, int, int]] = set()
    page_area = rect_area(page_rect) or 1.0
    for rect in rects:
        if rect_area(rect) <= 12.0 or rect_area(rect) >= page_area * 0.85:
            continue
        key = tuple(round(float(value)) for value in (rect.x0, rect.y0, rect.x1, rect.y1))
        if key in seen:
            continue
        seen.add(key)
        out.append(rect)
    return out


def extract_pdf_page_visuals(path: Path, source_id: str, asset_dir: Path, page_texts: list[str]) -> list[dict[str, Any]]:
    if path.suffix.lower() != ".pdf":
        return []
    try:
        import fitz  # type: ignore
    except Exception:
        return []
    visuals: list[dict[str, Any]] = []
    try:
        with fitz.open(path) as doc:
            asset_dir.mkdir(parents=True, exist_ok=True)
            for page_index, page in enumerate(doc):
                page_text = page_texts[page_index] if page_index < len(page_texts) else (page.get_text("text") or "")
                rects = pdf_visual_rects(page)
                full_page_review = False
                if not rects and not page_text.strip():
                    rects = [page.rect]
                    full_page_review = True
                if not rects:
                    continue
                for rect_index, rect in enumerate(rects, 1):
                    crop = expanded_rect(rect, page.rect)
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), clip=crop, alpha=False)
                    out = asset_dir / f"{source_id}_page{page_index + 1}_visual{rect_index}.png"
                    pix.save(out)
                    caption_match = re.search(
                        r"(?i)\b(fig(?:ure)?\.?\s*\d*|table\s*\d*|diagram|graph|plot|scheme)\b[^\n.]*[.\n]?",
                        page_text,
                    )
                    visuals.append({
                        "visual_id": f"{source_id}_P{page_index + 1}_V{rect_index}",
                        "source_id": source_id,
                        "source_name": path.name,
                        "asset_path": str(out),
                        "media_name": out.name,
                        "page": page_index + 1,
                        "page_number": page_index + 1,
                        "bbox": [round(crop.x0, 2), round(crop.y0, 2), round(crop.x1, 2), round(crop.y1, 2)],
                        "locator": f"page {page_index + 1}",
                        "locator_status": "complete",
                        "caption": (caption_match.group(0).strip() if caption_match else ""),
                        "nearby_text": re.sub(r"\s+", " ", page_text).strip(),
                        "extraction_method": "pdf_page_review_render" if full_page_review else "pdf_page_visible_render",
                        "manual_review_required": full_page_review or not has_visual_signal(page_text),
                        "knowledge_signals": knowledge_signals(page_text),
                        "provenance": provenance_record(
                            source_id,
                            path.name,
                            locator=f"page {page_index + 1}",
                            page_number=page_index + 1,
                        ),
                    })
    except Exception:
        return visuals
    return visuals


def _zip_member_is_symlink(info: zipfile.ZipInfo) -> bool:
    return ((info.external_attr >> 16) & 0o170000) == 0o120000


def _extract_archive_sources(
    archive: Path,
    logical_archive: str,
    destination: Path,
) -> list[tuple[Path, str]]:
    selected: list[tuple[Path, str]] = []
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            member = Path(info.filename)
            if info.is_dir() or member.is_absolute() or ".." in member.parts or _zip_member_is_symlink(info):
                continue
            if member.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
                continue
            target = (destination / member).resolve()
            if destination.resolve() not in target.parents:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            logical = f"{logical_archive}!/{member.as_posix()}"
            if target.suffix.lower() in ARCHIVE_SUFFIXES:
                selected.extend(_extract_archive_sources(target, logical, target.parent / f".{target.stem}_expanded"))
            else:
                selected.append((target, logical))
    return selected


def _is_within(path: Path, roots: tuple[Path, ...]) -> bool:
    resolved = path.expanduser().resolve()
    return any(resolved == root or root in resolved.parents for root in roots)


@contextmanager
def expanded_source_inputs(paths: list[str], excluded_dirs: tuple[Path, ...] = ()):
    """Yield physical files and stable logical paths for files, directories, and ZIPs."""
    with tempfile.TemporaryDirectory(prefix="everything-exam-preparation-") as temporary:
        temp_root = Path(temporary)
        selected: list[tuple[Path, str]] = []
        for index, raw in enumerate(paths, 1):
            path = Path(raw).expanduser()
            if not path.exists():
                raise FileNotFoundError(f"Source does not exist: {path}")
            if path.is_dir():
                for child in sorted(item for item in path.rglob("*") if item.is_file() and not item.is_symlink()):
                    if _is_within(child, excluded_dirs):
                        continue
                    if child.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
                        continue
                    if child.suffix.lower() in ARCHIVE_SUFFIXES:
                        selected.extend(_extract_archive_sources(
                            child,
                            str(child),
                            temp_root / f"archive_{index}_{len(selected) + 1}",
                        ))
                    else:
                        selected.append((child, str(child)))
            elif path.suffix.lower() in ARCHIVE_SUFFIXES:
                selected.extend(_extract_archive_sources(path, str(path), temp_root / f"archive_{index}"))
            else:
                selected.append((path, str(path)))
        yield selected


def _source_display_name(logical_path: str) -> str:
    if "!/" in logical_path:
        archive, member = logical_path.split("!/", 1)
        return f"{Path(archive).name}!/{member}"
    return Path(logical_path).name


def build_scan(
    paths: list[str],
    asset_dir: str = ".skill_assets",
    visual_mode: str = "embedded_media",
    excluded_dirs: tuple[Path, ...] = (),
) -> dict[str, Any]:
    asset_root = Path(asset_dir).expanduser().resolve()
    generated_dirs = tuple(dict.fromkeys((*excluded_dirs, asset_root)))
    with expanded_source_inputs(paths, generated_dirs) as expanded:
        return _build_scan_expanded(expanded, asset_dir, visual_mode)


def _build_scan_expanded(
    paths: list[tuple[Path, str]],
    asset_dir: str = ".skill_assets",
    visual_mode: str = "embedded_media",
) -> dict[str, Any]:
    asset_root = Path(asset_dir).expanduser().resolve()
    documents: list[dict[str, Any]] = []
    fragments: list[dict[str, Any]] = []
    visuals: list[dict[str, Any]] = []
    extraction_notes: list[str] = []
    for idx, (path, logical_path) in enumerate(paths, 1):
        display_name = _source_display_name(logical_path)
        classification_path = Path(logical_path.replace("!/", "/"))
        source_id = f"S{idx}"
        text, notes = read_source_text(path)
        page_texts = pdf_page_texts(path) if path.suffix.lower() == ".pdf" else []
        if not text:
            notes = notes + ["no_text_extracted_automatically"]
        hint = classify_source(classification_path, text)
        exam_source_role = classify_exam_source_role(classification_path, text, hint)
        lecture_order = lecture_order_from_path(classification_path)
        lecture_source = is_lecture_source(classification_path, text)
        doc_content_role = content_triage(text)
        doc_signals = knowledge_signals(text)
        doc_roles = knowledge_roles(doc_signals)
        doc_units = knowledge_unit_candidates(text)
        doc_question_signals = question_signals(classification_path, text, hint)
        slide_units = slide_like_units(path, page_texts) if path.suffix.lower() in (OFFICE_SUFFIXES | IMAGE_SUFFIXES) else []
        if not slide_units and path.suffix.lower() in (OFFICE_SUFFIXES | IMAGE_SUFFIXES):
            slide_units = [{"locator": None, "text": "", "likely_slide_title": path.stem}]
        time_units = timed_text_units(path)
        documents.append({
            "id": source_id,
            "path": logical_path,
            "name": display_name,
            "source_hint": hint,
            "category": hint,
            "exam_source_role": exam_source_role,
            "source_order": idx,
            "lecture_order": lecture_order,
            "lecture_source": lecture_source,
            "content_triage": doc_content_role,
            "notes_obligation": notes_obligation(doc_content_role),
            "text_chars": len(text),
            "knowledge_signals": doc_signals,
            "knowledge_roles": doc_roles,
            "knowledge_unit_candidates": doc_units,
            "question_signals": doc_question_signals,
            "slide_like_fragment_count": len(slide_units),
            "extraction_notes": notes,
        })
        extraction_notes.extend(f"{source_id}:{note}" for note in notes)
        previous_slide_text = ""
        if slide_units:
            for frag_idx, unit in enumerate(slide_units, 1):
                chunk = str(unit.get("text") or "")
                unit_locator = unit.get("locator")
                frag_signals = knowledge_signals(chunk)
                frag_content_role = content_triage(chunk)
                triage = slide_triage(chunk, previous_slide_text)
                fragments.append({
                    "id": f"{source_id}_F{frag_idx}",
                    "source_id": source_id,
                    "source_name": display_name,
                    "source_hint": hint,
                    "category": hint,
                    "exam_source_role": exam_source_role,
                    "source_order": idx,
                    "fragment_order": frag_idx,
                    "lecture_order": lecture_order,
                    "lecture_source": lecture_source,
                    "content_triage": frag_content_role,
                    "notes_obligation": notes_obligation_for_slide(frag_content_role, triage),
                    "locator": unit_locator,
                    "slide_number": unit.get("slide_number"),
                    "page_number": unit.get("page_number"),
                    "paragraph_start": unit.get("paragraph_start"),
                    "paragraph_end": unit.get("paragraph_end"),
                    "heading_path": unit.get("heading_path"),
                    "image_number": unit.get("image_number"),
                    "locator_status": "complete" if unit_locator else "incomplete",
                    "knowledge_status": "incomplete" if not chunk else "complete",
                    "likely_slide_title": unit.get("likely_slide_title") or likely_slide_title(chunk),
                    "provenance": provenance_record(
                        source_id,
                        display_name,
                        locator=str(unit_locator) if unit_locator else None,
                        page_number=unit.get("page_number"),
                        slide_number=unit.get("slide_number"),
                    ),
                    "slide_decision": triage["slide_decision"],
                    "notes_role": triage["notes_role"],
                    "detailed_explanation_allowed": triage["detailed_explanation_allowed"],
                    "manual_review_required": bool(triage.get("manual_review_required")),
                    "triage_reason": triage["triage_reason"],
                    "text": chunk,
                    "knowledge_signals": frag_signals,
                    "knowledge_roles": knowledge_roles(frag_signals),
                    "knowledge_unit_candidates": knowledge_unit_candidates(chunk),
                })
                if triage["slide_decision"] in {"use", "merge_with_previous"}:
                    previous_slide_text = chunk
        elif time_units:
            for frag_idx, unit in enumerate(time_units, 1):
                chunk = str(unit.get("text") or "")
                frag_signals = knowledge_signals(chunk)
                frag_content_role = content_triage(chunk)
                fragments.append({
                    "id": f"{source_id}_F{frag_idx}",
                    "source_id": source_id,
                    "source_name": display_name,
                    "source_hint": hint,
                    "category": hint,
                    "exam_source_role": exam_source_role,
                    "source_order": idx,
                    "fragment_order": frag_idx,
                    "lecture_order": lecture_order,
                    "lecture_source": lecture_source,
                    "content_triage": frag_content_role,
                    "notes_obligation": notes_obligation(frag_content_role),
                    "locator": unit.get("locator"),
                    "time_offset_seconds": unit.get("time_offset_seconds"),
                    "time_range": unit.get("time_range"),
                    "provenance": provenance_record(
                        source_id,
                        display_name,
                        locator=str(unit.get("locator") or ""),
                        time_offset_seconds=unit.get("time_offset_seconds"),
                        time_range=unit.get("time_range"),
                    ),
                    "text": chunk,
                    "knowledge_signals": frag_signals,
                    "knowledge_roles": knowledge_roles(frag_signals),
                    "knowledge_unit_candidates": knowledge_unit_candidates(chunk),
                })
        else:
            for frag_idx, chunk in enumerate(chunk_text(text), 1):
                frag_signals = knowledge_signals(chunk)
                frag_content_role = content_triage(chunk)
                fragments.append({
                    "id": f"{source_id}_F{frag_idx}",
                    "source_id": source_id,
                    "source_name": display_name,
                    "source_hint": hint,
                    "category": hint,
                    "exam_source_role": exam_source_role,
                    "source_order": idx,
                    "fragment_order": frag_idx,
                    "lecture_order": lecture_order,
                    "lecture_source": lecture_source,
                    "content_triage": frag_content_role,
                    "notes_obligation": notes_obligation(frag_content_role),
                    "locator": f"chunk {frag_idx}",
                    "provenance": provenance_record(source_id, display_name, locator=f"chunk {frag_idx}"),
                    "text": chunk,
                    "knowledge_signals": frag_signals,
                    "knowledge_roles": knowledge_roles(frag_signals),
                    "knowledge_unit_candidates": knowledge_unit_candidates(chunk),
                })
        if visual_mode != "none":
            source_visuals = extract_media(path, source_id, asset_root)
            source_visuals.extend(extract_pdf_page_visuals(path, source_id, asset_root, page_texts))
            if path.suffix.lower() in IMAGE_SUFFIXES:
                image_visual = preserve_direct_image(path, source_id, asset_root)
                image_visual["manual_review_required"] = not bool(text)
                source_visuals.append(image_visual)
            for visual in source_visuals:
                visual["source_name"] = display_name
                if isinstance(visual.get("provenance"), dict):
                    visual["provenance"]["source_name"] = display_name
            visuals.extend(source_visuals)

    excluded_fragments: list[dict[str, Any]] = []
    safe_fragments: list[dict[str, Any]] = []
    for fragment in fragments:
        if fragment.get("content_triage") != "embedded_ai_instruction":
            safe_fragments.append(fragment)
            continue
        text_digest = hashlib.sha256(str(fragment.get("text") or "").encode("utf-8")).hexdigest()
        excluded_fragments.append({
            key: fragment.get(key)
            for key in (
                "id", "source_id", "source_name", "locator", "locator_status",
                "slide_number", "page_number", "paragraph_start", "paragraph_end",
                "heading_path", "time_offset_seconds", "time_range", "provenance",
            )
            if fragment.get(key) is not None
        } | {
            "content_triage": "embedded_ai_instruction",
            "exclusion_reason": "instructions_inside_source_are_not_agent_instructions",
            "text_sha256": text_digest,
        })
    fragments = safe_fragments
    hints: dict[str, int] = {}
    signals: dict[str, int] = {}
    roles: dict[str, int] = {}
    content_roles: dict[str, int] = {}
    slide_decisions: dict[str, int] = {}
    notes_roles: dict[str, int] = {}
    for doc in documents:
        hints[doc["source_hint"]] = hints.get(doc["source_hint"], 0) + 1
        content_roles[doc["content_triage"]] = content_roles.get(doc["content_triage"], 0) + 1
        for signal in doc.get("knowledge_signals", []):
            signals[signal] = signals.get(signal, 0) + 1
        for role in doc.get("knowledge_roles", []):
            roles[role] = roles.get(role, 0) + 1
    for frag in fragments:
        if frag.get("slide_decision"):
            slide_decision = str(frag["slide_decision"])
            slide_decisions[slide_decision] = slide_decisions.get(slide_decision, 0) + 1
        if frag.get("notes_role"):
            notes_role = str(frag["notes_role"])
            notes_roles[notes_role] = notes_roles.get(notes_role, 0) + 1
    return {
        "schema_version": 3,
        "documents": documents,
        "fragments": fragments,
        "excluded_fragments": excluded_fragments,
        "visuals": visuals,
        "summary": {
            "source_count": len(documents),
            "fragment_count": len(fragments),
            "excluded_embedded_ai_instruction_count": len(excluded_fragments),
            "visual_count": len(visuals),
            "question_source_count": sum(1 for doc in documents if doc.get("question_signals", {}).get("has_questions")),
            "past_paper_question_source_count": sum(1 for doc in documents if doc.get("question_signals", {}).get("has_past_paper")),
            "practical_question_source_count": sum(1 for doc in documents if doc.get("question_signals", {}).get("has_practical_questions")),
            "practical_worked_question_source_count": sum(1 for doc in documents if doc.get("question_signals", {}).get("has_practical_worked_questions")),
            "solution_evidence_source_count": sum(1 for doc in documents if doc.get("question_signals", {}).get("has_solution_evidence")),
            "source_hints": hints,
            "content_triage": content_roles,
            "slide_decisions": slide_decisions,
            "notes_roles": notes_roles,
            "slide_like_fragment_count": sum(1 for frag in fragments if frag.get("slide_decision")),
            "manual_review_required_count": sum(1 for frag in fragments if frag.get("manual_review_required")),
            "lecture_source_count": sum(1 for doc in documents if doc.get("lecture_source")),
            "knowledge_signals": signals,
            "knowledge_roles": roles,
            "knowledge_unit_candidate_count": sum(len(doc.get("knowledge_unit_candidates", [])) for doc in documents),
            "extraction_notes": extraction_notes,
        },
    }


def _scan_self_test() -> None:
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "source_a.md"
        p2 = Path(td) / "source_b.txt"
        p3 = Path(td) / "source_c.txt"
        p4 = Path(td) / "practical_sheet.txt"
        p5 = Path(td) / "L1-Origin of Life.pptx"
        p6 = Path(td) / "lecture_recording.vtt"
        p1.write_text("Learning objectives\nDefine enzyme activity.\nThe mechanism leads to dose response changes.\nCompare treated and control results.", encoding="utf-8")
        p2.write_text("1. Which statement is correct? A) One B) Two", encoding="utf-8")
        p3.write_text("Abstract Methods Results DOI 10.1000/test", encoding="utf-8")
        p4.write_text("Practical task: calculate the rate from the graph and interpret the control data.", encoding="utf-8")
        p6.write_text(
            "WEBVTT\n\n00:01:00.000 --> 00:01:10.000\nThe receptor activates a signalling mechanism.\n",
            encoding="utf-8",
        )
        with zipfile.ZipFile(p5, "w") as zf:
            zf.writestr(
                "ppt/slides/slide1.xml",
                "<p:sld><a:t>Lecture 1 Intended Learning Outcomes</a:t>"
                "<a:t>By the end of this session you should be able to describe protocells.</a:t></p:sld>",
            )
            zf.writestr(
                "ppt/slides/slide10.xml",
                "<p:sld><a:t>Copyright and office hour</a:t>"
                "<a:t>Email the lecturer for attendance and password housekeeping.</a:t></p:sld>",
            )
            zf.writestr(
                "ppt/slides/slide2.xml",
                "<p:sld><a:t>Protocell formation mechanism</a:t>"
                "<a:t>The mechanism leads to membrane compartment formation and activates primitive metabolism.</a:t></p:sld>",
            )
            zf.writestr(
                "ppt/slides/slide3.xml",
                "<p:sld><a:t>Protocell formation mechanism</a:t>"
                "<a:t>The mechanism leads to membrane compartment formation and activates primitive metabolism.</a:t></p:sld>",
            )
            zf.writestr(
                "ppt/slides/slide4.xml",
                "<p:sld><a:t>Copyright Example Press</a:t>"
                "<a:t>Figure: membrane pathway</a:t></p:sld>",
            )
        sources = [str(p1), str(p2), str(p3), str(p4), str(p5), str(p6)]
        try:
            import fitz  # type: ignore
            pdf_path = Path(td) / "lecture_visual.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.draw_rect(fitz.Rect(72, 80, 260, 180), color=(0, 0, 0), fill=(0.9, 0.9, 0.9))
            page.insert_text((72, 200), "Figure 1. Reaction pathway diagram")
            doc.save(pdf_path)
            doc.close()
            sources.append(str(pdf_path))
            text_only_pdf = Path(td) / "text_only_figure_locator.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), "Figure 2. Text-only locator without a concrete visual region")
            doc.save(text_only_pdf)
            doc.close()
            sources.append(str(text_only_pdf))
        except Exception:
            pass
        scan = build_scan(sources, asset_dir=str(Path(td) / "assets"))
        assert scan["summary"]["source_count"] == len(sources)
        assert scan["fragments"]
        assert scan["summary"]["knowledge_signals"]
        assert any("mechanism" in frag["knowledge_roles"] for frag in scan["fragments"])
        assert all("provenance" in frag for frag in scan["fragments"])
        assert any(doc["source_hint"] == "extra_reading_source" for doc in scan["documents"])
        assert scan["summary"]["question_source_count"] >= 1
        assert scan["summary"]["practical_question_source_count"] == 1
        assert scan["summary"]["practical_worked_question_source_count"] == 1
        assert any(doc["question_signals"]["has_practical_worked_questions"] for doc in scan["documents"])
        lecture_doc = next(doc for doc in scan["documents"] if doc["name"] == "L1-Origin of Life.pptx")
        assert lecture_doc["source_hint"] == "knowledge_material"
        assert lecture_doc["lecture_order"] == 1
        assert lecture_doc["lecture_source"] is True
        lecture_frags = [frag for frag in scan["fragments"] if frag["source_name"] == "L1-Origin of Life.pptx"]
        assert [frag["slide_number"] for frag in lecture_frags] == [1, 2, 3, 4, 10]
        assert lecture_frags[0]["slide_decision"] == "use"
        assert lecture_frags[0]["notes_role"] == "structure_marker"
        assert lecture_frags[0]["detailed_explanation_allowed"] is False
        assert lecture_frags[1]["slide_decision"] == "use"
        assert lecture_frags[1]["notes_role"] == "knowledge_source"
        assert lecture_frags[1]["detailed_explanation_allowed"] is True
        assert lecture_frags[2]["slide_decision"] == "merge_with_previous"
        assert lecture_frags[2]["manual_review_required"] is True
        assert lecture_frags[3]["slide_decision"] == "use"
        assert lecture_frags[3]["notes_role"] == "visual_review_required"
        assert lecture_frags[3]["manual_review_required"] is True
        assert lecture_frags[4]["slide_decision"] == "exclude"
        assert lecture_frags[4]["notes_role"] == "non_teaching_material"
        assert lecture_frags[4]["manual_review_required"] is False
        assert scan["summary"]["slide_decisions"]["exclude"] >= 1
        assert scan["summary"]["manual_review_required_count"] >= 2
        assert any(frag["content_triage"] == "core_lecture_content" for frag in lecture_frags)
        timed_frag = next(frag for frag in scan["fragments"] if frag["source_name"] == "lecture_recording.vtt")
        assert timed_frag["time_range"] == {"start_seconds": 60.0, "end_seconds": 70.0}
        assert timed_frag["provenance"]["time_offset_seconds"] == 60.0
        if any(Path(source).suffix.lower() == ".pdf" for source in sources):
            assert any(visual.get("extraction_method") == "pdf_page_visible_render" for visual in scan["visuals"])
            assert any(Path(visual["asset_path"]).exists() for visual in scan["visuals"])
            for visual in scan["visuals"]:
                if visual.get("source_name") == "text_only_figure_locator.pdf":
                    raise AssertionError("text-only PDF locator should not create a page visual asset")
                bbox = visual.get("bbox") or []
                if len(bbox) == 4:
                    assert (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) < 500000


def _count_values(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key) or "")
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


ROLE_TO_HINT = {
    "coverage_authority": "knowledge_material",
    "course_knowledge": "knowledge_material",
    "reference_notes": "style_reference",
    "formal_past_paper": "practice_material",
    "official_mock_specimen": "practice_material",
    "practice_worksheet": "practice_material",
    "mark_scheme": "marking_material",
    "style_reference": "style_reference",
    "essay_evidence": "extra_reading_source",
}
EXAM_SOURCE_ROLES = {
    "formal_past_paper",
    "official_mock_specimen",
    "practice_worksheet",
    "lecture_material",
    "mark_scheme",
    "other",
}


def apply_source_role_overrides(scan: dict[str, Any], task_context: dict[str, Any] | None) -> None:
    """Apply explicit user role labels after extraction and before focused indexing."""
    context = task_context or {}
    raw_mapping = context.get("source_roles") or {}
    if not isinstance(raw_mapping, dict):
        return
    mapping = {str(key).casefold(): str(value).strip().lower() for key, value in raw_mapping.items()}
    documents = scan.get("documents", [])
    for document in documents:
        candidates = {
            str(document.get("path") or "").casefold(),
            str(document.get("name") or "").casefold(),
            Path(str(document.get("path") or "unknown")).name.casefold(),
        }
        role = next((mapping[key] for key in candidates if key in mapping), None)
        if not role:
            continue
        document["declared_source_role"] = role
        if role in ROLE_TO_HINT:
            document["source_hint"] = ROLE_TO_HINT[role]
            document["category"] = ROLE_TO_HINT[role]
        if role in EXAM_SOURCE_ROLES:
            document["exam_source_role"] = role
        elif role in {"coverage_authority", "course_knowledge", "reference_notes"}:
            document["exam_source_role"] = "lecture_material"
        for fragment in scan.get("fragments", []):
            if fragment.get("source_id") != document.get("id"):
                continue
            fragment["declared_source_role"] = role
            fragment["source_hint"] = document.get("source_hint")
            fragment["category"] = document.get("category")
            fragment["exam_source_role"] = document.get("exam_source_role")
    summary = scan.get("summary")
    if isinstance(summary, dict):
        summary["source_hints"] = _count_values(documents, "source_hint")
        summary["exam_source_roles"] = _count_values(documents, "exam_source_role")


def _source_fingerprint(paths: list[str], excluded_dirs: tuple[Path, ...] = ()) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in paths:
        path = Path(raw).expanduser()
        if not path.exists():
            records.append({"path": str(path), "missing": True})
            continue
        candidates = [path]
        if path.is_dir():
            candidates = sorted(
                item for item in path.rglob("*")
                if item.is_file() and not item.is_symlink() and not _is_within(item, excluded_dirs)
            )
        for item in candidates:
            if _is_within(item, excluded_dirs):
                continue
            stat = item.stat()
            records.append({
                "path": str(item.resolve()),
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            })
    return records


def _course_index_path(
    cache_dir: str,
    paths: list[str],
    purpose: str,
    visual_mode: str,
    task_context: dict[str, Any] | None,
    asset_dir: str,
) -> Path:
    root = Path(cache_dir).expanduser().resolve()
    asset_root = Path(asset_dir).expanduser().resolve()
    workspace = Path.cwd().resolve()
    if root != workspace and workspace not in root.parents:
        raise ValueError("The optional course index must stay inside the current task workspace")
    payload = {
        "cache_contract_version": 2,
        "sources": _source_fingerprint(paths, (root, asset_root)),
        "purpose": purpose,
        "visual_mode": visual_mode,
        "asset_dir": str(asset_root),
        "task_context": task_context or {},
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()
    root.mkdir(parents=True, exist_ok=True)
    return root / f"course-index-{digest}.json"


def _task_mode(value: str) -> str:
    mode = str(value or "").strip().lower()
    if mode not in TASK_MODES:
        raise ValueError(f"task_mode must be one of {sorted(TASK_MODES)}")
    return mode


def _gap(code: str, detail: str, severity: str = "blocking") -> dict[str, str]:
    return {"code": code, "severity": severity, "detail": detail}


def _assessment_fragments(scan: dict[str, Any]) -> list[dict[str, Any]]:
    documents = {str(item.get("id")): item for item in scan.get("documents", [])}
    selected: list[dict[str, Any]] = []
    for fragment in scan.get("fragments", []):
        source = documents.get(str(fragment.get("source_id")), {})
        category = fragment.get("category") or source.get("category") or source.get("source_hint")
        signals = source.get("question_signals", {}) or {}
        if category in ASSESSMENT_CATEGORIES or signals.get("has_questions") or signals.get("has_solution_evidence"):
            selected.append(fragment)
    return selected


def _fragment_provenance(fragment: dict[str, Any]) -> dict[str, Any]:
    nested = fragment.get("provenance") if isinstance(fragment.get("provenance"), dict) else {}
    return {
        "source_id": nested.get("source_id") or fragment.get("source_id"),
        "source_name": nested.get("source_name") or fragment.get("source_name"),
        "locator": nested.get("locator") or fragment.get("locator"),
        "page_number": nested.get("page_number") or fragment.get("page_number"),
        "slide_number": nested.get("slide_number") or fragment.get("slide_number"),
        "time_offset_seconds": nested.get("time_offset_seconds") or fragment.get("time_offset_seconds"),
        "time_range": nested.get("time_range") or fragment.get("time_range"),
    }


def _unique_provenance(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique_items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in items:
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    return unique_items


def _duration_minutes(text: str) -> list[int]:
    values: set[int] = set()
    for raw_value, unit in ASSESSMENT_DURATION_RE.findall(text or ""):
        value = float(raw_value)
        minutes = round(value * 60) if unit.lower().startswith(("hour", "hr")) else round(value)
        if minutes > 0:
            values.add(minutes)
    return sorted(values)


def build_exam_format_profile(scan: dict[str, Any] | None, task_mode: str = "practice") -> dict[str, Any]:
    """Return an evidence-only ExamFormatProfile without inferring absent rules."""
    mode = _task_mode(task_mode)
    scan = scan or {"documents": [], "fragments": []}
    fragments = _assessment_fragments(scan)
    formats: list[dict[str, Any]] = []
    durations: set[int] = set()
    marks: set[int] = set()
    for format_name, patterns in EXAM_FORMAT_PATTERNS.items():
        matched = [
            fragment for fragment in fragments
            if any(re.search(pattern, str(fragment.get("text") or ""), flags=re.I) for pattern in patterns)
        ]
        if matched:
            formats.append({
                "format": format_name,
                "evidence_count": len(matched),
                "provenance": _unique_provenance([_fragment_provenance(item) for item in matched]),
            })
    for fragment in fragments:
        text = str(fragment.get("text") or "")
        durations.update(_duration_minutes(text))
        marks.update(int(value) for value in ASSESSMENT_MARK_RE.findall(text))

    gaps: list[dict[str, str]] = []
    if not scan.get("documents") or not scan.get("fragments"):
        gaps.append(_gap("missing_sources", "No readable source evidence is available for exam-format diagnosis."))
        status = "blocked"
    elif not fragments:
        gaps.append(_gap(
            "missing_assessment_format_evidence",
            "No question, paper, rubric, or marking fragment establishes the assessment format.",
            "advisory",
        ))
        status = "partial"
    elif not formats:
        gaps.append(_gap(
            "unresolved_question_format",
            "Assessment fragments are present, but no supported question format was detected.",
            "advisory",
        ))
        status = "partial"
    else:
        status = "ready"
    return {
        "contract": "ExamFormatProfile",
        "schema_version": 1,
        "task_mode": mode,
        "status": status,
        "gaps": gaps,
        "degraded": status != "ready",
        "question_formats": formats,
        "duration_minutes": sorted(durations),
        "mark_values": sorted(marks),
        "evidence_fragment_count": len(fragments),
    }


def build_assessment_architecture(
    scan: dict[str, Any] | None,
    task_mode: str = "practice",
    exam_format_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return source-evidenced components and weights without inventing missing percentages."""
    mode = _task_mode(task_mode)
    scan = scan or {"documents": [], "fragments": []}
    profile = exam_format_profile or build_exam_format_profile(scan, mode)
    fragments = _assessment_fragments(scan)
    weights: list[dict[str, Any]] = []
    seen_weights: set[tuple[str, float, str, str]] = set()
    for fragment in fragments:
        text = re.sub(r"\s+", " ", str(fragment.get("text") or ""))
        provenance = _fragment_provenance(fragment)
        for label, raw_weight in ASSESSMENT_WEIGHT_RE.findall(text):
            weight = float(raw_weight)
            if weight > 100:
                continue
            normalized_label = re.sub(r"\s+", " ", label).strip(" :-")[-80:]
            key = (normalized_label.casefold(), weight, str(provenance.get("source_name")), str(provenance.get("locator")))
            if key in seen_weights:
                continue
            seen_weights.add(key)
            weights.append({
                "component": normalized_label,
                "weight_percent": int(weight) if weight.is_integer() else weight,
                "provenance": provenance,
            })
    components = [
        {
            "component": item.get("format"),
            "evidence_count": item.get("evidence_count"),
            "provenance": item.get("provenance") or [],
        }
        for item in profile.get("question_formats", [])
    ]
    gaps = list(profile.get("gaps") or [])
    if components and not weights:
        gaps.append(_gap(
            "missing_explicit_component_weights",
            "No component percentages were found; the architecture reports coverage without inferred weights.",
            "advisory",
        ))
    status = "blocked" if profile.get("status") == "blocked" else ("ready" if components else "partial")
    return {
        "contract": "AssessmentArchitecture",
        "schema_version": 1,
        "task_mode": mode,
        "status": status,
        "gaps": gaps,
        "degraded": status != "ready",
        "components": components,
        "explicit_weights": weights,
        "weighting_basis": "explicit_source_percentages_only",
    }


def _has_task_context_value(context: dict[str, Any], *keys: str) -> bool:
    return any(bool(context.get(key)) for key in keys)


def build_diagnostic_assessment(
    scan: dict[str, Any] | None,
    task_mode: str,
    task_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose a lightweight DiagnosticAssessment for any focused Skill."""
    mode = _task_mode(task_mode)
    scan = scan or {"documents": [], "fragments": []}
    context = task_context or {}
    profile = build_exam_format_profile(scan, mode)
    architecture = build_assessment_architecture(scan, mode, profile)
    source_counts = _count_values(scan.get("documents", []), "source_hint")
    knowledge_count = source_counts.get("knowledge_material", 0)
    assessment_count = sum(source_counts.get(key, 0) for key in ASSESSMENT_CATEGORIES)
    formal_paper_count = sum(
        1 for item in scan.get("documents", []) if item.get("exam_source_role") == "formal_past_paper"
    )
    has_direct_source = _has_task_context_value(context, "source_text", "readings", "source_materials_supplied")
    gaps: list[dict[str, str]] = []

    if (not scan.get("documents") or not scan.get("fragments")) and not has_direct_source:
        gaps.append(_gap("missing_sources", "No usable source fragment or direct source text was supplied."))

    capability = str(context.get("requested_capability") or context.get("capability") or "").strip().lower()
    if mode in {"atlas", "notes"}:
        if scan.get("documents") and knowledge_count == 0 and not has_direct_source:
            gaps.append(_gap("missing_course_knowledge", f"{mode.title()} requires course-knowledge evidence."))
    elif mode == "analysis":
        if assessment_count == 0 and not has_direct_source:
            gaps.append(_gap("missing_question_evidence", "Exam Analysis requires supplied papers or question evidence."))
        elif formal_paper_count == 0:
            gaps.append(_gap(
                "missing_formal_past_papers",
                "No formal past paper is available; auxiliary analysis may proceed but formal recurrence remains empty.",
                "advisory",
            ))
    elif mode == "practice":
        if capability in {"answer_evaluation", "evaluate_answer"}:
            if not _has_task_context_value(context, "student_answer"):
                gaps.append(_gap("missing_student_answer", "Answer evaluation requires the student's answer."))
            if not _has_task_context_value(context, "criteria", "rubric", "mark_scheme"):
                gaps.append(_gap("missing_evaluation_criteria", "Answer evaluation requires explicit expected concepts, a rubric, or a mark scheme."))
        elif capability in {"question_recurrence", "question_organisation", "organize_questions"} and assessment_count == 0:
            gaps.append(_gap("missing_question_evidence", "This Practice capability requires supplied question or paper evidence."))
        elif capability in {"question_solving", "solve_question"}:
            if not _has_task_context_value(context, "question", "target_question"):
                gaps.append(_gap("missing_target_question", "Question solving requires a target question."))
            if knowledge_count == 0 and not has_direct_source:
                gaps.append(_gap("missing_course_knowledge", "Question solving requires course-knowledge evidence."))
        elif capability in {"timed_practice", "build_timed_practice"}:
            if not _has_task_context_value(context, "duration_minutes"):
                gaps.append(_gap("missing_timed_duration", "Timed practice requires an explicit duration."))
        elif scan.get("documents") and knowledge_count == 0 and assessment_count == 0 and not has_direct_source:
            gaps.append(_gap("missing_practice_evidence", "Practice requires course knowledge, question evidence, or explicit evaluation criteria."))
    else:
        if capability not in {"extra_reading", "discover_extra_reading"} and not _has_task_context_value(context, "question", "target_question"):
            gaps.append(_gap("missing_essay_question", "Essay preparation requires the target essay question."))
        if knowledge_count == 0 and not has_direct_source:
            gaps.append(_gap("missing_essay_evidence", "Essay preparation requires course material or supplied readings."))

    blocking = [item for item in gaps if item.get("severity") == "blocking"]
    advisory = [item for item in gaps if item.get("severity") != "blocking"]
    status = "blocked" if blocking else ("partial" if advisory else "ready")
    return {
        "contract": "DiagnosticAssessment",
        "schema_version": 1,
        "task_mode": mode,
        "status": status,
        "gaps": gaps,
        "degraded": status != "ready",
        "can_proceed": status != "blocked",
        "requested_capability": capability or None,
        "source_summary": {
            "document_count": len(scan.get("documents", [])),
            "fragment_count": len(scan.get("fragments", [])),
            "source_hint_counts": source_counts,
        },
        "exam_format_profile": profile,
        "assessment_architecture": architecture,
    }


def build_fragment_index(scan: dict[str, Any] | None, purpose: str = "notes") -> dict[str, Any]:
    scan = scan or {"documents": [], "fragments": []}
    documents = {str(item.get("id")): item for item in scan.get("documents", [])}
    fragments: list[dict[str, Any]] = []
    for source_fragment in scan.get("fragments", []):
        source = documents.get(str(source_fragment.get("source_id")), {})
        text = str(source_fragment.get("text") or "")
        signals = list(source_fragment.get("knowledge_signals") or [])
        score = sum(
            2 if signal in {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation", "evidence"} else 1
            for signal in signals
        )
        fragments.append({
            **source_fragment,
            "source_name": source_fragment.get("source_name") or source.get("name"),
            "source_order": source_fragment.get("source_order") or source.get("source_order") or 0,
            "lecture_order": source_fragment.get("lecture_order") or source.get("lecture_order"),
            "lecture_source": bool(source_fragment.get("lecture_source") or source.get("lecture_source")),
            "content_triage": source_fragment.get("content_triage") or source.get("content_triage") or "core_lecture_content",
            "notes_obligation": source_fragment.get("notes_obligation") or source.get("notes_obligation") or "must_cover",
            "knowledge_score": score,
            "preview": re.sub(r"\s+", " ", text).strip()[:220],
        })
    if purpose in {"atlas", "notes"}:
        fragments.sort(key=lambda item: (
            int(item.get("lecture_order") or 10_000),
            int(item.get("source_order") or 10_000),
            int(item.get("slide_number") or item.get("page_number") or item.get("fragment_order") or 10_000),
        ))
    else:
        fragments.sort(key=lambda item: (-int(item.get("knowledge_score") or 0), int(item.get("source_order") or 10_000)))
    usable = [item for item in fragments if item.get("slide_decision") != "exclude"]
    detailed = [
        item for item in usable
        if item.get("slide_decision") is None or item.get("detailed_explanation_allowed") is True
    ]
    source_audit: list[dict[str, Any]] = []
    for document in scan.get("documents", []):
        source_items = [item for item in fragments if item.get("source_id") == document.get("id")]
        source_visuals = [item for item in scan.get("visuals", []) if item.get("source_id") == document.get("id")]
        source_audit.append({
            "source_id": document.get("id"),
            "source_name": document.get("name"),
            "source_hint": document.get("source_hint"),
            "lecture_order": document.get("lecture_order"),
            "fragment_count": len(source_items),
            "use_count": sum(item.get("slide_decision") == "use" for item in source_items),
            "merge_count": sum(item.get("slide_decision") == "merge_with_previous" for item in source_items),
            "exclude_count": sum(item.get("slide_decision") == "exclude" for item in source_items),
            "manual_review_required_count": sum(bool(item.get("manual_review_required")) for item in source_items),
            "visual_count": len(source_visuals),
            "extraction_notes": document.get("extraction_notes") or [],
        })
    return {
        "schema_version": 3,
        "purpose": purpose,
        "fragment_count": len(fragments),
        "coverage_profile": {
            "source_count": len(documents),
            "content_triage_counts": _count_values(fragments, "content_triage"),
            "notes_obligation_counts": _count_values(fragments, "notes_obligation"),
            "slide_decision_counts": _count_values(fragments, "slide_decision"),
            "notes_role_counts": _count_values(fragments, "notes_role"),
            "source_audit": source_audit,
        },
        "notes_generation_fragments": usable if purpose == "notes" else fragments,
        "detailed_knowledge_fragments": detailed if purpose in {"atlas", "notes"} else fragments,
        "fragments": fragments,
    }


def readiness_report(scan: dict[str, Any] | None, purpose: str = "notes") -> dict[str, Any]:
    scan = scan or {"documents": [], "fragments": []}
    signals: dict[str, int] = {}
    for fragment in scan.get("fragments", []):
        for signal in fragment.get("knowledge_signals", []) or []:
            signals[signal] = signals.get(signal, 0) + 1
    core = {"definition", "mechanism", "method", "comparison", "calculation", "data_interpretation", "evidence"}
    return {
        "schema_version": 3,
        "purpose": purpose,
        "status": "ready" if scan.get("documents") and scan.get("fragments") else "missing_sources",
        "document_count": len(scan.get("documents", [])),
        "fragment_count": len(scan.get("fragments", [])),
        "source_hint_counts": _count_values(scan.get("documents", []), "source_hint"),
        "knowledge_signal_counts": signals,
        "has_core_knowledge": any(signal in signals for signal in core),
        "observations": (scan.get("summary") or {}).get("extraction_notes", []),
    }


def process_sources(
    paths: list[str],
    asset_dir: str = ".skill_assets",
    visual_mode: str = "embedded_media",
    purpose: str = "notes",
    task_context: dict[str, Any] | None = None,
    cache_dir: str | None = None,
) -> dict[str, Any]:
    cache_root = Path(cache_dir).expanduser().resolve() if cache_dir else None
    cache_path = (
        _course_index_path(cache_dir, paths, purpose, visual_mode, task_context, asset_dir)
        if cache_dir else None
    )
    if cache_path and cache_path.is_file():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = None
        if isinstance(cached, dict):
            asset_paths = [
                Path(str(item["asset_path"]))
                for item in (cached.get("scan") or {}).get("visuals", [])
                if item.get("asset_path")
            ]
            if all(path.is_file() for path in asset_paths):
                cached["cache"] = {"optional": True, "status": "hit", "path": str(cache_path)}
                return cached
    excluded_dirs = (cache_root,) if cache_root else ()
    scan = build_scan(paths, asset_dir, visual_mode, excluded_dirs=excluded_dirs)
    apply_source_role_overrides(scan, task_context)
    index = build_fragment_index(scan, purpose)
    readiness = readiness_report(scan, purpose)
    diagnostic = build_diagnostic_assessment(scan, purpose, task_context)
    result = {
        "schema_version": 3,
        "purpose": purpose,
        "scan": scan,
        "index": index,
        "readiness": readiness,
        "diagnostic": diagnostic,
        "coverage_audit": index["coverage_profile"]["source_audit"],
        "cache": {
            "optional": True,
            "status": "miss" if cache_path else "disabled",
            "path": str(cache_path) if cache_path else None,
        },
    }
    if cache_path:
        cache_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def _load_scan(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> None:
    _scan_self_test()
    scan = {
        "documents": [{"id": "S1", "name": "Lecture 1.pptx", "source_hint": "knowledge_material", "source_order": 1}],
        "fragments": [{
            "id": "S1_F1",
            "source_id": "S1",
            "fragment_order": 1,
            "slide_number": 1,
            "slide_decision": "use",
            "detailed_explanation_allowed": True,
            "knowledge_signals": ["definition", "mechanism"],
            "text": "A receptor is defined as a protein that initiates a signalling mechanism.",
        }],
        "visuals": [],
        "summary": {"extraction_notes": []},
    }
    index = build_fragment_index(scan)
    assert index["fragment_count"] == 1
    assert index["coverage_profile"]["source_audit"][0]["use_count"] == 1
    readiness = readiness_report(scan)
    assert readiness["status"] == "ready"
    assert readiness["has_core_knowledge"]
    notes_diagnostic = build_diagnostic_assessment(scan, "notes")
    assert notes_diagnostic["contract"] == "DiagnosticAssessment"
    assert notes_diagnostic["task_mode"] == "notes"
    assert notes_diagnostic["status"] == "ready"
    assert notes_diagnostic["degraded"] is False

    assessment_scan = {
        "documents": [
            {
                "id": "K1",
                "name": "Lecture 1.pptx",
                "source_hint": "knowledge_material",
                "question_signals": {},
            },
            {
                "id": "P1",
                "name": "Assessment brief and past paper.pdf",
                "source_hint": "practice_material",
                "question_signals": {"has_questions": True, "has_past_paper": True},
            },
        ],
        "fragments": [
            {
                "source_id": "K1",
                "source_name": "Lecture 1.pptx",
                "category": "knowledge_material",
                "locator": "slide 3",
                "text": "A receptor initiates a signalling mechanism.",
            },
            {
                "source_id": "P1",
                "source_name": "Assessment brief and past paper.pdf",
                "category": "practice_material",
                "locator": "page 2",
                "text": "Time allowed: 90 minutes. MCQ component: 40%. Short answer component: 60%. Explain the mechanism. 10 marks.",
            },
        ],
    }
    profile = build_exam_format_profile(assessment_scan, "practice")
    assert profile["contract"] == "ExamFormatProfile"
    assert profile["status"] == "ready"
    assert profile["duration_minutes"] == [90]
    assert profile["mark_values"] == [10]
    assert {item["format"] for item in profile["question_formats"]} >= {"mcq", "short_answer"}
    architecture = build_assessment_architecture(assessment_scan, "practice", profile)
    assert architecture["contract"] == "AssessmentArchitecture"
    assert {item["weight_percent"] for item in architecture["explicit_weights"]} == {40, 60}

    scientific_values_scan = {
        "documents": [{
            "id": "P2",
            "name": "Experimental question.pdf",
            "source_hint": "practice_material",
            "question_signals": {"has_questions": True},
        }],
        "fragments": [{
            "source_id": "P2",
            "source_name": "Experimental question.pdf",
            "category": "practice_material",
            "locator": "page 4",
            "text": "Cells were incubated for 15 minutes and viability fell by 50%. Explain these data.",
        }],
    }
    scientific_profile = build_exam_format_profile(scientific_values_scan, "practice")
    scientific_architecture = build_assessment_architecture(
        scientific_values_scan,
        "practice",
        scientific_profile,
    )
    assert scientific_profile["duration_minutes"] == []
    assert scientific_architecture["explicit_weights"] == []

    false_source_flag = build_diagnostic_assessment(
        {"documents": [], "fragments": []},
        "notes",
        {"source_materials_supplied": False},
    )
    assert false_source_flag["status"] == "blocked"
    assert false_source_flag["can_proceed"] is False
    assert any(item["code"] == "missing_sources" for item in false_source_flag["gaps"])
    practice_diagnostic = build_diagnostic_assessment(
        assessment_scan,
        "practice",
        {"requested_capability": "timed_practice", "duration_minutes": 90},
    )
    assert practice_diagnostic["status"] == "ready"
    assert practice_diagnostic["can_proceed"] is True
    blocked_evaluation = build_diagnostic_assessment(
        assessment_scan,
        "practice",
        {"requested_capability": "answer_evaluation", "student_answer": "A short answer."},
    )
    assert blocked_evaluation["status"] == "blocked"
    assert any(item["code"] == "missing_evaluation_criteria" for item in blocked_evaluation["gaps"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract sources, index fragments, report readiness, and audit coverage.")
    parser.add_argument("sources", nargs="*")
    parser.add_argument(
        "--mode",
        choices=("process", "scan", "index", "readiness", "exam-format-profile", "assessment-architecture", "diagnostic"),
        default="process",
    )
    parser.add_argument("--source-scan")
    parser.add_argument("--purpose", choices=("atlas", "analysis", "notes", "practice", "essay"), default="notes")
    parser.add_argument("--task-context")
    parser.add_argument("--out")
    parser.add_argument("--asset-dir", default=".skill_assets")
    parser.add_argument("--cache-dir")
    parser.add_argument("--visual-mode", default="embedded_media")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    existing_scan = _load_scan(args.source_scan)
    task_context = _load_scan(args.task_context) or {}
    analysis_scan = existing_scan
    if analysis_scan is None and args.sources and args.mode in {"exam-format-profile", "assessment-architecture", "diagnostic"}:
        analysis_scan = build_scan(args.sources, args.asset_dir, args.visual_mode)
    if analysis_scan is not None:
        apply_source_role_overrides(analysis_scan, task_context)
    if args.mode == "scan":
        result = build_scan(args.sources, args.asset_dir, args.visual_mode)
    elif args.mode == "index":
        result = build_fragment_index(existing_scan, args.purpose)
    elif args.mode == "readiness":
        result = readiness_report(existing_scan, args.purpose)
    elif args.mode == "exam-format-profile":
        result = build_exam_format_profile(analysis_scan, args.purpose)
    elif args.mode == "assessment-architecture":
        result = build_assessment_architecture(analysis_scan, args.purpose)
    elif args.mode == "diagnostic":
        result = build_diagnostic_assessment(analysis_scan, args.purpose, task_context)
    else:
        result = process_sources(
            args.sources,
            args.asset_dir,
            args.visual_mode,
            args.purpose,
            task_context,
            args.cache_dir,
        )
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
