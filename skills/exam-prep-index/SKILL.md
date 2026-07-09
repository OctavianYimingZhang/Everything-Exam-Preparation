---
name: exam-prep-index
description: Route broad Everything Exam Prep requests after analyzing all supplied material and asking the user to confirm Exam type, whether to generate Notes, and route-specific follow-up choices. Use for exam prep, course notes, past-paper preparation, exam-format diagnosis, MCQ or short-answer preparation, long-answer or practical preparation, worked solutions, essay preparation, Online Essay Exam drafting, mixed exam formats, question solving, question organization, and essay-style Extra Reading enrichment.
---

# Everything Exam Prep Index

Use this Skill as the controller for the Everything Exam Prep multiple Skill system. Treat direct invocation of this index as intent to use the exam-prep skill family.

Default public output for every focused route is English. Change the language only when the user explicitly overrides it for the current task; examples in another language do not change the default.

## Direct Invocation Gate

Direct invocation of this index starts the full Auto-diagnosis review workflow. Build the confirmed review state described in `references/input_and_evidence_protocol.md` before generating public Notes, Specific Research Reports, Worked Solutions, Question Solving output, organized question DOCX files, evidence maps, plans, or drafts.

## Required Workflow

1. Analyze all material the user supplied before choosing a public route.
2. Build a source map, fragment index, preliminary source-role diagnosis, and preliminary Exam type diagnosis.
3. When Notes may be generated from slide decks or slide-like PDFs, run [`exam-prep-slide-triage`](../exam-prep-slide-triage/SKILL.md) as internal material analysis before Notes drafting.
4. Display the Auto-diagnosis review plan.
5. Use `request_user_input` to ask the user to confirm or correct:
   - Exam type or route.
   - Material type and source roles when source roles are uncertain or materially affect output.
   - Whether to generate explanation Notes before the exam-specific output.
6. Ask route-specific follow-up questions for the confirmed Exam type. For Online Essay Exam, ask whether Online Materials are required, optional, forbidden, or unclear; whether Lecture Materials may be used as primary evidence, background only, forbidden, or unclear; which supporting source types are allowed; citation expectations; and draft output format before planning.
7. Apply the user's answers. If the user confirms a mixed exam format, activate every selected exam-type Sub Skill in the order that best fits the material.
8. Generate Notes first when the user chooses Notes. If the user declines Notes, skip this step explicitly.
9. Route to the confirmed exam-type Sub Skill or Sub Skills and generate the corresponding Specific Research Report. For Online Essay Exam, route to the drafting Skill and generate the locked-brief plan, evidence map, approved structure, draft, and QA instead of a Specific Research Report.
10. Own the `assessment_blueprint` route: confirm blueprint scope, use source fragments plus relevant Everything University memory references, preserve page/slide/time provenance, and avoid inventing assessment weights not supported by the sources.

For every report-style exam case, offer Notes as the default first output. Do not silently skip Notes unless the user says they do not want Notes. For Online Essay Exam, treat Notes as optional support and do not force them before drafting unless the user asks to review lecture content first.

## Asking Questions

The routing Skill must preserve the Asking Questions function. Use `scripts/build_review_questions.py` or an equivalent `request_user_input` payload.

The Exam type question should let the user choose the route instead of accepting the automatic diagnosis as final. Include a mixed-format option when the material shows several exam signals. If the user selects or writes a mixed format, load all matching Sub Skills.

The Notes question should ask whether to generate Notes before the Specific Research Report. Recommended default: generate Notes first.

Then ask the route-specific questions:

- Essay: ask whether to generate Example Essays. If yes, ask how many essays and whether to use the user's own prepared or predicted questions.
- Online Essay Exam: ask Online Materials permission, Lecture Materials permission, allowed supporting source set, citation expectation, and final draft output format before any evidence map, plan, Notes, report, or draft.
- MCQ or Short Answer: ask whether to generate the Exam Specific Research Report.
- Long Answer: ask whether to generate detailed analysis.
- Worked Solutions: ask whether the user wants question-by-question teaching.
- Assessment Blueprint: ask which confirmed assessment scope the blueprint should represent.
- Answer Evaluation: ask which supplied rubric, mark scheme, or expected-concept criteria should be used.
- Timed Practice: ask for the explicit duration and confirmed blueprint.
- Mixed: ask every relevant route-specific question for the selected routes.

Because `request_user_input` supports small question batches, ask these in staged batches when more than three questions are needed.

