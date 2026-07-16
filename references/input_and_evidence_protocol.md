# Source and Evidence Processing

## Intake

Use the task, files, and source roles the user supplies. When a required file is missing, request that file directly. When the user has already named the requested artifact, begin that workflow.

Common source roles are:

- course knowledge: lectures, teaching notes, textbooks, practical teaching, recordings, and revision content;
- practice: past papers, mock papers, question banks, and recap questions;
- evaluation: mark schemes, rubrics, expected concepts, and model answers;
- essay evidence: uploaded readings, reliable external academic sources, and permitted online material.

Explicit user labels control source role. Content-based classification supplies a useful default for unlabeled material.

## Unified Source Flow

Use `scripts/extract_sources.py` to:

1. inventory readable files;
2. extract text and embedded or page-region visuals;
3. preserve filename, page, slide, timestamp, and time-range locators;
4. classify fragments by teaching role and knowledge signal;
5. triage slide-like content;
6. build a reusable fragment index;
7. report readiness and a source-level coverage audit.

Keep extraction observations in the internal record. Surface a source problem when it prevents reliable completion.

## Evidence Use

Connect each substantive claim to the supplied course material or a reliable permitted source. Use past papers to understand assessment demand and relative emphasis. Use mark schemes and rubrics as evaluation criteria. Use reliable academic sources for essay enrichment.

Represent uncertainty plainly when a source is incomplete, ambiguous, or unreadable. Preserve locators wherever they support checking or later revision.

## Coverage Audit

For Notes, record every instructional source and count its substantive fragments, merged fragments, excluded fragments, and selected visuals. For Practice and Essay, record the evidence set used for each requested capability. Keep the audit as an internal quality-control artifact by default and provide it when requested.
