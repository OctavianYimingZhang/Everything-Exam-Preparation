# Online Essay Exam Protocol

Online Essay Exam is a first-class drafting branch, parallel to the existing exam branches such as MCQ, Short Answer, Long Answer, Worked Solutions, and Essay Question. It is not a subtype of ordinary Essay Question preparation. Timing such as 48 hours is metadata, not the route identity.

## Route Purpose

Use `online_essay_exam_drafting` when the confirmed assessment type is Online Essay Exam. Phrases such as take-home, open-book, timed, or 48h may help detect that branch, but they must not become separate public Types. The output is an exam-facing draft built from confirmed source rules, not a Specific Research Report.

Ordinary `essay_preparation` remains for essay exam prep, essay-topic reports, example essays, model-answer support, and Extra Reading reinforcement.

## Material Collection Gate

Before any plan, evidence map, Notes, report, or draft, display the Auto-diagnosis review plan and ask the user to confirm:

- Exam branch: Online Essay Exam as a peer option beside MCQ, SAQ, Long Answer Question, Essay Question, and existing route options.
- Material type and source roles.
- Whether Notes are needed as optional support after source permissions are confirmed.
- Whether Online Materials are required, optional, forbidden, or unclear.
- Whether Lecture Materials may be used as primary evidence, background only, forbidden, or unclear.
- Whether the confirmed assessment rules explicitly permit assistance with a complete draft.
- Whether Past Papers, rubrics, module handbooks, uploaded readings, and external academic sources may be used.
- Whether citations or references are required, optional, forbidden, or not specified.
- Whether the final output should be a chat draft, DOCX draft, or both.

Missing permission answers remain plan-changing unresolved items. Generate optional Notes, the essay plan, evidence map, report, or draft only after the relevant source-use rule is resolved or explicitly recorded as a user-confirmed default. A complete draft additionally requires an explicitly allowed assessment-draft permission. If that permission is denied, preserve the denial, do not re-ask it automatically, and limit support to allowed review, evidence mapping, feedback, and planning until the user explicitly changes the permission.

## Locked Brief

The internal Online Essay Exam locked brief should record:

- exact question or title;
- module or course context;
- assessment setting and timing when supplied;
- allowed source set, including Online Materials and Lecture Materials status;
- complete-draft permission from the confirmed assessment rules;
- word limit or expected scope when supplied;
- citation style, citation quantity, or no-citation expectation when supplied;
- output language;
- output format;
- user preferences that affect thesis, structure, or evidence;
- unresolved plan-changing items.

Do not delegate evidence extraction, drafting, or QA before the brief and source-permission rules are locked.

## Evidence Map

Build an evidence map before claim-heavy drafting. Use only allowed source types:

- Lecture Materials as primary evidence only when confirmed.
- Lecture Materials as background only when confirmed.
- Online Materials only when allowed or required.
- Uploaded readings, rubrics, Past Papers, module handbooks, and external academic sources only within the confirmed source rules.

Each evidence item should support a claim, mechanism, method, limitation, counterargument, or interpretation move. Keep unsupported claims out of the draft.

## Planning and Drafting

Create a paragraph-level plan before writing:

- central answer or thesis;
- section order;
- paragraph function;
- claim and evidence path;
- critical-analysis placement;
- expected citation use;
- conclusion route back to the exact question.

Create a CriticalAnalysisPlan when the answer requires evaluation, comparison, limitation, counterargument, or judgement. Present the integrated plan and run Planning Approval. After approval, draft directly from the approved plan.

If a new issue would change source permissions, thesis, section order, citation burden, or output format, stop and run a writing gate.

## QA

Before final output, check:

- route is `online_essay_exam_drafting`;
- exact question or title is known or explicitly unresolved;
- Online Materials and Lecture Materials permissions are recorded;
- complete-draft permission is explicitly allowed before a complete draft is generated;
- claims use only allowed source types;
- citation expectations are followed without inventing metadata;
- draft follows the approved plan;
- critical analysis fits the evidence;
- conclusion answers the exact question;
- DOCX formatting follows the confirmed or default academic style when requested.
