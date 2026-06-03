---
name: everything-exam-preparation
description: Simple student-facing exam preparation workflow for notes, lecture slides, practice material, past papers, MCQ, short answer, long answer, and essay exams.
---

# Everything Exam Preparation

This Skill helps students prepare for exams from uploaded course material and practice material.

## Core job

Students provide knowledge material and practice material. The Skill reads the material, works out what the course teaches, works out how the course is examined, connects the two, and produces student-facing exam preparation output.

The default output is:

```text
Exam_Preparation_Notes.docx
```

## Simple workflow

1. Read the supplied files.
2. Build a simple fragment index from readable content.
3. Diagnose the exam mode from the prompt and practice material.
4. Generate preparation notes in the target language style.
5. Render the notes in the target output format style.
6. Add MCQ, short-answer, long-answer, practical/data/problem, or essay preparation when relevant.

## Output language style

Use `references/language_quality_contract.md` as the writing style guide.

Write like a strong tutor preparing a student for an exam. Explain what each topic means, why it matters, how it appears in questions, and how the student can use it in an answer.

Mode-specific writing:

- MCQ: tested point, MCQ wording, correct reasoning, plausible wrong statement, why it is wrong.
- Short Answer: definition, mark points, explain sentence, example answer.
- Long Answer: question demand, relevant knowledge, answer structure, example answer, why the answer works.
- Practical/Data/Problem: method aim, readout, control, calculation or interpretation, limitation, exam conclusion.
- Essay: claim, explanation, course detail, analysis, link back to the question.

## Output format style

Use `references/exam_prep_notes_protocol.md` as the document format guide.

Render `Exam_Preparation_Notes.docx` with Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact tables, and clear exam preparation sections.

Recommended section order:

1. Course Overview.
2. Exam Pattern and Examiner Habits.
3. High-Yield Topics.
4. Topic-by-Topic Exam Preparation Notes.
5. Mode-specific preparation.
6. Final Revision Checklist when useful.

## Routes

| User request | Route | Output |
|---|---|---|
| make notes, revise, prepare this course, go through lectures | `exam_prep_notes` | `Exam_Preparation_Notes.docx` |
| identify exam format, how is this course examined | `exam_mode_diagnosis` | chat or JSON diagnosis |
| MCQ, SBA, multiple choice | `mcq_preparation` | notes plus MCQ preparation |
| short answer, SAQ, definitions, state/list questions | `short_answer_preparation` | notes plus short-answer preparation |
| long answer, problem, data, practical, past-paper walkthrough | `long_answer_preparation` | notes plus worked question preparation |
| essay, in-campus essay, example essay, model essay | `essay_preparation` | notes plus essay questions and example essays |
