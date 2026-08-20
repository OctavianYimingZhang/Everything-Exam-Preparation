---
name: exam-prep-essay
description: Prepare exam essay plans, annotated model essays, paragraph exemplars, closed past-assessment review, and exam-answer adaptation from course material, essay prompts, closed past papers, and supplied verifiable evidence.
---

# Exam Prep Essay

Create the requested exam-essay preparation output with a clear claim-evidence-analysis structure.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/essay_exam_prep_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Identify the exam essay question, command word, scope, assessment lifecycle, and requested artifact. Public task modes are exam essay planning, annotated model essay, paragraph exemplar, closed past-assessment review, and exam-answer adaptation.
2. If the request concerns an assessment rather than general revision, establish whether it is `active`, `closed`, or `unknown`. A complete draft for an active assessed task is out of scope even when a legacy permission field says it is allowed. A complete model answer is available only for a closed past assessment. At the builder boundary, `build_essay_views` must stop before canonical-body or view construction when an explicit state is `active` or `unknown`: return `restricted` for `active` or `needs_clarification` for `unknown`, set `views_generated: false`, and omit `views`. A closed or omitted lifecycle may proceed under the normal evidence rules.
3. Accept raw PPTX, PDF, DOCX, image, transcript, text, or archive inputs directly and map course knowledge to the claims needed to answer the question. When called without the Router, obtain the Essay `DiagnosticAssessment` from `scripts/extract_sources.py --purpose essay` and resolve only blocking gaps.
4. Use `scripts/essay_exam_tools.py` for question analysis, planning, source checks, the single canonical essay body, clean view, annotated teaching view, adaptation, and language QA.
5. Treat course sources as the primary basis for course facts and scope. Use past papers only to set question scope and emphasis; never cite a past paper as evidence for a scientific or disciplinary claim.
6. Use external evidence only when it was actually supplied and its identity and claim support can be verified in the non-past-paper source fragment resolved from that essay segment's own source reference and locator. Evidence found only in an unreferenced fragment does not verify the segment. Do not invent Extra Reading, citations, DOIs, authors, dates, experiments, quantitative results, or source locators.
7. Produce and verify the requested plan, exemplar, closed-assessment review, adaptation, or dual-view model essay.

## Output

Use a question-led thesis, coherent paragraph sequence, accurate course detail, explicit analysis, and a conclusion that resolves the question.

For an Example Essay, create one canonical ordered body and project both views from it:

- clean essay view: the essay prose without teaching labels;
- annotated teaching view: the identical prose marked for thesis, claim, evidence, analysis, limitation, synthesis, paragraph function, and adaptation notes.

Verify that both views have the same canonical body hash. If a required annotation or source is missing, mark the output `needs_review`; do not fill the gap with invented prose or citation data.

Return the public result envelope from `references/input_and_evidence_protocol.md`. Preserve any lifecycle refusal as an internal safety record, surface blocked actions and evidence gaps, and name the actual format and QA state only for an artifact that was generated.
