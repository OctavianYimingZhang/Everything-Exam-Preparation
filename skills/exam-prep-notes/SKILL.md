---
name: exam-prep-notes
description: Create course-complete, knowledge-only Notes from lecture and course material using one-pass extraction, connected explanation, selective visuals, and bounded output checks.
---

# Exam Prep Notes

Create course-complete, knowledge-only teaching Notes.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Apply the user's source roles. When lecture slides are the coverage authority, use the complete extracted fragment index so every substantive teaching point is available during drafting.
2. Run `scripts/extract_sources.py` once when extraction is needed. Reuse its fragment index and Notes `DiagnosticAssessment`; ask only for a blocking gap.
3. Organise the material into connected knowledge units in a course-logical order before generating the file.
4. Choose prose, learning-point lists, tables, equations, or visuals according to the relationship being taught. Keep a visual only when it materially improves clarity; prefer a suitable original lecture-slide image or page over generating an equivalent graphic.
5. Integrate recap and interactive material into the relevant knowledge units.
6. Use practice and assessment material only to calibrate emphasis and explanation depth.
7. Include course knowledge only. Keep assessment strategy, answer plans, essay routes, model-answer scaffolds, question banks, revision schedules, timing plans, and exam-day advice out of Notes.
8. Generate the requested Notes document once. Do not create a companion Practice or Essay file unless explicitly requested.
9. Run one bounded sanity check: file existence and readability, requested title and main sections, expected format, and absence of unresolved placeholders or reported generation errors. Do not render or inspect every page by default.

## Output

Use the requested language and default to English. Use black academic text, restrained hierarchy, a single main title, centred professional display equations, and content-aware tables. Let knowledge density determine length and detail; retain coherent longer paragraphs where they explain the material best.

Keep source filenames and locators internal unless requested. A compact source summary is sufficient by default; do not build a fragment-by-fragment coverage ledger or rendered-page audit unless the user explicitly requests one.

Return the public result envelope from `references/input_and_evidence_protocol.md`. Declare `artifact_generated` and `docx` after the file exists and passes the bounded sanity check. Use a deeper QA state only when deeper QA was explicitly requested or a concrete error triggered it.
