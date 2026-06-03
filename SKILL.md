---
name: everything-exam-preparation
description: Source-bound exam preparation workflow for lecture material, practical material, past papers, and exam-mode add-ons.
---

# Everything Exam Preparation

This Skill turns supplied study and practice material into student-facing exam preparation outputs.

## Purpose

1. Analyse Lecture Slides, Lecture Notes, official course notes, practical material, past papers, answer keys, exemplars, feedback, and verified extra reading supplied by the user.
2. Build `Exam_Preparation_Notes.docx` as the default Exam Preparation Notes artifact.
3. Choose the correct render mode for each knowledge block: compact list, compact table, mechanism chain, source image plus key points, or short paragraph.
4. Identify exam mode from past papers or the user's prompt: MCQ, Short Answer, Long Answer, Practical/Data/Problem, or Essay.
5. Generate only the add-on content required by the detected or requested exam mode.

## Non-goals

This Skill is not:

- a slide archive converter;
- a fixed-length summariser;
- an exact prediction engine;
- a remembered-example system;
- a style-copying system.

Use only the sources supplied by the user unless the user explicitly permits verified academic lookup. Preserve source boundaries between course material, past papers, practical material, extra reading, examples, and style references. Treat unsupported points as gaps.

## Canonical protocols

Load only the protocol required for the requested function.

| Function | Canonical file |
|---|---|
| Source intake, source roles, authority, extraction, evidence boundaries | `references/input_and_evidence_protocol.md` |
| Default Exam Preparation Notes | `references/exam_prep_notes_protocol.md` |
| Exam mode detection and MCQ/Short Answer/Long Answer/Practical/Data add-ons | `references/exam_mode_and_addons_protocol.md` |
| Essay Exam Prep and Example Essay add-on | `references/essay_exam_prep_protocol.md` |
| Student-facing prose quality | `references/language_quality_contract.md` |
| Run control, lineage, reuse, QA/release quality | `references/runtime_quality_protocol.md` |

No other reference file is authoritative.

## Route table

| User request | Route | Output |
|---|---|---|
| revise, make notes, general exam preparation, go through lectures | `exam_prep_notes` | `Exam_Preparation_Notes.docx` |
| source-order or lecture-order notes | `exam_prep_notes` with `ordering=source_order` | `Exam_Preparation_Notes.docx` |
| identify exam format only | `exam_mode_diagnosis` | chat/report diagnosis |
| MCQ / SBA preparation | `exam_prep_notes` + `mcq_addon` | notes plus MCQ add-on |
| Short Answer preparation | `exam_prep_notes` + `short_answer_addon` | notes plus short-answer add-on |
| Long Answer / Practical / Data / Problem preparation | `exam_prep_notes` + `long_answer_practical_addon` | notes plus methods/data/problem add-on |
| Essay exam preparation / Example Essays / model essays | `exam_prep_notes` + `essay_addon` | notes plus essay-specific outputs |
| source inventory / lint / release check | `source_inventory_only`, `audit_lint_only`, or `github_ready_qa` | inventory or QA result |

Past papers shape exam mode, emphasis, and answer operations only. They do not replace the course-source baseline.

Run-control manifests are internal QA artifacts. They may support reproducibility and release checks, but they must not appear in student-facing prose and must not make the notes sound like object, action, or link records.

## Student-facing output rules

`Exam_Preparation_Notes.docx` must be source-backed, readable, visually efficient, and proportional to the source pack. It must explain what each concept is, why it matters, how the mechanism, method, calculation, graph, assay, or comparison works, and what limitation or interpretation follows.

Use fewer words where possible, but do not collapse explanations into labels. Expand high-frequency, high-value, or difficult exam content. Compress weakly tested or peripheral material.

Use source images only when they improve explanation efficiency. Keep images size-controlled.

Student-facing output must not expose source maps, confidence bands, evidence scores, internal manifests, QA flags, extraction notes, source-route narration, AI-process text, prediction traces, or planning scaffolds.

## Execution boundary

Run the minimum route that satisfies the user request. If required source material is missing, report the missing source class and block only conclusions that depend on it.

Examples are style or layout evidence only. They never supply factual course claims or direct predictions for a new target.

Prediction anchor: predicted essay theme means theme-level preparation scope, not exact future wording.
