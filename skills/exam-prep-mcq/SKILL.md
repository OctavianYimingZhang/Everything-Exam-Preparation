---
name: exam-prep-mcq
description: Produce MCQ or SBA Exam Type Related preparation from course material, practice questions, answer keys, mark schemes, or past papers, with correct reasoning, plausible wrong statements, and question-derived high-frequency knowledge points.
---

# MCQ Preparation

Create an MCQ-focused Specific Research Report as a separate output after `exam-prep-index` has confirmed the MCQ route. Use this Skill for multiple-choice, SBA, true/false, distractor, or answer-key-driven preparation.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/exam_prep_notes_protocol.md` only when the index confirmed Notes or existing Notes need to be referenced

Use `scripts/exam_mode_tools.py`, `scripts/plan_workflow.py`, and `scripts/build_review_questions.py` for extraction, route planning, and human review.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Workflow

1. Extract MCQ/SBA items, answer keys, option text, and surrounding lecture/source context.
2. Preserve source order where possible.
3. Identify the tested point, correct reasoning, plausible wrong statement, and why it is wrong.
4. Derive high-frequency knowledge points for the add-on from recurring question signals.
5. Confirm the final output set before writing public output if this Skill was invoked directly without `exam-prep-index`.

## Output Contract

Produce a separate MCQ Specific Research Report unless the user explicitly asks for chat output. Include source questions in lecture order, tested point, MCQ wording, correct reasoning, plausible wrong statement, why it is wrong, and question-derived high-frequency knowledge points for the report.

Do not let MCQ coverage replace Notes coverage. Practice material can calibrate add-on emphasis while Notes coverage still comes from the full course knowledge-unit map.
