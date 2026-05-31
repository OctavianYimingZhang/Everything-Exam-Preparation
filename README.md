# Everything Exam Preparation

`everything-exam-preparation` is the Codex Skill in this repository. It turns a student's exam materials into Word-first, evidence-grounded revision artifacts: Academic Exam-Ready Notes plus question-type add-on reports for MCQ, Short Answer, Long Answer/Project/Scenario, and Essay exams.

The Skill name follows the GitHub repository name in Codex-safe lowercase hyphen form. The workflow itself is course-agnostic: it must learn from uploaded materials and validated sources, not from hard-coded course, topic, or example names.

The project exists because exam preparation is not one task. The correct output depends on the evidence available and on the way the exam asks questions. A student who uploads slides and MCQs should not receive essay-theme planning by default; a student who uploads essay prompts should not receive a generic flashcard table unless that is the requested artifact.

## What This Skill Does

The Skill reads the supplied materials, classifies their evidence role, and organises examinable knowledge first. The default route for general revision is `exam_prep_notes_docx`: it accepts readable ordered course notes, ranks source authority, reconstructs course sections, decomposes sources into an atomic knowledge ledger, locks a source-first baseline, then uses formal past papers for emphasis only after baseline coverage passes. It writes Academic Exam-Ready Notes in the compatible public artifact `Lecture_Knowledge_Walkthrough.docx`.

Question-type routes are add-ons to those base notes: MCQ Exam Analysis Report, Short Answer Exam Analysis Report, Long Answer/Project/Scenario Report, and Essay Module Example Essays. Essay work now has an explicit tutor-style layer for intake, DeepResearch, subtitle-level planning, plan approval, citation strategy, figure/table/data gates, and final QA before complete drafting unless the user explicitly requests direct generation. `knowledge_walkthrough_docx` remains a compatibility route for explicitly lecture-first walkthroughs. Past-paper analysis is used as a chat-only pre-generation brief to guide outputs. Excel workbooks and public prediction workbooks are no longer student-facing output routes.

The invariant is that process helper files stay separate. Public outputs may include any requested student-facing artifact, but run manifests, source maps, QA JSON, lineage files, citation logs, rendered previews, and other internal validation files must not be mixed into the student-facing folder unless the user explicitly requests an audit package.

## Custom GPT Knowledge Bundle

`custom_gpt_knowledge/Everything-Exam-Preparation-Knowledge-Combined.md` is the single-file Custom GPT upload bundle. It preserves the ChatGPT website adapter layer and combines the public Skill knowledge files so the GPT builder can upload one file instead of a folder.

## Evidence, Output, And Quality Boundaries

The workflow is course-agnostic and evidence-bound. It routes from the uploaded source pack, verified reading, and requested exam format rather than hard-coded course, lecture, or example names. It can identify examinable themes, question archetypes, and likely emphasis, but prediction language stays probabilistic and source-qualified.

Public student-facing outputs are Word-first study artifacts. Excel workbooks, run manifests, source maps, QA JSON, citation logs, lineage files, rendered previews, and internal audit folders remain helper artifacts unless the user explicitly requests an audit package.

Ordinary Academic Exam-Ready Notes are knowledge documents, not exam-format audits. Assessment timing, mark splits, paper comparability notes, source-coverage caveats, ELM warnings, and provenance text stay internal unless explicitly requested.

Example Essay output quality should be calibrated against submission-ready assessed work: polished argument, precise source integration, clean paragraph logic, complete formatting, and examiner-fit synthesis.

## Safety And Privacy

This repository should contain only the Skill, public fixtures, sanitized benchmark metadata, protocols, schemas, and helper scripts. Do not commit private lecture slides, past papers, books, student data, generated student outputs, run manifests, source maps, QA JSON, citation logs, or internal audit folders.

Example Essay outputs are revision exemplars whose language, structure, formatting, and source control should be strong enough to model submission-ready assessed work.

## Core Principle

The Skill is designed around one first-principles chain:

```text
inputs -> source authority -> course reconstruction -> atomic knowledge ledger -> source-first baseline notes -> coverage QA -> knowledge-only public view -> public output points -> exam overlay -> preparation output
```

It is not a topic-hotness predictor. Frequency and recency are useful signals, but they may adjust priority, density, order, and add-ons only after source-backed knowledge coverage is locked.

For any non-trivial run, the Skill uses a typed planning chain before generation:

```text
User request -> SkillConfig -> WorkflowPlan -> InputReadinessReport -> validated output
```

This makes the workflow configurable and auditable. The Skill first decides the requested output mode, then checks which source classes are needed, then plans the minimum action path, then blocks only the conclusions that lack evidence.

## At A Glance

