---
name: exam-prep-mcq
description: Produce MCQ or SBA Exam Type Related preparation from course material, answer keys, mark schemes, Past Papers, Mock Papers, or official exam papers, with a result-only recurrence report of high-frequency knowledge points.
---

# MCQ Preparation

Create an MCQ-focused Specific Research Report as a separate output after `exam-prep-index` has confirmed the MCQ route. Use this Skill for multiple-choice, SBA, true/false, distractor, or answer-key-driven preparation.

Default public output is English. Use Chinese, bilingual, or multiple-language output only when the user explicitly asks for it. User-supplied bilingual examples are format references and do not change the language default.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/exam_prep_notes_protocol.md` only when the index confirmed Notes or existing Notes need to be referenced

Use `scripts/exam_mode_tools.py`, `scripts/plan_workflow.py`, and `scripts/build_review_questions.py` for extraction, route planning, and human review.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Workflow

1. Extract MCQ/SBA items, answer keys, option text, and surrounding lecture/source context.
2. Use only Past Papers, Mock Papers, and official exam papers for high-frequency recurrence analysis. Do not count ordinary Practice Material toward recurrence.
3. Match each question to the most direct lecture knowledge unit and exam demand that decide the answer.
4. Cluster recurring questions only when the same or clearly explicit knowledge unit, direct exam demand, shared specific terms, and compatible distractor or answer-operation pattern all match.
5. Build a result-only report in lecture order, written as concise exam-needed knowledge points rather than a field-by-field template, answer walkthrough, or Notes-style teaching document. Keep source evidence, recurrence calculation, matching debug, and workflow steps internal.
6. Confirm the final output set before writing public output if this Skill was invoked directly without `exam-prep-index`.

## Output Contract

Produce a separate MCQ Specific Research Report unless the user explicitly asks for chat output. The public report should follow the user's reference-document style: Lecture heading, numbered knowledge-point title, concise exam-needed knowledge-point content, and a short exam scope line when useful. Do not use template labels such as distractor logic, option selection, or elimination steps. Do not expand into Notes-style teaching or full answer walkthroughs.

Do not render evidence tables, source locators, recurrence scores, frequency calculations, matching method, debug data, verification fields, or Codex workflow steps in the public report. Internal recurrence levels may be used for planning but must not be shown as public scoring.

Do not let MCQ coverage replace Notes coverage. Practice material can provide context, but Past Paper, Mock Paper, and official exam questions are the recurrence basis for the MCQ report.
