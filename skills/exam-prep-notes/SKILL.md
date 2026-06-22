---
name: exam-prep-notes
description: Generate explanation-only DOCX exam-preparation notes from lecture, course, textbook, handout, slide, or revision material, with visible formulas, academic source visuals, and worked examples when they teach the relevant knowledge unit.
---

# Exam Prep Notes

Create student-facing Notes that teach the lecture and exam-relevant knowledge the student needs to master. Notes are broad lecture reconstruction documents for weakly prepared students, not concise Past Paper priority reports. Use this Skill after `exam-prep-index` has analyzed the material and the user has accepted Notes, or when the user explicitly asks for Notes with no exam-specific report.

## Load First

Read these shared resources before drafting:

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`
- `references/language_quality_contract.md`
- `../exam-prep-slide-triage/SKILL.md` when the input includes slide decks or slide-like PDFs
- `references/extra_reading_workflow.md` only when the confirmed Exam type includes essay and the Notes need essay-context enrichment

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Workflow

1. Reuse the source map, fragment index, confirmed source roles, and confirmed Notes decision from `exam-prep-index` when available.
2. If this Skill is invoked directly, read supplied files, build a source map, and ask the user whether Notes should be generated before public document generation.
3. Use `scripts/extract_sources.py` and `scripts/build_fragment_index.py` when local extraction or a reusable fragment index improves reliability.
4. Identify source roles and open knowledge signals: definitions, mechanisms, methods, comparisons, calculations, evidence, applications, visuals, and explanatory examples.
5. For slide decks and slide-like PDFs, apply slide triage before writing: `use` substantive knowledge slides, `merge_with_previous` supporting or repeated slides, and keep `exclude` slides only in the internal `slide_triage_audit`.
6. Group connected signals into lecture-unit complete knowledge units in source order. Preserve lecture/source order for Notes instead of sorting the public Notes primarily by exam frequency or signal score.
7. Apply content triage: cover `core_lecture_content`, include or compress `supporting_example`, and exclude `reading_reference`, `admin_or_boilerplate`, or `low_exam_relevance_context` unless directly examinable.
8. Calibrate teaching depth from source complexity, knowledge density, novelty, and exam relevance. Expand dense or unfamiliar lecture units enough for a student who has not learned the lecture well.
9. Generate DOCX Notes with `scripts/generate_exam_prep_notes_docx.py` when appropriate.

## Output Contract

Write as a strong tutor. Explain what each topic means, why it matters, how it works, and how it is interpreted or applied.

Use `coverage_policy: lecture_unit_complete`. The intended output is near slide-by-slide coverage at the level of substantive lecture units, not literal commentary on every slide or image. Cover most definitions, mechanisms, methods, pathways, comparisons, diagram meanings, important examples, and conceptual applications from the lecture material.

Slide triage is not a detail-level grading system. It prevents non-teaching slides from becoming detailed public explanation while preserving useful lecture structure. ILOs, agendas, topic boundaries, section dividers, summaries, non-core visuals, non-essential data, examples, and recap slides may guide topic order or merge into nearby units, but should not become long Notes explanations unless they contain substantive course knowledge.

Include visible formulas, tables, academic source visuals, method explanations, mechanism explanations, and worked examples only where they strengthen the relevant knowledge unit. Keep source intake narration, extraction notes, route planning, QA, and workflow records internal.

Keep Notes separate from MCQ, SAQ, and other Specific Research Reports. Reports provide concise exam-priority reinforcement; Notes provide broad lecture walkthrough teaching.

Use Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact academic tables, centered display formulas, academically useful source visuals, and clear knowledge sections.
