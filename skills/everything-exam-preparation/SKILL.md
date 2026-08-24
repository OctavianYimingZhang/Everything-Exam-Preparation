---
name: everything-exam-preparation
description: Router for exam-preparation requests covering course Notes, question-based Practice, and Essay support from trusted course and assessment material.
---

# Everything Exam Preparation Router

Use the package workflow in [`../../SKILL.md`](../../SKILL.md) and the shared result contract in `references/input_and_evidence_protocol.md`.

Route explicit requests directly:

- Notes and lecture revision → `exam-prep-notes`
- Questions, papers, worked answers, blueprints, evaluation, or timed work → `exam-prep-practice`
- Essay planning, drafting, Online Essay work, or Extra Reading → `exam-prep-essay`

Ask once only when a missing input would materially change the requested artifact. Otherwise route once, execute once, and return the result. Do not add a separate audit or render loop.

Return the public result envelope with the selected `task_mode`, artifact owner, assumptions, material gaps, evidence summary, public completion status, and bounded QA state. Declare a real artifact format only after that file exists.
