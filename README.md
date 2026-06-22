# Everything Exam Preparation

Signal-driven exam preparation and Online Essay Exam drafting Skill for uploaded course content, practice material, Online Materials, and Extra Reading.

## Output naming

The default output type is DOCX notes. If the user requests filenames or a multi-file output set, follow that request. Otherwise generate clear, distinct DOCX filenames for each output from the source, course, prompt, or note title.

## What it does

1. Reads supplied course files, practice material, mark schemes, examples, Extra Reading, and other useful files.
2. Uses rough source hints as provenance labels.
3. Builds a fragment index from readable content.
4. Applies slide triage before Notes generation for slide decks and slide-like PDFs so useless slides are excluded from detailed public explanation while ILO, topic, visual, example, and summary slides can still support lecture order.
5. Extracts open knowledge signals and groups connected signals into knowledge units.
6. Calibrates Notes coverage from the knowledge units and required explanation.
7. Identifies Extra Reading and Online Materials only when the confirmed branch and source permissions allow essay-style enrichment.
8. Matches confirmed Extra Reading to essay claims or course points that need external enrichment.
9. Makes a preliminary diagnosis of Exam type/route, Material type/source roles, and proposed output set from the prompt and practice material.
10. Displays an **Auto-diagnosis review plan** and uses `request_user_input` for human review of Exam type, Material type, and whether Notes should be generated.
11. Updates the route, source-role handling, and final output plan from the user's confirmed or corrected answers.
12. Produces explanation-only teaching Notes first when the user accepts Notes.
13. Produces the confirmed Specific Research Report for MCQ, short answer, long answer, practical/data/problem, worked-solution, essay, or mixed exams.
14. For Online Essay Exam, asks Online Materials and Lecture Materials source-permission questions, locks the brief, builds an evidence map and approved paragraph-level plan, then produces a draft and QA instead of a Specific Research Report.
15. When Past Paper or question-containing Practical Materials are supplied and confirmed, produces a separate question-based Specific Research Report alongside Notes when Notes are accepted.
16. When Past Paper or Practical Materials contain calculation, derivation, estimate, proof, data, or problem questions and are confirmed, produces a separate detailed worked-solutions DOCX.
17. When the user asks how to solve a supplied question, produces a `question_solution_report` that explains the target question, shows the matching knowledge unit, and retrieves strict same-knowledge-point questions from the supplied Past Paper or Practice Material.
18. When the user asks to organize Past Paper or Practice Material, produces `organized_questions_docx` sorted by Lecture Slides or lecture knowledge-unit order and containing questions plus minimal provenance.

Student-facing Notes explain the lecture and exam-relevant knowledge the student needs to master. They are broad lecture reconstruction documents for students who may not have learned the material yet. MCQ, SAQ, and other Specific Research Reports remain separate concise exam-priority reinforcement outputs. Source intake, extraction notes, coverage calibration, QA state, route planning, subagent narration, and similar workflow records remain internal.

## Multiple Skill system

This repository now exposes Everything Exam Prep as a multiple Skill system. The root `SKILL.md` remains as a compatibility entrypoint, while focused entrypoints live under `skills/`.

Focused Skills:

- `exam-prep-index`: routes broad requests to the right focused Skill.
- `exam-prep-notes`: generates explanation-only DOCX Notes.
- `exam-prep-slide-triage`: internal Notes material analysis for excluding non-teaching slides and preserving useful slide structure without detailed explanation.
- `exam-prep-mcq`: produces MCQ/SBA Specific Research Reports.
- `exam-prep-short-answer`: produces SAQ and short-answer Specific Research Reports.
- `exam-prep-long-answer`: produces long-answer, practical, data, scenario, and problem Specific Research Reports.
- `exam-prep-worked-solutions`: produces calculation, derivation, estimate, proof, data, and problem worked-solution teaching notes.
- `exam-prep-essay`: produces essay preparation and Extra Reading enriched essay outputs.
- `exam-prep-online-essay-exam`: produces Online Essay Exam locked briefs, allowed-source evidence maps, approved plans, drafts, and QA.
- `exam-prep-extra-reading`: finds, classifies, and matches Extra Reading for essay enrichment.
- `exam-prep-question-solver`: explains a target question, displays the matched course knowledge, and returns strict same-knowledge-point transfer questions.
- `exam-prep-question-organizer`: compiles Past Paper and Practice Material questions into a DOCX ordered by lecture knowledge-unit sequence.

