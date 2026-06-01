# GitHub Release Protocol

Before publishing a release:

1. Confirm `SKILL.md` is the canonical entrypoint.
2. Confirm generated bundles, local outputs, caches, and private materials are absent.
3. Run script compilation.
4. Run public safety scans.
5. Run interaction, planning, language, source-scale, reference-density and deliverable checks.
6. Confirm README commands match existing files.
7. If a compacted Custom GPT or upload-file copy is maintained locally, regenerate or patch it from the canonical source after the repository checks pass. Keep that compacted copy outside `main` unless a separate generated-artifact branch is explicitly intended.

Do not publish:

- generated combined knowledge exports
- local runtime stores
- private course material
- user work
- local filesystem paths
- institution-specific private data

The GitHub repository source is canonical. Local compacted versions are adapters for constrained upload environments; they must preserve the same route table, source-scale floor, knowledge-surface boundary, evidence policy and revision contract as `SKILL.md`, but generated combined exports remain local-only by default.
