---
name: exam-prep-notes
description: Create course-complete, knowledge-only Notes from lecture slides, PDFs, documents, recordings, reference notes, revision material, and assessment sources used only for internal emphasis. Includes source-role control, slide coverage auditing, selective source visuals, display equations, adaptive tables, methods, worked examples, and rendered-page QA; excludes unrequested Practice, Essay, and exam-strategy artifacts.
---

# Exam Prep Notes

Create course-complete, knowledge-only teaching Notes.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Inventory every supplied source and apply the user's stated source roles. When lecture slides are the coverage authority, audit every substantive slide; use text-only reference notes for emphasis and expression without letting them narrow slide coverage.
2. Run `scripts/extract_sources.py` to extract content, preserve locators, triage slide-like material, build the fragment index, and produce a coverage audit.
3. Organise substantive teaching content into connected knowledge units in a course-logical order.
4. Choose prose, learning-point lists, tables, equations, or visuals according to the knowledge relationship. Keep a visual only when it materially improves clarity beyond a well-written text or table explanation; prefer a suitable original slide image or slide page over making a new equivalent graphic.
5. Integrate recap and interactive material into the relevant knowledge units.
6. Use practice and assessment material only to calibrate emphasis and explanation depth while keeping Notes course-complete.
7. Include course knowledge only: definitions, structures, mechanisms, processes, taught methods, equations, evidence, data interpretation, comparisons, applications, and explanatory examples. Keep assessment strategy, command-word coaching, answer plans, essay routes, model-answer scaffolds, question banks, revision schedules, timing plans, and exam-day advice out of Notes.
8. Keep source filenames and slide or page locators in the internal audit. Do not print source labels, figure legends, or captions unless the user explicitly requests them.
9. Generate the requested Notes document only, render it to page images, inspect every page, and repeat correction and rendering until the layout is clean. Do not create a companion Practice or Essay file unless explicitly requested.

## Output

Use the user's requested language and default to English. Use black academic text, restrained hierarchy, a single main title, centred professional display equations, and tables whose widths, type size, wrapping, and alignment adapt to their content. Let knowledge density determine length and detail: retain coherent longer paragraphs where they explain the material best, and use bullet points only where list structure helps. Add supplementary title text when requested.

The public document contains course knowledge only. The internal coverage audit records every instructional source and its use, merge, or exclusion decision.
