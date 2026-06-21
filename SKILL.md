---
name: everything-exam-preparation
description: Compatibility entrypoint and index for the Everything Exam Prep multiple Skill system. Analyze all supplied material, ask the user to choose Exam type, whether to generate Notes, and route-specific options, then route to focused skills for notes, MCQ, short answer, long answer, practical/data/problem, worked solutions, essay preparation, question solving, question organization, and essay-only Extra Reading enrichment.
---

# Everything Exam Preparation

This Skill helps students prepare for exams from uploaded course material, practice material, and academically useful Extra Reading.

## Core job

Students provide course material, practice material, and optionally Extra Reading. The Skill reads the material, extracts open knowledge signals, groups connected signals into knowledge units, calibrates the required explanation for each unit, uses Extra Reading for essay-style enrichment when relevant, and produces student-facing exam preparation output.

Student-facing Notes are explanation-only, knowledge-only teaching notes that show the lecture and exam-relevant knowledge a student needs to master. They explain concepts, mechanisms, methods, calculations, assumptions, interpretations, conceptual applications, academically useful source visuals, and calculation worked examples when those examples teach the relevant knowledge unit. Exam Type Related preparation is produced as a separate Specific Research Report for the relevant route.

Automatic Exam type, Material type, and Notes-choice recognition is a preliminary diagnosis. Before generating Notes, Specific Research Reports, or Worked Solutions, display an **Auto-diagnosis review plan** and use `request_user_input` to confirm or correct Exam type/route, Material type/source roles, and whether Notes should be generated. Mixed exam signals mean the confirmed output should cover each relevant component in the mix.

If the user requests a filename or file set, follow that request. Otherwise generate a clear, distinct DOCX filename for each output from the source, course, prompt, or note title.

Default output language is English unless the user explicitly requests Chinese, bilingual, or multiple-language output. Bilingual examples supplied by the user are format references and do not change the default language by themselves.

## Multiple Skill system

This root Skill is the compatibility entrypoint. For new work, load `exam-prep-index` first when routing has not already been confirmed. The index analyzes all material, asks the user to confirm Exam type and whether to generate Notes, generates Notes first when accepted, then routes to the confirmed Specific Research Report Skill.

| User request | Focused Skill |
|---|---|
| make notes, revise, prepare this course, go through lectures | [`exam-prep-notes`](skills/exam-prep-notes/SKILL.md) |
| identify exam format, classify assessment type, diagnose past-paper structure | [`exam-prep-index`](skills/exam-prep-index/SKILL.md) |
| MCQ, SBA, multiple choice | [`exam-prep-mcq`](skills/exam-prep-mcq/SKILL.md) |
| short answer, SAQ, definitions, state/list questions | [`exam-prep-short-answer`](skills/exam-prep-short-answer/SKILL.md) |
| long answer, scenario, data, practical, past-paper walkthrough | [`exam-prep-long-answer`](skills/exam-prep-long-answer/SKILL.md) |
| calculation, derivation, estimate, proof, data, problem walkthrough | [`exam-prep-worked-solutions`](skills/exam-prep-worked-solutions/SKILL.md) |
| essay, in-campus essay, example essay, model essay | [`exam-prep-essay`](skills/exam-prep-essay/SKILL.md) |
| Extra Reading, external academic evidence, essay enrichment | [`exam-prep-extra-reading`](skills/exam-prep-extra-reading/SKILL.md) |
| solve this question, how do I answer this question, question walkthrough | [`exam-prep-question-solver`](skills/exam-prep-question-solver/SKILL.md) |
| organize Past Paper questions, sort Practice Material by lecture order | [`exam-prep-question-organizer`](skills/exam-prep-question-organizer/SKILL.md) |

Use [`exam-prep-index`](skills/exam-prep-index/SKILL.md) when the user asks broadly and the route is not yet clear. If a focused Skill is installed as a sibling local Skill, prefer that installed focused Skill. If not, follow the linked source entrypoint and the shared references in this package.

Notes are offered for every exam type and should be generated before the route-specific Specific Research Report unless the user declines Notes. Extra Reading is available only when the confirmed Exam type includes essay.

## Simple workflow

1. Read the supplied files.
2. Build a simple fragment index from readable content.
3. Calibrate coverage from knowledge signals and knowledge units.
4. Identify Extra Reading sources for essay-style enrichment when the user supplies them or the confirmed output calls for them.
5. Match confirmed Extra Reading to essay claims or course points that need external enrichment.
6. Make a preliminary diagnosis of Exam type/route, Material type/source roles, and proposed output set from the prompt and source material.
7. Display an **Auto-diagnosis review plan**, then call `request_user_input` with concrete options for Exam type, Material type, and whether to generate Notes.
8. Ask route-specific follow-up questions for Essay, MCQ, Short Answer, Long Answer, Worked Solutions, or Mixed routes.
9. Update the route, source-role handling, and final output plan from the user's confirmed or corrected answers.
10. Generate explanation-only teaching Notes from the confirmed coverage map when the user accepts Notes.
11. Render visible formulas, tables, academic source visuals, worked examples, and explanations in the target output format style.
12. Produce the confirmed MCQ, short-answer, long-answer, practical/data/problem, essay preparation, or Math/Physics/Practical Worked Solutions Specific Research Report as separate output. For mixed exam formats, produce every confirmed report.

