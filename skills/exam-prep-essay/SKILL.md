---
name: exam-prep-essay
description: Prepare essay plans, model answers, permitted Online Essay work, critical analysis, and Extra Reading from course material and reliable academic evidence.
---

# Exam Prep Essay

Create the requested essay-preparation output with a clear claim-evidence-analysis structure.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/essay_exam_prep_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Identify the essay question, command word, scope, assessment setting, and requested artifact.
2. Map course knowledge to the claims needed to answer the question. When extraction is needed, call `scripts/extract_sources.py` once and reuse its Essay `DiagnosticAssessment`; resolve only blocking gaps.
3. Use `scripts/essay_exam_tools.py` for topic analysis, essay structure, language support, Extra Reading discovery, and evidence placement.
4. For Online Essay work, establish the action-specific permission state and proceed only at the permitted support level.
5. Match reliable Extra Reading to claims needing mechanism depth, experimental evidence, counterargument, or evaluation.
6. Produce the requested plan, evidence map, paragraph support, feedback, or permitted draft once.
7. Perform one bounded sanity check that the output answers the question, follows the requested structure and format, contains no unresolved placeholders, and uses sources only where permitted. Do not run repeated review passes.

## Output

Use a question-led thesis, coherent paragraph sequence, accurate course detail, explicit analysis, and a conclusion that resolves the question. Cite external evidence in the requested style.

Return the public result envelope from `references/input_and_evidence_protocol.md`. Preserve the Online Essay permission result internally, surface blocked actions and material gaps, and name the actual format and bounded QA state only for an artifact that was generated.
