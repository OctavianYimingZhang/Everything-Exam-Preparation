---
name: everything-exam-preparation
description: Source-bound, function-first exam preparation workflow for lecture material, practical material, past papers, and question-type add-ons.
---

# Everything Exam Preparation

This Skill turns supplied study and practice material into exam preparation outputs. Its purpose is narrow:

1. Analyse Lecture Slides, Lecture Notes, official notes, course notes, practical material, past papers, answer keys, exemplars, feedback, and verified extra reading.
2. Build `Lecture_Knowledge_Walkthrough.docx` as the default Exam Preparation Notes artifact.
3. Identify the exam mode from past papers or the user's prompt: MCQ, Short Answer, Long Answer, Practical/Data/Problem, or Essay.
4. Generate only the add-on content required by that exam mode after the core notes are coherent.

The Skill is not a slide archive converter, fixed-length summariser, prediction engine, or example library. It must not copy benchmark/example content into production output. Use only the sources supplied by the user unless the user explicitly permits verified academic lookup. Preserve source boundaries between course material, past papers, practical material, extra reading, examples, and style references. Treat unsupported points as gaps instead of filling them from memory.

## Canonical Protocols

Load only the protocol needed for the requested function:

| Function | Canonical file |
| --- | --- |
| Course-source intake, roles, authority, extraction, evidence boundaries | `references/input_and_evidence_protocol.md` |
| Default Exam Preparation Notes and lecture-first public DOCX | `references/exam_prep_core_workflow.md` |
| Exam mode detection and MCQ/Short Answer/Long Answer/Practical/Data add-ons | `references/exam_mode_and_addons_protocol.md` |
| Essay Exam Prep and Example Essay DOCX add-on | `references/essay_exam_prep_protocol.md` |
| Student-facing prose quality for every route | `references/language_quality_contract.md` |
| Setup, modular execution, subagents, regression, QA, release checks | `references/runtime_qa_release_protocol.md` |

No other reference file is authoritative. If a rule appears to duplicate another rule, follow the canonical file for the function above.

## Route Table

| User request | Route | Output |
| --- | --- | --- |
| revise, make notes, go through lectures, general exam preparation | `exam_prep_notes_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| explicitly lecture/source-order walkthrough | `knowledge_walkthrough_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| identify exam format from past papers | `exam_format_diagnosis` | chat/report diagnosis |
| MCQ or single-best-answer preparation | `mcq_exam_prep` | core notes plus MCQ add-on |
| short-answer preparation | `short_answer_exam_prep` | core notes plus short-answer add-on |
| long-answer, project, scenario, practical, data, graph, calculation, or problem preparation | `long_answer_project_scenario_prep` | core notes plus long-answer/practical/data add-on |
| essay exam preparation, Example Essays, model essays, full essay-style answers | `essay_exam_prep` | core notes plus Essay Module Example Essays DOCX |
| source inventory, lint, audit, release check | `source_inventory_only`, `audit_lint_only`, or `github_ready_qa` | QA or inventory result |

Past papers shape exam mode, emphasis, and answer operations only. They do not replace the course-source baseline. Question-type add-ons come after the base notes unless the user explicitly requests diagnosis only.

## Public Output Rules

The default public artifact is `Lecture_Knowledge_Walkthrough.docx`. It must be lecture-first, knowledge-only, source-backed, and proportional to the source pack. Public notes must explain what each concept is, why it matters, how the mechanism, method, calculation, graph, assay, or comparison works, and what limitation or interpretation follows.

Student-facing output must not expose source maps, confidence bands, evidence scores, internal manifests, QA flags, extraction notes, source-route narration, AI-process text, prediction traces, or rigid planning scaffolds. Use `references/language_quality_contract.md` as the only prose polish authority.

## Execution Boundary

Run the minimum route that satisfies the user request. If required source material is missing, report the missing source class and block only conclusions that depend on it. Examples are user-supplied style or layout evidence only; they never supply factual course claims or direct predictions for a new target. Internal checks live in script self-tests, not committed example corpora.

Prediction anchor: Predicted essay theme means a theme-level preparation scope, not exact future wording.
