---
name: exam-prep-notes
description: Create explanation-first course Notes from lecture slides, PDFs, documents, recordings, revision material, and past papers used for emphasis. Includes slide triage, coverage auditing, useful source visuals, equations, methods, and worked examples.
---

# Exam Prep Notes

Create course-complete teaching Notes for a student preparing for assessment.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Inventory every supplied source and apply the user's stated source roles.
2. Run `scripts/extract_sources.py` to extract content, preserve locators, triage slide-like material, build the fragment index, and produce a coverage audit.
3. Organise substantive teaching content into connected knowledge units in a course-logical order.
4. Explain definitions, mechanisms, methods, comparisons, calculations, evidence, interpretation, and application at the depth needed to learn the course.
5. Integrate recap and interactive material into the relevant knowledge units.
6. Use practice material to calibrate emphasis and explanation depth while keeping Notes course-complete.
7. Select source visuals that materially improve understanding and label each with the source filename and slide or page locator.
8. Generate the requested document and complete structural and rendered-page verification.

## Output

Use the user's requested language and default to English. Use black academic text, restrained hierarchy, and a single main title. Add supplementary title text when requested.

The public document contains teaching content. The internal coverage audit records every instructional source and its use, merge, or exclusion decision.
