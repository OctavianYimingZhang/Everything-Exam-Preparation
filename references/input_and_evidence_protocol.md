# Source and Evidence Processing

## Intake

Use the task, files, and source roles supplied by the user. When an indispensable file is missing, request it directly. When the requested artifact is already clear, begin that workflow.

Common source roles are:

- coverage authority: lecture slides or other designated instructional sources whose substantive knowledge defines Notes scope;
- course knowledge: lectures, textbooks, practical teaching, recordings, and revision content;
- reference notes: summaries used for emphasis, phrasing, and organisation;
- practice: past papers, mock papers, question banks, and recap questions;
- evaluation: mark schemes, rubrics, expected concepts, and model answers;
- essay evidence: uploaded readings and permitted reliable academic sources.

Explicit user labels control source role. Source type never grants permission to create a different artifact. Questions, rubrics, or essay materials may inform another artifact internally without triggering it.

For Notes, draft from the complete extracted coverage-authority index. Reference notes may improve emphasis or expression but must not narrow the course scope.

## One-Pass Source Flow

Use `scripts/extract_sources.py` once per source set when programmatic extraction is needed:

1. inventory readable files;
2. extract text and available visual metadata;
3. preserve filename, page, slide, timestamp, and time-range locators;
4. classify fragments by teaching role and knowledge signal;
5. triage slide-like content;
6. build one reusable fragment index;
7. return the focused diagnostic requested by the active Skill.

Reuse this output throughout the task. Do not rerun extraction, rebuild indexes, or rescore readiness solely to obtain a cleaner internal status.

Keep a compact internal source summary: files read, files unreadable, material gaps, and any specific fragment that required manual inspection. Do not create a fragment-by-fragment coverage audit by default. Produce a detailed audit only when the user explicitly requests one.

Inspect a rendered source page only when its extracted text is missing or garbled, or when an essential teaching visual cannot otherwise be interpreted. Inspect the relevant page only.

## Shared Diagnostic Contracts

A focused Skill may call `scripts/extract_sources.py --mode diagnostic --purpose <notes|practice|essay>` directly. The result may contain:

- `ExamFormatProfile`: question formats, durations, and marks evidenced by assessment fragments;
- `AssessmentArchitecture`: evidenced assessment components and explicit source percentages;
- `DiagnosticAssessment`: readiness for the selected focused Skill.

Each contract exposes `task_mode`, `status`, `gaps`, and `degraded`; `DiagnosticAssessment` also exposes `can_proceed`. Treat `blocked` as an indispensable missing input, `partial` as usable evidence with a material limitation, and `ready` as sufficient. A degraded assessment profile does not block Notes when course knowledge is sufficient. Never infer absent formats, weights, permissions, or marks.

## Public Skill Result Envelope

Wrap the public result in schema `1.0` with `skill_id`, `task_mode`, one public `status`, `assumptions`, `gaps`, `evidence_summary`, `primary_output`, and `qa`. Use one status: `completed`, `completed_with_gaps`, `needs_material_input`, `source_conflict`, `artifact_generated`, or `analysis_only`.

For a real file, include `artifact_id`, `artifact_type`, actual `file_format`, `content_schema_version`, `source_corpus_ids`, and `qa_status`. Do not claim `docx`, `pdf`, or `artifact_generated` for a plan, payload, or chat response.

Default `qa_status` to a bounded state such as `basic_pass` after confirming file existence, openability, real format, expected main sections, and absence of unresolved generation errors. Use a deeper QA state only when the user explicitly requested deeper inspection or a concrete failure required it.

## Evidence Use

Connect substantive claims to the supplied course material or a reliable permitted source. Keep coverage authority, reference material, practice evidence, evaluation criteria, and external essay evidence distinct.

Represent uncertainty plainly when a source is incomplete, ambiguous, or unreadable. Preserve locators where they materially support the requested output or later revision.

## Optional Audit

A detailed source, coverage, criterion, or rendering audit is a separate output. Build it only when explicitly requested. Its absence does not degrade an otherwise complete learning artifact.