| Area | Behaviour |
| --- | --- |
| Default route | `exam_prep_notes_docx`, Academic Exam-Ready Notes in `Lecture_Knowledge_Walkthrough.docx`. |
| Question-type routes | MCQ, Short Answer, Long Answer/Project/Scenario, and Essay add-ons built on top of the base notes. |
| Essay tutor layer | Essay-specific intake, DeepResearch, detailed plan approval, candidate-source labelling, citation strategy, and figure/table/data QA. |
| Prediction route | Chat-only Exam Analysis Brief for module/point selection, not a public prediction file. |
| Planning layer | `SkillConfig -> WorkflowPlan -> InputReadinessReport`. |
| Evidence model | Each source has a role and a limit before it can support a claim. |
| Public boundary | Student-facing artifacts are separated from internal helper and QA files. |
| Maintenance layer | Read-only doctor, dry-run update preview, explicit approved update, backup, and health checks. |
| Release gate | Local validation, identity-trigger linting, public-output linting, repository QA, and Skill health CI. |

## Skill Package Architecture

The package is intentionally layered:

```text
SKILL.md -> route selection, hard boundaries, reference navigation
references/ -> protocol layer for evidence, Academic Exam-Ready Notes, routing, outputs, essays, visual aids, QA, and release
schemas/ -> typed contracts for configs, plans, objects, claims, outputs, and lineage
scripts/ -> deterministic planning, generation, linting, audit, and release checks
skill_manifest.json -> package identity, health commands, and post-update commands
.github/workflows/ -> CI checks for repository and Skill health
benchmarks/ and tests/ -> sanitized fixtures that validate generic behaviour only
```

`SKILL.md` is the router, not the full manual. It should decide the narrowest valid route, enforce source and output boundaries, and load only the relevant reference files. Detailed rules for Example Essays, DOCX formatting, question-type reports, and release checks live in `references/` so trigger logic stays readable and harder to misapply.

## Core Workflow

1. Classify source files by role, trust level, extraction quality, and evidence limits.
2. Record visual-inspection status for diagrams, tables, figures, presentations, image exemplars, and image-only sources.
3. Convert source fragments into reconstructed course sections, knowledge points, and an `AtomicKnowledgeLedger`.
4. Build a source-first baseline and run coverage-floor QA before loading past-paper evidence.
5. When formal papers are present, extract question records and archetypes as optional evidence modules for emphasis and answer operations.
6. Apply the exam overlay only to priority, density, ordering, examples, traps, and question-type add-ons.
7. Filter the public view to `Course Knowledge Map`, lecture headings, and compact public output points.
8. Select output-language and route-specific DOCX style profiles before rendering.
9. Convert examples and feedback into `ExampleReviewLedger` records, transferable-rule synthesis, rule-promotion QA, and example-transfer linting before any production rule changes.
10. Run public-point, output-language, DOCX style, coverage, example-transfer, student-output, and helper-file QA so unsupported claims and process helper files do not enter the final public output.

## Quick Start

Clone the public repository as a Codex Skill:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/OctavianYimingZhang/Everything-Exam-Preparation.git ~/.codex/skills/everything-exam-preparation
cd ~/.codex/skills/everything-exam-preparation
```

Install helper-script dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Run a fixture-based planning check:

```bash
python scripts/plan_workflow.py \
  --config tests/fixtures/planner/skill_config_knowledge_walkthrough.json \
  --output /tmp/sbs_workflow_plan.json
```

Generate a fixture-based Lecture Knowledge Walkthrough DOCX while keeping public output and internal QA separate:

```bash
python scripts/generate_knowledge_walkthrough_docx.py \
  --plan tests/fixtures/knowledge_walkthrough/knowledge_walkthrough_plan.json \
  --output-dir /tmp/sbs_public_output \
  --qa-dir /tmp/sbs_internal_qa \
  --deliverable-only \
  --strict
