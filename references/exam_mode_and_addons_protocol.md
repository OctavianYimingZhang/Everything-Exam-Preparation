# Exam Mode And Add-ons Protocol

This is the only canonical protocol for exam-mode diagnosis and non-essay question-type add-ons.

## Mode Detection

Use formal past papers, exam guidance, answer keys, and the user's prompt to identify the current exam mode. Separate current-regime evidence from older or structurally different papers. Do not pool target groups unless comparability is proven.

Recognised modes:

- `mcq_exam_prep`: MCQ, SBA, multiple choice, negative marking.
- `short_answer_exam_prep`: definitions, brief explanations, mark-point answers, short calculations.
- `long_answer_project_scenario_prep`: project, scenario, practical design, data interpretation, graph/table/problem, method/readout/control/limitation answers.
- `essay_exam_prep`: broad essay, problem essay, complete essay-style answers, Example Essays.
- `exam_format_diagnosis`: diagnosis only, no study artifact unless requested.

Past papers identify section structure, command verbs, mark operations, repeated question families, input format, and answer operations. They do not authorise unsupported factual claims.

## Add-on Rules

All add-ons start from the core notes baseline. The base `Lecture_Knowledge_Walkthrough.docx` must remain source-first and knowledge-only.

MCQ add-on: produce student-facing point cards and discriminator logic without exposing answer keys, source anchors, confidence, recurrence, or separate trap banks.

Short Answer add-on: produce compact point cards, keywords, and natural Example Answers without exposing mark-producing schema, task-verb audit, source anchors, or reference expansion.

Long Answer / Practical / Data add-on: produce question analysis, answer order, reusable method/readout/interpretation/control/limitation blocks, worked calculation or graph interpretation logic where supported, Example Answer, and adaptation notes. It must read as a compact experimental or scenario argument, not a broad essay.

Essay mode is routed to `references/essay_exam_prep_protocol.md`.

## Prediction Boundary

The prediction target is a question family and preparation action, not exact future wording. Do not generate predicted questions as the default student-facing output. If the user asks for prediction, keep it as a labelled diagnosis/report and state evidence limits.

Internal essay-mode objects may be named `EssayThemePrediction` and `EssayProblemThemeResult`; both describe theme-level scope and practice angle, not exact future wording.
