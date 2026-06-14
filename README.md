# Everything Exam Preparation

Signal-driven exam preparation Skill for uploaded course content, practice material, and Extra Reading.

## Output naming

The default output type is DOCX notes. If the user requests filenames or a multi-file output set, follow that request. Otherwise generate clear DOCX filenames from the source, course, prompt, or note title.

## What it does

1. Reads supplied course files, practice material, mark schemes, examples, Extra Reading, and other useful files.
2. Uses rough source hints as provenance labels.
3. Builds a fragment index from readable content.
4. Extracts open knowledge signals and groups connected signals into knowledge units.
5. Calibrates Notes coverage from the knowledge units and required explanation.
6. Discovers Extra Reading from uploaded files, source mentions, and academic-paper search queries.
7. Matches Extra Reading to course knowledge units.
8. Diagnoses the exam mode from the prompt and practice material.
9. Produces explanation-only teaching Notes and separate Exam Type Related add-ons for MCQ, short answer, long answer, practical/data/problem, or essay exams.
10. When Past Paper or question-containing Practical Materials are supplied, produces a separate question-based Exam Type Related DOCX alongside Notes.

Student-facing Notes explain knowledge. They do not expose source intake, extraction notes, coverage calibration, QA state, route planning, subagent narration, or other workflow internals.

## Extra Reading

Extra Reading can include any academically useful source that strengthens a knowledge unit, including textbook-like background, chapters, journal articles, primary research, DOI/PMID sources, lecture-mentioned references, method detail, mechanism evidence, and research context.

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

This version focuses on signal-driven coverage, teaching depth, domain-neutral formula visibility, academic source visuals, output language style, and output format style.

### 1. Coverage calibration

`references/input_and_evidence_protocol.md` defines open knowledge signals. `references/exam_prep_notes_protocol.md` defines how those signals become a coverage map before Notes are written. Coverage planning is internal; the final document contains only knowledge explanations.

Coverage is driven by:

- knowledge units;
- concepts and definitions;
- mechanisms and causal chains;
- methods, assays, controls, and readouts;
- comparisons;
- calculations and data interpretation;
- evidence and Extra Reading;
- conceptual applications and interpretation use.
- source visuals when they clarify a concept, mechanism, method, formula, graph, table, pathway, scheme, or data interpretation.

Examples are used when they clarify knowledge, mechanism, method, calculation, interpretation, or conceptual application.

### 2. Teaching depth and formula visibility

`references/exam_prep_notes_protocol.md` defines how the notes should teach:

- strong tutor voice;
- direct course explanation;
- concept identity, mechanism, method, calculation, assumptions, interpretation, and conceptual application;
- visible formulas using Word equation/OMML where possible;
- readable Unicode mathematical fallback when equation conversion is unavailable;
- domain-neutral formula normalization for mathematics, physics, chemistry, biological science, and coding-adjacent technical material;
- academically useful PDF page-visible visuals and embedded DOCX/PPTX media when they strengthen a knowledge unit;
- Extra Reading depth after relevant lecture explanation;
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
- clear knowledge sections that teach the material without workflow or process sections.

### 4. Separate question-based add-on

`references/exam_mode_and_addons_protocol.md` defines Past Paper and Practical question outputs. MCQ and Short Answer questions are arranged by lecture/source order and include high-frequency knowledge points derived from the question material. Long Answer and Practical/Data/Problem outputs contain source questions, example answers, and academic Analysis/Prediction results without workflow narration or study-advice content.

## Routes

- `exam_prep_notes`
- `exam_mode_diagnosis`
- `mcq_preparation`
- `short_answer_preparation`
- `long_answer_preparation`
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
