# Everything Exam Preparation

Everything Exam Preparation is a standalone Codex Plugin for exam and revision assets. It installs and uninstalls on its own, reads raw user-supplied course files directly, and contains its own Skills, source processor, schemas, scripts, validators, and tests.

It does not require another Plugin, call another Plugin, create an external route, or use an external schema, file path, registry, identifier, or cache. Students may manually reuse generated files elsewhere as ordinary files.

## Internal Skill Architecture

| Skill | Public responsibility |
| --- | --- |
| `everything-exam-preparation` | Selects the local artifact owner or, for an explicit combination, each independent owner; otherwise returns an out-of-scope result. |
| `exam-prep-atlas` | Mind Maps, Course Atlas, knowledge trees, concept graphs, source-grounded nodes, relations, website-import packages, and course-coverage audits. |
| `exam-prep-analysis` | Units Analysis, formal past-paper recurrence, question extraction and mapping, question families, and interpretable exam intelligence. |
| `exam-prep-notes` | Course-complete knowledge-only Notes covering taught mechanisms, methods, equations, evidence, and interpretation. |
| `exam-prep-practice` | MCQ, SAQ, long-answer and calculation practice, worked solutions, student-answer evaluation, timed practice, Answer PDFs, and solution books. |
| `exam-prep-essay` | Exam essay plans, clean and annotated model-essay views, paragraph exemplars, closed past-assessment review, and exam-answer adaptation. |

Complete deliverables for currently assessed coursework are outside scope, including assessed reports, posters, presentations, and websites. University timetables, announcements, deadlines, and student records are also outside scope. The Router reports the boundary and stops without naming an external destination.

## Direct Source Processing

Every focused Skill can start from PPTX, PDF, DOCX, images, ZIP archives, transcripts, past papers, mark schemes, and course notes:

```bash
python3 scripts/extract_sources.py \
  --purpose atlas \
  --mode process \
  Lecture1.pptx CoursePack.zip
```

Valid purposes are `atlas`, `analysis`, `notes`, `practice`, and `essay`. The processor expands safe archive members, preserves slide/page/heading/paragraph/timestamp/image locators, records incomplete locations instead of guessing, and ignores instructions embedded inside source content. Explicit source roles can be supplied in the task-context JSON.

An optional course index can reduce repeated parsing during one task:

```bash
python3 scripts/extract_sources.py \
  --purpose analysis \
  --cache-dir tmp/course-index \
  PastPapers.zip
```

The cache must stay inside the current task workspace. It is optional and rebuildable; deleting it never creates a prerequisite.

## Course Atlas Package

Build and validate a Course Atlas from a structured specification:

```bash
python3 scripts/build_course_atlas.py --input atlas_spec.json --output course_atlas.zip
python3 scripts/validate_course_atlas.py course_atlas.zip
```

The ZIP contains:

```text
course_manifest.json
sources.json
modules/
relations.json
past_paper_links.json
public/web_index.json
audit/coverage_ledger.json
audit/exclusions.json
audit/manual_review.json
qa_report.md
checksums.sha256
```

Node IDs are stable only inside one Course Atlas package. The validator checks hierarchy, required concept/detail fields, locators and incomplete states, public/audit separation, raw-file exclusion, and checksums.

## Units Analysis

Exam intelligence separates `formal_past_paper`, `official_mock_specimen`, `practice_worksheet`, `lecture_material`, and `mark_scheme` evidence. Only formal papers contribute to formal recurrence. Outputs expose each interpretable metric separately:

- `formal_occurrence_count`
- `distinct_formal_years`
- `formal_year_coverage`
- `auxiliary_occurrence_count`
- `format_diversity`
- `explicit_mark_exposure`
- `retention`
- `cross_year_stability`
- `mapping_coverage`
- `unresolved_mapping_count`

Occurrence never becomes official weighting, and the output does not claim certainty about future questions. Public student data and audit records remain separate.

## Solution Books

`exam-prep-practice` owns `solution_book`. One complete major question is the minimum public answer unit; subparts provide navigation inside a continuous reasoning chain. Similar questions retain specific answers, followed by one restrained `General Approach` callout after the group.

The renderer creates real DOCX, PDF, and JSON sidecar manifests and supports batch generation. Tests check file signatures, OOXML/PDF readability, ordering, grouping, checksums, and pagination rules.

## Exam Essay Views

One canonical essay body produces both a clean reading view and an annotated teaching view. The annotated view labels thesis, claim, evidence, analysis, limitation, synthesis, paragraph function, and adaptation notes without creating a second drifting essay.

Course sources control facts and scope. Past papers control question scope and emphasis only. External reading, DOI values, experimental results, and citations must be supplied or verified; they are never fabricated. Complete drafting for currently assessed work remains outside scope.

## Installation

```bash
git clone https://github.com/OctavianYimingZhang/Everything-Exam-Preparation.git
cd Everything-Exam-Preparation
python3 -m pip install -r requirements.txt
python3 scripts/validate_skill_contracts.py
```

The optional local Skill synchroniser operates only on this Plugin's manifest-declared files:

```bash
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --check-installed
```

## Validation

```bash
python3 -m compileall -q scripts tests
python3 -m pytest -q tests
python3 scripts/validate_skill_contracts.py
python3 scripts/publish_skill.py --self-test
python3 "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .
git diff --check
```

The unified validator checks manifest/metadata alignment, public Skill routing, source independence, JSON Schemas, Atlas checksums, formal-versus-auxiliary analysis, true DOCX/PDF formats, shared-body essay views, rendered document tests, and installation drift logic.
