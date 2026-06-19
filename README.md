# Everything Exam Preparation

Signal-driven exam preparation Skill for uploaded course content, practice material, and Extra Reading.

## Output naming

The default output type is DOCX notes. If the user requests filenames or a multi-file output set, follow that request. Otherwise generate clear, distinct DOCX filenames for each output from the source, course, prompt, or note title.

## What it does

1. Reads supplied course files, practice material, mark schemes, examples, Extra Reading, and other useful files.
2. Uses rough source hints as provenance labels.
3. Builds a fragment index from readable content.
4. Extracts open knowledge signals and groups connected signals into knowledge units.
5. Calibrates Notes coverage from the knowledge units and required explanation.
6. Identifies Extra Reading for essay-style enrichment when the user supplies it or the confirmed output calls for it.
7. Matches confirmed Extra Reading to essay claims or course points that need external enrichment.
8. Makes a preliminary diagnosis of Exam type/route, Material type/source roles, and proposed output set from the prompt and practice material.
9. Displays an **Auto-diagnosis review plan** and uses `request_user_input` for human review of Exam type, Material type, and output set confirmation.
10. Updates the route, source-role handling, and final output plan from the user's confirmed or corrected answers.
11. Produces explanation-only teaching Notes and separate Exam Type Related add-ons for MCQ, short answer, long answer, practical/data/problem, or essay exams.
12. When Past Paper or question-containing Practical Materials are supplied and confirmed, produces a separate question-based Exam Type Related DOCX alongside Notes.
13. When Past Paper or Practical Materials contain calculation, derivation, estimate, proof, data, or problem questions and are confirmed, produces a separate detailed worked-solutions DOCX.

Student-facing Notes explain the lecture and exam-relevant knowledge the student needs to master. Source intake, extraction notes, coverage calibration, QA state, route planning, subagent narration, and similar workflow records remain internal.

## Extra Reading

Extra Reading is mainly for Essay Question and Example Essay enrichment. It can include academically useful sources such as textbook-like background, chapters, journal articles, primary research, DOI/PMID sources, lecture-mentioned references, mechanism evidence, counterargument material, and evaluation sources that help earn Extra Reading credit in essay-style outputs.

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

Before public output is generated, automatic routing remains a preliminary diagnosis. `scripts/plan_workflow.py` marks `human_review_required: true`, stores automatic files under `proposed_outputs`, and inserts `human_review_exam_material_output_confirmation` before writing. `scripts/build_review_questions.py` builds the `request_user_input` payload for Exam type/route, Material type/source roles, and output set confirmation.

### 1. Coverage calibration

`references/input_and_evidence_protocol.md` defines open knowledge signals. `references/exam_prep_notes_protocol.md` defines how those signals become a coverage map before Notes are written. Coverage planning is internal; the final document is a knowledge-explanation document. Formulas, visuals, worked examples, and confirmed add-on content function as parts of knowledge explanation; exam advice, workflow display, Skill explanation, and high-frequency-analysis process stay in the internal workflow record.

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
- separate Exam Type Related add-ons for MCQ, short answer, long answer, practical/data/problem, and essay preparation.

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

### 4. Separate question-based add-on

`references/exam_mode_and_addons_protocol.md` defines Past Paper and Practical question outputs. MCQ and Short Answer questions are arranged by lecture/source order and include question-derived high-frequency knowledge points for the add-on. Long Answer and Practical/Data/Problem outputs contain source questions, example answers, and academic Analysis/Prediction results that develop exam-answering ability.

Complete worked-solution notes are generated as a separate DOCX when Past Paper or Practical Materials contain calculation, derivation, estimate, proof, data, or problem questions. Available solutions or mark schemes are used as evidence for formula choice, algebra path, units, assumptions, final result, and interpretation.

## Routes

- `exam_prep_notes`
- `exam_mode_diagnosis`
- `mcq_preparation`
- `short_answer_preparation`
- `long_answer_preparation`
- `worked_solution_preparation`
- `essay_preparation`

## Step 8: publish and update

```bash
python3 scripts/validate_skill_contracts.py
python3 scripts/github_ready_check.py
python3 scripts/publish_skill.py --push
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --push --sync-local-skill
```

`--push` runs `git push` from the repository root. `--sync-local-skill` copies the repository into `~/.codex/skills/everything-exam-preparation` so the local Skill installation updates from the current repository files.
