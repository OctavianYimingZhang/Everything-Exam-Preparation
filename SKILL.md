---
name: everything-exam-preparation
description: Signal-driven exam preparation workflow that produces explanation-only teaching notes with visible formulas, academic source visuals, calculation worked examples, and separate Exam Type Related add-ons for MCQ, short answer, long answer, practical/data/problem, and essay exams.
---

# Everything Exam Preparation

This Skill helps students prepare for exams from uploaded course material, practice material, and academically useful Extra Reading.

## Core job

Students provide course material, practice material, and optionally Extra Reading. The Skill reads the material, extracts open knowledge signals, groups connected signals into knowledge units, calibrates the required explanation for each unit, enriches course content with extra reading where useful, and produces student-facing exam preparation output.

Student-facing Notes are explanation-only, knowledge-only teaching notes. They explain concepts, mechanisms, methods, calculations, assumptions, interpretations, conceptual applications, academically useful source visuals, and calculation worked examples when those examples teach the relevant knowledge unit. Exam Type Related preparation is produced as separate add-on output for the relevant route.

If the user requests a filename or file set, follow that request. Otherwise generate a clear DOCX filename from the source, course, prompt, or note title. Do not treat an exact filename as part of the Skill contract.

Default output language is English unless the user explicitly requests another language.

## Simple workflow

1. Read the supplied files.
2. Build a simple fragment index from readable content.
3. Calibrate coverage from knowledge signals and knowledge units.
4. Discover Extra Reading from uploaded sources, source mentions, and academic search queries.
5. Match Extra Reading to course knowledge units.
6. Diagnose the exam mode from the prompt and practice material when the request asks for exam type-related preparation.
7. Generate explanation-only teaching Notes from the coverage map.
8. Render visible formulas, tables, academic source visuals, worked examples, and explanations in the target output format style.
9. Produce MCQ, short-answer, long-answer, practical/data/problem, essay preparation, or Math/Physics/Practical Worked Solutions as separate outputs when the route or source signals call for them.

## Extra Reading workflow

Use `references/extra_reading_workflow.md` for the Extra Reading workflow.

Extra Reading can add background, molecular explanation, mechanism explanation, pathway context, conceptual background, method detail, primary findings, experimental evidence, recent research context, and support for conclusions.

Example Essays use an Extra Reading blend of 15%-30% through paragraph slots that add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation.

## Output contract

Use `references/exam_prep_notes_protocol.md` as the canonical coverage, language, formula-visibility, and format guide for Notes output.

Write like a strong tutor preparing a student for an exam. Explain what each topic means, why it matters, how it works, and how the knowledge is interpreted or applied.

Formula-heavy content must be visible in the final document. Use Word equation/OMML rendering where possible. Use a domain-neutral formula normalization pipeline and readable Unicode mathematical fallback when equation conversion is unavailable.

Render Notes as knowledge explanations with integrated formula, method, calculation, worked example, mechanism, comparison, visual, and interpretation support.

Exam Type Related add-on writing:

- MCQ: source questions in lecture order, tested point, MCQ wording, correct reasoning, plausible wrong statement, why it is wrong, and high-frequency knowledge points derived from question material.
- Short Answer: source questions in lecture order, definition, mark points, explain sentence, example answer, and high-frequency knowledge points derived from question material.
- Long Answer: source question, question demand, relevant knowledge, answer structure, example answer, and academic analysis/prediction result.
- Practical/Data/Problem: source task, method aim, readout, control, calculation or interpretation, limitation, conclusion, and academic analysis/prediction result.
- Math/Physics/Practical Worked Solutions: every extracted calculation, derivation, estimate, proof, data, or problem question with detailed answer-only solution, assumptions, unit or dimension check, interpretation, and concise evidence status.
- Essay: claim, explanation, course detail, Extra Reading evidence, analysis, link back to the question.

For math, physics, calculation, derivation, estimate, proof, and data/problem walkthrough outputs, render detailed answers rather than diagnosis or examiner-habit summaries. Keep mode diagnosis and high-frequency answer-demand analysis internal for that answer-only route.

Render DOCX Notes with Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact tables, centered display formulas, academically useful source visuals, and clear knowledge sections. Use restrained academic styling only. Filename and file-set choices may follow the user's request or the source pack; do not make exact filenames part of the knowledge-quality contract.

Recommended section order:

1. Knowledge-unit sections in course order or knowledge-priority order.
2. Formula and method explanations inside the relevant knowledge unit.
3. Extra Reading depth immediately after the course point it strengthens.

## Routes

| User request | Route | Output |
|---|---|---|
| make notes, revise, prepare this course, go through lectures | `exam_prep_notes` | DOCX explanation Notes |
| identify exam format, how is this course examined | `exam_mode_diagnosis` | chat or JSON diagnosis |
| MCQ, SBA, multiple choice | `mcq_preparation` | separate MCQ Exam Type Related add-on |
| short answer, SAQ, definitions, state/list questions | `short_answer_preparation` | separate short-answer Exam Type Related add-on |
| long answer, problem, data, practical, past-paper walkthrough | `long_answer_preparation` | separate long-answer/practical/data/problem add-on or answer-only worked solutions when calculation/problem signals dominate |
| essay, in-campus essay, example essay, model essay | `essay_preparation` | separate essay Exam Type Related add-on |
