---
name: exam-prep-notes
description: Generate explanation-only DOCX exam-preparation notes from lecture, course, textbook, handout, slide, or revision material, with visible formulas, academic source visuals, and worked examples when they teach the relevant knowledge unit.
---

# Exam Prep Notes

Create student-facing Notes that teach the lecture and exam-relevant knowledge the student needs to master. Use this Skill after `exam-prep-index` has analyzed the material and the user has accepted Notes, or when the user explicitly asks for Notes with no exam-specific report.

## Load First

Read these shared resources before drafting:

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`
- `references/language_quality_contract.md`
- `references/extra_reading_workflow.md` only when the confirmed Exam type includes essay and the Notes need essay-context enrichment

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Workflow

1. Reuse the source map, fragment index, confirmed source roles, and confirmed Notes decision from `exam-prep-index` when available.
2. If this Skill is invoked directly, read supplied files, build a source map, and ask the user whether Notes should be generated before public document generation.
3. Use `scripts/extract_sources.py` and `scripts/build_fragment_index.py` when local extraction or a reusable fragment index improves reliability.
4. Identify source roles and open knowledge signals: definitions, mechanisms, methods, comparisons, calculations, evidence, applications, visuals, and explanatory examples.
5. Group connected signals into knowledge units and calibrate teaching depth from source complexity, knowledge density, novelty, and exam relevance.
6. Generate DOCX Notes with `scripts/generate_exam_prep_notes_docx.py` when appropriate.

## Output Contract

Write as a strong tutor. Explain what each topic means, why it matters, how it works, and how it is interpreted or applied.

Include visible formulas, tables, academic source visuals, method explanations, mechanism explanations, and worked examples only where they strengthen the relevant knowledge unit. Keep source intake narration, extraction notes, route planning, QA, and workflow records internal.

Use Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact academic tables, centered display formulas, academically useful source visuals, and clear knowledge sections.