```

Run the main repository QA gate:

```bash
python scripts/github_ready_check.py --ci
```

## Self-Check And Safe Update

The Skill includes a controlled maintenance layer. It is explicit by design: self-checks are read-only, update previews do not modify files, and real updates require approval and health validation.

Run a read-only package doctor:

```bash
python3 scripts/skill_maintenance.py doctor
```

Preview remote changes before updating:

```bash
python3 scripts/skill_maintenance.py update --dry-run
```

Apply a fast-forward update only after reviewing the dry run:

```bash
python3 scripts/skill_maintenance.py update --yes
```

The updater refuses dirty working trees, creates a local backup before changing code, runs post-update commands from `skill_manifest.json`, and then runs every health command in the manifest. If validation fails, the update is treated as failed. Installed Skill copies should be git checkouts rather than static file copies so this maintenance flow can inspect and fast-forward them safely.

## Operational Ontology

The Skill treats exam preparation as an operational object graph rather than a loose file index:

```text
SourceDocument -> SourceFragment -> AtomicKnowledgeLedger -> SourceBaselineNotesPlan -> KnowledgeOnlyStudentView -> ExamOverlayPass -> PrepArtifact -> QAFlag
```

This matters because exam preparation needs evidence permissions, not only retrieval. For example:

- lecture slides can support factual course content;
- formal past papers can support exam structure and archetype inference;
- old-format papers can support coverage but not current blueprint prediction;
- external examples can support workflow rules but not target factual claims;
- recommended books and papers can enrich only after chapter, section, DOI, PubMed, publisher, or original-source verification;
- helper artifacts stay internal unless an audit package is requested.

The machine-readable ontology contract lives in [`ontology/ontology.json`](ontology/ontology.json). The workflow protocol is in [`references/operational_ontology_protocol.md`](references/operational_ontology_protocol.md).

## Runtime Control Plane

The Skill treats each non-trivial run as a small auditable data product. Internal helper artifacts stay out of the student-facing folder, but they can be generated under `internal_qa/` to make the run reproducible:

```text
Bronze: source inventory, extraction status, source hashes
Silver: source fragments, fragment partitions, past-paper question records
Gold: course sections, atomic knowledge ledgers, source baselines, knowledge-only student views, knowledge points, examiner operations, archetypes, evidence claims, QA flags
Serving: Academic Exam-Ready Notes DOCX, compatibility walkthrough DOCX, question-type report DOCX, direct answer, optional audit package
```

The publish gate is:

```text
No object -> no link.
No valid link -> no claim.
No verified claim -> no student-facing synthesis.
No lineage -> no reproducible publish.
No QA pass -> no publish.
```

This is implemented with a fragment metadata index, optional past-paper evidence modules, example-learning promotion gates, visual-inspection metadata, a runtime ontology validator, and run manifest/lineage linting. The goal is not to run a cloud data platform; the goal is to make local exam-prep generation pruneable, auditable, and reproducible.

## Output Routes

Choose one mode, or provide materials and ask for exam prep. General revision requests use `full_workflow`, which resolves to `exam_prep_notes_docx`. Question-type prep modes add a second DOCX report on top of the base notes unless the user explicitly opts out.

| Mode | Use when | Output |
| --- | --- | --- |
| `full_workflow` | You want the default revision workflow. | Source coverage card plus Academic Exam-Ready Notes in `Lecture_Knowledge_Walkthrough.docx`. |
| `source_inventory` | You only want file roles and extraction status. | Source inventory and evidence-use limits. |
| `exam_format_diagnosis` or `exam_analysis_brief` | You want exam/past-paper analysis before file generation. | Chat-only exam analysis brief; no prediction file. |
| `exam_prep_notes_docx` | You want notes, revision, exam-prep notes, or to go through the material generally. | Exam-informed Academic Exam-Ready Notes in the compatible Word artifact. |
| `knowledge_walkthrough_docx` | You explicitly want to go through lecture knowledge in source order. | Lecture-first Word walkthrough with module overviews, knowledge walkthroughs, key logic, common confusions, and recap. |
| `mcq_exam_prep` | You need MCQ-focused preparation. | Base notes plus MCQ Point Card report. |
| `short_answer_exam_prep` | You need short-answer preparation. | Base notes plus module logic, point cards, highlighted keywords, and Example Answers. |
| `long_answer_project_scenario_prep` | You need practical, data, project, scenario, method, case, or long-answer prep. | Base notes plus question analysis, answer order, reusable blocks, Example Answer, and adaptation notes. |
| `essay_exam_prep` | You need essay preparation. | Base notes plus module-level big Example Essays with adaptation maps and paragraph banks. |
| `essay_planning_only` | You need a thesis, outline, DeepResearch plan, or plan approval stage before drafting. | Chat-only detailed essay plan with subtitle-level body logic, citation strategy, visual/data strategy, assumptions, and blockers. |
| `evidence_gap_audit` | You want to know what is missing. | Source coverage, blockers, unresolved conflicts, next-source checklist. |
| `incremental_refresh` | You add new slides, papers, readings, answers, or feedback after a prior run. | Only affected objects and artifacts are refreshed. |

The strongest source pack includes lecture slides/official notes, formal past papers, mark schemes or answer keys where available, practical/data materials, essay or long-answer prompts, extra reading recommendations/books, and any user weak areas or time budget if personalization is requested. Missing sources do not automatically stop the run; only unsupported conclusions are blocked.

Mode names are user-facing entry points. Preset names are planning-layer objects. Old workbook-style request wording is normalized internally to the current Word-first routes; it is not a public output contract.

## Setup And Planning Layer

The Skill separates configuration from execution.

| Layer | File or object | Role |
| --- | --- | --- |
| Setup | `SkillConfig` | Stores target details, source inputs, evidence policy, output preset, QA strictness, and advanced reuse settings. |
| Plan | `WorkflowPlan` | Converts the chosen preset into ordered actions, dependencies, expected outputs, skipped modules, blockers, and publish gates. |
| Readiness | `InputReadinessReport` | Checks whether the selected preset has its required source classes. |
| Preview | rendered plan | Shows the user what will run, what will be skipped, and what is blocked. |
| Execution | ontology actions | Produces source objects, knowledge objects, prep artifacts, QA flags, manifests, and lineage. |

The planning layer supports these presets:

| Preset | Minimum source classes | Main route |
| --- | --- | --- |
| `source_inventory_only` | any readable source | file classification and evidence limits |
| `exam_format_diagnosis` | formal past papers | chat-only exam analysis brief |
| `exam_prep_notes_docx` | readable course notes, with factual authority limits | default Academic Exam-Ready Notes |
| `knowledge_walkthrough_docx` | lecture slides or official notes | compatibility lecture-first walkthrough |
| `mcq_exam_prep` | lecture slides or official notes | base notes plus MCQ report |
| `short_answer_exam_prep` | lecture slides or official notes | base notes plus Short Answer report |
| `long_answer_project_scenario_prep` | lecture slides or official notes | base notes plus long-answer/project/scenario report |
| `essay_exam_prep` | lecture slides or official notes | base notes plus module-level Example Essays |
| `audit_lint_only` | none | requested checks only |
| `github_ready_qa` | none | repository release gate |

The setup protocol is in [`references/interactive_setup_protocol.md`](references/interactive_setup_protocol.md). Practical usage guidance is in [`references/best_usage_guide.md`](references/best_usage_guide.md).

## Student-Facing Outputs

Student-facing outputs are Word-first. The selected route controls which DOCX artifacts are produced. The hard rule is that internal helper and QA files are not mixed into ordinary student-facing output.

Default revision output is Academic Exam-Ready Notes in a Word artifact. Complete Example Essays are generated only when explicitly requested.

Typical student-facing outputs:

| Request type | Main output | Purpose |
| --- | --- | --- |
| Source inventory | JSON or concise report | Identify files, roles, extraction status, and evidence limits. |
| General revision / exam-prep notes | `Lecture_Knowledge_Walkthrough.docx` | Build source-first baseline notes, protect source coverage, then apply optional exam overlay. |
| Explicit lecture-order walkthrough | `Lecture_Knowledge_Walkthrough.docx` | Go through lectures in order through AI-inferred conceptual modules. |
| Exam analysis brief | Chat-only pre-generation note | Use paper patterns to choose modules and points without creating a prediction file. |
| Essay/problem-essay prep | `Essay_Module_Example_Essays.docx` | Prepare module-level big Example Essays with adaptation maps and paragraph banks. |
| MCQ prep | MCQ Point Cards and optional separate practice packs | Train recognition of close alternatives, common distractors, and expected-value answer strategy. |
| Short-answer prep | Module logic, point cards, highlighted keywords, and example answers | Convert content into source-linked mark-scaled answer shapes. |
| Long-answer/project/scenario prep | `LongAnswer_Project_Scenario_Report.docx` | Train scenario, method, readout, interpretation, control, limitation, and adaptation logic. |

Internal helper files such as manifests, source maps, QA JSON, citation logs, rendered previews, and source-audit files may be generated for validation. They are not mixed into the final user-facing output unless an audit package is explicitly requested.

## Workflow Logic

```mermaid
flowchart TD
    A[User request] --> B[SkillConfig]
    B --> C[WorkflowPlan]
    C --> D[InputReadinessReport]
    D --> E[Source inventory]
    E --> I[Course-section reconstruction]
    I --> J[Knowledge-point segmentation]
    J --> K[Source-first baseline notes]
    K --> U[Baseline coverage floor QA]
    U --> F[Optional exam-regime and question analysis]
    F --> V[Exam overlay pass]
    V --> W[Overlay coverage QA]
    W --> R[Exam-ready notes plan]
    R --> S{Output route}
    S --> L[Lecture Knowledge Walkthrough DOCX]
    S --> M[MCQ Exam Analysis Report DOCX]
    S --> N[Short Answer Exam Analysis Report DOCX]
    S --> O[Long-answer / project / scenario report DOCX]
    S --> Q[Essay Module Example Essays DOCX]
    L --> P[Language, source, identity, and deliverable QA]
    M --> P
    N --> P
    O --> P
    Q --> P
