# Everything Exam Preparation

Function-first exam preparation Skill for supplied lecture material, practical material, past papers, and exam-mode add-ons.

## Default output

The default student-facing notes artifact is:

```text
Exam_Preparation_Notes.docx
```

## What the Skill does

1. Classifies supplied learning and practice sources.
2. Generates source-backed Exam Preparation Notes with paragraph, list, table, chain, and visual render modes.
3. Detects exam mode from past papers or the user prompt: MCQ, Short Answer, Long Answer, Practical/Data/Problem, or Essay.
4. Generates only the add-on content needed for the detected or requested mode.

Past papers shape emphasis, answer operations, and mode. They do not replace the course-source baseline. Internal run manifests support QA and reproducibility; they are not student-facing output and must not shape prose.

## Canonical files

References are limited to six protocol files in `references/`. Schemas are consolidated by function in `schemas/`. Scripts are consolidated into routing, extraction, generation, linting, and release checks in `scripts/`.

## Health commands

```bash
python3 -m compileall -q scripts
python3 scripts/validate_skill_contracts.py --self-test
python3 scripts/plan_workflow.py --self-test
python3 scripts/input_readiness_check.py --self-test
python3 scripts/extract_sources.py --self-test
python3 scripts/exam_mode_tools.py --self-test
python3 scripts/generate_exam_prep_notes_docx.py --self-test
python3 scripts/exam_prep_notes_quality_linter.py --self-test
python3 scripts/output_sufficiency_linter.py --self-test
python3 scripts/essay_exam_tools.py --self-test
python3 scripts/deliverable_surface_linter.py --self-test
python3 scripts/run_control_plane.py --self-test
python3 scripts/github_ready_check.py --ci
```

## Release rule

The repository should contain only canonical protocols, functional schemas, consolidated scripts, agents, CI, manifest, and top-level project files. Generated outputs and private course packs stay out of version control.
