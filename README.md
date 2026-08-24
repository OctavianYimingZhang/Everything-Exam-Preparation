# Everything Exam Preparation

Everything Exam Preparation is a Codex Plugin that turns trusted course and assessment material into the requested student artifact through a single-pass workflow.

## Structure

| Skill | Responsibility |
| --- | --- |
| `everything-exam-preparation` | Routes explicit requests. |
| `exam-prep-notes` | Creates course-complete, knowledge-only Notes. |
| `exam-prep-practice` | Handles question-based preparation, blueprints, evaluation, and timed practice. |
| `exam-prep-essay` | Handles ordinary and permitted Online Essay support plus Extra Reading. |

The router acts directly when the requested artifact and required inputs are clear.

## Core Workflow

```text
request + trusted sources
    -> select Notes, Practice, or Essay
    -> extract once and reuse the source index
    -> plan structure
    -> generate once
    -> bounded sanity check
    -> deliver
```

Normal student tasks do not trigger page-image rendering, exhaustive coverage ledgers, repeated diagnostics, or correction-and-rerender loops. Targeted visual inspection is used only when explicitly requested or when a concrete extraction or layout failure identifies a specific page or element.

Four references define the shared behaviour:

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/essay_exam_prep_protocol.md`

## Tools

| Script | Responsibility |
| --- | --- |
| `scripts/extract_sources.py` | One-pass extraction, fragment indexing, and focused diagnostics. |
| `scripts/generate_exam_prep_notes_docx.py` | Deterministic academic DOCX generation. |
| `scripts/exam_mode_tools.py` | Practice analysis and generation. |
| `scripts/essay_exam_tools.py` | Essay and Extra Reading analysis. |
| `scripts/validate_skill_contracts.py` | Repository-maintenance validation. |
| `scripts/publish_skill.py` | Local installation synchronisation and drift checking. |

Validation and render self-tests are maintenance commands. They are not part of ordinary Notes, Practice, or Essay generation.

## Installation

```bash
git clone https://github.com/OctavianYimingZhang/Everything-Exam-Preparation.git
cd Everything-Exam-Preparation
python3 -m pip install -r requirements.txt
python3 scripts/validate_skill_contracts.py
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --check-installed
```

## Validation

```bash
python3 -m compileall -q scripts
python3 scripts/validate_skill_contracts.py
python3 scripts/publish_skill.py --self-test
for skill in skills/*; do
  test -f "$skill/SKILL.md" && python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"
done
python3 "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

## Repository Map

| Path | Responsibility |
| --- | --- |
| `SKILL.md` | Package router and one-pass shared rules. |
| `skills/` | Manifest-declared Plugin Skill entries. |
| `references/` | Source, Notes, Practice, and Essay protocols. |
| `scripts/` | Processing, generation, validation, and synchronisation. |
| `agents/` | Optional presets and setup metadata. |
| `.codex-plugin/plugin.json` | Plugin metadata. |
| `skill_manifest.json` | Version, public Skill list, tools, and local cleanup list. |

Generated course material remains outside the published Plugin package.
