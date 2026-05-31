"""Shared knowledge-only public rendering rules for student-facing routes."""

from __future__ import annotations

import re
from typing import Any


FORBIDDEN_ADVISORY_PHRASES = [
    "a strong answer should",
    "all unit sections are separated",
    "answer logic",
    "exam strategy",
    "generic exam advice",
    "how to answer",
    "how to use this document",
    "included unit files",
    "integrated practical reasoning",
    "integrated reasoning",
    "lecture/practical facts come from",
    "local course folders listed in this thread",
    "not driven by question type",
    "not reliable by question type",
    "past papers are used only",
    "prior compiled preview material",
    "question-type dependent",
    "recommended approach",
    "recommended output route",
    "selected route",
    "source coverage",
    "source limits",
    "source rules",
    "source role map",
    "source scale budget",
    "this pack uses only",
    "the notes are organised",
    "this document is organised",
    "use this module",
    "workflow plan",
]

FORBIDDEN_ADVISORY_HEADINGS = [
    "Answer Logic",
    "Exam Strategy",
    "How To Answer This Exam",
    "How To Use This Document",
    "Included Unit Files",
    "Integrated Practical Reasoning",
    "Integrated Reasoning",
    "Must Master",
    "Recommended Approach",
    "Selected Route",
    "Source Coverage",
    "Source Limits",
    "Source Rules",
    "Source Role Map",
    "Source Scale Budget",
    "Workflow Plan",
    "What This Lecture Is About",
    "What This Module Explains",
]

FORBIDDEN_NON_KNOWLEDGE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "source_route_narration",
        re.compile(r"\b(?:this|the|first|second|third|next|final)\s+slide\s+(?:shows|says|mentions|illustrates|explains)\b", re.I),
    ),
    (
        "source_route_narration",
        re.compile(r"\b(?:according to|on|in)\s+(?:the\s+)?(?:slide|slides|ppt|page|notes)\b", re.I),
    ),
    (
        "source_route_narration",
        re.compile(r"\b(?:slide|slides|ppt|page)\s+(?:shows|say|says|mention|mentions|illustrate|illustrates)\b", re.I),
    ),
    (
        "public_source_workflow_scaffold",
        re.compile(r"\b(?:Source\s+Rules|Included\s+Unit\s+Files|Source\s+Coverage|Source\s+Limits|Course\s+folders\s+listed\s+in\s+this\s+thread|local\s+extracted\s+materials|extracted\s+characters|PDF/page\s+sources|slide\s+sources|legacy\s+PPT\s+strings)\b", re.I),
    ),
    (
        "public_workflow_or_schema_scaffold",
        re.compile(r"\b(?:Selected\s+Route|Workflow\s+Plan|SourceRoleMap|Source\s+Role\s+Map|NonKnowledgeNoiseFilter|SourceDistillationPass|SourceScaleBudget|Source\s+Scale\s+Budget|Coverage\s+Floor(?:\s+Status)?|KnowledgeSurfaceContract|ExaminableKnowledgeUnit|CourseModule|QA\s+Gate|Generation\s+Process)\b", re.I),
    ),
    (
        "public_workflow_or_schema_scaffold",
        re.compile(r"\b(?:route\s+selected|selected\s+route|workflow\s+used|generation\s+workflow|internal\s+workflow|coverage\s+floor\s+(?:passes|fails|status)|public\s+surface\s+gate)\b", re.I),
    ),
    (
        "public_source_workflow_scaffold",
        re.compile(r"\b(?:All\s+Unit\s+sections\s+are\s+separated|lecture/practical\s+facts\s+come\s+from|prior\s+compiled\s+preview\s+material\s+was\s+excluded|Past\s+papers\s+(?:are|were)\s+used\s+only)\b", re.I),
    ),
    (
        "ai_process_or_provenance",
        re.compile(r"\b(?:AI|ChatGPT)\s+(?:generated|created|extracted|used|summarised|summarized)\b", re.I),
    ),
    (
        "ai_process_or_provenance",
        re.compile(r"\bI\s+(?:extracted|used|generated|created|omitted|excluded|did not include|included)\b", re.I),
    ),
    (
        "ai_process_or_provenance",
        re.compile(r"\bEnglish\s+explanations\s+extracted\s+from\b", re.I),
    ),
    (
        "audit_trace",
        re.compile(r"\b(?:source\s+anchor|source\s+map|qa\s+flag|run\s+manifest|lineage|evidence\s+score|confidence\s+band)\b", re.I),
    ),
    (
        "evidence_justification_trace",
        re.compile(r"\b(?:evidence\s+used|coverage\s+note|extraction\s+quality|ELM\s+should\s+be\s+checked)\b", re.I),
    ),
    (
        "admin_logistics_noise",
        re.compile(r"\b(?:Unit\s+Attendance|SEAtS|Mentimeter|QR\s+code|Blackboard|SoftChalk|Unit\s+Assessment|Meet\s+the\s+Staff|Unit\s+Coordinator|office\s+hours|Lecture\s+Theatre|live\s+face[- ]to[- ]face|closed\s+book|coursework\s*-?\s*\d+%|End\s+of\s+Semester\s+Exam|available\s+in\s+(?:Main\s+)?Library)\b", re.I),
    ),
    (
        "admin_contact_noise",
        re.compile(r"(?:\b(?:Tel|Telephone|Phone|Location)\s*:|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.I),
    ),
]

RIGID_TEMPLATE_LABELS = [
    "Application",
    "Calculation logic",
    "Definition",
    "Definitions",
    "Graph logic",
    "Interpretation",
    "Limitation",
    "Principle",
]