```

The Skill first classifies the evidence, reconstructs source-backed course structure, and protects a baseline note set before applying exam emphasis. It avoids applying essay logic to MCQ, short-answer, data/problem, or practical questions.

## Student-Facing Output Filter

Internal reasoning can use source anchors, confidence, recurrence, lecture centrality, examiner operation, discriminator axes, and evidence rules. Ordinary student-facing reports must not display those internal fields.

Visible output should be rewritten as:

```text
star priority -> module -> source-backed explanation -> canonical example -> exam use
```

Forbidden in ordinary student-facing reports:

```text
source anchor
evidence rationale
confidence
recurrence count
lecture centrality
examiner operation
discriminator axis
task verb
reference expansion
common omissions
past-paper year mapping
prediction score
```

For MCQ reports, the default visible item is an MCQ Point Card: priority, point, knowledge explanation, how the exam tests it, common traps, and must-remember rule. Practice questions, answer keys, contrast tables, and separate trap banks are separate optional outputs, not part of the default MCQ high-yield report.

For Short Answer reports, each section starts with module logic, then point cards. Required keywords are bolded inside the explanation, and mark logic is absorbed into the Example Answer. The student report does not show mark-producing schema, required-term fields, reference expansion, common omissions, task verb, confidence, evidence, or source anchors.

The full policy is in [`references/student_facing_output_policy.md`](references/student_facing_output_policy.md).

## Exam Prep Notes And Knowledge Walkthrough

The `exam_prep_notes_docx` route is the default for general revision. It accepts readable ordered course notes, verifies source authority, reconstructs course sections, maps lecture sessions, creates a source-first baseline plan, runs protected coverage QA, applies any exam overlay, converts internal cards into compact `PublicOutputPoint` blocks, runs a public-point consistency gate, writes Academic Exam-Ready Notes, and may append question-type add-ons after the base notes. It does not create helper files in the student-facing folder.

Ordinary Academic Exam-Ready Notes do not expose the internal card scaffold. They render by lecture, with each lecture on a new page, visible star priority labels, compact public point titles, main explanations, and only knowledge-bearing blocks such as Definitions, Criteria, Steps, Mechanism, Equation, Calculation Logic, Graph Logic, Comparison, Example, and Limitation. Headings such as `Exam Specificity`, `Core Exam Claim`, `Exam Use`, `Common Error / Trap`, and `Must Master` stay internal unless the user requests a question-type add-on or trap/checklist output.

The public-point consistency gate prevents hidden coverage loss: every visible KnowledgeCard must render in at least one public point, public points must reference real source cards, block-level atomic coverage must be visible, and point coverage must match `PointCoverageBinding`.

A knowledge-only rendering gate blocks generic advice in ordinary notes and compatibility walkthroughs. Public DOCX output should not contain `How To Answer`, `How To Use`, `Integrated reasoning`, `Integrated practical reasoning`, `Answer Logic`, `Exam Strategy`, `Recommended Approach`, `A strong answer should`, `Use this module`, or question-type reliability commentary; any real content inside those drafts must be rewritten as source-backed knowledge points or knowledge-bearing blocks.

For Example Essay and Extra Reading citation-source prose, academic author names stay inside parenthetical author-year citations in normal public output. The sentence should state the content claim, mechanism, evidence, limitation, or comparison directly; author-led literature narration is reserved for explicit literature-history requests.

The exam-prep notes DOCX style is route-specific: Arial, 2.0 cm margins, 1.5 line spacing, justified body text, left-aligned title/headings, centered images, and black visible text. Theme colours, blue heading styles, and non-black visible text are forbidden unless the user explicitly asks for colour. Example Essay DOCX output keeps its separate essay-submission format.

The `knowledge_walkthrough_docx` route remains available for explicitly lecture-first walkthroughs. It uses the same public DOCX style as ordinary notes: Arial, 2.0 cm margins, 1.5 line spacing, justified body text, left-aligned title/headings, centered images, black visible text, and stable headings. It does not predict papers, write essays, or create practice packs by default.

When the user iteratively revises a DOCX output, the latest compatible file-level instructions become release requirements for the actual document. The Skill must not overcompress below an explicit safe target range, must preserve source image objects when asked, must delete intro-only content rather than keep decorative topic labels, must use English academic annotations/formula labels/pre-colon labels when requested for bilingual or Chinese-facing notes, and must render-check the final DOCX when tooling is available before release.

Each lecture becomes:

```text
Lecture Overview
Module Map
Module 1
Module 2
...
Lecture Recap
```

Each module contains:

```text
What This Module Explains
Knowledge Walkthrough
Key Logic
Common Confusions
Must Master
```

The default notes route is defined in [`references/exam_prep_notes_protocol.md`](references/exam_prep_notes_protocol.md). The compatibility lecture-first route is defined in [`references/knowledge_walkthrough_docx_protocol.md`](references/knowledge_walkthrough_docx_protocol.md).

## Exam Analysis Brief

Past-paper analysis is handled as preparation allocation and shown in chat before file generation:

```text
past papers -> current exam regime -> PastPaperQuestion records -> QuestionArchetype registry -> slot grammar -> KP compatibility -> chat brief -> output selection
```

The Skill should not answer "what exact question will appear?" or create a separate prediction file. It should answer briefly in chat:

```text
What exam type is visible, what module/point selection follows from the evidence, what files will be generated, and which weak areas will not be overclaimed?
```

The prediction protocol is in [`references/past_paper_prediction_protocol.md`](references/past_paper_prediction_protocol.md).

## Evidence Model

Each input has a role and a limit.

| Source type | How it is used |
| --- | --- |
| Lecture slides and official notes | Primary factual source for course content and lecture logic. |
| Formal past papers | Exam format, answer rules, question type, and current prediction evidence. |
| Practical materials, mocks, quizzes, answer keys, exemplars | Coverage, answer style, practice planning, and schema evidence, with provenance kept separate. |
| Extra reading recommendations and recommended books | Enrichment only after the relevant chapter, section, paper, DOI, PubMed record, publisher page, or textbook source is verified. |
| External examples, screenshots, previous essays, benchmark fixtures | Transferable workflow and language lessons only. They cannot supply factual content or prediction evidence for a new source set. |

Failed extraction, weak OCR, unreadable images, missing files, and unsupported formats become QA flags. The Skill does not infer hidden content from them.

## Strategy Routing

The same source set can contain several question types, so the add-on report changes by detected exam strategy.

| Detected strategy | Preparation logic |
| --- | --- |
| Stable essay or problem-essay regime | Select examinable modules and generate module-level big Example Essays with adaptation maps. |
| MCQ-heavy regime | Generate MCQ Point Cards: point, explanation, how the exam tests it, traps, must-remember rule. |
| Short-answer regime | Generate module logic plus point cards with highlighted keywords and Example Answers. |
| Data/problem/practical regime | Route into the long-answer/project/scenario report when the answer needs input, operation, inference, limitation, control, or follow-up. |
| Project/scenario long-answer regime | Generate question analysis, answer order, reusable blocks, Example Answer, and adaptation notes. |
| Mixed-format regime | Generate the walkthrough plus the relevant DOCX add-on reports. |

Prediction safety rules:

- do not claim exact future wording;
- do not expose precise numerical probabilities from small paper sets;
- do not let lecturer/source-block style raise confidence above `Medium` without repeated current-regime evidence;
- do not generate unbounded short-answer question lists;
- do not claim MCQ official answers without answer-key evidence.

## Knowledge-Point Design

Knowledge points are reasoning blocks, not slide dumps.

Valid knowledge points usually follow one of these shapes:

```text
mechanism -> evidence -> consequence
process input -> actors -> mechanism -> output
method principle -> scenario application -> readout -> interpretation -> control
data -> inference -> limitation -> further test
comparison axis -> examples -> synthesis
problem -> proposed solution -> evidence -> implication
```

Student-facing prose is written as synthesis:

```text
claim -> mechanism -> evidence/example -> consequence
```

It should not narrate pages, slides, source order, or instructions about how to write an answer.

## Example Essay Mode

Example Essay mode is a separate DOCX-first revision-exemplar branch. It runs only when the user explicitly asks for complete Example Essays, model essays, full essay-style answers, or complete essay documents, and its quality target is polished, evidence-grounded prose at submission-ready assessed work standard.

For complete Example Essay generation, the Skill runs this internal sequence:

```text
question analysis
source scope detection
source reading
ppt/source logic reconstruction
citation detection and original-source reading
classic-experiment fallback when slide citations are absent
extra-reading scope matching
knowledge inventory
paragraph plan
first draft
citation and Extra Reading integration
compression budget estimate
expression-efficiency compression pass
accuracy-preservation pass
analytic argument pass
sentence-level Extra Reading micro-detail pass
highlight plan
source-to-run mapping
DOCX generation
DOCX formatting lint
visual/render QA
source audit
examiner-fit checklist
```

Essay language is controlled by the shared language contract:

- start with the answer or problem, not metacommentary;
- build paragraphs through claim, mechanism, evidence, scope, and consequence;
- convert evidence-heavy examples into `evidence -> mechanism -> interpretation -> limitation`;
- use lecture/PPT/source logic as the skeleton and Extra Reading only as a precision layer;
- do not pad essays to increase Extra Reading, citation, or molecular-detail volume;
- add named molecular, cellular, channel, receptor, pathway, assay, circuit, gene, method, or case detail only when it sharpens a parent PPT/source mechanism slot;
- reject true-but-unneeded catalogues, review-style drift, and details that need a new explanatory sentence before they are useful;
- estimate a safe compression budget before shortening, protecting the source skeleton, essential evidence, citation-supported named details, and analytic limitations;
- run final compression after citation and Extra Reading integration, preserving causal strength, scope qualifiers, model boundaries, and evidence interpretation;
- remove lecture-route narration, exam-guidance phrasing, repeated `not...but` framing, and A-B-A-C claim restarts;
- calibrate citation strength, using cautious verbs unless a source directly proves causality;
- require analytic sentences, not just descriptive lists of components;
- conclude by synthesis, not by adding new evidence.

DOCX output uses Arial, 2.5 cm margins, justified body text, centered title, left-aligned headings, 1.5 line spacing, and 0 pt paragraph spacing. The essay-question/topic subtitle is plain, left-aligned, not bold, not italic, and not enlarged.

Final Essay DOCX files must not contain public preambles or diagnostic labels such as `Model answer built from...`, `This is not a predicted exam question`, `Exam-style question`, decorative `Question:` / `Essay Topic:` labels, or standalone `Example essay` labels. Source-basis notes belong in the short chat response or internal audit artefacts, not in the student-facing Word document.

Highlighting rules:

| Highlight | Meaning |
| --- | --- |
| Green | Verified Citation / Extra Reading Paper, original citation source, or verified classic experiment, after it has been resolved and read. |
| Yellow | Uploaded Extra Reading Book content matched to the relevant chapter or section. |
| No highlight | Ordinary lecture-slide or official-source content. |

Academic papers are citation sources even when the user calls them extra reading: they require parenthetical author-year citation and green highlight. Yellow is reserved for uploaded Extra Reading Books with chapter/section anchors.

## Academic Integrity Boundary

This Skill is for preparation, revision, source organization, Word-first report generation, and practice-route planning. The same high prose standard used for assessed work is a quality benchmark for revision exemplars, while the permitted-use boundary remains strict.

Excluded requests:

- live exams;
- active assessed submissions;
- contract-cheating requests;
- presenting predicted themes as official questions;
- inventing citations, statistics, dates, mark schemes, source names, mechanisms, or lecturer preferences.

Essay/problem-essay predictions must be labelled as predicted themes. Practice stems may be included only as practice variants derived from the theme.

## Repository Structure

| Path | Role |
| --- | --- |
| `SKILL.md` | Top-level Codex Skill instructions and output contract. |
| `skill_manifest.json` | Skill identity, repository metadata, health commands, and post-update commands for doctor/update maintenance. |
| `ontology/` | Machine-readable operational ontology: object types, link types, action types, validation rules, and query templates. |
| `references/` | Protocols for evidence handling, routing, Academic Exam-Ready Notes, visual aids, planning, student-facing filters, language quality, Example Essays, legacy internal workbook compatibility, regression, and release. |
| `scripts/` | Helper CLIs for planning, readiness checks, extraction, grouping, DOCX generation, student-output linting, language linting, citation resolution, source audit, deliverable linting, gap reporting, and GitHub-ready QA. |
| `schemas/` | JSON schemas for setup config, workflow plans/actions, readiness reports, student output contracts, knowledge walkthrough plans, Academic Exam-Ready Notes, Example Essay plans, language deltas, example review ledgers, runtime objects, fragment partitions, run manifests, and lineage events. |
| `benchmarks/` | Sanitized benchmark metadata and lint fixtures. They preserve transferable workflow rules only. |
| `tests/fixtures/` | Small public fixtures for DOCX, source-grounding, and citation-fallback checks. |
| `agents/` | Optional Skill interface metadata, presets, prompt cards, and setup wizard metadata. |
| `.github/workflows/` | Repository CI and scheduled Skill health checks. |

Key public contracts:

| Contract | File |
| --- | --- |
| Student-facing output filter | `references/student_facing_output_policy.md` |
| Default Academic Exam-Ready Notes route | `references/exam_prep_notes_protocol.md` |
| Compatibility lecture walkthrough route | `references/knowledge_walkthrough_docx_protocol.md` |
| Setup and planning route | `references/interactive_setup_protocol.md` |
| Exam-analysis brief route | `references/past_paper_prediction_protocol.md` |
| Example Essay route | `references/essay_generation_protocol.md` and `references/example_essay_docx_output_protocol.md` |
| Optional visual-aid route | `references/visual_aid_generation_protocol.md` |
| Release gate | `references/github_release_protocol.md` |

## Install

Clone as a Codex Skill:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/OctavianYimingZhang/Everything-Exam-Preparation.git ~/.codex/skills/everything-exam-preparation
```

