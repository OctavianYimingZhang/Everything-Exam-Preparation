# Everything Exam Preparation

Everything Exam Preparation is an independently installable Codex Plugin for turning trusted course material into explanation-first Notes, exam-specific preparation, assessment practice, and permission-controlled Online Essay Exam support.

> **Repository boundary:** this repository contains Plugin code only: Skills, manifests, contracts, local adapters, scripts, schemas, tests, and documentation. It does not contain or deploy the Everything University website. The owner-only Site is a separate optional control plane.

The Plugin keeps a traceable path from evidence to output:

```text
trusted source fragments -> human review -> route and inputs locked
                         -> permissions confirmed -> plan approved
                         -> local execution -> QA -> optional mastery update
```

It does not treat every uploaded page as equally useful or allow an automatic recommendation to become a confirmed decision. Source roles, route choices, permissions, and plans remain reviewable before execution.

## What the Plugin does

- Builds broad, explanation-first course Notes with `coverage_policy: lecture_unit_complete`.
- Triages slide-like material so structural or non-teaching slides remain traceable without becoming unnecessary public sections.
- Produces focused MCQ, short-answer, long-answer, worked-solution, essay, and mixed-format preparation.
- Solves a supplied question or organises supplied questions in lecture or knowledge-unit order.
- Builds source-grounded assessment blueprints, evaluates answers against explicit criteria, and creates duration-bound timed practice.
- Supports a complete Online Essay Exam draft only when the assessment rules and source permissions explicitly allow it.
- Preserves page, slide, timestamp, and time-range provenance through planning and assessment outputs.
- Maintains default-enabled, per-course mastery and weakness history with independent enable, disable, export, and deletion controls.
- Defaults all shipped prompts, questions, plans, metadata, errors, documentation, tests, and generated output to English unless the user explicitly overrides the language for that task.

## Independent Multiple Skill system

The Plugin can run without Everything University or any other Soleil Plugin. Versioned contracts allow those systems to interoperate when installed, but they do not merge their generation logic. The router loads only the focused sibling Skills required by the confirmed task.

| Layer | Entry point | Responsibility |
| --- | --- | --- |
| Plugin discovery | [`skills/everything-exam-preparation/SKILL.md`](skills/everything-exam-preparation/SKILL.md) | Loads the package workflow from the root entrypoint. |
| Compatibility and shared workflow | [`SKILL.md`](SKILL.md) | Preserves the established invocation and common evidence, language, output, and review rules. |
| Routing | [`exam-prep-index`](skills/exam-prep-index/SKILL.md) | Handles broad requests, mixed exams, route review, and assessment blueprints. |
| Route Skills | [`skills/`](skills/) | Separates Notes, MCQ, short answer, long answer, worked solutions, essay, Online Essay Exam, question solving, and question organisation. |
| Internal analysis | [`exam-prep-slide-triage`](skills/exam-prep-slide-triage/SKILL.md) | Classifies slide-like material as `use`, `merge_with_previous`, or `exclude` before Notes generation. |
| Permitted enrichment | [`exam-prep-extra-reading`](skills/exam-prep-extra-reading/SKILL.md) | Maps academically useful Extra Reading to essay claims when the confirmed route and permissions allow it. |
| Typed execution boundary | [`plugin_capability_manifest.json`](plugin_capability_manifest.json) and [`scripts/soleil_adapter.py`](scripts/soleil_adapter.py) | Declares route ownership and validates context, gates, lifecycle state, and terminal results. |

Directly invoking a focused Skill selects a candidate route; it does not bypass required-input review, permissions, or Planning Approval.

## Thirteen declared routes

[`plugin_capability_manifest.json`](plugin_capability_manifest.json) is the canonical `PluginCapabilityManifest v2` route registry.

| Route ID | Owning Skill | Declared result |
| --- | --- | --- |
| `exam_prep_notes` | `exam-prep-notes` | Explanation Notes in DOCX |
| `mcq_preparation` | `exam-prep-mcq` | Notes and MCQ preparation output |
| `short_answer_preparation` | `exam-prep-short-answer` | Notes and short-answer preparation output |
| `long_answer_preparation` | `exam-prep-long-answer` | Notes and long-answer, practical, data, or problem output |
| `worked_solution_preparation` | `exam-prep-worked-solutions` | Notes and worked-solutions DOCX |
| `essay_preparation` | `exam-prep-essay` | Notes and essay-preparation output |
| `online_essay_exam_drafting` | `exam-prep-online-essay-exam` | Permitted Markdown draft and optional DOCX |
| `mixed_exam_preparation` | `exam-prep-index` | Confirmed combination of selected component outputs |
| `question_solving` | `exam-prep-question-solver` | Question Solution Report |
| `question_organizing` | `exam-prep-question-organizer` | Organised Questions DOCX |
| `assessment_blueprint` | `exam-prep-index` | Source-grounded assessment blueprint |
| `answer_evaluation` | `exam-prep-question-solver` | Criterion-level answer-evaluation report |
| `timed_practice` | `exam-prep-question-solver` | Timed practice session |

