# Everything Exam Preparation

A Codex Skill for source-bound exam preparation.

## What it does

- Builds revision notes, essay plans, model answers, question drills, source walkthroughs, and past-paper analysis.
- Uses user-provided course materials as the evidence base.
- Keeps unsupported claims visible as gaps instead of filling them in.
- Includes scripts for source extraction, planning, DOCX rendering, and public-release checks.

## Entrypoint

Use [`SKILL.md`](SKILL.md). Reference files are loaded only when a task needs them.

## Repository layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Agent-facing workflow. |
| `references/` | Route-specific protocols. |
| `agents/` | Presets, prompt cards, and setup metadata. |
| `schemas/` | JSON schemas for plans, outputs, and QA records. |
| `scripts/` | Local processing and lint utilities. |
| `benchmarks/` | Public regression suites. |
| `tests/fixtures/` | Small public fixtures for script checks. |

## Removed from the public skill package

Generated all-in-one knowledge bundles and local runtime stores are not part of the open-source Skill package. The repository keeps the source files instead of generated combined exports.

Local compacted copies, such as Custom GPT knowledge bundles or flattened upload folders, must be regenerated or patched from the canonical source after repository checks pass. They are adapters for constrained upload environments and should not be committed to `main` unless the release explicitly targets a generated-artifact branch.

## Local checks

```bash
python3 -m compileall -q scripts
python3 scripts/no_identity_trigger_linter.py --forbid-legacy-label
python3 scripts/validate_workflow_planning_contract.py
python3 scripts/validate_interaction_contract.py
python3 scripts/validate_student_output_contract.py
python3 scripts/public_lecture_notes_renderer.py --self-test
python3 scripts/source_information_profiler.py --self-test
python3 scripts/github_ready_check.py --ci
```

## License

See [`LICENSE`](LICENSE).
