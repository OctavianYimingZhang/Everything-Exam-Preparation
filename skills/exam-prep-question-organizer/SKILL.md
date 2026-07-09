---
name: exam-prep-question-organizer
description: Organize user-supplied Past Paper and Practice Material questions into a DOCX question list ordered strictly by Lecture Slides or lecture knowledge-unit order, with no answers or explanations.
---

# Question Organizer

Use this Skill when the user asks to organize, collect, sort, or compile Past Paper and Practice Material questions by lecture order.

Default public output is English. Change the language only when the user explicitly overrides it for the current task; examples in another language do not change the default.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`

Use `scripts/exam_mode_tools.py` for question extraction, lecture knowledge-unit matching, lecture-order sorting, and DOCX rendering.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Question Organization output. Confirm the Question Organization route, Material type/source roles, and lecture-order basis before rendering the organized DOCX.

## Workflow

1. Read all user-supplied Lecture Slides, course material, Past Papers, and Practice Material.
2. Extract questions only from Past Paper and Practice Material sources.
3. Match each question to lecture knowledge units using source-grounded terms and locators.
4. Sort questions strictly by Lecture Slides or lecture knowledge-unit order.
5. If a question matches multiple lecture units, assign it to the latest matching lecture unit.
6. Render the default output as a DOCX file that shows only questions plus minimal provenance.

## Output Contract

The default DOCX must not include answers, solution steps, explanations, knowledge summaries, or predictions. Each question should show the original question text and minimal provenance: source file, locator, and original question order when available.

If a question cannot be matched to a lecture unit, place it after matched questions under an unmatched section rather than guessing an order.
