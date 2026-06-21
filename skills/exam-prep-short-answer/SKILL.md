---
name: exam-prep-short-answer
description: Produce short-answer or SAQ Exam Type Related preparation from course material, past papers, practice questions, mark schemes, definitions, list/state prompts, or answer fragments.
---

# Short Answer Preparation

Create a short-answer Specific Research Report as a separate output after `exam-prep-index` has confirmed the short-answer route. Use this Skill for SAQ, definition, list, state, describe briefly, or mark-point-oriented preparation.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/exam_prep_notes_protocol.md` only when the index confirmed Notes or existing Notes need to be referenced

Use `scripts/exam_mode_tools.py`, `scripts/plan_workflow.py`, and `scripts/build_review_questions.py` for extraction, route planning, and human review.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Workflow

1. Extract SAQ-style prompts, mark schemes, answer fragments, definitions, and source context.
2. Keep question order aligned with lecture/source order when possible.
3. Convert each item into definition, mark points, explain sentence, and example answer.
4. Identify recurring short-answer knowledge points for the add-on.
5. Confirm Exam type, Material type, and output set before writing public output if this Skill was invoked directly without `exam-prep-index`.

## Output Contract

Produce a separate short-answer Specific Research Report unless the user asks for chat output. Include source question, definition, mark points, explain sentence, example answer, and question-derived high-frequency knowledge points for the report.

Use concise exam-ready wording, but keep enough explanation for the student to understand why the mark points are correct.
