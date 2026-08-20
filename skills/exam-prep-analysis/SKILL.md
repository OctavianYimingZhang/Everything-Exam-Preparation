---
name: exam-prep-analysis
description: Build source-auditable Units Analysis and exam-intelligence packages from formal past papers, auxiliary question material, course material, and mark schemes without turning recurrence into weighting or prediction.
---

# Exam Prep Analysis

Produce Units Analysis and past-paper intelligence as a standalone exam-preparation artifact.

## Read First

- `references/input_and_evidence_protocol.md`
- `references/exam_intelligence_protocol.md`

Shared resources are two directories above this file in the source checkout.

## Workflow

1. Accept the user's raw PPTX, PDF, DOCX, image, archive, paper, mark-scheme, or notes files directly. Call `scripts/extract_sources.py --mode diagnostic --purpose analysis`; do not require another focused Skill or a prebuilt index.
2. Assign every source exactly one `source_role`: `formal_past_paper`, `official_mock_specimen`, `practice_worksheet`, `lecture_material`, or `mark_scheme`. Preserve an explicit user label; request review when classification remains ambiguous.
3. Extract examinable prompts with their source locators. Keep mark-scheme text linked as evidence rather than counting it as another question occurrence.
4. Map questions to lecture, unit, or concept only from explicit course evidence. Record an unsupported or ambiguous match as `unresolved`; do not choose the nearest-looking topic.
5. Form question families from explicit labels, confirmed mappings, or transparent similarity evidence. Put heuristic and singleton families in the audit review queue.
6. Run `scripts/exam_intelligence_tools.py build` to calculate the protocol metrics. Formal recurrence must use only `formal_past_paper` records.
7. Export a student-facing `public` analysis separately from the traceable `audit` data, then run `scripts/exam_intelligence_tools.py validate` against the package.

## Evidence Boundaries

- Official mocks and specimen papers remain auxiliary evidence; their official status does not make them a formal sitting.
- Practice worksheets can illustrate format or coverage but never add a formal year.
- Lecture material supports mapping and interpretation, not recurrence.
- Mark schemes can support explicit marks and answer expectations only when linked unambiguously; they are not independent question occurrences.
- Source occurrence does not establish official assessment weighting.
- Recurrence, retention, and stability are historical descriptions, not certain predictions of a future question.
- Do not publish an unexplained composite score.

## Output

Return an `exam_intelligence` JSON package conforming to `schemas/exam_intelligence_package.schema.json`. The `public` section contains family-level metrics, their definitions, limitations, and completion state. The `audit` section contains source records, question records, family membership, metric evidence, unresolved mappings, exclusions, and warnings.

Use the public result envelope from `references/input_and_evidence_protocol.md` when presenting the generated artifact. Name the real file format and QA state; do not label a plan or chat payload as a generated file.
