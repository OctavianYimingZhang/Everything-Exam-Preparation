---
name: everything-exam-preparation
description: Router for exam-preparation requests covering course Notes, question-based Practice, and Essay support from lectures, past papers, questions, answers, readings, and assessment instructions.
---

# Everything Exam Preparation Router

Use the package workflow in [`../../SKILL.md`](../../SKILL.md).

Route explicit requests directly:

- Notes and lecture revision → `exam-prep-notes`
- Questions, papers, worked answers, blueprints, evaluation, or timed work → `exam-prep-practice`
- Essay planning, drafting, Online Essay work, or Extra Reading → `exam-prep-essay`

Ask once only when a missing choice would materially change the requested artifact.

Return the public result envelope from `references/input_and_evidence_protocol.md`, including the selected `task_mode`, single artifact owner, assumptions, gaps, evidence summary, public completion status, and QA. Declare a real artifact format only after that file exists.
