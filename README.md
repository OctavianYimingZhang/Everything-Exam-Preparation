# Everything Exam Preparation

A function-first Codex Skill for source-bound exam preparation.

## What it does

- Analyses lecture slides/notes, official course notes, practical material, past papers, answer keys, exemplars, feedback, and verified readings.
- Generates `Lecture_Knowledge_Walkthrough.docx` as the default Exam Preparation Notes artifact.
- Detects exam mode from past papers or user prompts: MCQ, Short Answer, Long Answer, Practical/Data/Problem, or Essay.
- Generates only the question-type add-ons required by the detected/requested exam mode.

## Entrypoint

Use `SKILL.md`. The Skill has a small canonical protocol set in `references/`; duplicate legacy protocol files, committed fixtures, and benchmark/example memory are intentionally removed.

## Repository layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Agent-facing entrypoint and route table. |
| `references/` | Canonical functional protocols only. |
| `agents/` | Presets, prompt cards, setup metadata. |
| `schemas/` | JSON schemas for production plans, sources, outputs, and QA records. |
| `scripts/` | Source processing, planning, DOCX rendering, lint, self-tests, and release checks. |

## Local checks

```bash
python3 -m compileall -q scripts
python3 scripts/no_identity_trigger_linter.py --forbid-legacy-label
python3 scripts/validate_workflow_planning_contract.py
python3 scripts/validate_interaction_contract.py
python3 scripts/validate_student_output_contract.py
python3 scripts/plan_workflow.py --self-test
python3 scripts/input_readiness_check.py --self-test
python3 scripts/extract_sources.py --self-test
python3 scripts/extract_past_paper_questions.py --self-test
python3 scripts/generate_public_lecture_notes_docx.py --self-test
python3 scripts/public_lecture_notes_renderer.py --self-test
python3 scripts/deliverable_surface_linter.py --self-test
python3 scripts/generate_example_essay_docx.py --self-test
python3 scripts/citation_fallback_linter.py --self-test
python3 scripts/example_essay_language_linter.py --self-test
python3 scripts/past_paper_prediction_linter.py --self-test
python3 scripts/output_sufficiency_linter.py --self-test
python3 scripts/runtime_audit.py --self-test
python3 scripts/github_ready_check.py --ci
```

## License

See `LICENSE`.
