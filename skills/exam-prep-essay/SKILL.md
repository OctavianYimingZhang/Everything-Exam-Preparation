---
name: exam-prep-essay
description: Prepare essay plans, model answers, permitted Online Essay work, critical analysis, and Extra Reading enrichment from course material, essay prompts, assessment instructions, and reliable academic sources.
---

# Exam Prep Essay

Create the requested essay-preparation output with a clear claim-evidence-analysis structure.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/essay_exam_prep_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Identify the essay question, command word, scope, assessment setting, and requested artifact.
2. Map course knowledge to the claims needed to answer the question. When called without the Router, obtain the Essay `DiagnosticAssessment` from `scripts/extract_sources.py` and resolve only blocking gaps.
3. Use `scripts/essay_exam_tools.py` for topic analysis, essay structure, language checks, Extra Reading discovery, and evidence placement.
4. For Online Essay work, establish whether the assessment is `active`, `closed`, or `unknown`, then run the action-specific permission check. For `active`, allow only permission-neutral support plus explicitly permitted source use or drafting; for `closed`, allow post-assessment review and model-answer support under normal evidence rules; for `unknown`, continue only permission-neutral help and clarify the state before restricted source use or complete drafting.
5. Match reliable Extra Reading to specific claims needing mechanism depth, experimental evidence, counterargument, or evaluation.
6. Produce the requested plan, evidence map, paragraph support, feedback, or permitted draft and verify its source use.

## Output

Use a question-led thesis, coherent paragraph sequence, accurate course detail, explicit analysis, and a conclusion that resolves the question. Cite external evidence in the style requested by the user or assessment.

Return the public result envelope from `references/input_and_evidence_protocol.md`. Preserve the Online Essay permission result as an internal policy record, surface blocked actions and gaps, and name the actual format and QA state only for an artifact that was generated.
