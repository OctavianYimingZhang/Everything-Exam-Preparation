---
name: everything-exam-preparation
description: Route exam-preparation requests to course Notes, question-based Practice, or Essay support. Use when a student supplies lectures, past papers, questions, answers, essay prompts, readings, or assessment instructions and asks to study, revise, practise, organise questions, evaluate an answer, build a blueprint, prepare timed work, or draft a permitted essay.
---

# Everything Exam Preparation

Turn trusted course material into the exam-preparation output the student explicitly requests.

## Public Skills

- `exam-prep-notes`: explanation-first course Notes; includes slide triage.
- `exam-prep-practice`: MCQ, short answer, long answer, calculations, worked solutions, question solving and organisation, assessment blueprints, answer evaluation, and timed practice.
- `exam-prep-essay`: essay plans, model answers, permitted Online Essay work, and Extra Reading.

## Skill Boundaries

Treat the manifest-declared Skill list as the current architecture rather than a fixed quota. Split a focused Skill when its learning intent, evidence role, workflow, toolchain, or output is materially independent. Merge focused Skills when those elements are shared and one workflow can handle the variants reliably.

## Routing

1. Read the request and supplied material.
2. Select the Skill that directly matches the requested artifact.
3. Use more than one focused Skill when the request explicitly combines outputs.
4. For a broad revision request, use Notes when the material is primarily instructional, Practice when the material is primarily questions, and Essay when an essay prompt or essay assessment is central.
5. Ask one concise question only when the missing choice would materially change the artifact. Ask for missing source files, the target question or answer, an explicit timed duration, evaluation criteria, or Online Essay source permission when that information is required.
6. Execute the selected workflow and verify the finished artifact.

Explicit user instructions establish the task. Source roles stated by the user take priority over filename inference.

## Shared Rules

Read `references/input_and_evidence_protocol.md` for every task, then read the focused protocol:

- Notes: `references/exam_prep_notes_protocol.md`
- Practice: `references/exam_mode_and_addons_protocol.md`
- Essay: `references/essay_exam_prep_protocol.md`

Use the user's requested output language and default to English. Treat examples in another language as structural examples; use that language for output when requested.

Use the user's requested filename. Otherwise create a clear filename from the course and artifact.

Keep public output focused on learning content. Maintain source coverage, slide decisions, extraction observations, and verification results as internal working records.

For DOCX output, use A4, Arial, 2.5 cm margins, 1.5 line spacing, a centred main title, left-aligned headings, justified body text, black academic text, restrained hierarchy, compact tables, readable equations, and useful source visuals.

## Tools

- `scripts/extract_sources.py`: extract sources, build the fragment index, report readiness, and create a coverage audit.
- `scripts/generate_exam_prep_notes_docx.py`: render structured Notes and related academic DOCX files.
- `scripts/exam_mode_tools.py`: analyse and generate Practice outputs.
- `scripts/essay_exam_tools.py`: prepare essays and Extra Reading support.
- `scripts/validate_skill_contracts.py`: validate the Plugin, Skills, scripts, metadata, and installation declarations.
- `scripts/publish_skill.py`: synchronise and compare the manifest-declared local Skill installations.

## Completion

Verify source coverage and output structure. For office documents, render the finished file and inspect every page for clipping, overflow, image placement, pagination, and font consistency.
