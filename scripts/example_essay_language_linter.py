#!/usr/bin/env python3
"""Lint complete Example Essay prose against the shared language contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None

from citation_rendering_rules import author_led_citation_hits


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")
AUTHOR_YEAR_RE = re.compile(r"\([A-Z][A-Za-z'’-]+(?:\s+et\s+al\.|\s+and\s+[A-Z][A-Za-z'’-]+)?(?:,\s*|\s+)(?:19|20)\d{2}[a-z]?\)")

CLAIM_CONNECTORS = re.compile(
    r"\b(because|therefore|consequently|as a result|depends on|regulates|drives|converts|constrains|enables|explains|links|integrates|supports|limits|whereas|although|while|thereby|so)\b",
    re.I,
)

META_OPENERS = re.compile(
    r"^\s*(this essay will|in this essay|this paragraph will|the following (essay|section|paragraph)|i will|we will)\b",
    re.I,
)

SOURCE_TRACE = [
    ("page_trace", re.compile(r"\bPages?\s+\d+\b", re.I)),
    ("slide_trace", re.compile(r"\bSlides?\s+\d+\b", re.I)),
    ("lecture_cited_source_route", re.compile(r"\blecture-cited\b", re.I)),
    ("lecture_sequence_narration", re.compile(r"\blecture sequence\b", re.I)),
    ("source_walkthrough", re.compile(r"\b(first establishes|then develops|then closes|later pages add|slide sequence)\b", re.I)),
    (
        "visible_source_role_narration",
        re.compile(
            r"\b(?:the\s+)?(?:lecture|lectures|slides?|source|chapter|uploaded\s+reading|reading\s+chapter|uploaded\s+material)\s+"
            r"(?:frames?|shows?|refines?|supports?|defines?)\b",
            re.I,
        ),
    ),
    (
        "lecture_route_narration",
        re.compile(
            r"\b(?:the\s+)?(?:lecture|lectures|slides|source|chapter|section|module)\s+(?:\d+\s+)?"
            r"(?:establishes|establish|adds|add|introduces|introduce|covers|cover|moves from|move from|develops|develop|closes with|close with)\b",
            re.I,
        ),
    ),
]

HOW_TO_WRITE = [
    ("how_to_write", re.compile(r"\b(should be written as|write this as|use these pages|turn pages|in an essay answer)\b", re.I)),
    (
        "exam_guidance_sentence",
        re.compile(
            r"\b(final\s+exam\s+thesis\s+should\s+be|exam\s+thesis\s+should\s+be|"
            r"in\s+an\s+exam\s+answer|for\s+the\s+exam|the\s+answer\s+should\s+be|"
            r"the\s+correct\s+conclusion\s+is|should\s+frame\s+this\s+as)\b",
            re.I,
        ),
    ),
    (
        "mechanical_compression_trace",
        re.compile(
            r"\b(?:compressed|compress(?:ion|ing)?|reduce(?:d)?|cut)\s+(?:by|about|around|approximately)?\s*\d{1,3}%\b|"
            r"\b(?:target|safe|lossless)\s+word[-\s]?count\b|"
            r"\b(?:safe|lossless)\s+compression\s+(?:range|budget|limit)\b",
            re.I,
        ),
    ),
]

WEAK_OPENERS = re.compile(r"^\s*(background|introduction|firstly|secondly|thirdly|to begin with)\b[:,]?", re.I)
EXAMPLE_TERMS = re.compile(r"\b(for example|case study|case|firm|company|example)\b", re.I)
EXAMPLE_TO_ARGUMENT = re.compile(r"\b(shows|demonstrates|supports|indicates|suggests|therefore|consequently|implies|evidence|illustrates)\b", re.I)
NEGATIVE_FRAMING = re.compile(r"\b(not\s+(?:a|an|the|only|merely|simply)|rather than)\b", re.I)
NOT_BUT_FRAMING = re.compile(r"\bnot\b[^.!?]{0,140}\bbut\b", re.I)
RATHER_THAN_FRAMING = re.compile(r"\brather than\b", re.I)
NEGATIVE_SENTENCE_START = re.compile(
    r"^\s*(?:The|A|An|This|That|These|Those|[A-Z][A-Za-z0-9βγα/+\-\s]{1,80})\s+"
    r"(?:is|are|was|were)\s+not\b",
    re.I,
)
POSITIVE_RESTATEMENT_START = re.compile(
    r"^\s*(?:It|This|That|They|These|Those|The\s+[A-Za-z0-9βγα/+\-]+|[A-Z][A-Za-z0-9βγα/+\-\s]{1,70})\s+"
    r"(?:is|are|was|were|functions?|acts?|operates?|transforms?|converts?|provides?|generates?|organises?)\b",
    re.I,
)
NOT_BUT_CONTRAST = re.compile(r"\b(?:is|are|was|were)\s+not\b[^.!?]{0,120}\bbut\b", re.I)
BROAD_IMPORTANCE = re.compile(r"\b(this matters|this is important|this is critical|the important point)\b", re.I)
IMPORTANCE_WITH_CONSEQUENCE = re.compile(r"\b(because|therefore|consequently|as a result|so|means that|explains|limits|enables|constrains)\b", re.I)
SUPPORT_TO_CAUSE_OVERCLAIM = re.compile(
    r"\b(?:supports?|implicates?|suggests?|is consistent with|is associated with)\b[^.!?]{0,140}\b(?:the|a|single|sole)\s+cause\b",
    re.I,
)
CHANNEL_CATALOGUE_TERMS = re.compile(
    r"\b(?:persistent\s+Na\+?|persistent\s+sodium|low-threshold\s+Ca(?:2\+|\²\+)?|low-threshold\s+calcium|"
    r"NMDA(?:-dependent)?|HCN|Ca(?:2\+|\²\+)?-dependent\s+K\+?|calcium-dependent\s+potassium|"
    r"sodium\s+current|calcium\s+current|potassium\s+current|ionic\s+conductance|conductances?)\b",
    re.I,
)
SCOPE_COLLAPSE = re.compile(
    r"\b(?:sensory\s+(?:feedback|input|reafference)\s+(?:is\s+)?(?:unnecessary|dispensable|not\s+necessary)\s+for\s+locomotion|"
    r"feedback\s+(?:is\s+)?(?:unnecessary|dispensable)\s+for\s+movement)\b",
    re.I,
)
DESCRIPTIVE_START = re.compile(
    r"^\s*[A-Z][A-Za-z0-9βγα/+\-\s]{1,45}\s+"
    r"(?:is|are|mediates?|regulates?|controls?|provides?|encodes?|expresses?|contains?|projects?|activates?|inhibits?)\b",
    re.I,
)
ANALYTIC_SENTENCE_MARKERS = re.compile(
    r"\b(because|therefore|so|whereas|although|while|thereby|this\s+(?:means|shows|demonstrates|limits|explains)|"
    r"the\s+(?:point|key\s+issue|analytical\s+point|consequence)\s+is|matters\s+because|"
    r"solves?|distinguish(?:es)?|rules?\s+out|undermines?|supports?|proves?|fails?\s+to\s+prove|"
    r"rather than|in contrast|as a result|consequently|link(?:s|ed)?\s+to)\b",
    re.I,
)
INTRO_CONCLUSION_PART_LIST = re.compile(
    r"\b(this\s+essay\s+(?:will|has)\s+(?:first|shown|argued|demonstrated)|"
    r"first(?:ly)?[,;:]|second(?:ly)?[,;:]|third(?:ly)?[,;:]|finally[,;:]|"
    r"the\s+(?:first|second|third|final)\s+(?:part|section|paragraph))\b",
    re.I,
)
EVIDENCE_CLAIM_START = re.compile(r"\b(?:strongest|decisive|key)\s+evidence\b[^.!?]{0,160}\bis\s+that\b", re.I)
RESULT_CONNECTOR = re.compile(r"^\s*(?:yet|therefore|so|this|which|showing|supporting|indicating|demonstrating)\b|\b(?:yet|therefore|showing|supporting|indicating|demonstrating|because|so|which\s+means)\b", re.I)
SETUP_LIKE_SENTENCE = re.compile(
    r"\b(experiment|experiments|preparation|preparations|trial|assay|dataset|lesion|ablation|recording|"
    r"stimulation|condition|method|model|case|example|figure|measurement|comparison|observation)\b",
    re.I,
)
CLAIM_RESTART_STOPWORDS = {
    "about",
    "after",
    "also",
    "because",
    "before",
    "between",
    "could",
    "does",
    "from",
    "have",
    "into",
    "only",
    "over",
    "same",
    "should",
    "that",
    "their",
    "there",
    "these",
    "this",
    "through",
    "under",
    "when",
    "where",
    "which",
    "while",
    "with",
    "without",
    "would",
}


@dataclass
class ParagraphRecord:
    source: str
    essay_id: str | None
    paragraph_id: str | None
    index: int
    function: str | None
    text: str
    has_lecture_anchor: bool | None = None
    is_conclusion: bool = False


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def first_sentence(text: str) -> str:
    for match in SENTENCE_RE.finditer(text.strip()):
        sentence = match.group(0).strip()
        if sentence:
            return sentence
    return text.strip()


def sentences(text: str) -> list[str]:
    return [match.group(0).strip() for match in SENTENCE_RE.finditer(text.strip()) if match.group(0).strip()]


def has_three_descriptive_sentences_without_analysis(items: list[str]) -> bool:
    streak = 0
    for sentence in items:
        if DESCRIPTIVE_START.search(sentence) and not ANALYTIC_SENTENCE_MARKERS.search(sentence):
            streak += 1
            if streak >= 3:
                return True
        else:
            streak = 0
    return False


def sentence_balance(items: list[str]) -> dict[str, Any]:
    analytic = 0
    descriptive = 0
    for sentence in items:
        if ANALYTIC_SENTENCE_MARKERS.search(sentence):
            analytic += 1
        elif words(sentence):
            descriptive += 1
    total = analytic + descriptive
    ratio = analytic / total if total else 0.0
    return {
        "sentences": total,
        "analytic_sentences": analytic,
        "descriptive_sentences": descriptive,
        "analytic_ratio": round(ratio, 3),
    }


def has_negative_then_positive_restatement(items: list[str]) -> bool:
    if len(items) < 2:
        return False
    return bool(NEGATIVE_SENTENCE_START.search(items[0]) and POSITIVE_RESTATEMENT_START.search(items[1]))


def has_fragmented_evidence_sequence(items: list[str]) -> bool:
    if len(items) < 3:
        return False
    if not EVIDENCE_CLAIM_START.search(items[0]):
        return False
    setup = items[1]
    result = items[2]
    if RESULT_CONNECTOR.search(result):
        return False
    setup_like = re.search(r"\b(experiment|experiments|preparation|preparations|trial|assay|dataset|lesion|ablation|recording|stimulation|dorsal roots?|limb|condition)\b", setup, re.I)
    return bool(setup_like and words(result))


def content_tokens(text: str) -> list[str]:
    tokens = []
    for token in words(text.lower()):
        if len(token) < 4 or token in CLAIM_RESTART_STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def has_claim_restart_after_setup(items: list[str]) -> bool:
    if len(items) < 3:
        return False
    first_terms = set(content_tokens(items[0])[:12])
    if len(first_terms) < 4:
        return False
    for idx in range(1, len(items) - 1):
        setup = items[idx]
        restart = items[idx + 1]
        if RESULT_CONNECTOR.search(restart):
            continue
        if not SETUP_LIKE_SENTENCE.search(setup):
            continue
        restart_terms = set(content_tokens(restart)[:14])
        if len(first_terms & restart_terms) >= 4:
            return True
    return False


def is_intro_or_conclusion(record: ParagraphRecord) -> bool:
    function = (record.function or "").lower()
    return record.index == 1 or "intro" in function or record.is_conclusion


def paragraph_text(paragraph: dict[str, Any]) -> str:
    if "text" in paragraph:
        return str(paragraph.get("text") or "")
    return "".join(str(run.get("text", "")) for run in paragraph.get("text_runs", []))


def is_body_paragraph(paragraph: dict[str, Any]) -> bool:
    return not (paragraph.get("is_title") or paragraph.get("is_subtitle") or paragraph.get("is_heading"))


def load_plan_records(path: Path) -> list[ParagraphRecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        essays = data
    elif isinstance(data.get("essays"), list):
        essays = data["essays"]
    else:
        essays = [data]

    records: list[ParagraphRecord] = []
    for essay in essays:
        body = [p for p in essay.get("paragraphs", []) if is_body_paragraph(p)]
        for idx, paragraph in enumerate(body, start=1):
            text = paragraph_text(paragraph)
            function = paragraph.get("function")
            records.append(
                ParagraphRecord(
                    source=str(path),
                    essay_id=essay.get("essay_id"),
                    paragraph_id=paragraph.get("paragraph_id"),
                    index=idx,
                    function=function,
                    text=text,
                    has_lecture_anchor=bool(paragraph.get("lecture_anchors")),
                    is_conclusion=bool(function and "conclusion" in str(function).lower()),
                )
            )
    return records


def load_text_records(path: Path) -> list[ParagraphRecord]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    parts = [part.strip() for part in re.split(r"\n\s*\n", raw) if part.strip()]
    return [
        ParagraphRecord(source=str(path), essay_id=None, paragraph_id=None, index=idx, function=None, text=part, is_conclusion=bool(re.match(r"^\s*conclusion\b", part, re.I)))
        for idx, part in enumerate(parts, start=1)
    ]


def source_map_for_docx(path: Path) -> dict[str, Any] | None:
    candidates = [
        path.with_name(path.stem.split("_")[0] + "_source_map.json"),
        path.with_name(path.stem + "_source_map.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return None


def load_docx_records(path: Path) -> list[ParagraphRecord]:
    if Document is None:
        raise RuntimeError("python-docx is required to lint .docx files")
    doc = Document(path)
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    source_map = source_map_for_docx(path)
    if source_map and len(source_map.get("paragraphs", [])) == len(parts):
        records = []
        body_index = 0
        for visible_index, (text, paragraph) in enumerate(zip(parts, source_map.get("paragraphs", [])), start=1):
            if paragraph.get("kind") != "body":
                continue
            body_index += 1
            function = paragraph.get("function")
            records.append(
                ParagraphRecord(
                    source=str(path),
                    essay_id=source_map.get("essay_id"),
                    paragraph_id=paragraph.get("paragraph_id"),
                    index=body_index,
                    function=function,
                    text=text,
                    has_lecture_anchor=bool(paragraph.get("lecture_anchors")),
                    is_conclusion=bool(function and "conclusion" in str(function).lower()),
                )
            )
        return records

    body = []
    for idx, paragraph in enumerate(parts, start=1):
        if idx == 1:
            continue
        if idx == 2 and re.match(r"^\s*(explain|discuss|compare|evaluate|describe|how|why|what)\b", paragraph, re.I):
            continue
        if re.match(r"^\d+(?:\.\d+)*\s+\S+", paragraph):
            continue
        body.append(paragraph)
    return [
        ParagraphRecord(source=str(path), essay_id=None, paragraph_id=None, index=idx, function=None, text=part, is_conclusion=bool(re.match(r"^\s*conclusion\b", part, re.I)))
        for idx, part in enumerate(body, start=1)
    ]


def load_fixture_records(path: Path) -> tuple[list[ParagraphRecord], dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records: list[ParagraphRecord] = []
    expectations: dict[str, str] = {}
    for idx, case in enumerate(data.get("cases", []), start=1):
        case_id = case.get("id", f"case_{idx}")
        text = case.get("text", "")
        function = case.get("function")
        expectations[case_id] = str(case.get("expected", "")).lower()
        records.append(
            ParagraphRecord(
                source=str(path),
                essay_id=case_id,
                paragraph_id=case_id,
                index=idx,
                function=function,
                text=text,
                has_lecture_anchor=case.get("has_lecture_anchor"),
                is_conclusion=bool(function and "conclusion" in str(function).lower()),
            )
        )
    return records, expectations


def hit_patterns(text: str, patterns: Iterable[tuple[str, re.Pattern[str]]]) -> list[dict[str, str]]:
    hits = []
    for name, pattern in patterns:
        match = pattern.search(text)
        if match:
            hits.append({"type": name, "phrase": match.group(0)})
    return hits


def lint_paragraph(record: ParagraphRecord, min_words: int, max_words: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    text = record.text.strip()
    count = len(words(text))
    first = first_sentence(text)

    for hit in hit_patterns(text, SOURCE_TRACE + HOW_TO_WRITE):
        failures.append({"type": hit["type"], "phrase": hit["phrase"]})
    for phrase in author_led_citation_hits(text):
        failures.append({"type": "author_led_citation_prose", "phrase": phrase})
    if META_OPENERS.search(first):
        failures.append({"type": "generic_metacommentary_opener", "phrase": first[:120]})
    if record.has_lecture_anchor is False:
        failures.append({"type": "body_paragraph_missing_lecture_anchor"})
    if count < min_words:
        warnings.append({"type": "short_paragraph", "word_count": count})
    if count > max_words:
        warnings.append({"type": "overlong_paragraph", "word_count": count})
    if WEAK_OPENERS.search(first):
        warnings.append({"type": "weak_topic_label_opener", "phrase": first[:120]})
    if not CLAIM_CONNECTORS.search(text) and count >= min_words:
        warnings.append({"type": "no_visible_mechanism_or_inference_connector"})

    sentence_items = sentences(text)
    if has_negative_then_positive_restatement(sentence_items):
        failures.append({"type": "negative_opener_before_positive_claim", "phrase": " ".join(sentence_items[:2])[:220]})
    if NOT_BUT_CONTRAST.search(first):
        warnings.append({"type": "negative_but_opener_consider_direct_claim", "phrase": first[:160]})
    not_but_count = len(NOT_BUT_FRAMING.findall(text))
    rather_than_count = len(RATHER_THAN_FRAMING.findall(text))
    if not_but_count >= 2 or (not_but_count + rather_than_count) >= 4:
        failures.append({"type": "repeated_not_but_or_rather_than_framing", "not_but": not_but_count, "rather_than": rather_than_count})
    elif not_but_count + rather_than_count >= 2:
        warnings.append({"type": "contrast_framing_density_check", "not_but": not_but_count, "rather_than": rather_than_count})
    if has_fragmented_evidence_sequence(sentence_items):
        failures.append({"type": "fragmented_evidence_sequence", "phrase": " ".join(sentence_items[:3])[:260]})
    if has_claim_restart_after_setup(sentence_items):
        failures.append({"type": "claim_restart_after_setup", "phrase": " ".join(sentence_items[:3])[:260]})
    if is_intro_or_conclusion(record) and INTRO_CONCLUSION_PART_LIST.search(text):
        failures.append({"type": "intro_or_conclusion_lists_parts", "phrase": INTRO_CONCLUSION_PART_LIST.search(text).group(0)})
    if is_intro_or_conclusion(record) and text.count(";") >= 4 and sentence_balance(sentence_items)["analytic_sentences"] <= 1:
        warnings.append({"type": "intro_or_conclusion_summary_list_needs_synthesis"})

    for sentence in sentences(text):
        if len(AUTHOR_YEAR_RE.findall(sentence)) >= 3:
            failures.append({"type": "citation_stack", "phrase": sentence[:180]})

    example_count = len(EXAMPLE_TERMS.findall(text))
    if example_count >= 3 and not EXAMPLE_TO_ARGUMENT.search(text):
        failures.append({"type": "example_overload_without_inference", "example_terms": example_count})
    if SUPPORT_TO_CAUSE_OVERCLAIM.search(text):
        failures.append({"type": "citation_strength_overclaim", "phrase": SUPPORT_TO_CAUSE_OVERCLAIM.search(text).group(0)[:180]})
    channel_terms = {match.group(0).lower() for match in CHANNEL_CATALOGUE_TERMS.finditer(text)}
    if len(channel_terms) >= 4:
        failures.append({"type": "unnecessary_channel_catalogue", "terms": sorted(channel_terms)[:8]})
    if SCOPE_COLLAPSE.search(text):
        failures.append({"type": "compression_changed_claim_scope", "phrase": SCOPE_COLLAPSE.search(text).group(0)})
    if has_three_descriptive_sentences_without_analysis(sentence_items):
        failures.append({"type": "descriptive_list_without_analysis"})
    if len(NEGATIVE_FRAMING.findall(text)) >= 4:
        failures.append({"type": "repeated_negative_framing"})
    elif len(NEGATIVE_FRAMING.findall(text)) >= 2:
        warnings.append({"type": "repeated_negative_framing"})
    if BROAD_IMPORTANCE.search(text) and not IMPORTANCE_WITH_CONSEQUENCE.search(text):
        warnings.append({"type": "broad_importance_without_specific_consequence"})

    if record.is_conclusion:
        if AUTHOR_YEAR_RE.search(text):
            failures.append({"type": "conclusion_adds_citation_or_new_evidence"})
        if re.search(r"\b(for example|new evidence|another example)\b", text, re.I):
            failures.append({"type": "conclusion_adds_new_example"})

    return failures, warnings


def record_payload(record: ParagraphRecord, issues: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source": record.source,
        "essay_id": record.essay_id,
        "paragraph_id": record.paragraph_id,
        "paragraph_index": record.index,
        "function": record.function,
        "issues": issues,
        "preview": record.text[:240].replace("\n", " "),
    }


def lint_records(records: list[ParagraphRecord], min_words: int = 35, max_words: int = 280) -> dict[str, Any]:
    failures = []
    warnings = []
    all_sentences: list[str] = []
    for record in records:
        record_failures, record_warnings = lint_paragraph(record, min_words=min_words, max_words=max_words)
        all_sentences.extend(sentences(record.text))
        if record_failures:
            failures.append(record_payload(record, record_failures))
        if record_warnings:
            warnings.append(record_payload(record, record_warnings))
    balance = sentence_balance(all_sentences)
    if balance["sentences"] >= 5:
        ratio = balance["analytic_ratio"]
        if ratio < 0.35:
            failures.append(
                {
                    "source": records[0].source if records else None,
                    "essay_id": records[0].essay_id if records else None,
                    "paragraph_id": None,
                    "paragraph_index": None,
                    "function": "essay_level_language_balance",
                    "issues": [{"type": "essay_descriptive_analytic_imbalance_low_analytic", **balance}],
                    "preview": "",
                }
            )
        elif ratio < 0.4 or ratio > 0.7:
            warnings.append(
                {
                    "source": records[0].source if records else None,
                    "essay_id": records[0].essay_id if records else None,
                    "paragraph_id": None,
                    "paragraph_index": None,
                    "function": "essay_level_language_balance",
                    "issues": [{"type": "essay_descriptive_analytic_balance_outside_target", **balance}],
                    "preview": "",
                }
            )
    return {
        "pass": not failures,
        "fail_reasons": sorted({issue["type"] for row in failures for issue in row["issues"]}),
        "counts": {
            "paragraphs": len(records),
            "failing_paragraphs": len(failures),
            "warning_paragraphs": len(warnings),
            **balance,
        },
        "failures": failures,
        "warnings": warnings[:100],
    }


def fixture_report(path: Path, min_words: int, max_words: int) -> dict[str, Any]:
    records, expectations = load_fixture_records(path)
    cases = []
    for record in records:
        result = lint_records([record], min_words=min_words, max_words=max_words)
        expected = expectations.get(record.paragraph_id or "", "")
        expected_pass = expected == "pass" if expected in {"pass", "fail"} else None
        matched = expected_pass is None or result["pass"] == expected_pass
        cases.append(
            {
                "case_id": record.paragraph_id,
                "expected": expected,
                "actual_pass": result["pass"],
                "matched": matched,
                "fail_reasons": result["fail_reasons"],
            }
        )
    return {
        "pass": all(case["matched"] for case in cases),
        "cases": cases,
        "counts": {
            "cases": len(cases),
            "matched": sum(1 for case in cases if case["matched"]),
            "mismatched": sum(1 for case in cases if not case["matched"]),
        },
    }



def self_test() -> dict[str, Any]:
    good_records = [
        ParagraphRecord(
            source="inline_self_test",
            essay_id="EE_INLINE",
            paragraph_id="P1",
            index=1,
            function="argument",
            text=(
                "Competitive inhibition changes enzyme behaviour because inhibitor and substrate compete for the same active site, "
                "so the substrate concentration needed to reach a given rate rises while the maximal catalytic capacity remains available. "
                "This distinction matters because it separates binding-site competition from enzyme loss, and it lets the answer infer mechanism from a shifted Km without claiming a changed Vmax."
            ),
            has_lecture_anchor=True,
        )
    ]
    bad_records = [
        ParagraphRecord(
            source="inline_self_test",
            essay_id="EE_INLINE",
            paragraph_id="P1",
            index=1,
            function="argument",
            text="This essay will discuss the topic. Slides 1 to 3 show background. The answer should be written as a summary.",
            has_lecture_anchor=False,
        )
    ]
    good = lint_records(good_records, 20, 220)
    bad = lint_records(bad_records, 20, 220)
    failures = []
    if not good.get("pass"):
        failures.append({"type": "good_inline_case_rejected", "result": good})
    if bad.get("pass"):
        failures.append({"type": "bad_inline_case_accepted", "result": bad})
    return {"pass": not failures, "good": good, "bad": bad, "failures": failures}

def main() -> int:
    parser = argparse.ArgumentParser(description="Lint complete Example Essay language quality.")
    parser.add_argument("--plan", action="append", type=Path, default=[])
    parser.add_argument("--text", action="append", type=Path, default=[])
    parser.add_argument("--docx", action="append", type=Path, default=[])
    parser.add_argument("--fixture", action="append", type=Path, default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--min-words", type=int, default=35)
    parser.add_argument("--max-words", type=int, default=280)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0 if result["pass"] else 1

    reports = []
    overall_pass = True

    for path in args.plan:
        try:
            report = lint_records(load_plan_records(path), args.min_words, args.max_words)
        except Exception as exc:
            report = {"pass": False, "fail_reasons": ["read_error"], "error": str(exc)}
        report.update({"type": "plan", "path": str(path)})
        reports.append(report)
        overall_pass = overall_pass and bool(report["pass"])

    for path in args.text:
        try:
            report = lint_records(load_text_records(path), args.min_words, args.max_words)
        except Exception as exc:
            report = {"pass": False, "fail_reasons": ["read_error"], "error": str(exc)}
        report.update({"type": "text", "path": str(path)})
        reports.append(report)
        overall_pass = overall_pass and bool(report["pass"])

    for path in args.docx:
        try:
            report = lint_records(load_docx_records(path), args.min_words, args.max_words)
        except Exception as exc:
            report = {"pass": False, "fail_reasons": ["read_error"], "error": str(exc)}
        report.update({"type": "docx", "path": str(path)})
        reports.append(report)
        overall_pass = overall_pass and bool(report["pass"])

    for path in args.fixture:
        try:
            report = fixture_report(path, args.min_words, args.max_words)
        except Exception as exc:
            report = {"pass": False, "fail_reasons": ["read_error"], "error": str(exc)}
        report.update({"type": "fixture", "path": str(path)})
        reports.append(report)
        overall_pass = overall_pass and bool(report["pass"])

    if not reports:
        reports.append({"type": "none", "pass": False, "fail_reasons": ["no_inputs"]})
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
