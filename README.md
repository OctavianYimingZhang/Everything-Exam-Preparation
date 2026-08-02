# Everything Exam Preparation

Everything Exam Preparation is a Codex Plugin that turns trusted course and assessment material into the student artifact requested.

## Structure

The manifest currently exposes these Skill entries:

| Skill | Responsibility |
| --- | --- |
| `everything-exam-preparation` | Routes explicit requests. |
| `exam-prep-notes` | Creates course Notes and performs internal slide triage. |
| `exam-prep-practice` | Handles all question-based preparation, blueprints, evaluation, and timed practice. |
| `exam-prep-essay` | Handles ordinary and Online Essay support plus Extra Reading. |

The router selects the artifact from the user's request. It asks a concise question only when an indispensable input or a materially different output choice is unresolved.

The focused Skill list is manifest-driven. Split a Skill when its learning intent, evidence role, workflow, toolchain, or output is materially independent; merge it when those boundaries are shared.

## Core Workflow

```text
user request + trusted sources
    -> select Notes, Practice, or Essay
    -> process sources and preserve locators
    -> diagnose task readiness and evidenced assessment architecture
    -> generate the requested artifact
    -> validate content and rendered output
```

Four references define the shared behaviour:

- `references/input_and_evidence_protocol.md`
- `references/exam_prep_notes_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/essay_exam_prep_protocol.md`

## Tools

| Script | Responsibility |
| --- | --- |
| `scripts/extract_sources.py` | Extraction, fragment indexing, focused-Skill diagnostics, exam-format profiling, assessment architecture, slide triage, and coverage audit. |
| `scripts/generate_exam_prep_notes_docx.py` | Academic DOCX rendering. |
| `scripts/exam_mode_tools.py` | Practice analysis and generation. |
| `scripts/essay_exam_tools.py` | Essay and Extra Reading analysis. |
| `scripts/validate_skill_contracts.py` | Unified repository validation. |
| `scripts/publish_skill.py` | Manifest-driven local synchronisation and drift checking. |

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

The unified validator checks the manifest-declared Skills, references, metadata consistency, retained tool self-tests, retired structure, and installation declarations.

## Repository Map

| Path | Responsibility |
| --- | --- |
| `SKILL.md` | Package router and shared rules. |
| `skills/` | Manifest-declared Plugin Skill entries. |
| `references/` | Source, Notes, Practice, and Essay protocols. |
| `scripts/` | Core processing, rendering, validation, and synchronisation. |
| `agents/` | Optional presets, prompt cards, and setup metadata. |
| `.codex-plugin/plugin.json` | Plugin metadata. |
| `skill_manifest.json` | Version, public Skill list, tools, and local cleanup list. |

Generated course material remains outside the published Plugin package.
