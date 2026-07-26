---
name: everything-exam-preparation
description: Route course-study requests to knowledge-only Notes, question-based Practice, or Essay support. Default unspecified, broad, continuing, and bulk course-material work to knowledge-only Notes. Use Practice or Essay only when the student explicitly requests that separate artifact or capability.
---

# Everything Exam Preparation

Turn trusted course material into the requested learning artifact. Keep broad and bulk course-document work knowledge-only unless the student explicitly requests a separate Practice or Essay artifact.

## Public Skills

- `exam-prep-notes`: explanation-first course Notes; includes slide triage.
- `exam-prep-practice`: MCQ, short answer, long answer, calculations, worked solutions, question solving and organisation, assessment blueprints, answer evaluation, and timed practice.
- `exam-prep-essay`: essay plans, model answers, permitted Online Essay work, and Extra Reading.

## Skill Boundaries

Treat the manifest-declared Skill list as the current architecture rather than a fixed quota. Split a focused Skill when its learning intent, evidence role, workflow, toolchain, or output is materially independent. Merge focused Skills when those elements are shared and one workflow can handle the variants reliably.

## Routing

1. Read the request and supplied material.
2. Select Notes alone when the student asks to create, improve, rebuild, continue, or apply changes across course Notes, or when a broad or bulk course-material request does not explicitly name another artifact.
3. Select Practice or Essay only when the student explicitly requests a question-based, answer-evaluation, timed-practice, essay-planning, essay-drafting, or equivalent separate artifact.
4. Treat the supplied source mix as evidence, not output permission. Past papers, questions, rubrics, and assessment instructions can calibrate Notes internally but do not authorise Practice or Essay output by themselves.
5. Use more than one focused Skill only when the request explicitly combines outputs. Keep the artifacts separate unless the student explicitly requests a combined file.
6. Ask one concise question only when a required input for the explicitly requested artifact is missing. Ask for missing source files, the target question or answer, an explicit timed duration, evaluation criteria, or Online Essay source permission when that information is required.
7. Execute the selected workflow and verify the finished artifact.

Explicit user instructions establish the task. Source roles stated by the user take priority over filename inference.

## Notes Artifact Boundary

Build Notes from course knowledge: definitions, structures, mechanisms, processes, methods taught as subject matter, equations, evidence, data interpretation, comparisons, applications, and explanatory examples.

Keep assessment strategy, command-word coaching, answer-planning routes, thesis or paragraph templates, model-answer scaffolds, question banks, revision schedules, timing plans, and exam-day advice within an explicitly requested Practice or Essay artifact. Do not append these sections to Notes and do not create a companion exam-preparation file automatically.

When the student requests Notes plus Practice or Essay, preserve the Notes as a knowledge-only artifact and place the additional capability in its own requested artifact unless instructed otherwise.

## Shared Rules

Read `references/input_and_evidence_protocol.md` for every task, then read the focused protocol:

- Notes: `references/exam_prep_notes_protocol.md`
- Practice: `references/exam_mode_and_addons_protocol.md`
- Essay: `references/essay_exam_prep_protocol.md`

Use the user's requested output language and default to English. Treat examples in another language as structural examples; use that language for output when requested.

Use the user's requested filename. Otherwise create a clear filename from the course and artifact.

Keep public output focused on learning content. Maintain source roles, coverage, slide decisions, extraction observations, source locators, and verification results as internal working records.

For DOCX output, use A4, Arial, 2 cm margins, 1.5 line spacing, a centred main title, left-aligned headings, justified body text, black academic text, and restrained hierarchy. Apply artifact-specific visual, equation, table, and caption rules from the focused protocol.

## Tools

- `scripts/extract_sources.py`: extract sources, build the fragment index, report readiness, and create a coverage audit.
- `scripts/generate_exam_prep_notes_docx.py`: render structured Notes and related academic DOCX files.
- `scripts/exam_mode_tools.py`: analyse and generate Practice outputs.
- `scripts/essay_exam_tools.py`: prepare essays and Extra Reading support.
- `scripts/validate_skill_contracts.py`: validate the Plugin, Skills, scripts, metadata, and installation declarations.
- `scripts/publish_skill.py`: synchronise and compare the manifest-declared local Skill installations.

## Completion

Verify source coverage and output structure. Reject generic or source-like image alternative text: each embedded teaching visual must state its subject and the relationship it teaches without exposing provenance. For office documents, render the finished file to page images, inspect every page at readable zoom for clipping, overflow, table wrapping, equation display, image placement, avoidable blank space, pagination, and font consistency, then correct and re-render until clean.