FRAGMENT_SLOT_LABELS = [
    "A280",
    "A550",
    "Binding logic",
    "Calculation chain",
    "Caveat",
    "Components",
    "Concept",
    "Core knowledge spans",
    "Design",
    "Direction",
    "Elution mechanism",
    "Enzyme choice",
    "Exclusion logic",
    "Failure mode",
    "Formula",
    "Forward primer",
    "High-Yield Knowledge",
    "Identity",
    "Key detail",
    "Key point",
    "Logic",
    "Mechanism",
    "Practice Operations",
    "Protein charge",
    "Purpose",
    "Readout",
    "Reason",
    "Redox logic",
    "Reverse primer",
    "Rule",
    "Safety",
    "Timing",
    "Unit logic",
    "Values",
    "Variables",
    "Workflow",
]

ESSENTIAL_VISIBLE_LABELS = {
    "Equation",
    "Worked example",
    "Diagnostic pattern",
    "Control",
    "Comparison",
    "Table",
}

COLON_LABEL_RE = re.compile(r"(?im)^\s*(?:[-•*]\s*)?([A-Z][A-Za-z0-9 /+().-]{1,42})\s*:")
ARROW_CHAIN_RE = re.compile(r"(?m)^.{0,220}(?:->|→).{0,220}(?:->|→).*$")
RAW_BULLET_RE = re.compile(r"^\s*(?:[-•*]||◦|▪|▫)\s+")
FILE_EXTENSION_RE = re.compile(r"\b(?:pptx?|pdf|docx?|pptm)\b", re.I)
UNIT_CODE_RE = re.compile(r"\b(?:BIOL|CHEM)\d{5}\b", re.I)


def normalized_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").casefold().replace("–", "-").replace("—", "-")).strip()


def forbidden_advisory_phrase_hits(text: str) -> list[str]:
    normalized = normalized_text(text)
    return [phrase for phrase in FORBIDDEN_ADVISORY_PHRASES if normalized_text(phrase) in normalized]


def forbidden_advisory_heading_hits(text: str) -> list[str]:
    hits: list[str] = []
    for heading in FORBIDDEN_ADVISORY_HEADINGS:
        if re.search(rf"(?im)^\s*(?:#+\s*)?{re.escape(heading)}\s*:?\s*$", text):
            hits.append(heading)
    return hits


def _visible_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def forbidden_non_knowledge_hits(text: str) -> list[str]:
    """Return non-knowledge public-surface categories detected in text."""

    hits: list[str] = []
    for name, pattern in FORBIDDEN_NON_KNOWLEDGE_PATTERNS:
        if pattern.search(text):
            hits.append(name)

    lines = _visible_lines(text)
    first_block = "\n".join(lines[:100])
    if "Core knowledge spans" in first_block and (first_block.count(";") >= 3 or len(FILE_EXTENSION_RE.findall(first_block)) >= 2):
        hits.append("course_map_file_title_dump")
    if "Course Knowledge Map" in first_block and len([line for line in lines[:80] if re.search(r"\b(?:Lecture|Module|slides?|handout|presentation|ppt|source|Unit\s+Files)\b", line, re.I)]) >= 8:
        hits.append("course_map_file_title_dump")
    if "Included Unit Files" in first_block and len(UNIT_CODE_RE.findall(first_block)) >= 2:
        hits.append("multi_unit_inventory_in_public_output")
    if len(UNIT_CODE_RE.findall(first_block)) >= 8 and re.search(r"(?im)^\s*[-•*]\s*(?:BIOL|CHEM)\d{5}\b", first_block):
        hits.append("multi_unit_inventory_in_public_output")

    return sorted(set(hits))


def _colon_fragment_labels(text: str) -> list[str]:
    labels: list[str] = []
    essential = {normalized_text(label) for label in ESSENTIAL_VISIBLE_LABELS}
    for match in COLON_LABEL_RE.finditer(text):
        label = match.group(1).strip()
        if normalized_text(label) in essential:
            continue
        labels.append(label)
    return labels


def repeated_template_label_hits(text: str, threshold: int = 4) -> list[str]:
    """Flag rigid labels, arrow chains, raw bullet dumps and colon-slot fragmentation."""

    hits: list[str] = []
    for label in RIGID_TEMPLATE_LABELS:
        count = len(re.findall(rf"(?im)^\s*(?:[-•*]\s*)?{re.escape(label)}\s*:", text))
        if count >= threshold:
            hits.append(label)

    fragment_labels = _colon_fragment_labels(text)
    normalized_fragments = [normalized_text(label) for label in fragment_labels]
    nonessential_set = {normalized_text(label) for label in RIGID_TEMPLATE_LABELS + FRAGMENT_SLOT_LABELS}
    nonessential_hits = [label for label in normalized_fragments if label in nonessential_set]
    lines = _visible_lines(text)
    visible_line_count = max(1, len(lines))

    if len(nonessential_hits) >= 8 or (len(nonessential_hits) >= 5 and len(nonessential_hits) / visible_line_count >= 0.25):
        hits.append("colon_fragment_label_density")

    for label in sorted(set(fragment_labels)):
        if normalized_text(label) in nonessential_set and fragment_labels.count(label) >= 2:
            hits.append(label)

    if ARROW_CHAIN_RE.search(text):
        hits.append("arrow_chain_fragmentation")

    bullet_lines = [line for line in lines if RAW_BULLET_RE.search(line)]
    if len(bullet_lines) >= 18 and len(bullet_lines) / visible_line_count >= 0.35:
        hits.append("raw_slide_bullet_dump")

    short_fragment_lines = [line for line in lines if len(line.split()) <= 3 and not line.endswith(('.', ':', ';'))]
    if len(short_fragment_lines) >= 25 and len(short_fragment_lines) / visible_line_count >= 0.25:
        hits.append("ocr_fragment_dump")

    return sorted(set(hits))
