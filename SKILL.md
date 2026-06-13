---
name: everything-exam-preparation
description: Signal-driven exam preparation workflow that produces knowledge-only teaching notes with visible formulas for course material, practice material, extra reading, MCQ, short answer, long answer, practical/data/problem, and essay exams.
---

# Everything Exam Preparation

This Skill helps students prepare for exams from uploaded course material, practice material, and academically useful Extra Reading.

## Core job

Students provide course material, practice material, and optionally Extra Reading. The Skill reads the material, extracts open knowledge signals, groups connected signals into knowledge units, calibrates the required explanation for each unit, enriches course content with extra reading where useful, connects the material to exam answers, and produces student-facing exam preparation output.

Student-facing Notes are knowledge-only teaching documents. They explain concepts, mechanisms, methods, calculations, assumptions, interpretations, and exam use. They do not expose source intake, extraction notes, coverage calibration, QA, route planning, subagent narration, or workflow scaffolding.

If the user requests a filename or file set, follow that request. Otherwise generate a clear DOCX filename from the source, course, prompt, or note title. Do not treat an exact filename as part of the Skill contract.

## Simple workflow

1. Read the supplied files.
2. Build a simple fragment index from readable content.
3. Calibrate coverage from knowledge signals and knowledge units.
4. Discover Extra Reading from uploaded sources, source mentions, and academic search queries.
5. Match Extra Reading to course knowledge units.
6. Diagnose the exam mode from the prompt and practice material.
7. Generate knowledge-only teaching notes from the coverage map.
8. Render visible formulas, tables, and explanations in the target output format style.
9. Add MCQ, short-answer, long-answer, practical/data/problem, or essay preparation when relevant.

## Extra Reading workflow

Use `references/extra_reading_workflow.md` for the Extra Reading workflow.

Extra Reading can add background, molecular explanation, mechanism explanation, pathway context, conceptual background, method detail, primary findings, experimental evidence, recent research context, and support for conclusions.

Example Essays use an Extra Reading blend of 15%-30% through paragraph slots that add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation.

## Output contract

Use `references/exam_prep_notes_protocol.md` as the canonical coverage, language, formula-visibility, and format guide.

Write like a strong tutor preparing a student for an exam. Explain what each topic means, why it matters, how it appears in questions, and how the student can use it in an answer.

Formula-heavy content must be visible in the final document. Use Word equation/OMML rendering where possible. Use readable Unicode mathematical fallback when equation conversion is unavailable. Do not leave formulas as raw pseudo-code such as `partial`, `sqrt`, `sum_ij`, or `dot` in student-facing output.

Render only knowledge content. Do not create public sections for source intake, extraction limits, coverage calibration, example filtering, workflow QA, internal checklists, route decisions, or planning state.

Mode-specific writing:

- MCQ: tested point, MCQ wording, correct reasoning, plausible wrong statement, why it is wrong.
- Short Answer: definition, mark points, explain sentence, example answer.
- Long Answer: question demand, relevant knowledge, answer structure, example answer, why the answer works.
- Practical/Data/Problem: method aim, readout, control, calculation or interpretation, limitation, exam conclusion.
- Essay: claim, explanation, course detail, Extra Reading evidence, analysis, link back to the question.

Render DOCX notes with Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact tables, centered display formulas, and clear knowledge sections. Filename and file-set choices may follow the user's request or the source pack; do not make exact filenames part of the knowledge-quality contract.

Recommended section order:

1. Knowledge-unit sections in course order or exam-priority order.
2. Formula and method explanations inside the relevant knowledge unit.
3. Mode-specific preparation when relevant.
4. Extra Reading depth immediately after the course point it strengthens.

## Routes

| User request | Route | Output |
|---|---|---|
| make notes, revise, prepare this course, go through lectures | `exam_prep_notes` | DOCX notes |
| identify exam format, how is this course examined | `exam_mode_diagnosis` | chat or JSON diagnosis |
| MCQ, SBA, multiple choice | `mcq_preparation` | notes plus MCQ preparation |
| short answer, SAQ, definitions, state/list questions | `short_answer_preparation` | notes plus short-answer preparation |
| long answer, problem, data, practical, past-paper walkthrough | `long_answer_preparation` | notes plus worked question preparation |
| essay, in-campus essay, example essay, model essay | `essay_preparation` | notes plus essay questions and example essays |