The GitHub repository is named `Everything-Exam-Preparation`; the local folder name `everything-exam-preparation` is the Codex Skill id.

Install Python dependencies for helper scripts:

```bash
cd ~/.codex/skills/everything-exam-preparation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The scripts are plain Python files. Extraction and DOCX quality depend on the installed document libraries and source-file quality.

## Command Catalog

Generate a compatibility Lecture Knowledge Walkthrough DOCX:

```bash
python scripts/generate_knowledge_walkthrough_docx.py \
  --plan /path/to/knowledge_walkthrough_plan.json \
  --output-dir /path/to/public_output \
  --qa-dir /path/to/internal_qa \
  --deliverable-only \
  --strict
```

Lint a Lecture Knowledge Walkthrough DOCX:

```bash
python scripts/knowledge_walkthrough_linter.py /path/to/public_output
```

Create a workflow plan from a setup config:

```bash
python scripts/plan_workflow.py \
  --config /path/to/skill_config.json \
  --output /path/to/internal_qa/workflow_plan.json
```

Check whether the selected preset has enough source support:

```bash
python scripts/input_readiness_check.py \
  --config /path/to/skill_config.json \
  --output /path/to/internal_qa/input_readiness.json
```

Render a plan preview:

```bash
python scripts/render_workflow_plan.py \
  --plan /path/to/internal_qa/workflow_plan.json \
  --output /path/to/internal_qa/workflow_plan.md