`python3 scripts/publish_skill.py --sync-local-skill` installs both the legacy `everything-exam-preparation` local Skill and the focused sibling Skills under `~/.codex/skills/`.

The routing workflow is: analyze all supplied material, ask the user to choose or correct the Exam type, ask whether to generate Notes, ask route-specific follow-up questions, generate Notes first if accepted, then run the confirmed exam-type Sub Skill or Sub Skills to produce the Specific Research Report. Online Essay Exam is a parallel branch: ask Online Materials and Lecture Materials permissions before planning, then produce a draft workflow instead of a Specific Research Report. Mixed exam format activates every selected exam-type Sub Skill. Exam-mode diagnosis now lives inside `exam-prep-index`, not in a separate Skill.

## Extra Reading

Extra Reading is only for Essay Question, Example Essay, and Online Essay Exam enrichment when source permissions allow it. It can include academically useful sources such as textbook-like background, chapters, journal articles, primary research, DOI/PMID sources, lecture-mentioned references, mechanism evidence, counterargument material, and evaluation sources that help earn Extra Reading credit in essay-style outputs.

Workflow utility:

```bash
python3 scripts/extra_reading_tools.py all --source-scan source_scan.json --out extra_reading.json
python3 scripts/extra_reading_tools.py queries --source-scan source_scan.json --out extra_reading_queries.json
python3 scripts/essay_exam_tools.py generate-plan --source-scan source_scan.json --extra-reading extra_reading.json --out essay_plan.json
```

Expected Extra Reading output shape:

```json
{
  "schema_version": 2,
  "extra_reading_sources": [],
  "lecture_topics": [],
  "search_queries": [],
  "topic_enrichment": [],
  "essay_enrichment": {
    "extra_reading_blend": "15-30%",
    "paragraph_slots": []
  }
}
```

## Current output focus

This version focuses on signal-driven coverage, teaching depth, domain-neutral formula visibility, academic source visuals, calculation worked examples, output language style, output format style, and student-facing coverage of exam-relevant knowledge.

Before public output is generated, automatic routing remains a preliminary diagnosis. `scripts/plan_workflow.py` marks `human_review_required: true`, stores automatic files under `proposed_outputs`, and inserts `human_review_exam_material_output_confirmation` before writing. `scripts/build_review_questions.py` builds the `request_user_input` payload for Exam type/route, Material type/source roles, and whether Notes should be generated.

### 1. Coverage calibration

`references/input_and_evidence_protocol.md` defines open knowledge signals. `references/exam_prep_notes_protocol.md` defines how those signals become a coverage map before Notes are written. Coverage planning is internal; the final document is a knowledge-explanation document. Formulas, visuals, and worked examples function as parts of knowledge explanation; exam advice, workflow display, Skill explanation, and high-frequency-analysis process stay in the internal workflow record.

Exam Prep Notes use `coverage_policy: lecture_unit_complete`. They should preserve lecture/source order and reconstruct most substantive lecture content through coherent knowledge units. This is near slide-by-slide coverage at the level of lecture units, not a literal explanation of every slide or image. The aim is that a weakly prepared student can read the Notes once and understand most of the lecture before using the separate report to reinforce exam priorities.

Coverage is driven by:

- knowledge units;
- concepts and definitions;
- mechanisms and causal chains;
- methods, assays, controls, and readouts;
- comparisons;
- calculations and data interpretation;
- evidence and confirmed essay-style Extra Reading;
- conceptual applications and interpretation use.
- source visuals when they clarify a concept, mechanism, method, formula, graph, table, pathway, scheme, or data interpretation.
- worked-example signals when a calculation, derivation, estimate, proof, data, or problem example teaches reusable reasoning.

Examples are used when they clarify knowledge, mechanism, method, calculation, interpretation, or conceptual application.

Content triage keeps Notes broad without becoming a dump of every slide artifact:

- `core_lecture_content` is covered.
- `supporting_example` is included when useful and compressed when repetitive.
- `reading_reference`, `admin_or_boilerplate`, and `low_exam_relevance_context` are excluded unless directly needed for examinable course knowledge.

Slide triage adds page-level material analysis for slide decks and slide-like PDFs. It is not a detail-level grading system. Each slide-like fragment can be marked with `slide_decision: use`, `merge_with_previous`, or `exclude`; `notes_role`; `detailed_explanation_allowed`; and `triage_reason`. ILOs, agendas, topic boundaries, section dividers, summaries, non-core visuals, non-essential data, and examples may guide topic order or merge with nearby units without becoming long explanations. Administrative, copyright/license, reading-list-only, decorative, empty, pure transition, duplicate, and generic awareness slides remain in `slide_triage_audit` and do not become public Notes sections.

