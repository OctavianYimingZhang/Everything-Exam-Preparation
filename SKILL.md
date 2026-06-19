---
name: everything-exam-preparation
description: Signal-driven exam preparation workflow that produces explanation-only teaching notes with visible formulas, academic source visuals, calculation worked examples, and separate Exam Type Related add-ons for MCQ, short answer, long answer, practical/data/problem, and essay exams.
---

# Everything Exam Preparation

This Skill helps students prepare for exams from uploaded course material, practice material, and academically useful Extra Reading.

## Core job

Students provide course material, practice material, and optionally Extra Reading. The Skill reads the material, extracts open knowledge signals, groups connected signals into knowledge units, calibrates the required explanation for each unit, uses Extra Reading for essay-style enrichment when relevant, and produces student-facing exam preparation output.

Student-facing Notes are explanation-only, knowledge-only teaching notes that show the lecture and exam-relevant knowledge a student needs to master. They explain concepts, mechanisms, methods, calculations, assumptions, interpretations, conceptual applications, academically useful source visuals, and calculation worked examples when those examples teach the relevant knowledge unit. Exam Type Related preparation is produced as separate add-on output for the relevant route.

Automatic Exam type, Material type, and output-set recognition is a preliminary diagnosis. Before generating Notes, Exam Type Related add-ons, or Worked Solutions, display an **Auto-diagnosis review plan** and use `request_user_input` to confirm or correct Exam type/route, Material type/source roles, and the final output set. Mixed exam signals mean the confirmed output should cover each relevant component in the mix.

If the user requests a filename or file set, follow that request. Otherwise generate a clear, distinct DOCX filename for each output from the source, course, prompt, or note title.

Default output language is English unless the user explicitly requests another language.

## Simple workflow

1. Read the supplied files.
2. Build a simple fragment index from readable content.
3. Calibrate coverage from knowledge signals and knowledge units.
4. Identify Extra Reading sources for essay-style enrichment when the user supplies them or the confirmed output calls for them.
5. Match confirmed Extra Reading to essay claims or course points that need external enrichment.
6. Make a preliminary diagnosis of Exam type/route, Material type/source roles, and proposed output set from the prompt and source material.
7. Display an **Auto-diagnosis review plan**, then call `request_user_input` with concrete options for Exam type, Material type, and output set confirmation.
8. Update the route, source-role handling, and final output plan from the user's confirmed or corrected answers.
9. Generate explanation-only teaching Notes from the confirmed coverage map.
10. Render visible formulas, tables, academic source visuals, worked examples, and explanations in the target output format style.
11. Produce MCQ, short-answer, long-answer, practical/data/problem, essay preparation, or Math/Physics/Practical Worked Solutions as separate outputs when the confirmed route or source signals call for them.

## Extra Reading workflow

Use `references/extra_reading_workflow.md` for the Extra Reading workflow.

Extra Reading is mainly for Essay Question and Example Essay enrichment. Use it to add external evidence, mechanism depth, molecular evidence, counterargument, and evaluation that can help the user earn Extra Reading credit in essay-style outputs.

Example Essays use an Extra Reading blend of 15%-30% through paragraph slots that add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation.

## Output contract

Use `references/exam_prep_notes_protocol.md` as the canonical coverage, language, formula-visibility, and format guide for Notes output.

Write like a strong tutor preparing a student for an exam. Explain what each topic means, why it matters, how it works, and how the knowledge is interpreted or applied.

Formula-heavy content must be visible in the final document. Use Word equation/OMML rendering where possible. Use a domain-neutral formula normalization pipeline and readable Unicode mathematical fallback when equation conversion is unavailable.

Render Notes as knowledge explanations with integrated formula, method, calculation, worked example, mechanism, comparison, visual, and interpretation support.

Exam Type Related add-on writing:

- MCQ: source questions in lecture order, tested point, MCQ wording, correct reasoning, plausible wrong statement, why it is wrong, and question-derived high-frequency knowledge points for the add-on.
- Short Answer: source questions in lecture order, definition, mark points, explain sentence, example answer, and question-derived high-frequency knowledge points for the add-on.
- Long Answer: source question, question demand, relevant knowledge, answer structure, example answer, and academic analysis/prediction result.
- Practical/Data/Problem: source task, method aim, readout, control, calculation or interpretation, limitation, conclusion, and academic analysis/prediction result.
- Math/Physics/Practical Worked Solutions: every extracted calculation, derivation, estimate, proof, data, or problem question developed as worked-solution teaching notes with assumptions, unit or dimension reasoning, interpretation, and concise evidence status.
- Essay: claim, explanation, course detail, Extra Reading evidence, analysis, link back to the question.

For math, physics, calculation, derivation, estimate, proof, and data/problem walkthrough outputs, write complete worked-solution notes. They should teach the question interpretation, relevant givens, target, method choice, derivation or calculation path, answer explanation, assumptions, unit or dimension reasoning, result meaning, and evidence status in coherent prose rather than a fixed fill-in template.

Render DOCX Notes with Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact black-and-white academic tables, centered display formulas, academically useful source visuals, and clear knowledge sections. Use restrained academic styling. Filename and file-set choices should produce readable, distinct names for each output.

Recommended section order:

1. Knowledge-unit sections in course order or knowledge-priority order.
2. Formula and method explanations inside the relevant knowledge unit.
3. Essay-style external enrichment inside the confirmed essay/add-on paragraph or beside the course point it strengthens.

## Routes

| User request | Preliminary route | Output after human review |
|---|---|---|
| make notes, revise, prepare this course, go through lectures | `exam_prep_notes` | DOCX explanation Notes |
| identify exam format, how is this course examined | `exam_mode_diagnosis` | chat or JSON diagnosis |
| MCQ, SBA, multiple choice | `mcq_preparation` | separate MCQ Exam Type Related add-on |
| short answer, SAQ, definitions, state/list questions | `short_answer_preparation` | separate short-answer Exam Type Related add-on |
| long answer, problem, data, practical, past-paper walkthrough | `long_answer_preparation` | separate long-answer/practical/data/problem add-on or worked-solution teaching notes when calculation/problem signals dominate |
| essay, in-campus essay, example essay, model essay | `essay_preparation` | separate essay Exam Type Related add-on |
