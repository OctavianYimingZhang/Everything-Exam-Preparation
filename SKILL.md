---
name: everything-exam-preparation
description: Route course-study requests to knowledge-only Notes, question-based Practice, or Essay support, using a single-pass workflow and only bounded checks unless the user explicitly requests deeper QA.
---

# Everything Exam Preparation

Turn trusted course material into the requested learning artifact. Keep broad, continuing, and bulk course-document work knowledge-only unless the student explicitly requests a separate Practice or Essay artifact.

## Public Skills

- `exam-prep-notes`: explanation-first course Notes.
- `exam-prep-practice`: questions, worked solutions, answer evaluation, blueprints, and timed practice.
- `exam-prep-essay`: essay plans, model answers, permitted Online Essay work, and Extra Reading.

## Routing

1. Read the request and supplied material.
2. Select Notes for Notes creation, improvement, continuation, rebuild, or broad course-material work unless another artifact is explicitly requested.
3. Select Practice or Essay only when the student explicitly requests that capability.
4. Treat past papers, questions, rubrics, and assessment instructions as evidence. They do not authorise a different output by themselves.
5. Use more than one focused Skill only when the request explicitly combines outputs. Keep separate artifacts separate unless the student asks for one combined file.
6. Ask one concise question only when an indispensable input is missing. Otherwise proceed directly.

Explicit user instructions establish the task. User-stated source roles override filename inference.

## One-Pass Execution

1. Read and classify the supplied sources once.
2. Call `scripts/extract_sources.py --mode diagnostic --purpose <notes|practice|essay>` once when extraction or diagnostics are needed, then reuse that result throughout the task. Do not rerun extraction or diagnostics merely to improve a readiness label.
3. Decide the document or answer structure before drafting.
4. Generate the requested output once using deterministic styles and conservative layout choices.
5. Perform one bounded sanity check only: confirm the output exists and opens, uses the requested filename and real format, contains the expected main sections, and has no unresolved placeholders, extraction errors, or tool failures.
6. Do not render page images, inspect every page, build exhaustive coverage or figure audits, or enter correction-and-rerender loops by default.
7. Render or visually inspect only when the user explicitly requests visual or final-layout QA, source extraction is visibly incomplete and a specific page image is needed, or the renderer reports a concrete layout failure. Inspect only the affected page or element and apply at most one targeted correction. Report any remaining limitation instead of looping.
8. Treat `scripts/validate_skill_contracts.py`, `scripts/publish_skill.py`, self-tests, and render self-tests as repository-maintenance tools, not normal student-task steps.

## Notes Artifact Boundary

Build Notes from course knowledge: definitions, structures, mechanisms, processes, taught methods, equations, evidence, data interpretation, comparisons, applications, and explanatory examples.

Keep assessment strategy, command-word coaching, answer-planning routes, thesis or paragraph templates, model-answer scaffolds, question banks, revision schedules, timing plans, and exam-day advice within an explicitly requested Practice or Essay artifact. Do not append them to Notes and do not create a companion artifact automatically.

## Shared Rules

Read `references/input_and_evidence_protocol.md` for every task, then read the focused protocol:

- Notes: `references/exam_prep_notes_protocol.md`
- Practice: `references/exam_mode_and_addons_protocol.md`
- Essay: `references/essay_exam_prep_protocol.md`

Use the requested output language and default to English.

Return the public Skill result envelope from `references/input_and_evidence_protocol.md`. Keep diagnostic states and source observations internal. When a file is generated, declare its real format, source corpus identifiers, and QA state; never label a plan or payload as a generated artifact.

Use the requested filename. Otherwise create a clear filename from the course and artifact.

For DOCX output, use A4, Arial, 2 cm margins, 1.5 line spacing, a centred main title, left-aligned headings, justified black body text, and restrained hierarchy. Apply artifact-specific equation, table, and visual rules from the focused protocol.

## Tools

- `scripts/extract_sources.py`: one-pass extraction, fragment indexing, and optional diagnostics.
- `scripts/generate_exam_prep_notes_docx.py`: deterministic Notes DOCX generation.
- `scripts/exam_mode_tools.py`: Practice analysis and generation.
- `scripts/essay_exam_tools.py`: Essay and Extra Reading support.
- `scripts/validate_skill_contracts.py`: repository-maintenance validation.
- `scripts/publish_skill.py`: repository-maintenance synchronisation.

## Completion

Deliver the requested learning artifact after the bounded sanity check. Deeper source auditing, rendered-page inspection, accessibility audit, or layout repair is a separate QA task only when explicitly requested or triggered by a concrete failure.
