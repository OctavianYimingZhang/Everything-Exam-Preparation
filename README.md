# Everything Exam Preparation

[Everything Exam Preparation](https://github.com/OctavianYimingZhang/Everything-Exam-Preparation) is a multiple-Skill Plugin that converts trusted course sources into teachable exam preparation, assessment practice, and permission-controlled Online Essay Exam support.

Its purpose is not to summarize files indiscriminately. It reconstructs the knowledge a student must understand, separates broad teaching from route-specific practice, preserves source locators, and refuses execution until the route, inputs, permissions, and plan are explicit.

## First-principles workflow

Reliable exam preparation requires a traceable chain from source to learning outcome:

```text
trusted source fragments -> knowledge units -> human review
                         -> route and required inputs locked
                         -> permissions confirmed -> plan approved
                         -> local execution -> QA -> mastery update
```

The Plugin therefore:

1. Reads supplied lecture material, practice material, mark schemes, worked examples, allowed Online Materials, and confirmed Extra Reading.
2. Preserves page, slide, timestamp, and time-range provenance on every fragment.
3. Classifies Material type and source role before using a fragment as evidence.
4. Builds knowledge units rather than treating every page as equally important.
5. Presents an auto-diagnosis for human review of Exam type, Material type, and whether Notes should be generated.
6. Keeps every recommendation `suggested` until the user selects or corrects it.
7. Executes only after the route, route-specific questions, permissions, and plan are explicitly confirmed.
8. Returns artifacts, QA results or failure reasons, and an optional per-course mastery update.

## Multiple Skill system

The root [`SKILL.md`](SKILL.md) is the compatibility entrypoint. `exam-prep-index` is the router, and the focused sibling Skills own specialised preparation workflows.

| Skill | Responsibility |
| --- | --- |
| `exam-prep-index` | Route broad, mixed, blueprint, evaluation, and timed-practice requests. |
| `exam-prep-notes` | Produce explanation-first DOCX Notes from trusted knowledge units. |
| `exam-prep-slide-triage` | Analyse slide-like sources and retain a `slide_triage_audit` without turning administrative or decorative slides into teaching sections. |
| `exam-prep-mcq` | Prepare MCQ/SBA recurrence and exam-priority reinforcement. |
| `exam-prep-short-answer` | Prepare short-answer and SAQ knowledge reinforcement. |
| `exam-prep-long-answer` | Prepare long-answer, practical, data, scenario, and problem responses. |
| `exam-prep-worked-solutions` | Teach calculation, derivation, proof, estimate, data, and problem-solving paths. |
| `exam-prep-essay` | Prepare essay structures and permitted Extra Reading enrichment. |
| `exam-prep-online-essay-exam` | Lock the assessment brief, allowed source set, evidence map, paragraph plan, permissions, drafting boundary, and QA. |
| `exam-prep-extra-reading` | Discover, classify, and map academically useful enrichment to essay claims. |
| `exam-prep-question-solver` | Explain a target question, its knowledge unit, its solution path, and strict same-knowledge-point transfer questions. |
| `exam-prep-question-organizer` | Order supplied questions by lecture or knowledge-unit sequence with minimal provenance. |

Direct invocation is supported, but it does not bypass route review, required inputs, permissions, or Planning Approval.

## Versioned capability and contracts

[`plugin_capability_manifest.json`](plugin_capability_manifest.json) is a `PluginCapabilityManifest v2`. It declares 13 route IDs, owning Skills, triggers, required inputs, gates, outputs, the adapter entrypoint, and supported context versions.

The schemas under [`contracts/`](contracts/) are the shared boundary with the other independently installable Soleil Plugins and the private ChatGPT Sites:

| Contract | Purpose |
| --- | --- |
| `PluginCapabilityManifest v2` | Typed route ownership and execution requirements. |
| `AcademicTaskContext v1` | Original prompt, course, explicit route, source fragments, relevant memory, permissions, and decisions. |
| `TaskRunState v1` | One caller-supplied `run_id` from source readiness to QA or failure. |
| `SourceRecord v1` | Stable source identity, checksum, provenance, parser version, local reference, and page/time locators. |
| `LocalBridgeProtocol v1` | Version handshake, random session token, loopback/origin restrictions, rate limiting, and explicit transfer consent. |

[`scripts/soleil_adapter.py`](scripts/soleil_adapter.py) consumes `AcademicTaskContext v1` and preserves explicit route selection, source fragments, relevant-memory references, permissions, decisions, and the caller's `run_id`. It enforces the ordered lifecycle:

```text
source_ready -> route_or_brief_locked -> permissions_confirmed
             -> plan_approved -> running -> qa_passed | failed
```

The adapter never manufactures a completed execution. A terminal result must be supplied as an explicit `execution_result`, and the adapter accepts it only after every manifest-derived gate has passed.

## Routes

| Route ID | Owning Skill | Primary result |
| --- | --- | --- |
| `exam_prep_notes` | `exam-prep-notes` | `docx_notes` |
| `mcq_preparation` | `exam-prep-mcq` | Notes plus MCQ exam-priority output |
| `short_answer_preparation` | `exam-prep-short-answer` | Notes plus short-answer output |
| `long_answer_preparation` | `exam-prep-long-answer` | Notes plus long-answer/practical/data/problem output |
| `worked_solution_preparation` | `exam-prep-worked-solutions` | Notes plus worked-solutions DOCX |
| `essay_preparation` | `exam-prep-essay` | Notes plus essay-preparation output |
| `online_essay_exam_drafting` | `exam-prep-online-essay-exam` | Permitted draft and optional DOCX |
| `mixed_exam_preparation` | `exam-prep-index` | Confirmed combination of selected component routes |
| `question_solving` | `exam-prep-question-solver` | `question_solution_report` |
| `question_organizing` | `exam-prep-question-organizer` | `organized_questions_docx` |
| `assessment_blueprint` | `exam-prep-index` | Source-grounded assessment blueprint |
| `answer_evaluation` | `exam-prep-question-solver` | Answer-evaluation report against confirmed criteria |
| `timed_practice` | `exam-prep-question-solver` | Duration-bound timed practice session |

## Ask User, permission, and plan gates

[`scripts/build_review_questions.py`](scripts/build_review_questions.py) generates the route-specific Ask User payload. The user reviews concrete alternatives rather than a vague approval prompt.

Common controls include:

- direct-invocation review;
- Exam type and route selection;
- Material type and source-role confirmation;
- whether Notes should be generated;
- explicit component selection for mixed exams;
- required-input readiness from the capability manifest;
- local-execution permission;
- visible plan and Planning Approval.

Online Essay Exam adds stricter gates:

- Online Materials permission;
- Lecture Materials permission;
- exact allowed source set;
- explicit confirmation that the assessment permits a complete draft;
- citation and output-format expectations;
- locked brief, evidence map, paragraph plan, and CriticalAnalysisPlan.

If complete-draft permission is denied, missing, conflicting, or later revoked, the route cannot enter `running`. The Plugin can still provide permitted source organisation, evidence mapping, planning, review, and feedback.

## Notes, reports, and practice

Notes use `coverage_policy: lecture_unit_complete`. They are a broad lecture reconstruction for a student who may not yet understand the material. They preserve source order where useful, cover most substantive units, and teach the exam-relevant knowledge behind concepts, mechanisms, methods, calculations, assumptions, interpretation, and applications.

`core_lecture_content` is explained. Supporting examples are retained when useful and compressed when repetitive. Administrative, duplicate, decorative, transition, empty, and reading-list slides remain traceable in slide triage but do not become long public sections.

A route-specific Specific Research Report is separate concise exam-priority reinforcement. It does not replace the broader Notes. MCQ and SAQ recurrence use supplied past or official exam papers; long-answer, worked-solution, essay, question-solving, and question-organisation routes keep their own evidence logic.

`question_solution_report` presents the target question, matched course knowledge, solution reasoning, and strict same-knowledge-point transfer material. `organized_questions_docx` follows lecture or knowledge-unit order and keeps each question tied to minimal provenance.

Assessment tools support:

```bash
python3 scripts/assessment_tools.py blueprint \
  --fragments source_fragments.json \
  --memory relevant_memory.json

python3 scripts/assessment_tools.py evaluate \
  --input answer_evaluation_input.json

python3 scripts/assessment_tools.py timed \
  --blueprint assessment_blueprint.json \
  --duration-minutes 45
```

## Mastery and weakness history

Per-course mastery history is enabled by default and stored locally at:

```text
~/.codex/state/everything-exam-preparation/mastery_history.json
```

Disabling history stops new records without deleting existing ones. Export and deletion are separate explicit controls:

```bash
python3 scripts/mastery_history.py status --course-id BIO101
python3 scripts/mastery_history.py disable --course-id BIO101
python3 scripts/mastery_history.py enable --course-id BIO101
python3 scripts/mastery_history.py export --course-id BIO101 --out BIO101-history.json
python3 scripts/mastery_history.py delete --course-id BIO101
```

Relevant memory is passed by record ID and purpose. The Plugin does not need a monolithic memory dump to prepare a task.

## Private Everything University Site

The owner-only [Everything University Site](https://soleil-university.ready-loach-3659.chatgpt.site) is the source, memory, task, run-control, and artifact workspace. It discovers available Exam routes from this Plugin's manifest and sends an already reviewed `AcademicTaskContext`; it does not duplicate Exam generation logic.

The intended flow is:

```text
Today -> Courses -> Sources -> Memory/Mastery -> Tasks -> Runs -> Artifacts
```

File bytes go only to the authenticated local bridge. Local processing performs parsing, OCR or transcription, checksum deduplication, fragmentation, and locator attachment before the user reviews material for trusted memory. D1 stores confirmed structured state and opaque local references, not raw documents, audio, or full extracted text. R2 is not required.

The Plugin remains independently installable and can also consume a valid `AcademicTaskContext v1` and source fragments without the Site.

## Output language and private-data boundary

All shipped documentation, prompts, questions, plans, metadata, errors, tests, and generated output default to English. A request written in another language does not silently change the output language; only an explicit task-level override does.

Keep raw lecture files, past papers, permitted Online Materials, audio, extracted full text, generated DOCX files, and mastery history local. A task context may carry bounded source fragments for local execution; persistent shared state should contain checksums, provenance, permissions, decisions, QA, and opaque source or artifact identifiers, not raw or full extracted content. Never place credentials, access tokens, assessment answers, or private course archives in the repository.

## Installation

```bash
git clone https://github.com/OctavianYimingZhang/Everything-Exam-Preparation.git
cd Everything-Exam-Preparation
python3 -m pip install -r requirements.txt
python3 scripts/publish_skill.py --sync-local-skill
```

The synchroniser installs the compatibility entrypoint and every focused sibling Skill under `~/.codex/skills` while excluding generated outputs and private artifacts.

After an update:

```bash
git pull --ff-only
python3 scripts/publish_skill.py --sync-local-skill
```

## Example invocations

```text
$everything-exam-preparation
Use these lecture slides and past papers to propose the Exam type, Material type, Notes choice, and output plan for my review.
```

```text
$exam-prep-question-solver
Explain this question from the supplied course sources and retrieve strict same-knowledge-point practice.
```

```text
$exam-prep-online-essay-exam
Review the assessment and source permissions before deciding whether a complete draft is allowed.
```

## Validation

Run from the repository root:

```bash
python3 -m compileall -q scripts
python3 scripts/validate_skill_contracts.py
python3 scripts/github_ready_check.py --ci
python3 scripts/plan_workflow.py --self-test
python3 scripts/build_review_questions.py --self-test
python3 scripts/soleil_adapter.py --self-test
python3 scripts/assessment_tools.py --self-test
python3 scripts/mastery_history.py --self-test
python3 scripts/publish_skill.py --self-test
python3 scripts/publish_skill.py --dry-run --sync-local-skill
python3 "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

## Repository map

| Path | Responsibility |
| --- | --- |
| [`SKILL.md`](SKILL.md) | Compatibility entrypoint and shared workflow. |
| [`skills/`](skills/) | Router and focused Skills. |
| [`plugin_capability_manifest.json`](plugin_capability_manifest.json) | `PluginCapabilityManifest v2` route registry. |
| [`contracts/`](contracts/) | Shared Soleil schemas. |
| [`references/`](references/) | Source, Notes, route, essay, Online Essay Exam, Extra Reading, and language protocols. |
| [`scripts/`](scripts/) | Routing, Ask User payloads, adapters, assessment tools, mastery state, rendering helpers, validation, and local installation. |
| [`schemas/`](schemas/) | Route-specific structured-output schemas. |
| [`agents/`](agents/) | Presets, prompt cards, and setup metadata. |
| [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) | Plugin metadata and Codex interface declaration. |

## Security and provenance

- Use the exact source permissions confirmed for the task.
- Preserve page, slide, timestamp, and time-range locators in source fragments and derived claims.
- Reject missing, stale, conflicting, or merely suggested permission and planning decisions.
- Do not let direct invocation, mixed routing, or Online Essay Exam selection skip lifecycle gates.
- Treat external enrichment as optional evidence, not a substitute for supplied course material.
- Keep the local bridge on strict loopback with a random session token, origin allowlist, rate limiting, protocol-version checks, and explicit transfer consent.
- Return explicit failure reasons; do not project a persistence error into a fabricated academic result.

## Licence

MIT. See [`LICENSE`](LICENSE).
