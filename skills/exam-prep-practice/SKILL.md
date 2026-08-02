---
name: exam-prep-practice
description: Prepare and analyse exam practice from past papers, question sets, student answers, mark schemes, and course material. Covers MCQ, short answer, long answer, practical and data questions, worked solutions, question solving and organisation, assessment blueprints, answer evaluation, and timed practice.
---

# Exam Prep Practice

Build the requested question-based preparation artifact from supplied evidence.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Identify the requested Practice capability from the user's wording.
2. Extract course and question material with `scripts/extract_sources.py`, calling its Practice diagnostic directly when the Router is not involved. Use the returned `ExamFormatProfile`, `AssessmentArchitecture`, and `DiagnosticAssessment`; ask only for a gap that blocks the requested capability.
3. Use `scripts/exam_mode_tools.py` for question extraction, recurrence analysis, worked solutions, question solving, question organisation, blueprints, concept-and-negation-aware answer evaluation, and timed practice.
4. Ask only for an indispensable missing input: the target question, student answer, evaluation criteria, blueprint scope, or timed duration.
5. Preserve source page, slide, and time locators where they help verification.
6. Produce the requested chat, structured data, or DOCX artifact and verify it.

## Capability Selection

- MCQ and short-answer preparation: concise lecture-order exam-needed knowledge from actual papers.
- Long-answer, practical, and data work: question demand, relevant knowledge, method, reasoning, answer structure, and example response.
- Worked solutions: interpretation, givens, target, method, steps, units, assumptions, result, and meaning.
- Question solving: explain the target question and add closely matched transfer practice.
- Question organisation: place supplied questions in lecture or knowledge-unit order with provenance.
- Assessment blueprint: map evidenced coverage and derive weights only from explicit marks or assessment documentation.
- Answer evaluation: compare concepts and their asserted or negated relationships against explicit criteria, returning `correct`, `partial`, `incorrect`, `contradicted`, or `missing`; estimate a mark only when an explicit rubric or criterion marks support it.
- Timed practice: allocate an explicit duration across a source-grounded blueprint.

Return the public result envelope from `references/input_and_evidence_protocol.md`. Preserve internal diagnostic and criterion statuses, report material gaps explicitly, and name the actual output format and QA state of any generated artifact.