### 2. Teaching depth and formula visibility

`references/exam_prep_notes_protocol.md` defines how the notes should teach:

- strong tutor voice;
- direct course explanation;
- concept identity, mechanism, method, calculation, assumptions, interpretation, and conceptual application;
- visible formulas using Word equation/OMML where possible;
- readable Unicode mathematical fallback when equation conversion is unavailable;
- domain-neutral formula normalization for mathematics, physics, chemistry, biological science, and coding-adjacent technical material;
- academically useful cropped PDF visual-region assets and embedded DOCX/PPTX media when they strengthen a knowledge unit;
- `worked_example` blocks for physics/math calculation-heavy knowledge units;
- essay-style external enrichment when the confirmed output calls for it;
- separate Specific Research Reports for MCQ, short answer, long answer, practical/data/problem, worked solutions, essay preparation, and mixed exams.

### 3. Output format style

`references/exam_prep_notes_protocol.md` defines how the notes should be structured:

- DOCX notes with filenames requested by the user or generated from context;
- Arial;
- 2.5 cm margins;
- 1.5 line spacing;
- centered main title;
- left-aligned headings;
- justified body text;
- compact tables;
- compact academic captions and source visuals;
- clear knowledge sections that teach the material and keep workflow or process records internal.

### 4. Separate question-based Specific Research Report

`references/exam_mode_and_addons_protocol.md` defines Past Paper and Practical question outputs. MCQ and Short Answer reports are result-only Past Paper-driven recurrence reports: they use Past Papers, Mock Papers, and official exam papers to find recurring exam-needed knowledge points, then present those points in Lecture Slides order. Ordinary Practice Material can provide context but does not count toward high-frequency recurrence. SAQ subquestions are treated as independent question records. Public MCQ and Short Answer reports do not show evidence tables, recurrence calculations, source locators, matching debug, or workflow steps. These reports must not narrow or replace broad lecture reconstruction in Notes.

Slide triage is not used to narrow Specific Research Reports. MCQ, SAQ, Long Answer, Worked Solutions, Essay, Question Solving, and Question Organization keep their route-specific evidence logic.

Online Essay Exam keeps a separate drafting logic. It requires source-permission Ask Questions for Online Materials and Lecture Materials, a locked brief, allowed-source evidence map, paragraph-level plan, CriticalAnalysisPlan, Planning Approval, draft generation, and QA. It is not ordinary Essay Specific Research Report behavior.

Complete worked-solution notes are generated as a separate DOCX when Past Paper or Practical Materials contain calculation, derivation, estimate, proof, data, or problem questions. Available solutions or mark schemes are used as evidence for formula choice, algebra path, units, assumptions, final result, and interpretation.

Question solving uses `exam-prep-question-solver` and `scripts/exam_mode_tools.py solve-question`. The fixed student-facing order is question analysis, matching knowledge display and explanation, solution reasoning, strict same-knowledge-point Past Paper or Practice Material questions, and transfer-practice prompt. Strict same-point retrieval depends on user-supplied material, matched lecture knowledge unit, shared knowledge terms, question demand, and source locators.

Question organization uses `exam-prep-question-organizer` and `scripts/exam_mode_tools.py organize-questions`. The default output is `organized_questions_docx`; it shows questions plus minimal provenance and sorts by Lecture Slides or lecture knowledge-unit order. Questions that match more than one lecture unit are assigned to the latest matching lecture unit.

## Routes

- `exam_prep_notes`
- `mcq_preparation`
- `short_answer_preparation`
- `long_answer_preparation`
- `worked_solution_preparation`
- `essay_preparation`
- `online_essay_exam_drafting`
- `mixed_exam_preparation`
- `question_solving`
- `question_organizing`

## Step 8: publish and update

```bash
python3 scripts/validate_skill_contracts.py
python3 scripts/github_ready_check.py
python3 scripts/publish_skill.py --push
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --push --sync-local-skill
```

`--push` runs `git push` from the repository root. `--sync-local-skill` copies the repository into `~/.codex/skills/everything-exam-preparation` and installs each focused Skill as a sibling local Skill so the local Skill installation updates from the current repository files.