Do not draft public Notes, Specific Research Reports, add-ons, worked solutions, question solving output, or organized question DOCX files until the user answers the required routing questions or the user explicitly instructs a fixed route and fixed output set.

## Exam Type Diagnosis

Exam-mode diagnosis is part of this index Skill. Do not route diagnosis to a standalone `exam-prep-exam-mode` Skill.

Identify:

- Exam type or route: MCQ, short answer, long answer, practical/data/problem, worked solutions, essay, Online Essay Exam, question solving, question organization, or mixed.
- Material type and source roles: course-facing knowledge source, practice/question source, answer or marking source, style/example-answer source, Extra Reading source, or mixed/unclear source.
- Evidence strength: explicit instructions, section labels, question wording, mark schemes, answer keys, recurring task patterns, and source dates.
- Proposed outputs: Notes when accepted, then the confirmed Specific Research Report or Reports.

## Sub Skill Routing

Load the focused Sub Skill that owns each confirmed exam type:

| Confirmed exam type | Sub Skill |
| --- | --- |
| Notes accepted | [`exam-prep-notes`](../exam-prep-notes/SKILL.md) |
| Slide decks or slide-like PDFs before Notes | [`exam-prep-slide-triage`](../exam-prep-slide-triage/SKILL.md) |
| MCQ, SBA, multiple choice, distractor reasoning | [`exam-prep-mcq`](../exam-prep-mcq/SKILL.md) |
| Short answer, SAQ, definition/list/state questions | [`exam-prep-short-answer`](../exam-prep-short-answer/SKILL.md) |
| Long answer, scenario, practical, data, non-calculation problem walkthrough | [`exam-prep-long-answer`](../exam-prep-long-answer/SKILL.md) |
| Calculation, derivation, estimate, proof, data/problem worked solutions | [`exam-prep-worked-solutions`](../exam-prep-worked-solutions/SKILL.md) |
| Essay question, example essay, essay plan, essay exam prep | [`exam-prep-essay`](../exam-prep-essay/SKILL.md) |
| Online Essay Exam | [`exam-prep-online-essay-exam`](../exam-prep-online-essay-exam/SKILL.md) |
| Essay-only Extra Reading enrichment | [`exam-prep-extra-reading`](../exam-prep-extra-reading/SKILL.md) after [`exam-prep-essay`](../exam-prep-essay/SKILL.md) |
| Solving a user-supplied question and finding strict same-point practice | [`exam-prep-question-solver`](../exam-prep-question-solver/SKILL.md) |
| Organizing Past Paper or Practice Material questions by lecture order | [`exam-prep-question-organizer`](../exam-prep-question-organizer/SKILL.md) |

Mixed format means activate every selected route. Example: MCQ plus short answer means generate Notes if accepted, then run `exam-prep-mcq` and `exam-prep-short-answer`.

## Shared System Rules

All focused Skills use the same source and evidence layer:

- Read `references/input_and_evidence_protocol.md` for source-role handling, source signals, human review, and the Auto-diagnosis review plan.
- Read `references/exam_prep_notes_protocol.md` before writing explanation Notes.
- Use `exam-prep-slide-triage` before Notes generation for slide decks and slide-like PDFs. It is not a report-priority system and must not narrow Specific Research Reports.
- Read `references/exam_mode_and_addons_protocol.md` before writing exam-specific Specific Research Reports.
- Read `references/essay_exam_prep_protocol.md` before ordinary essay-preparation report work.
- Read `references/online_essay_exam_protocol.md` before Online Essay Exam drafting work.
- Read `references/extra_reading_workflow.md` only when the confirmed branch includes Essay Question or Online Essay Exam and source permissions allow it. Extra Reading is not a general Notes feature.
- Use `scripts/plan_workflow.py` and `scripts/build_review_questions.py` when a public output requires Exam type, Material type, and Notes-choice confirmation.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Operating Contract

Automatic diagnosis is preliminary. Before generating Notes, Specific Research Reports, Worked Solutions, or Online Essay Exam drafts, display the Auto-diagnosis review plan and use `request_user_input` to confirm or correct Exam type/route, Material type/source roles, and whether Notes should be generated. For Online Essay Exam, also confirm Online Materials and Lecture Materials permissions before planning or drafting.

Default output language is English unless the user explicitly requests another language. Follow user-requested filenames first; otherwise generate distinct DOCX filenames from the source, course, prompt, or note title.
