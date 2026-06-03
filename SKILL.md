---
name: everything-exam-preparation
description: Simple student-facing exam preparation workflow for notes, lecture slides, practice material, past papers, MCQ, short answer, long answer, and essay exams.
---

# Everything Exam Preparation

This Skill helps students prepare for exams from uploaded course material and practice material.

## Core job

Students provide two kinds of material:

- Knowledge material: lecture slides, lecture notes, official notes, module handbooks, reading notes, practical handouts.
- Practice material: past papers, practice questions, problem sheets, MCQs, short-answer questions, essay prompts, mark schemes, answer keys, example answers.

The Skill should:

1. Work out what the course teaches.
2. Work out how the course is examined.
3. Connect the knowledge material to the practice material.
4. Produce `Exam_Preparation_Notes.docx` as the default preparation notes.
5. Add mode-specific preparation when the exam format is MCQ, short answer, long answer, or essay.

## Simple workflow

1. Read the supplied files and classify each file as knowledge material, practice material, marking material, style/reference material, or other material.
2. Extract readable text and available embedded media when practical.
3. Build a simple fragment index so the assistant can find course topics, repeated exam topics, command words, mark values, and recurring question patterns.
4. Diagnose the exam mode from the prompt and practice material.
5. Generate student-facing preparation notes and the relevant exam-mode preparation.

## Routes

| User request | Route | Output |
|---|---|---|
| make notes, revise, prepare this course, go through lectures | `exam_prep_notes` | `Exam_Preparation_Notes.docx` |
| identify exam format, how is this course examined | `exam_mode_diagnosis` | chat or JSON diagnosis |
| MCQ, SBA, multiple choice | `mcq_preparation` | notes plus MCQ preparation |
| short answer, SAQ, definitions, state/list questions | `short_answer_preparation` | notes plus short-answer preparation |
| long answer, problem, data, practical, past-paper walkthrough | `long_answer_preparation` | notes plus worked question preparation |
| essay, in-campus essay, example essay, model essay | `essay_preparation` | notes plus essay questions and example essays |

## Exam preparation behaviour

### Base notes

Create notes that explain the course in the way a student should revise it:

- what each topic means;
- why it matters;
- how mechanisms, methods, calculations, graphs, assays, comparisons, or arguments work;
- which topics recur in practice material;
- how knowledge is likely to be used in answers.

### MCQ preparation

For frequently tested knowledge, add:

- how the point is tested in MCQ/SBA questions;
- how to apply the knowledge when choosing an option;
- plausible statements that look correct but are wrong;
- distinctions that prevent common distractor mistakes.

### Short-answer preparation

For short-answer material, add:

- definitions worth memorising;
- answer points that can be written as separate marks;
- explain-style moves that connect cause, mechanism, result, and significance;
- short examples showing how to turn notes into answer sentences.

### Long-answer preparation

For long-answer, practical, data, or problem questions, add:

- detailed walkthroughs of representative past-paper or practice questions;
- example answers;
- explanation of which course knowledge each answer uses;
- method, data, graph, calculation, control, limitation, and interpretation steps where relevant.

### Essay preparation

For essay or in-campus essay exams, add:

- exam-ready essay-style English explanations inside the notes;
- broad essay questions that can cover common modules;
- example essay plans and example essays;
- paragraph-level reasoning that links topic, evidence, explanation, counterpoint, and conclusion.

## Output style

Write directly for a student preparing for an exam. Prefer clear headings, compact explanations, useful tables, worked examples, and exam-ready paragraphs. Keep the workflow simple and focused on helping the student study and answer questions.