```

Create a run status object:

```bash
python scripts/run_status_report.py \
  --plan /path/to/internal_qa/workflow_plan.json \
  --output /path/to/internal_qa/run_status.json
```

Inventory sources:

```bash
python scripts/extract_sources.py /path/to/input_dir --output /path/to/output_dir --target "Target Course"
```

Group sources by target and regime:

```bash
python scripts/target_grouper.py /path/to/output_dir/source_scan.json --output /path/to/output_dir/target_groups.json
```

Extract question-level past-paper records:

```bash
python scripts/extract_past_paper_questions.py /path/to/past_papers \
  --target-group-key "Target Course" \
  --current-regime-key "current_regime" \
  --output-dir /path/to/internal_qa
```

Build a fragment metadata index:

```bash
python scripts/build_fragment_index.py \
  --source-scan /path/to/internal_qa/source_scan.json \
  --output-dir /path/to/internal_qa
```

Validate runtime ontology objects and links:

```bash
python scripts/ontology_validator.py \
  --objects-dir /path/to/internal_qa/ontology_objects \
  --links /path/to/internal_qa/ontology_links/links.jsonl
```

Lint a run manifest and lineage events:

```bash
python scripts/run_manifest_linter.py \
  --manifest /path/to/internal_qa/run_manifest.json \
  --lineage-events /path/to/internal_qa/lineage_events.jsonl

