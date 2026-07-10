---
name: exam-prep-online-essay-exam
description: Draft Online Essay Exam answers as a first-class Everything Exam Prep branch after route confirmation, source-permission Ask Questions, locked brief, evidence map, paragraph-level plan, critical-analysis plan, Planning Approval, draft generation, and QA. Use when the confirmed assessment type is Online Essay Exam.
---

# Online Essay Exam Drafting

Use this Skill after `exam-prep-index` confirms the `online_essay_exam_drafting` route. Treat Online Essay Exam as the only new Exam Type, parallel to MCQ, Short Answer, Long Answer, Worked Solutions, and Essay Question. Do not route it through ordinary `essay_preparation`.

Default public output is English. Change the language only when the user explicitly overrides it for the current task; examples in another language do not change the default.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/online_essay_exam_protocol.md`
- `references/extra_reading_workflow.md` when Online Materials, external academic sources, or Extra Reading are allowed
- `references/language_quality_contract.md`

Use `scripts/plan_workflow.py` and `scripts/build_review_questions.py` to keep route confirmation, material-role review, source-permission Ask Questions, and output-choice questions consistent with the index.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before any public Online Essay Exam output. Confirm the Online Essay Exam route, Material type/source roles, optional Notes choice, Online Materials permission, Lecture Materials permission, complete-draft permission under the assessment rules, allowed supporting source set, citation expectation, and output format before Notes support, evidence mapping, planning, reports, or drafting.

## Workflow

1. Display the Auto-diagnosis review plan and confirm the exam branch as `Online Essay Exam`.
2. Ask permission questions before planning: Online Materials status, Lecture Materials status, whether the assessment rules permit a complete draft, allowed supporting sources, citation expectation, and output format.
3. Build a locked Online Essay Exam brief from the exact question, module context, allowed source set, word/time limits when supplied, citation expectations, output language, and unresolved plan-changing items.
4. Do not plan or draft while Online Materials or Lecture Materials permissions remain unresolved unless the user explicitly records a user-confirmed default. Never generate a complete draft when complete-draft permission is denied or unclear; preserve the denial and provide only allowed review, evidence mapping, feedback, or planning support.
5. Build an evidence map only from allowed sources. Use Lecture Materials as primary evidence, background, or not at all according to the confirmed rule. Use Online Materials only when confirmed as allowed or required.
6. Create thesis or central-answer options when the question direction is not already fixed.
7. Produce a paragraph-level structure plan and CriticalAnalysisPlan. Keep claims, evidence, interpretation, limitation, and links back to the exact question close together.
8. Run Planning Approval after the integrated plan is visible. After approval, draft directly without a redundant start-writing question.
9. If a plan-changing contradiction appears during writing, stop drafting and use a writing gate rather than silently changing source rules, thesis, or structure.
10. Run QA before delivery or DOCX rendering.

## Output Contract

The public output is an exam-facing Online Essay Exam draft, not a Specific Research Report. It should contain the approved answer structure, developed paragraphs, citations when required and available, and a conclusion that answers the exact question.

Use DOCX output when the user requests Word, DOCX, file output, or formatted output. Apply the package academic default: Arial, 2.5 cm margins, centered main title, left-aligned headings, justified body text, and 1.5 line spacing unless the exam instructions say otherwise.

Notes are optional support for this route. Do not force Notes before drafting unless the user asks to review Lecture Materials first.

## QA

Before final output, verify:

- `online_essay_exam_drafting` is the confirmed route.
- The exact question or title is known or explicitly unresolved.
- Online Materials and Lecture Materials permissions are recorded.
- Complete-draft permission is explicitly allowed by the confirmed assessment rules before a complete draft is generated.
- Evidence claims match the allowed source types.
- Citation style, citation quantity, or no-citation expectation is recorded when relevant.
- The draft follows the approved paragraph-level plan and CriticalAnalysisPlan.
- The conclusion answers the exact question.
- DOCX formatting follows the confirmed or default academic style when DOCX is requested.
