# Source and Evidence Processing

## Intake

Use the task, files, and source roles the user supplies. When a required file is missing, request that file directly. When the user has already named the requested artifact, begin that workflow. For Notes creation, improvement, continuation, rebuild, and bulk course-file work, select Notes alone unless the user explicitly requests a separate Practice or Essay artifact.

Common source roles are:

- coverage authority: lecture slides or other user-designated instructional sources whose substantive knowledge must be covered completely;
- course knowledge: lectures, textbooks, practical teaching, recordings, and revision content that may expand or corroborate the coverage authority;
- reference notes: text summaries used to identify emphasis, helpful phrasing, and organisation without replacing or narrowing the coverage authority;
- practice: past papers, mock papers, question banks, and recap questions;
- evaluation: mark schemes, rubrics, expected concepts, and model answers;
- essay evidence: uploaded readings, reliable external academic sources, and permitted online material.

Explicit user labels control source role. Content-based classification supplies a useful default for unlabeled material. Source type never grants permission to create a different artifact: question, rubric, or essay-assessment sources may inform Notes internally without triggering Practice or Essay output.

For Notes, build the coverage ledger from the coverage authority. When the user says lecture slides are primary and text notes are reference material, require every substantive slide knowledge point to be represented even if the reference notes omit it. Use reference notes to adjust emphasis or expression; do not promote reference-only additions to required course content without corroboration or an explicit user instruction.

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

## Shared Diagnostic Contracts

Every focused Skill can call `scripts/extract_sources.py --mode diagnostic --purpose <notes|practice|essay>` without going through the Router. The lightweight result contains:

- `ExamFormatProfile`: only question formats, durations, and mark values evidenced by assessment fragments;
- `AssessmentArchitecture`: evidenced assessment components and explicit source percentages, without inferred weighting;
- `DiagnosticAssessment`: capability readiness for the selected focused Skill.

Each contract exposes `task_mode`, `status`, `gaps`, and `degraded`. `DiagnosticAssessment` also exposes `can_proceed`. Treat `blocked` gaps as indispensable missing inputs, `partial` as a usable but incomplete evidence state, and `ready` as sufficient for the requested capability. A degraded assessment profile does not block Notes when course-knowledge evidence is sufficient. Never convert source occurrence into assessment weight or an absent instruction into permission.

## Public Skill Result Envelope

Wrap the requested public result in schema `1.0` with `skill_id`, `task_mode`, one public `status`, `assumptions`, `gaps`, `evidence_summary`, `primary_output`, and `qa`. Use one status: `completed`, `completed_with_gaps`, `needs_material_input`, `source_conflict`, `artifact_generated`, or `analysis_only`. Diagnostic `ready`, `partial`, and `blocked` are internal readiness states and do not replace the public status.

When a real file is created, include an artifact manifest with `artifact_id`, `artifact_type`, the actual `file_format`, `content_schema_version`, `source_corpus_ids`, and `qa_status`. Do not claim `docx`, `pdf`, or `artifact_generated` when only a plan, payload, or chat response exists. Name any fallback and the source or assessment gap that caused it.

## Evidence Use

Connect each substantive claim to the supplied course material or a reliable permitted source. Preserve the distinction between coverage authority and reference material while drafting. For Notes, use past papers only to understand relative emphasis and keep assessment planning out of the public artifact. For explicitly requested Practice, use mark schemes and rubrics as evaluation criteria. For explicitly requested Essay work, use reliable academic sources for enrichment.

Represent uncertainty plainly when a source is incomplete, ambiguous, or unreadable. Preserve locators wherever they support checking or later revision.

## Coverage Audit

For Notes, record every instructional source and count its substantive fragments, merged fragments, excluded fragments, and selected visuals. For Practice and Essay, record the evidence set used for each requested capability. Keep the audit as an internal quality-control artifact by default and provide it when requested.