python scripts/lineage_report.py \
  --manifest /path/to/internal_qa/run_manifest.json \
  --lineage-events /path/to/internal_qa/lineage_events.jsonl \
  --output /path/to/internal_qa/lineage_report.json
```

Validate action writer coverage and the interaction contract:

```bash
python scripts/validate_action_writer_coverage.py
python scripts/validate_interaction_contract.py
python scripts/validate_workflow_planning_contract.py
```

Lint ontology and past-paper prediction outputs:

```bash
python scripts/ontology_linter.py
python scripts/past_paper_prediction_linter.py \
  --input /path/to/internal_qa/past_paper_questions.json \
  --suite benchmarks/past_paper_prediction_suite.json
```

Lint student-facing prose fixtures:

```bash
python scripts/essay_style_linter.py --fixture benchmarks/kp_essay_style_linter_fixtures.json
```

Lint complete Example Essay language:

```bash
python scripts/example_essay_language_linter.py --plan /path/to/example_essay_plan.json
```

Generate Example Essay DOCX files from a plan:

```bash
python scripts/generate_example_essay_docx.py --plan /path/to/example_essay_plan.json --output-dir /path/to/output --strict
```

Prepare citation resolution or classic-experiment fallback:

```bash
python scripts/lecture_citation_resolver.py --input /path/to/slides.pptx --output-dir /path/to/internal_qa --classic-search-if-no-citations
```

Check that public output excludes helper artefacts:

```bash
python scripts/final_deliverable_linter.py /path/to/public_output
```

Analyse external examples into review-ledger records and transferable deltas:

```bash
python scripts/analyze_example_corpus.py /path/to/examples --output /path/to/example_analysis.json --max-files 80
python scripts/example_transfer_linter.py /path/to/example_review_ledger.json
```

Run metadata-only regression checks:

```bash
python scripts/cross_subject_regression_check.py --metadata-only --suite benchmarks/cross_subject_regression_suite.json
python scripts/cross_subject_regression_check.py --metadata-only --suite benchmarks/method_long_answer_suite.json
python scripts/cross_subject_regression_check.py --metadata-only --suite benchmarks/past_paper_prediction_suite.json
```

Run the full local QA gate:

```bash
python scripts/github_ready_check.py --ci
```

Run the maintenance doctor:

```bash
python3 scripts/skill_maintenance.py doctor
```

## Benchmark Sanitization

The public benchmark files are regression fixtures. They test generic behaviours such as regime splitting, question-type routing, output layout adaptation, source-boundary discipline, Example Essay language quality, ontology contract integrity, action writer coverage, interaction contract coverage, runtime object-store validation, run-manifest lineage, past-paper prediction hard failures, and cross-source leakage prevention.

They intentionally exclude private lecture slides, past papers, notes, mocks, student files, generated outputs, local absolute paths, and cached run outputs.

## License

MIT.
