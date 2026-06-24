---
name: exam-prep-question-solver
description: Solve a user-supplied exam or practice question using the user's supplied material, explain the matching course knowledge, and retrieve strictly same-knowledge-point Past Paper or Practice Material questions for transfer practice.
---

# Question Solver

Use this Skill when the user asks how to solve a specific question, asks for a question walkthrough, or wants to test whether they can transfer the same knowledge to other questions.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`
- `references/exam_mode_and_addons_protocol.md`

Use `scripts/exam_mode_tools.py` for question extraction, knowledge-unit matching, strict same-point retrieval, and transfer-practice grouping.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Question Solving output. Confirm the Question Solving route, supplied target question, and Material type/source roles for the question and source pack before answering.

## Workflow

1. Identify the user's target question exactly.
2. Use only the user-supplied material and its source scan; do not search external sources or unrelated local files.
3. Match the target question to the most specific lecture knowledge unit that is clearly evidenced by shared question demand, knowledge terms, source locator, and lecture/source context.
4. Explain the question in this fixed order:
   - Question analysis.
   - Matching knowledge display and explanation.
   - Solution or answer reasoning.
   - Strictly same-knowledge-point Past Paper or Practice Material questions.
   - Transfer-practice prompt that asks the student to apply the same knowledge.
5. If no strict same-point question exists in the supplied material, state that no strict match was found and do not substitute broad related questions.

## Strict Match Rule

Return other Past Paper or Practice Material questions only when they match the same lecture knowledge unit and share specific knowledge terms with the target question. Similar topic area, same lecture file, or broad conceptual overlap is not enough.

## Output Contract

Keep the answer student-facing. The goal is to help the student understand the target question and then test the same knowledge through tightly matched questions. Do not include unrelated question banks, broad recommendations, or unverified matches.
