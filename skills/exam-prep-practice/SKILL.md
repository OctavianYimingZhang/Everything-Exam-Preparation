---
name: exam-prep-practice
description: Prepare and analyse exam practice from past papers, questions, answers, mark schemes, and course material using one-pass extraction and bounded result checks.
---

# Exam Prep Practice

Build the requested question-based preparation artifact from supplied evidence.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Identify the requested Practice capability from the user's wording.
2. Extract course and question material once with `scripts/extract_sources.py` when needed. Reuse the returned `ExamFormatProfile`, `AssessmentArchitecture`, and `DiagnosticAssessment`; ask only for a blocking gap.
3. Use `scripts/exam_mode_tools.py` for question extraction, recurrence analysis, worked solutions, question solving, question organisation, blueprints, answer evaluation, and timed practice.
4. Ask only for an indispensable missing input such as the target question, student answer, explicit evaluation criteria, blueprint scope, or timed duration.
5. Preserve source locators only where they assist the requested output.
6. Produce the requested chat, structured data, or DOCX artifact once, then perform one bounded sanity check for existence, format, expected sections, and unresolved errors. Do not add a render or iterative review loop.

## Capability Selection

- MCQ and short-answer preparation: concise lecture-order exam-needed knowledge from actual papers.
- Long-answer, practical, and data work: question demand, relevant knowledge, method, reasoning, answer structure, and example response.
- Worked solutions: interpretation, givens, target, method, steps, units, assumptions, result, and meaning.
- Question solving: explain the target question and add closely matched transfer practice.
- Question organisation: place supplied questions in lecture or knowledge-unit order with useful provenance.
- Assessment blueprint: map evidenced coverage and derive weights only from explicit marks or assessment documentation.
- Answer evaluation: return `correct`, `partial`, `incorrect`, `contradicted`, or `missing`; estimate a mark only when explicit criteria support it.
- Timed practice: allocate an explicit duration across a source-grounded blueprint.

Return the public result envelope from `references/input_and_evidence_protocol.md`. Report material gaps precisely and name the actual output format and bounded QA state of any generated artifact.
