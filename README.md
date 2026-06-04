# Everything Exam Preparation

Simple exam preparation Skill for uploaded course content, practice material, and Extra Reading.

## Default output

```text
Exam_Preparation_Notes.docx
```

## What it does

1. Reads notes, lecture slides, practical material, past papers, practice questions, mark schemes, answer keys, example answers, Books, Academic Papers, and other useful course files.
2. Uses rough source hints to understand what the files contain.
3. Builds a fragment index from readable content.
4. Discovers Extra Reading from uploaded files, lecture-slide mentions, and academic-paper search queries.
5. Matches Extra Reading to lecture topics.
6. Diagnoses the exam mode from the prompt and practice material.
7. Produces exam preparation notes and mode-specific preparation for MCQ, short answer, long answer, practical/data/problem, or essay exams.

## Extra Reading

Extra Reading Material has two main forms:

- Books: textbooks and book chapters used to add background, molecular explanation, mechanism explanation, pathway context, and conceptual background.
- Academic Papers: journal articles, primary research, recent research, DOI/PMID papers, and lecture-mentioned references used to add molecular mechanisms, experimental evidence, method detail, research context, and support for conclusions.

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
  "book_mentions": [],
  "paper_mentions": [],
  "lecture_topics": [],
  "search_queries": [],
  "topic_enrichment": [],
  "essay_enrichment": {
    "extra_reading_blend": "15-30%",
    "paragraph_slots": []
  }
}
```

## Current style focus

This version focuses on output language style and output format style.

### 1. Output language style

`references/language_quality_contract.md` defines how the notes should sound:

- strong tutor voice;
- direct course explanation;
- exam application after each important concept;
- Extra Reading depth after relevant lecture explanation;
- MCQ reasoning with plausible wrong statements;
- short-answer definitions, mark points, explain sentences, and example answers;
- long-answer walkthroughs;
- practical/data interpretation;
- exam-ready essay paragraphs with 15%-30% Extra Reading content when generating Example Essays.

### 2. Output format style

`references/exam_prep_notes_protocol.md` defines how the notes should be structured:

- `Exam_Preparation_Notes.docx`;
- Arial;
- 2.5 cm margins;
- 1.5 line spacing;
- centered main title;
- left-aligned headings;
- justified body text;
- compact tables;
- clear sections for course overview, exam pattern, high-yield topics, topic notes, Extra Reading Evidence, and mode-specific preparation.

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
