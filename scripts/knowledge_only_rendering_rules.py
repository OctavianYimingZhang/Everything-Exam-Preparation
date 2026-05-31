"""Shared knowledge-only public rendering rules for student-facing routes."""

from __future__ import annotations

import re
from typing import Any


FORBIDDEN_ADVISORY_PHRASES = [
    "a strong answer should",
    "answer logic",
    "exam strategy",
    "generic exam advice",
    "how to answer",
    "how to use this document",
    "integrated practical reasoning",
    "integrated reasoning",
    "not driven by question type",
    "not reliable by question type",
    "question-type dependent",
    "recommended approach",
    "recommended output route",
    "source coverage",
    "the notes are organised",
    "this document is organised",
    "use this module",
]

FORBIDDEN_ADVISORY_HEADINGS = [
    "Answer Logic",
    "Exam Strategy",
    "How To Answer This Exam",
    "How To Use This Document",
    "Integrated Practical Reasoning",
    "Integrated Reasoning",
    "Must Master",
    "Recommended Approach",
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

# Labels that often appear when a plan has been torn into slots instead of
# being rewritten as an explanatory knowledge point. These are not banned as
# single labels, but high density is a public-surface failure.
FRAGMENT_SLOT_LABELS = [
    "A280",
    "A550",
    "Binding logic",
    "Calculation chain",
    "Caveat",
    "Components",
    "Concept",
    "Design",
    "Direction",
    "Elution mechanism",
    "Enzyme choice",
    "Exclusion logic",
    "Failure mode",
    "Formula",
    "Forward primer",
    "Identity",
    "Key detail",
    "Key point",
    "Logic",
    "Mechanism",
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

# Labels that can remain visible when they genuinely prevent ambiguity.
ESSENTIAL_VISIBLE_LABELS = {
    "Equation",
    "Worked example",
    "Diagnostic pattern",
    "Control",
    "Comparison",
    "Table",
}

COLON_LABEL_RE = re.compile(r"(?im)^\s*(?:[-•*]\s*)?([A-Z][A-Za-z0-9 /+().-]{1,42})\s*:")


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


def forbidden_non_knowledge_hits(text: str) -> list[str]:
    """Return non-knowledge public-surface categories detected in text."""

    hits: list[str] = []
    for name, pattern in FORBIDDEN_NON_KNOWLEDGE_PATTERNS:
        if pattern.search(text):
            hits.append(name)
    return sorted(set(hits))


def _visible_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


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
    """Flag rigid labels and colon-slot fragmentation in public notes.

    Occasional semantic labels are acceptable. Failure means the public surface
    reads like a planning schema (``Components:``, ``Workflow:``, ``Logic:``)
    rather than a connected explanation of a knowledge point.
    """

    hits: list[str] = []
    for label in RIGID_TEMPLATE_LABELS:
        count = len(re.findall(rf"(?im)^\s*(?:[-•*]\s*)?{re.escape(label)}\s*:", text))
        if count >= threshold:
            hits.append(label)

    fragment_labels = _colon_fragment_labels(text)
    normalized_fragments = [normalized_text(label) for label in fragment_labels]
    nonessential_set = {normalized_text(label) for label in RIGID_TEMPLATE_LABELS + FRAGMENT_SLOT_LABELS}
    nonessential_hits = [label for label in normalized_fragments if label in nonessential_set]
    visible_line_count = max(1, len(_visible_lines(text)))

    # Catch the current failure mode: many different one-word slot labels that
    # look individually harmless but collectively tear a concept into fragments.
    if len(nonessential_hits) >= 8 or (len(nonessential_hits) >= 5 and len(nonessential_hits) / visible_line_count >= 0.25):
        hits.append("colon_fragment_label_density")

    for label in sorted(set(fragment_labels)):
        if normalized_text(label) in nonessential_set and fragment_labels.count(label) >= 2:
            hits.append(label)

    return sorted(set(hits))
