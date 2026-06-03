# Everything Exam Preparation

Simple exam preparation Skill for uploaded course content and practice material.

## Default output

```text
Exam_Preparation_Notes.docx
```

## What it does

1. Reads notes, lecture slides, practical material, past papers, practice questions, mark schemes, answer keys, example answers, and other useful course files.
2. Uses rough source hints to understand what the files contain.
3. Builds a fragment index from readable content.
4. Diagnoses the exam mode from the prompt and practice material.
5. Produces exam preparation notes and mode-specific preparation for MCQ, short answer, long answer, practical/data/problem, or essay exams.

## Current style focus

This version focuses on two output style layers.

### 1. Output language style

`references/language_quality_contract.md` defines how the notes should sound:

- strong tutor voice;
- direct course explanation;
- exam application after each important concept;
- MCQ reasoning with plausible wrong statements;
- short-answer definitions, mark points, explain sentences, and example answers;
- long-answer walkthroughs;
- practical/data interpretation;
- exam-ready essay paragraphs.

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
- clear sections for course overview, exam pattern, high-yield topics, topic notes, and mode-specific preparation.

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
