# Output Format Style Guide

Default artifact: `Exam_Preparation_Notes.docx`.

This file defines the target document structure and visual format for student-facing exam preparation notes.

## Document style

Use these document settings:

| Element | Style |
|---|---|
| Font | Arial |
| Page margins | 2.5 cm on all sides |
| Line spacing | 1.5 |
| Main title | Centered |
| Section headings | Left aligned |
| Body text | Justified |
| Tables | Compact Word tables with visible borders |

## Recommended document order

Use this order when the material supports it:

1. Main title.
2. Course Overview.
3. Exam Pattern and Examiner Habits.
4. High-Yield Topics.
5. Topic-by-Topic Exam Preparation Notes.
6. MCQ Preparation, Short-Answer Preparation, Long-Answer Preparation, or Essay Preparation as relevant.
7. Final Revision Checklist when useful.

## Section types

### Course Overview

Use short paragraphs or a compact table to explain what the course covers and how major topics connect.

Suggested format:

```text
Course Overview
This course is mainly about [...]. The central topics connect through [...]. In exam answers, these topics are usually used to explain [...].
```

### Exam Pattern and Examiner Habits

Use a table when practice material shows repeated question types.

Suggested columns:

| Question type | Common wording | What the examiner wants | How to prepare |
|---|---|---|---|

### High-Yield Topics

Use bullets or a table to show frequently tested topics.

Suggested format:

```text
High-Yield Topic: [topic]
Why it matters: [...]
How it is tested: [...]
How to answer: [...]
```

### Topic Notes

Use short paragraphs for concepts and mechanisms. Use bullets for answer points. Use tables for comparisons.

Suggested topic format:

```text
[Topic heading]
Core explanation: [...]
Exam use: [...]
Common question style: [...]
Example answer move: [...]
```

## Mode-specific sections

### MCQ Preparation

Use this format for MCQ content:

```text
Tested point: [...]
How it appears in MCQ: [...]
Correct reasoning: [...]
Plausible wrong statement: [...]
Why it is wrong: [...]
```

### Short-Answer Preparation

Use this format for short-answer content:

```text
Definition: [...]
Mark points: [...]
Explain sentence: [...]
Example answer: [...]
```

### Long-Answer Preparation

Use this format for long-answer content:

```text
Question: [...]
What the examiner wants: [...]
Relevant knowledge: [...]
Answer structure: [...]
Example answer: [...]
Why this answer works: [...]
```

### Practical/Data/Problem Preparation

Use this format for practical and data content:

```text
Task: [...]
Method aim: [...]
Readout: [...]
Control: [...]
Calculation or interpretation: [...]
Limitation: [...]
Exam conclusion: [...]
```

### Essay Preparation

Use this format for essay content:

```text
Module theme: [...]
Broad essay question: [...]
Thesis options: [...]
Paragraph plan: [...]
Example essay paragraph: [...]
```

## Renderer input shape

The DOCX renderer accepts flexible JSON. Useful top-level fields include:

```json
{
  "title": "Exam Preparation Notes",
  "course_overview": "...",
  "exam_habit_analysis": [...],
  "high_yield_topics": [...],
  "sections": [...],
  "mcq_preparation": [...],
  "short_answer_preparation": [...],
  "long_answer_preparation": [...],
  "essay_preparation": [...]
}
```

Section blocks can use plain text, dictionaries, points, tables, and worked examples. The renderer formats the content into a student-facing DOCX using the style above.