## Versioned contracts and run lifecycle

The schemas in [`contracts/`](contracts/) form the shared boundary used by the independently installable Soleil Plugins and private ChatGPT Sites.

| Contract | Purpose |
| --- | --- |
| `PluginCapabilityManifest v2` | Declares each route's owner, triggers, required inputs, gates, outputs, adapter, and supported context versions. |
| `AcademicTaskContext v1` | Carries the original prompt, explicit route, course, source references, relevant memory, permissions, and decisions. Decisions are `suggested` or `explicitly_confirmed`. |
| `TaskRunState v1` | Preserves one caller-supplied `run_id` across planning, execution, QA, or failure. |
| `SourceRecord v1` | Identifies a local source by stable ID, checksum, type, provenance, parser version, opaque local reference, processing status, and page or time locators. |
| `LocalBridgeProtocol v1` | Defines version negotiation, random session tokens, strict loopback and origin checks, rate limiting, and explicit transfer consent. |

The adapter enforces this ordered lifecycle:

```text
source_ready -> route_or_brief_locked -> permissions_confirmed
             -> plan_approved -> running -> qa_passed | failed
```

It preserves an explicit route and supplied source fragments instead of re-detecting intent from an empty prompt. It also refuses to fabricate completion: `running` and a terminal state require an explicit local `execution_result` after all gates pass.

## Ask User and execution gates

[`scripts/build_review_questions.py`](scripts/build_review_questions.py) generates concrete, route-specific Ask User payloads. Recommended answers remain unconfirmed until the user selects or corrects them.

The initial human review confirms the Exam type, Material type and source roles, and whether Notes should be generated before route-specific follow-up questions are asked.

Every route requires:

1. direct-invocation and route review;
2. all manifest-declared required inputs;
3. explicitly confirmed local-execution permission; and
4. an explicitly confirmed plan.

Additional gates apply where needed:

- Notes-capable routes require an explicit Notes output choice.
- Mixed preparation requires `confirmed_mixed_routes` before component follow-ups or output generation.
- Assessment blueprints require a confirmed scope.
- Answer evaluation requires the supplied answer and explicit criteria or marking material.
- Timed practice requires a blueprint and explicit positive duration.
- Online Essay Exam requires confirmed Online Materials and Lecture Materials permissions, an exact allowed source set, citation and format decisions, and explicit confirmation that the assessment permits a complete draft.

If complete-draft permission is missing, denied, conflicting, or revoked, the Online Essay Exam route cannot enter `running` for full drafting. Permitted source organisation, evidence mapping, planning, review, and feedback remain available.

## Source model and outputs

Source fragments retain locators such as `page_number`, `slide_number`, `time_offset_seconds`, and `time_range`. Notes are a broad lecture reconstruction: they explain most substantive `core_lecture_content` and its exam-relevant knowledge in useful course order rather than collapsing the course into high-frequency exam points. A route-specific Specific Research Report is separate concise exam-priority reinforcement and does not replace the broader Notes.

Slide triage keeps a private `slide_triage_audit` of structural, duplicate, decorative, administrative, reading-list-only, and other non-teaching material. Useful examples may be merged or compressed; excluded material is not silently repurposed as evidence.

Question Solving returns `question_solution_report`, connecting the target question to course knowledge, reasoning, and strict same-knowledge-point transfer practice. Question Organisation returns `organized_questions_docx`, ordering supplied Past Paper or Practice Material questions with minimal provenance and no added answers.

The assessment utilities are available directly:

```bash
python3 scripts/assessment_tools.py blueprint \
  --fragments source_fragments.json \
  --memory relevant_memory.json \
  --out assessment_blueprint.json

python3 scripts/assessment_tools.py evaluate \
  --input answer_evaluation_input.json \
  --out answer_evaluation.json

python3 scripts/assessment_tools.py timed \
  --blueprint assessment_blueprint.json \
  --duration-minutes 45 \
  --out timed_practice.json
```

Blueprint weighting describes source-fragment occurrence, not invented predicted marks. Answer evaluation reports criterion evidence and requires human review; it does not manufacture a mark. Timed practice preserves both source provenance and the explicit time allocation.

## Mastery and weakness history

History is enabled by default for each course and stored locally at:

```text
~/.codex/state/everything-exam-preparation/mastery_history.json
```

Disabling a course stops new records without deleting its existing history. Export and deletion are separate explicit actions.