## Extra Reading workflow

Use `references/extra_reading_workflow.md` for the Extra Reading workflow.

Extra Reading is only for Essay Question and Example Essay enrichment. Use it to add external evidence, mechanism depth, molecular evidence, counterargument, and evaluation that can help the user earn Extra Reading credit in essay-style outputs.

Example Essays use an Extra Reading blend of 15%-30% through paragraph slots that add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation.

## Output contract

Use `references/exam_prep_notes_protocol.md` as the canonical coverage, language, formula-visibility, and format guide for Notes output.

Write like a strong tutor preparing a student for an exam. Explain what each topic means, why it matters, how it works, and how the knowledge is interpreted or applied.

Formula-heavy content must be visible in the final document. Use Word equation/OMML rendering where possible. Use a domain-neutral formula normalization pipeline and readable Unicode mathematical fallback when equation conversion is unavailable.

Render Notes as knowledge explanations with integrated formula, method, calculation, worked example, mechanism, comparison, visual, and interpretation support.

Specific Research Report writing:

- MCQ: a result-only Past Paper-driven recurrence report in lecture order, written as concise exam-needed knowledge points in the reference-document style rather than as a field-by-field template, answer walkthrough, or Notes-style teaching document.
- Short Answer: a result-only Past Paper-driven recurrence report in lecture order, written as concise exam-needed knowledge points in the reference-document style rather than as a field-by-field template, answer walkthrough, or Notes-style teaching document.
- Long Answer: source question, question demand, relevant knowledge, answer structure, example answer, and academic analysis/prediction result.
- Practical/Data/Problem: source task, method aim, readout, control, calculation or interpretation, limitation, conclusion, and academic analysis/prediction result.
- Math/Physics/Practical Worked Solutions: every extracted calculation, derivation, estimate, proof, data, or problem question developed as worked-solution teaching notes with assumptions, unit or dimension reasoning, interpretation, and concise evidence status.
- Essay: claim, explanation, course detail, Extra Reading evidence, analysis, link back to the question.
- Question Solving: target question analysis, matching knowledge display and explanation, solution reasoning, strict same-knowledge-point Past Paper or Practice Material questions, and transfer-practice prompt.
- Question Organization: `organized_questions_docx` with Past Paper and Practice Material questions sorted by Lecture Slides or lecture knowledge-unit order, with minimal provenance and without answer or explanation content.

For math, physics, calculation, derivation, estimate, proof, and data/problem walkthrough outputs, write complete worked-solution notes. They should teach the question interpretation, relevant givens, target, method choice, derivation or calculation path, answer explanation, assumptions, unit or dimension reasoning, result meaning, and evidence status in coherent prose rather than a fixed fill-in template.

Render DOCX Notes with Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact black-and-white academic tables, centered display formulas, academically useful source visuals, and clear knowledge sections. Use restrained academic styling. Filename and file-set choices should produce readable, distinct names for each output.

Recommended section order:

1. Knowledge-unit sections in course order or knowledge-priority order.
2. Formula and method explanations inside the relevant knowledge unit.
3. Essay-style external enrichment inside the confirmed essay report paragraph or beside the course point it strengthens.

## Routes

| User request | Preliminary route | Output after human review |
|---|---|---|
| make notes, revise, prepare this course, go through lectures | `exam_prep_notes` | DOCX explanation Notes |
| identify exam format, how is this course examined | `mixed_exam_preparation` through `exam-prep-index` | ask user to confirm Exam type, then route |
| MCQ, SBA, multiple choice | `mcq_preparation` | Notes if accepted, then separate MCQ Specific Research Report |
| short answer, SAQ, definitions, state/list questions | `short_answer_preparation` | Notes if accepted, then separate short-answer Specific Research Report |
| long answer, problem, data, practical, past-paper walkthrough | `long_answer_preparation` | Notes if accepted, then separate long-answer/practical/data/problem Specific Research Report or worked-solution report when calculation/problem signals dominate |
| essay, in-campus essay, example essay, model essay | `essay_preparation` | Notes if accepted, then separate essay Specific Research Report |
| solve this question, how do I answer this question, question walkthrough | `question_solving` | Question Solution Report with matched knowledge and strict same-point transfer questions |
| organize Past Paper questions, sort Practice Material by lecture order | `question_organizing` | Organized Questions DOCX in lecture knowledge-unit order |
