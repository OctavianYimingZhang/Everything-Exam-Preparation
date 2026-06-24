---
name: exam-prep-essay
description: Produce essay exam preparation, example essay plans, model-answer support, claim-evidence-analysis structures, and Extra Reading enriched essay outputs from course material, essay questions, examples, and external academic sources.
---

# Essay Preparation

Create an essay-focused Specific Research Report after `exam-prep-index` has confirmed the essay route. Use this Skill for essay questions, in-campus essay preparation, example essays, essay plans, model-answer support, paragraph planning, and Extra Reading enriched evaluation.

Do not use this Skill for Online Essay Exam drafting. Online Essay Exam is a parallel branch owned by `exam-prep-online-essay-exam`; it requires Online Materials and Lecture Materials source-permission Ask Questions, locked brief, evidence map, paragraph-level plan, Planning Approval, draft generation, and QA.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/essay_exam_prep_protocol.md`
- `references/extra_reading_workflow.md`
- `references/language_quality_contract.md`

Use `scripts/essay_exam_tools.py`, `scripts/extra_reading_tools.py`, `scripts/plan_workflow.py`, and `scripts/build_review_questions.py` when structured planning or review payloads are useful.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Essay output. Confirm the ordinary Essay route, Material type/source roles, Notes generation choice, Example Essay choices, and Extra Reading source role before writing.

## Workflow

1. Identify essay question demand, course knowledge, conceptual scope, and assessment expectations.
2. Determine whether Extra Reading is supplied, requested, or required by the confirmed output.
3. Match Extra Reading to claims or course points that need mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation.
4. Use the confirmed review state before public generation if this Skill was invoked directly without `exam-prep-index`.
5. Produce the requested essay-preparation output.

## Output Contract

For essay Specific Research Reports, use claim, explanation, course detail, Extra Reading evidence, analysis, and link back to the question. Example Essays use an Extra Reading blend of 15%-30% through paragraph slots that add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation.

Keep unsupported claims out. If evidence is insufficient, state the gap or omit the claim.
