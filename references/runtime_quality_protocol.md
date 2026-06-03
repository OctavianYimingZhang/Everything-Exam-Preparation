# Runtime quality protocol

Keep runtime checks tied to behaviour that affects student-facing outputs or release safety.

## Local validation

Run consolidated self-tests for contracts, routing, intake, mode detection, notes generation, notes quality, sufficiency, essay tools, deliverable surface, run control, and release readiness.

## Run control

Each run should be representable as a control manifest with:

- stable source document and source fragment object IDs;
- workflow action records for planned or executed route steps;
- output artifact objects for generated student-facing files or reports;
- lineage links connecting source documents, fragments, workflow actions, and artifacts;
- validation errors for missing objects, invalid links, duplicate object IDs, or unsupported link shapes;
- reuse decisions based on object fingerprints from a previous manifest.

The control manifest is an internal artifact. Student-facing DOCX or chat output must not expose object IDs, lineage links, reuse decisions, validation internals, source maps, or gate records.

Use `scripts/run_control_plane.py` to build or lint the manifest from existing `source_scan`, fragment index, and workflow plan JSON. If the manifest status is `fail`, block release until the invalid links or duplicate objects are corrected.

## Clutter guards

The repository must not contain generated outputs, private course packs, remembered example mechanisms, obsolete route names, deleted script references, or stale architecture terminology.

## Release checks

Release checks must confirm canonical file counts, existing manifest commands, valid JSON schemas, no stale references, no local generated deliverables, run control self-test success, and passing health commands.
