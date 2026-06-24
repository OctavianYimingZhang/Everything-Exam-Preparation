---
name: exam-prep-short-answer
description: Produce short-answer or SAQ Exam Type Related preparation from course material, Past Papers, Mock Papers, official exam papers, mark schemes, definitions, list/state prompts, or answer fragments, with a result-only recurrence report of high-frequency knowledge points.
---

# Short Answer Preparation

Create a short-answer Specific Research Report as a separate output after `exam-prep-index` has confirmed the short-answer route. Use this Skill for SAQ, definition, list, state, describe briefly, or mark-point-oriented preparation.

Default public output is English. Use Chinese, bilingual, or multiple-language output only when the user explicitly asks for it. User-supplied bilingual examples are format references and do not change the language default.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/exam_prep_notes_protocol.md` only when the index confirmed Notes or existing Notes need to be referenced

Use `scripts/exam_mode_tools.py`, `scripts/plan_workflow.py`, and `scripts/build_review_questions.py` for extraction, route planning, and human review.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Short Answer output. Confirm the Short Answer route, Material type/source roles, Notes generation choice, and Short Answer report choice before writing.

## Workflow

1. Extract SAQ-style prompts, subquestions, mark schemes, answer fragments, definitions, and source context.
2. Treat every SAQ subquestion, subpart, and mark-point prompt as an independent question record.
3. Use only Past Papers, Mock Papers, and official exam papers for high-frequency recurrence analysis. Do not count ordinary Practice Material toward recurrence.
4. Match each question record to the most direct lecture knowledge unit and exam demand that decide the answer.
5. Cluster recurring questions only when the same or clearly explicit knowledge unit, direct exam demand, shared specific terms, and compatible answer-operation pattern all match.
6. Build a result-only report in lecture order, written as concise exam-needed knowledge points rather than a field-by-field template, answer walkthrough, or Notes-style teaching document. Keep source evidence, recurrence calculation, matching debug, and workflow steps internal.
7. Use the confirmed review state before writing public output if this Skill was invoked directly without `exam-prep-index`.

## Output Contract

Produce a separate short-answer Specific Research Report unless the user asks for chat output. The public report should follow the user's reference-document style: Lecture heading, numbered knowledge-point title, concise exam-needed knowledge-point content, and a short exam scope line when useful. Do not use template labels such as definition or concept core, expected mark points, concise answer wording, or missing-mark traps. Do not expand into Notes-style teaching or full answer walkthroughs.

Use concise exam-ready knowledge-point wording. Keep the output narrower than Notes: it should identify what the student needs to know for recurring SAQ prompts, not teach the full lecture or write full answer walkthroughs.
