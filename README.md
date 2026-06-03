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
5. Produces exam preparation notes and mode-specific preparation for MCQ, short answer, long answer, or essay exams.

## Routes

- `exam_prep_notes`
- `exam_mode_diagnosis`
- `mcq_preparation`
- `short_answer_preparation`
- `long_answer_preparation`
- `essay_preparation`

## Step 8: publish and update

The repository keeps one simple publish/update layer:

```bash
python3 scripts/validate_skill_contracts.py
python3 scripts/github_ready_check.py
python3 scripts/publish_skill.py --push
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --push --sync-local-skill
```

`--push` runs `git push` from the repository root. `--sync-local-skill` copies the repository into `~/.codex/skills/everything-exam-preparation` so the local Skill installation updates from the current repository files. The manifest also declares this local sync command in `post_update_commands` for automatic Skill update after repository updates.
