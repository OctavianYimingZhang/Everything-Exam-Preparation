# GitHub Release Protocol

Use this protocol before committing and pushing Skill updates.

## Pre-Push Checklist

1. Run compile checks for all scripts.
2. Run the ontology contract linter.
3. Run action writer coverage validation.
4. Run interaction contract validation.
5. Run the fragment-index fixture.
6. Run the runtime ontology validator fixture, including a negative cross-target leakage case.
7. Run the run-manifest and lineage fixture.
8. Run student-facing prose fixture lint.
9. Run benchmark metadata/regression checks.
10. Generate the positive Example Essay DOCX fixture in strict mode.
11. Lint the generated DOCX formatting and source mapping.
12. Run the Example Essay language linter.
13. Run the no-identity-trigger linter.
14. Run the public safety scan for private absolute paths and institutional-private markers.
15. Confirm the installed Skill copy matches the repository copy.
16. Confirm `git status --short` contains only intentional changes.

## Identity Trigger Rule

Production files must not branch on course names, benchmark names, or private folder identities.

Allowed:

- generic course-code regex;
- target-group fields;
- benchmark fixture data under `benchmarks/`;
- tests under `tests/`.

Forbidden:

- course-name alias tables;
- hardcoded benchmark names in production routing;
- file names from private source folders as production triggers.

## Push Rule

Commit only after local GitHub-ready checks pass. Push only the repository changes, not generated temporary artefacts or private source material.

The GitHub repository source is canonical. Local compacted versions, including Custom GPT knowledge bundles and flattened upload-file copies, are adapters for constrained upload environments; they must preserve the same route table, source-scale floor, knowledge-surface boundary, evidence policy and revision contract as `SKILL.md`. Keep generated combined exports out of `main` unless a separate generated-artifact branch is explicitly intended.

## Maintenance Doctor And Safe Update

The repository exposes a controlled maintenance layer through `skill_manifest.json` and `scripts/skill_maintenance.py`.

Use it when the user asks to check, doctor, validate, update, repair, refresh, sync, or release the Skill package:

1. Run `python3 scripts/skill_maintenance.py doctor` first. This is read-only.
2. For update requests, run `python3 scripts/skill_maintenance.py update --dry-run` and summarize incoming commits and changed files before modifying anything.
3. Run `python3 scripts/skill_maintenance.py update --yes` only after explicit user approval.
4. Refuse to update a dirty git working tree.
5. After any real update, run the manifest health commands.
6. If health checks fail, treat the update as failed and do not rely on the updated state.

Installed copies should be git checkouts. If an installed copy is a plain file copy, preserve it as a backup before replacing it with a fresh clone from the public repository.

## Runtime Control-Plane Rule

When a run generates public artifacts through helper scripts, the internal QA folder should be able to provide:

- `ontology_objects/*.jsonl` or equivalent object JSON;
- `ontology_links/links.jsonl`;
- `run_manifest.json`;
- `lineage_events.jsonl`.

These are helper artifacts. They should be linted before publish, but they must not be mixed into the default student-facing output folder unless the user explicitly asks for an audit package.