```bash
python3 scripts/mastery_history.py status --course-id BIO101
python3 scripts/mastery_history.py disable --course-id BIO101
python3 scripts/mastery_history.py enable --course-id BIO101
python3 scripts/mastery_history.py export --course-id BIO101 --out BIO101-history.json
python3 scripts/mastery_history.py delete --course-id BIO101
```

Relevant Everything University memory is consumed by record ID and purpose. The Plugin does not require a monolithic memory dump.

## Optional Everything University control plane

The owner-only [Everything University Site](https://soleil-university.ready-loach-3659.chatgpt.site) is a separate source, memory, task, run-control, and artifact workspace. It discovers routes from this Plugin's manifest and sends a reviewed `AcademicTaskContext v1`; it does not reproduce this Plugin's Exam generation logic.

The Site may store confirmed structured state and opaque local references in D1. Raw documents, audio, full extracted text, generated artifacts, mastery files, and Codex execution remain local and are transferred only to the authenticated loopback bridge with explicit consent. R2 is not used for this workflow.

The Plugin remains fully usable without the Site when invoked with valid local inputs.

## Installation

Clone the repository, install its Python dependencies, and synchronise the compatibility Skill plus every focused sibling Skill into `~/.codex/skills`:

```bash
git clone https://github.com/OctavianYimingZhang/Everything-Exam-Preparation.git
cd Everything-Exam-Preparation
python3 -m pip install -r requirements.txt
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --check-installed
```

The synchroniser excludes generated outputs, caches, and private artifacts. The Plugin manifest remains at [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) for Codex Plugin discovery.

After updating the checkout, update dependencies before re-synchronising. The sync command copies files but does not install changed Python requirements:

```bash
git pull --ff-only
python3 -m pip install --upgrade -r requirements.txt
python3 scripts/publish_skill.py --sync-local-skill
python3 scripts/publish_skill.py --check-installed
```

## Example invocations

```text
$everything-exam-preparation
Review these lecture slides and past papers. Propose the exam route, source roles,
Notes choice, and output plan for my confirmation.
```

```text
$exam-prep-question-solver
Explain this supplied question from the trusted course sources and create strict
same-knowledge-point transfer practice.
```

```text
$exam-prep-online-essay-exam
Review the assessment rules and allowed sources before deciding whether a complete
draft is permitted.
```

```text
$exam-prep-index
Build a source-grounded assessment blueprint for the confirmed course scope.
```

## Validation

Run from the repository root:

```bash
python3 -m compileall -q scripts
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/validate_skill_contracts.py
python3 scripts/github_ready_check.py --ci
python3 scripts/publish_skill.py --dry-run --sync-local-skill
python3 scripts/publish_skill.py --check-installed
python3 "$HOME/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py" .
```

`validate_skill_contracts.py` verifies route ownership, schema and relative-path integrity, required gates, default-English rules, mastery controls, helper self-tests, and manifest synchronisation.

## Repository map

| Path | Responsibility |
| --- | --- |
| [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json) | Codex Plugin metadata and interface declaration. |
| [`SKILL.md`](SKILL.md) | Compatibility entrypoint and shared workflow contract. |
| [`skills/`](skills/) | Plugin router, index, and focused Skills. |
| [`plugin_capability_manifest.json`](plugin_capability_manifest.json) | Canonical `PluginCapabilityManifest v2` with 13 routes. |
| [`skill_manifest.json`](skill_manifest.json) | Package, installation, language, provenance, and mastery metadata. |
| [`contracts/`](contracts/) | Shared versioned Soleil JSON Schemas. |
| [`references/`](references/) | Evidence, Notes, route, essay, Online Essay Exam, Extra Reading, and language protocols. |
| [`schemas/`](schemas/) | Route-specific structured-output schemas. |
| [`scripts/`](scripts/) | Extraction, planning, Ask User, adapters, assessment tools, mastery state, rendering, validation, and local synchronisation. |
| [`tests/`](tests/) | Adapter lifecycle and gate regression tests with fixtures. |
| [`agents/`](agents/) | Presets, prompt cards, and setup metadata. |
| [`.github/workflows/`](.github/workflows/) | CI and Skill-health validation. |

No website source, website build, GitHub Pages workflow, or hosted-site asset belongs in this Plugin repository.

## Security and private-data boundary

- Use only the source set and permissions explicitly confirmed for the current task.
- Keep raw course files, past papers, assessment material, Online Materials, audio, full extracts, generated artifacts, and mastery history local.
- Do not commit credentials, tokens, private course archives, assessment answers, or user data.
- Keep bridge traffic on strict loopback with a random session token, origin allowlist, protocol-version checks, rate limiting, and explicit transfer consent.
- Treat stale, conflicting, denied, or merely suggested permissions and decisions as unresolved.
- Return explicit QA failures instead of projecting a fabricated academic result.

## Licence

MIT. See [`LICENSE`](LICENSE).
