# ChatGPT Website Adapter For Everything Exam Preparation

This adapter controls the single-file Everything Exam Preparation Skill inside the ChatGPT website and Custom GPT environment. It is an output-channel layer: it decides when to answer in chat and when to create a Word document. The underlying Skill still controls evidence, routing, factual standards, formatting contracts, and QA.

## Website Constraint Model

Official OpenAI Help Center limits checked on 2026-05-29:

- Files uploaded to GPTs or ChatGPT conversations have a hard limit of 512 MB per file.
- Text and document files uploaded to GPTs or ChatGPT conversations are capped at 2,000,000 tokens per file.
- GPT Knowledge supports a limited number of uploaded files, so this bundle is intentionally compressed into one file.

Do not claim an exact public "single conversation limit". ChatGPT website context, message, attachment, and data-analysis limits can vary by plan, model, workspace settings, quota, and system load. Use the conservative output policy below instead of relying on an assumed hidden limit.

This knowledge bundle is far below the known per-file upload limits. The runtime should therefore optimise answer delivery, not knowledge-file count.

## Universal Output Gate

Before every answer, choose one route: `chat`, `word`, or `brief chat + word`.

Use direct chat output when the final student-facing content is small:

- estimated final output is <=4 pages;
- or approximately <=2,500 English words;
- or approximately <=4,500 Chinese characters;
- and the task can remain readable in one ChatGPT answer.

Use Word output by default when the final student-facing content is large:

- estimated final output is >=5 pages;
- or approximately >2,500 English words;
- or approximately >4,500 Chinese characters;
- or the answer needs large tables, many headings, many questions, dense source synthesis, figures, appendices, or repeated examples;
- or the user asks for a complete artifact, full notes, full walkthrough, full essay, full report, full question pack, or final polished submission-style document.

This gate applies to all tasks, including routes whose original names contain `docx`. If the requested result is short, answer in chat unless the user explicitly requests a file. If the requested result is long, create a Word document unless the user explicitly requests chat-only output.

## Page Estimation Rule

Estimate output pages before drafting:

- Essay-style Word page: about 450-600 English words per page.
- Compact revision-note page: about 650-900 English words per page.
- Chinese-heavy output: about 800-1,200 Chinese characters per page.
- Mixed English/Chinese output: use the stricter estimate.

If uncertain, choose Word when the answer may exceed 4 pages. The goal is to prevent truncation, unreadable chat walls, and loss of document structure.

## Source-Size Trigger

Use source page count only as a risk signal. Final output size is the main decision.

- <=15 source pages and <=4 output pages: direct chat is allowed.
- 16-40 source pages: direct chat is allowed only for summaries, plans, narrow explanations, or small question sets; complete study artifacts should be Word unless the estimated final output stays under 4 pages.
- >40 source pages, multiple lectures, multiple PDFs, or multi-module inputs: Word by default for any complete synthesis, notes, walkthrough, essay pack, report, or question bank.
- If the user asks for only a brief diagnosis from a large source pack, direct chat is allowed, but state that the answer is a brief diagnosis rather than full synthesis.

## Route-Specific Defaults

Academic Exam-Ready Notes:

- Small topic note, one concept, or short source excerpt: chat.
- Complete notes, module notes, lecture-pack notes, cross-source synthesis, or anything likely over 4 pages: Word.

Knowledge Walkthrough:

- One short block or one narrow concept: chat.
- Ordered lecture walkthrough, several slides/PDFs, or page-by-page learning guide: Word.

MCQ / Short Answer:

- <=10 questions on one small topic: chat.
- >10 questions, mixed topics, answer-key rationales, diagnostic report, or full practice pack: Word.

Long Answer / Project / Scenario / Practical / Data:

- One compact answer or one small dataset explanation: chat.
- Multi-part scenario, practical report, data-analysis pack, method workflow, project report, or graph/table-heavy output: Word.

Example Essay:

- Thesis, outline, paragraph plan, examiner-fit checklist, or one short model paragraph: chat.
- Complete essay, multi-essay module document, citation-controlled essay, submission-style exemplar, or anything over 4 pages: Word.

Past-Paper / Exam-Format Diagnosis:

- Brief diagnosis, likely question-family list, or short revision priorities: chat.
- Multi-year pattern report, paper-by-paper extraction, full revision plan, or evidence table: Word.

Audit / QA / Skill Maintenance:

- Short pass/fail, issue list, or release note summary: chat.
- Full audit report, source coverage audit, regression report, or change log with evidence: Word.

## Word Response Contract

When generating a Word document, the chat response must stay short:

- state the document was generated;
- give the file name;
- give a 3-6 bullet summary of contents;
- state material evidence limitations if any;
- do not paste the full document body into chat.

If file generation is unavailable in the current ChatGPT session, do not force a long answer into one message. Give a compact structure in chat, then split only when the user explicitly asks for staged chat output. Keep each part under the direct-chat threshold.

## Chat Response Contract

- Start with the answer.
- Do not include internal process traces, source maps, manifests, QA JSON, hidden scoring, or helper artifacts.
- Do not create both a full chat answer and a full Word file for the same large task unless the user explicitly asks.
- If the user asks for chat-only output for a long task, provide a compressed answer and state that completeness is reduced by chat length.

## Word File Formatting

Use Word files for long deliverables because they preserve structure, headings, page layout, and readability.

- Essay-style documents: Arial, 2.5 cm margins, body justified, title centered, subheadings left-aligned, 1.5 line spacing, 0 pt paragraph spacing.
- Ordinary exam-prep notes and walkthroughs: compact revision-note layout, Arial, 2.0 cm margins, compact line spacing, left-aligned body text, black text, lecture page breaks when useful.
- Keep helper artifacts out of the student-facing output unless explicitly requested.

## Conflict Rule

If this ChatGPT Website Adapter conflicts with the underlying Everything Exam Preparation Skill, use this adapter only for output-channel choice and chat/file length control. Use the underlying Skill for evidence rules, routing, factual standards, formatting contracts, and QA requirements.

---

# Everything Exam Preparation Skill Knowledge Bundle

This single file combines the flattened Custom GPT knowledge files. Each section preserves its original source filename.



---

---

---

## Source File: `README.md`

---

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

---

## Source File: `SKILL.md`

---

---
name: everything-exam-preparation
description: Purpose-first, source-adaptive, Word-first exam preparation workflow for lecture slides, notes, practical materials, past papers, extra reading and recommended books.
---

# Everything Exam Preparation

This Skill turns supplied course materials into revision artifacts. It is not a slide archive converter and it is not a fixed-length summariser. It must not force the model to dump extraction fragments, file titles, administrative text, or internal planning fields. The model should read the source set for meaning, reconstruct the examinable knowledge, and explain it clearly at a length proportional to the source pack.

## Core Output

The default public artifact is:

```text
Lecture_Knowledge_Walkthrough.docx
```

Other reports are add-ons. They are generated only after the core knowledge walkthrough is clear.

## Default Workflow

Use `references/exam_prep_core_workflow.md` as the source of truth for ordinary notes.

```text
source pack
-> classify source roles
-> remove non-knowledge noise
-> reconstruct lecture/session order and conceptual modules
-> calculate source-adaptive coverage budget
-> build `PublicLectureNotesPlan`
-> write lecture-first micro-module teaching notes
-> run exam-ready direct prose, module teaching depth and readability layout gates
-> keep exam overlays internal unless separately requested
-> run public-surface, density and layout QA
```

The output should explain what each concept is, why it matters, how the mechanism, method or calculation works, and what result, limitation or interpretation follows.

All student-facing prose must reach exam-ready level. Public notes should not sound like a source-derived teaching summary. They must state the knowledge directly so the student can revise, recall and adapt it in an exam answer. Do not write `The course frames...`, `The source material identifies...`, `The lecture material uses...`, `The source states...`, or equivalent source narration. Rewrite those forms as direct claims about the concept, method, readout, calculation, distinction, consequence or limitation.

## Source Roles

Before drafting, classify material as:

- `subject_knowledge`: definitions, mechanisms, structures, pathways, experiments, methods, calculations, graphs, data patterns, examples, diagnostic rules and limitations.
- `practical_operation`: apparatus, reagents, protocol logic, controls, safety handling, calculations and interpretation rules.
- `exam_pattern`: question form, command verbs, mark operations and repeated discriminators.
- `extra_reading`: verified books, chapters, papers or academic sources that deepen source logic.
- `style_or_layout_example`: reference output used only for structure, density and layout.
- `non_knowledge_noise`: admin, logistics, contact details, attendance systems, URLs, decorative text, OCR debris, file titles and slide artifacts.

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` may become public knowledge prose. Past papers shape emphasis and answer operations only. Cross-unit examples never provide facts for a new target unit.

Use only the sources supplied by the user unless the user explicitly permits verified academic source lookup. Preserve source boundaries between current course material, past papers, extra reading, examples and style/layout references. Treat unsupported points as gaps instead of filling them from memory.

## Noise Filter

Discard these from ordinary public notes:

- lecturer names, emails, phone numbers, office locations, staff lists and coordinator details;
- attendance systems, QR codes, live-session instructions, room or timetable instructions and platform instructions;
- assessment logistics unless the user asks for a separate exam-analysis brief;
- bookshop adverts, library availability, URL-only lines, image credits, copyright lines, acknowledgements and decorative quotations;
- slide agendas, contents pages, generic learning outcomes and generic advice unless rewritten into a specific knowledge claim;
- raw slide bullets, file-title lists, broken OCR fragments, font names, page artifacts and extraction debris.

Default public notes must not show a `Course Knowledge Map`, source role summary, extraction limitation, strategy section, prediction section, or file inventory. Those objects are internal planning aids only.

## Route Table

| User request | Route | Public output |
| --- | --- | --- |
| revise / make notes / go through lectures / general preparation / analyse this course | `exam_prep_notes_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| explicitly source-order walkthrough | `knowledge_walkthrough_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| MCQ / single-best-answer | `mcq_exam_prep` | core walkthrough plus MCQ add-on |
| short answer | `short_answer_exam_prep` | core walkthrough plus short-answer add-on |
| long answer / project / scenario / practical / data / calculation | `long_answer_project_scenario_prep` | core walkthrough plus long-answer/data add-on |
| essay preparation / full essay-style answers | `essay_exam_prep` | core walkthrough plus essay add-on |
| source inventory / lint / release check / information profile only | `audit_lint_only` or `github_ready_qa` | QA result only |
| past-paper pattern or exam format only | `exam_analysis_brief` | chat-only brief unless a report is requested |

Prediction, study strategy, Section A/Section B strategy and answer-advice language are never part of ordinary notes or walkthroughs. If the user asks for prediction or exam format analysis, produce it as a separate chat/report add-on after the knowledge document.

## Course Reconstruction

For ordinary notes and walkthroughs, render one shared public plan:

```yaml
PublicLectureNotesPlan:
  title:
  target_group_key:
  source_scale_budget:
  output_language_profile:
    output_language: English
    allow_bilingual: false
  route_docx_style_profile:
    route: exam_prep_notes_docx | knowledge_walkthrough_docx
    margin_cm: 2.0
    line_spacing: 1.05-1.15
    body_alignment: left
  public_lecture_sections:
    - lecture_title:
      lecture_scope:
      modules:
        - module_title:
          knowledge_functions:
            - definition_boundary | mechanism_process | method_readout | graph_data_interpretation | calculation_unit_worked_example | named_example | limitation_trap
          explanation:
          blocks:
            - block_type:
              label:
              content:
```

Preserve official lecture/session order when it explains prerequisites. Do not dump slide order or file names. Inside each lecture, group material into concept-specific modules. Each public module must have at least two knowledge functions so it teaches definition or boundary plus mechanism, method, readout, calculation, example or limitation.

Use micro-module grouping. A lecture heading may stay broad, but module headings should name the exact examinable operation, distinction or mechanism. Prefer `Initial slope gives initial reaction rate` over `Enzyme kinetics`, and `Dimension-aware substitution prevents concentration errors` over `Calculation`. If a module still contains several separable operations, split it.

## Source-Adaptive Coverage Budget

Never use the same small output size for every course. The amount of public knowledge must scale with the amount of examinable source material.

The reference-quality target is the supplied Experimental Biology style of output: topic-specific headings, dense connected explanations, formulas or worked examples when useful, black Arial text, 2.0 cm margins, compact 1.05-1.15 spacing and left-aligned body/headings. Use that file only as a style, density and layout exemplar; it is not factual evidence and it is not a length cap.

When the user says `analyse this course`, `分析这门课`, or asks for course-level prep analysis without explicitly requesting an audit-only file, produce the core knowledge walkthrough. Do not satisfy that request with a short metrics report, source profile summary, or sample-only file. If an audit/profile file is also useful, it is an add-on and must not replace the knowledge document.

Before drafting, create:

```yaml
SourceScaleBudget:
  source_units_count:
  source_pages_or_slides_estimate:
  source_information_profile_status: measured | estimated | missing | not_applicable
  informative_page_count:
  non_informative_page_count:
  information_mass_units:
  average_information_score:
  page_information_profile:
    - source_id:
      page_index:
      category: knowledge_dense | knowledge_standard | light_context | cover | lecture_plan_or_admin | video_or_media_placeholder | blank
      informative: true | false
      information_score:
      exclusion_reason:
  source_types:
  conceptual_module_target_range:
  examinable_unit_target_range:
  target_public_units_min:
  target_words_min:
  minimum_visible_coverage_floor:
  compression_reason:
  coverage_floor_status: pass | warn | block
```

Rules:

- A broad course pack must not be compressed to the size of a short practical or mock paper.
- Before budgeting, inspect every slide/page for information. Exclude covers, title-only pages, lecture plans, reading/admin pages, pure video/media placeholders and blank pages from `informative_page_count`, but record them in `page_information_profile` with an exclusion reason.
- Quantify each informative slide/page. Use higher scores for dense mechanism text, definitions, equations, diagrams, tables, graph logic, calculations, method workflows, named examples, speaker-note detail and source-backed explanations. Use low scores for light context.
- When `source_information_profile_status` is `measured` or `estimated`, derive the public size from `informative_page_count` and `information_mass_units`. Raw slide/page count is then audit context, not the main length driver.
- Keep a small number of conceptual modules when useful, but include enough examinable units inside each module to cover the source scale.
- A pack with many lectures, figures, practicals, calculations or mechanisms requires expanded coverage.
- Do not use Experimental Biology or any other short unit as a size cap for larger courses.
- `source_pages_or_slides_estimate` is a hard sizing input, not a comment. When the source has hundreds of slides/pages, the public DOCX must become a whole-course notebook or multiple volumes, not a 5k-word overview.
- Use these minimum internal floors unless the source is demonstrably sparse or unreadable and the exclusion ledger proves it:
  - 1-10 pages/slides: at least 8 public units and about 420 visible words.
  - 11-80 pages/slides: at least 12-25 public units and 1k-3k visible words.
  - 81-200 pages/slides: at least 50 public units and about 5.8k visible words, matching the Experimental Biology density scale.
  - 201-500 pages/slides: at least 105 public units and about 14k visible words.
  - 501-800 pages/slides: at least 150 public units and about 20k visible words.
  - 801+ pages/slides: at least 180 public units and about 25k visible words, or split into multiple deliverable volumes.
- `information_mass_units` can raise the floor above the coarse page bands when many pages are dense. Use `scripts/source_information_profiler.py` and `scripts/source_scale_budget_linter.py` as the local reference implementation.
- If a reference-quality DOCX such as Experimental Biology is supplied, run reference-density calibration. A course-analysis or walkthrough DOCX for a larger source pack must exceed the reference in visible knowledge prose unless the information profile proves the source pack is smaller or sparse. A 500-1000 word course-analysis file for a broad source pack is a failure even if it contains correct metrics.
- If `target_public_units_min` or `target_words_min` is below the derived source-scale floor, the budget is invalid even if the draft is polished.
- If the first draft feels like a route summary, file inventory, checklist, or brief overview, it is not acceptable. Regenerate from the source-distillation pass until the public document teaches the examinable mechanisms, calculations, methods, examples, boundaries and interpretations in connected prose.
- If the public output falls below the source-scale floor, block the run and regenerate from source distillation instead of releasing a short file.

## Public Lecture Modules

Write public content as coherent lecture-first modules:

```yaml
PublicLectureModule:
  module_title:
  knowledge_functions:
  explanation:
  blocks:
```

The visible module is a topic-specific heading followed by connected explanatory prose. A valid module explains what the point is, why it matters, how the mechanism, method, readout or calculation works, and what interpretation, limitation or boundary follows. Bullets are allowed only after an explanatory lead sentence and only for naturally parallel items.

Module teaching depth is a release gate. A public module is not enough if it only announces that a topic exists. It must include at least one direct identity or boundary claim and at least one teaching operation:

- definition or boundary: what the concept is and what it excludes;
- mechanism or process: how the change happens and why the order matters;
- method or readout: what is measured, controlled and interpreted;
- graph or data interpretation: axes, pattern, inference and boundary;
- calculation: equation, units, substitution logic and interpretation;
- named example: what the example demonstrates, not only that it exists;
- limitation or trap: what false reading, overclaim or common error it prevents.

Readability layout is also a release gate. Use short explanatory paragraphs, micro-headings, separated equations, worked examples, comparison blocks and list blocks when they reduce cognitive load. Do not compress criteria lists, formulas, graph-reading rules or workflows into one dense paragraph. Keep visuals near the relevant module only when a source-backed diagram, graph, table or workflow materially improves understanding.

Do not write notes as:

```text
Definition: ...
Components: ...
Workflow: ...
Logic: ...
Interpretation: ...
```

## Public DOCX Surface

For ordinary notes and walkthroughs:

- body text, titles, lecture headings and subheadings are left aligned;
- images are centered;
- default text line spacing is compact, 1.05-1.15;
- text is black Arial in a readable size;
- theme colours, blue heading styles and non-black visible text are forbidden unless the user explicitly asks for colour;
- images are scaled to the content area while preserving aspect ratio and readability;
- large blank areas should be reduced by fitting images to context and avoiding unnecessary page breaks.

Public notes must not contain source-route narration, AI-process text, source maps, QA flags, evidence scores, confidence bands, internal manifests, helper JSON or raw extraction text.

Public notes must also not contain visible workflow explanations such as selected route, workflow plan, source role map, source scale budget, coverage floor status, KnowledgeSurfaceContract, ExaminableKnowledgeUnit, CourseModule, QA gate, generation process, or statements about what the Skill did. Keep those objects internal and render only the resulting lecture-first knowledge.

## Final Output Revision Contract

When the user gives iterative edits to an output file, the latest compatible edit set is a hard release contract. Do not release a DOCX that satisfies the first request but violates later file-level requirements.

For revised notes and walkthrough DOCX files:

- do not overcompress: if the user gives a target length or character range, keep the final public text inside that range unless source protection makes it unsafe;
- improve expression efficiency by removing repetition, merging duplicate explanations, tightening causal order and keeping formulas, worked examples, method logic, controls, interpretation rules and limitations;
- delete intro-only sections that introduce a topic without explaining examinable logic, unless they can be rewritten into a specific knowledge unit;
- if the user asks for bilingual or Chinese-facing notes with academic English support, put academic terms in English at first meaningful use and use English for formula labels, calculation labels, table labels and text before colon-style labels;
- formulas, variables, units and worked calculation labels should be in English unless the user explicitly requests another language;
- if revising from an existing DOCX and the user says not to change images, preserve image objects, order, sizing and placement as far as the document format allows;
- if the user asks to remove sentence-ending full stops, remove Chinese full stops and sentence-final periods from body text while preserving decimal points, formula notation, file names and necessary scientific abbreviations;
- render the final DOCX to PDF or page images when tooling is available and inspect for missing images, row splits, unreadable tables, large blank areas, colour drift and visible formatting defects before release.

## Required References

- `references/exam_prep_core_workflow.md`
- `references/knowledge_surface_protocol.md`
- `references/protected_source_coverage_protocol.md`
- `references/scientific_precision_protocol.md`
- `references/student_facing_output_policy.md`
- `references/exam_prep_notes_protocol.md`
- `references/knowledge_walkthrough_docx_protocol.md`
- `references/question_type_protocol.md`
- `references/practical_data_problem_protocol.md`
- `references/essay_generation_protocol.md`
- `references/example_essay_docx_output_protocol.md`
- `references/input_processing_protocol.md`
- `references/evidence_policy.md`
- `references/github_release_protocol.md`

## QA Gate

Fail and rewrite if the public output contains:

- admin, logistics, staff, contact or attendance material;
- Course Knowledge Map, Source Role Summary, Source Scope, Extraction Limitation, Examinable Knowledge Units, Predicted Essay Theme, Study Order, Section A Strategy, Section B Strategy, How To Answer, A strong answer should, or Use This Module;
- source narration such as `The course frames`, `The lecture states`, `The source material identifies`, `The source states`, or `The lecture material uses`;
- inventory-only prose that lists concepts without explaining what each one means, does, measures, proves or limits;
- broad lecture-theme modules where smaller micro-module headings would make the knowledge usable;
- examples that do not state what they demonstrate;
- formulas, graph rules, criteria lists or workflows buried inside long prose;
- file-title maps or source inventories;
- raw slide bullets or broken OCR fragments;
- copied extraction text instead of explanation;
- dense lists of names without mechanisms;
- repeated `Definition`, `Components`, `Workflow`, `Logic`, `Graph logic` or equivalent labels;
- shorthand arrow chains used as the main explanation;
- a broad source pack compressed below the source-adaptive coverage floor;
- unsupported claims, fake citations or over-strong scientific claims;
- unbound protected source units;
- public AI-process text, source anchors, QA JSON, manifests or lineage files;
- non-black visible text, theme-colour headings, non-Arial text, wrong alignment, justified ordinary-note body text, or non-compact line spacing.

Targeted checks:

```bash
python3 scripts/no_identity_trigger_linter.py --forbid-legacy-label
python3 scripts/validate_workflow_planning_contract.py
python3 scripts/validate_interaction_contract.py
python3 scripts/validate_student_output_contract.py
python3 scripts/public_lecture_notes_renderer.py --self-test
python3 scripts/notes_exam_ready_language_linter.py --self-test
python3 scripts/module_teaching_depth_linter.py --self-test
python3 scripts/notes_readability_layout_linter.py --self-test
python3 scripts/source_information_profiler.py --self-test
python3 scripts/zero_mention_lint.py --self-test
python3 scripts/reference_density_linter.py --self-test
python3 scripts/knowledge_surface_linter.py --self-test
python3 scripts/scientific_precision_linter.py --self-test
python3 scripts/github_ready_check.py --ci
```

---

## Source File: `agents__openai.yaml`

---

interface:
  display_name: "Everything Exam Preparation"
  short_description: "Evidence-grounded exam-prep workflow with lecture-first public notes, question-type DOCX add-on routes, and explicit Skill maintenance checks"
  default_prompt: "Use $everything-exam-preparation to turn my lecture slides, official notes, ordered course notes, past papers, practical materials, answer keys, exemplars, feedback, and readings into the narrowest valid exam-prep route. Build a SkillConfig, create a WorkflowPlan, check input readiness, and by default generate English lecture-first knowledge notes in Lecture_Knowledge_Walkthrough.docx. If I ask for MCQ, Short Answer, Long Answer/Project/Scenario, or Essay preparation, add the matching DOCX report after the base notes. Use past-paper analysis as a chat-only brief before file generation. Keep helper artifacts separate unless I ask for an audit package. If I ask to check, doctor, update, validate, refresh, or release the Skill package, run the explicit maintenance route first."

policy:
  allow_implicit_invocation: true

---

## Source File: `agents__presets.yaml`

---

presets:
  source_inventory_only:
    purpose: "Classify supplied or discovered files before deeper analysis."
    required_source_classes: ["any_source"]
    modules: ["source_inventory"]
    student_outputs: ["source coverage card"]
  exam_format_diagnosis:
    purpose: "Extract exam structure, sections, rules, question types, and route recommendation."
    required_source_classes: ["formal_past_papers"]
    modules: ["source_inventory", "exam_regime", "question_type"]
    student_outputs: ["exam format diagnosis"]
  exam_prep_notes_docx:
    purpose: "Build default English lecture-first public knowledge notes from official course sources, with optional question-type add-ons kept separate."
    required_source_classes: ["readable_course_notes"]
    recommended_source_classes: ["formal_past_papers", "practical_materials", "extra_reading"]
    modules: ["source_inventory", "fragment_index", "lecture_session_mapping", "lecture_concept_module_extraction", "knowledge_points", "source_baseline_notes_plan", "baseline_coverage_floor_qa", "knowledge_only_student_view_filter", "public_output_point_build", "exam_prep_notes_plan", "question_type_addon_generation", "visual_aid_planning", "visual_aid_generation_optional", "exam_prep_notes_docx_generation", "exam_prep_docx_style_linter", "exam_prep_notes_linter", "deliverable_qa"]
    student_outputs: ["Lecture Knowledge Walkthrough DOCX"]
  knowledge_walkthrough_docx:
    purpose: "Compatibility route for an explicitly lecture-first Word walkthrough that explains each lecture through AI-inferred conceptual modules."
    required_source_classes: ["lecture_or_official_notes"]
    recommended_source_classes: ["formal_past_papers", "practical_materials", "extra_reading"]
    modules: ["source_inventory", "fragment_index", "lecture_module_extraction", "knowledge_walkthrough_plan", "knowledge_walkthrough_docx_generation", "deliverable_qa"]
    student_outputs: ["Lecture Knowledge Walkthrough DOCX"]
  mcq_exam_prep:
    purpose: "Generate the default Academic Exam-Ready Notes artifact plus an MCQ point-card report."
    required_source_classes: ["lecture_or_official_notes"]
    recommended_source_classes: ["formal_past_papers", "answer_keys"]
    modules: ["source_inventory", "fragment_index", "course_section_reconstruction", "lecture_session_mapping", "lecture_concept_module_extraction", "knowledge_points", "atomic_knowledge_ledger", "source_baseline_notes_plan", "baseline_coverage_floor_qa", "exam_emphasis_profile", "exam_overlay_pass", "overlay_did_not_damage_coverage_qa", "knowledge_only_student_view_filter", "exam_prep_notes_plan", "question_type_addon_generation", "visual_aid_planning", "visual_aid_generation_optional", "exam_prep_notes_docx_generation", "exam_prep_docx_style_linter", "exam_prep_notes_linter", "mcq_policy", "mcq_exam_report_docx", "deliverable_qa"]
    student_outputs: ["Lecture Knowledge Walkthrough DOCX", "MCQ Exam Analysis Report DOCX"]
  short_answer_exam_prep:
    purpose: "Generate the default Academic Exam-Ready Notes artifact plus a short-answer report with highlighted Example Answers."
    required_source_classes: ["lecture_or_official_notes"]
    recommended_source_classes: ["formal_past_papers", "answer_keys"]
    modules: ["source_inventory", "fragment_index", "course_section_reconstruction", "lecture_session_mapping", "lecture_concept_module_extraction", "knowledge_points", "atomic_knowledge_ledger", "source_baseline_notes_plan", "baseline_coverage_floor_qa", "exam_emphasis_profile", "exam_overlay_pass", "overlay_did_not_damage_coverage_qa", "knowledge_only_student_view_filter", "exam_prep_notes_plan", "question_type_addon_generation", "visual_aid_planning", "visual_aid_generation_optional", "exam_prep_notes_docx_generation", "exam_prep_docx_style_linter", "exam_prep_notes_linter", "short_answer_variants", "short_answer_exam_report_docx", "deliverable_qa"]
    student_outputs: ["Lecture Knowledge Walkthrough DOCX", "Short Answer Exam Analysis Report DOCX"]
  long_answer_project_scenario_prep:
    purpose: "Generate the default Academic Exam-Ready Notes artifact plus a long-answer/project/scenario report with analysis and Example Answer."
    required_source_classes: ["lecture_or_official_notes"]
    recommended_source_classes: ["practical_materials", "exemplars_or_feedback"]
    modules: ["source_inventory", "fragment_index", "course_section_reconstruction", "lecture_session_mapping", "lecture_concept_module_extraction", "knowledge_points", "atomic_knowledge_ledger", "source_baseline_notes_plan", "baseline_coverage_floor_qa", "exam_emphasis_profile", "exam_overlay_pass", "overlay_did_not_damage_coverage_qa", "knowledge_only_student_view_filter", "exam_prep_notes_plan", "question_type_addon_generation", "visual_aid_planning", "visual_aid_generation_optional", "exam_prep_notes_docx_generation", "exam_prep_docx_style_linter", "exam_prep_notes_linter", "method_blocks", "long_answer_project_report_docx", "deliverable_qa"]
    student_outputs: ["Lecture Knowledge Walkthrough DOCX", "Long Answer Project Scenario Report DOCX"]
  essay_exam_prep:
    purpose: "Generate the default Academic Exam-Ready Notes artifact plus module-level Example Essays for essay exams."
    required_source_classes: ["lecture_or_official_notes"]
    recommended_source_classes: ["formal_past_papers", "extra_reading", "exemplars_or_feedback"]
    modules: ["source_inventory", "fragment_index", "course_section_reconstruction", "lecture_session_mapping", "lecture_concept_module_extraction", "knowledge_points", "atomic_knowledge_ledger", "source_baseline_notes_plan", "baseline_coverage_floor_qa", "exam_emphasis_profile", "exam_overlay_pass", "overlay_did_not_damage_coverage_qa", "knowledge_only_student_view_filter", "exam_prep_notes_plan", "question_type_addon_generation", "visual_aid_planning", "visual_aid_generation_optional", "exam_prep_notes_docx_generation", "exam_prep_docx_style_linter", "exam_prep_notes_linter", "essay_coverage_plan", "citation_resolution", "essay_module_example_essays_docx", "deliverable_qa"]
    student_outputs: ["Lecture Knowledge Walkthrough DOCX", "Essay Module Example Essays DOCX"]
  audit_lint_only:
    purpose: "Run source, workflow, language, deliverable, or release checks without generating new student outputs."
    required_source_classes: []
    modules: ["audit"]
    student_outputs: ["QA report"]
  github_ready_qa:
    purpose: "Run repository release checks before sync, commit, and push."
    required_source_classes: []
    modules: ["repository_qa"]
    student_outputs: ["GitHub-ready QA result"]

---

## Source File: `agents__prompt_cards.yaml`

---

prompt_cards:
  - card_id: "source_inventory"
    preset: "source_inventory_only"
    purpose: "Classify files, evidence use, extraction status, and missing source classes."
    minimum_inputs: ["at least one supplied source path or discovered academic source"]
    output_contract:
      - "Return source roles and evidence-use limits."
      - "Do not infer hidden content from unreadable or unsupported files."
    hard_stops:
      - "No supplied or discoverable sources."
  - card_id: "exam_prep_notes_docx"
    preset: "exam_prep_notes_docx"
    purpose: "Build source-first Academic Exam-Ready Notes for general revision."
    minimum_inputs: ["readable_course_notes"]
    output_contract:
      - "Generate Lecture_Knowledge_Walkthrough.docx as the compatible public artifact."
      - "Accept readable ordered course notes, but use only official or verified sources for factual claims."
      - "Build an atomic knowledge ledger and baseline coverage floor before using past papers."
      - "Use past papers for overlay emphasis only when supplied; do not invent exam frequency."
      - "Keep the public DOCX lecture-first and knowledge-only; do not render Course Knowledge Map, source summaries, strategy, or prediction text."
      - "Append question-type add-ons only after the base notes."
      - "Generated visual aids are optional revision schematics, not evidence."
    hard_stops:
      - "No lecture slides, official notes, or verified course notes."
      - "Blocking evidence or student-output QA flag."
  - card_id: "mcq_exam_prep"
    preset: "mcq_exam_prep"
    purpose: "Build Academic Exam-Ready Notes plus a student-facing MCQ point-card report."
    minimum_inputs: ["lecture_or_official_notes"]
    output_contract:
      - "Generate Academic Exam-Ready Notes as the foundation."
      - "Generate MCQ Exam Analysis Report DOCX using point cards only."
      - "Do not expose source anchors, confidence, discriminator axes, answer keys, practice questions, or contrast tables."
    hard_stops:
      - "No lecture slides or official notes."
      - "Blocking workflow or language QA flag."
  - card_id: "knowledge_walkthrough_docx"
    preset: "knowledge_walkthrough_docx"
    purpose: "Build a compatibility lecture-first Word walkthrough for revising lecture knowledge in source order."
    minimum_inputs: ["lecture_or_official_notes"]
    output_contract:
      - "Preserve lecture order."
      - "Split each lecture into conceptual modules, not slide/page summaries."
      - "Use the shared PublicLectureNotesPlan with public_lecture_sections and module-level knowledge_functions."
      - "Do not show source anchors, confidence, recurrence, examiner operations, essay plans, practice questions, or answer keys."
    hard_stops:
      - "No lecture slides or official notes."
  - card_id: "short_answer_exam_prep"
    preset: "short_answer_exam_prep"
    purpose: "Build Academic Exam-Ready Notes plus short-answer point cards and Example Answers."
    minimum_inputs: ["lecture_or_official_notes"]
    output_contract:
      - "Generate Academic Exam-Ready Notes as the foundation."
      - "Generate module logic, point cards, highlighted keywords, and Example Answers."
      - "Do not expose mark-producing schema, source anchors, confidence, task verbs, or reference expansion."
    hard_stops:
      - "No lecture slides or official notes."
  - card_id: "long_answer_project_scenario_prep"
    preset: "long_answer_project_scenario_prep"
    purpose: "Build Academic Exam-Ready Notes plus a long-answer/project/scenario report with analysis and Example Answer."
    minimum_inputs: ["lecture_or_official_notes"]
    output_contract:
      - "Generate Academic Exam-Ready Notes as the foundation."
      - "Generate question analysis, answer order, reusable answer blocks, Example Answer, and adaptation notes."
      - "Do not expose evidence rationale, confidence, recurrence, or source anchors."
    hard_stops:
      - "No lecture slides or official notes."
  - card_id: "essay_exam_prep"
    preset: "essay_exam_prep"
    purpose: "Produce module-level Example Essays from verified source logic for essay exams."
    minimum_inputs: ["lecture_or_official_notes"]
    output_contract:
      - "Generate Academic Exam-Ready Notes as the foundation."
      - "Generate module-level big Example Essays with adaptation maps and paragraph banks."
      - "Verify citations or use an explicit classic-study fallback plan."
      - "Run DOCX formatting and language lint before delivery."
    hard_stops:
      - "No lecture or official content."
      - "Unverified citation used as factual support."
  - card_id: "audit_lint_only"
    preset: "audit_lint_only"
    purpose: "Run checks and report blockers without creating new student outputs."
    minimum_inputs: []
    output_contract:
      - "Return pass/fail checks and blocking reasons."
      - "Do not generate or publish new study artifacts."
    hard_stops: []

---

## Source File: `agents__setup_wizard.yaml`

---

wizard:
  sections:
    - id: "project"
      label: "Project"
      fields: ["course_name", "module_code", "target_group_key", "exam_year", "output_folder"]
    - id: "source_inputs"
      label: "Source Inputs"
      fields:
        - "lecture_slides"
        - "official_notes"
        - "course_notes"
        - "student_notes"
        - "ai_generated_notes"
        - "formal_past_papers"
        - "practical_materials"
        - "mocks_quizzes_answer_keys"
        - "exemplars_or_feedback"
        - "extra_reading_books_or_papers"
    - id: "output_mode"
      label: "Output Mode"
      fields: ["preset", "include_audit_package", "student_visible_only"]
    - id: "evidence_policy"
      label: "Evidence Policy"
      fields:
        - "allow_online_academic_search"
        - "allow_extra_reading_enrichment"
        - "require_verified_citations"
        - "treat_examples_as_style_only"
    - id: "qa"
      label: "QA Gates"
      fields:
        - "strict_publish_gate"
        - "require_lineage"
        - "run_language_lint"
        - "run_workflow_validator"
        - "fail_on_blocking_flags"
    - id: "plan_preview"
      label: "Plan Preview"
      fields: ["actions", "skipped_modules", "blockers", "publish_gate"]
    - id: "run_status"
      label: "Run Status"
      fields: ["current_action", "completed_actions", "blocked_actions"]
    - id: "outputs"
      label: "Outputs"
      fields: ["student_outputs", "internal_qa_outputs", "audit_package"]

---

## Source File: `benchmarks__cross_subject_regression_suite.json`

---

{
  "suite_name": "cross_subject_regression_suite",
  "purpose": "Validate generic Skill behaviour across target-group separation, exam-regime split, question-type routing, KP granularity, lecture-order coverage, and visual Excel adaptation.",
  "hard_rule": "Benchmark target groups are never pooled for content prediction.",
  "target_groups": [
    {
      "target_group_key": "Benchmark_RegimeShift_VisualWorkbook",
      "lecture_source_examples": [
        "examples/private_sources/regime_shift_visual_workbook.pdf"
      ],
      "past_paper_glob": "regime_shift_visual_workbook*",
      "expected_behaviour": [
        "answer-one essay exam",
        "lecture-order slide coverage",
        "source images aligned with essay-style explanation",
        "predicted essay theme in far-right area"
      ],
      "must_not": [
        "use old answer-all short-answer papers as direct current essay blueprint",
        "pool content from another benchmark group"
      ],
      "generic_contribution": "Validates exam-regime split when older answer-all short-answer/problem papers differ from recent answer-one essay/problem-essay papers, and validates source-aligned visual workbook output.",
      "transferable_rules": [
        "Compare answer rules, section structure, timing, mark weighting, and question families across years before pooling past-paper evidence.",
        "Use old structurally different papers for coverage or answer-schema evidence only, not as current blueprint prediction evidence.",
        "For visually taught slide-based courses, preserve lecture order and align locator, original source image, explanation, and exam-facing preparation output."
      ],
      "future_target_diagnostic_questions": [
        "Did the answer rule change from answer-all to answer-one?",
        "Did the dominant question type change across years?",
        "Are old papers useful for coverage but unsafe for current blueprint prediction?",
        "Does the target source set need visual source-image alignment to make the explanation usable?"
      ],
      "non_transferable_content": [
        "benchmark-specific topics",
        "named examples",
        "year-specific recurrence claims"
      ],
      "workflow_steps_tested": [
        "target_grouping_regime_split",
        "exam_format_diagnosis",
        "archetype_mapping",
        "past_paper_statistics",
        "pattern_detection",
        "question_type_outputs",
        "excel_generation",
        "cross_subject_regression"
      ],
      "anti_patterns_guarded_against": [
        "using old short-answer papers as direct current essay blueprint",
        "treating topic recurrence as more important than exam-format comparability",
        "outputting a non-visual evidence-heavy workbook instead of the requested visual student workbook"
      ]
    },
    {
      "target_group_key": "Benchmark_MechanismEvidence_Essay",
      "lecture_source_examples": [
        "examples/private_sources/mechanism_evidence_essay.pptx"
      ],
      "past_paper_glob": "mechanism_evidence_essay*",
      "expected_regimes": [
        {
          "name": "old_section_a_answer_all_plus_section_b_essay",
          "years": ["2015", "2016", "2017"],
          "format": "short conceptual section plus major essay section",
          "evidence_use": "concept_and_short_answer_schema_only"
        },
        {
          "name": "current_short_conceptual_plus_major_essay",
          "years": ["2023", "2024", "2025"],
          "format": "current paper requires separate short-concept and major-essay preparation",
          "evidence_use": "current_blueprint"
        }
      ],
      "required_archetypes": [
        "mechanism plus experimental evidence",
        "gain/loss or perturbation inference",
        "model-system comparison",
        "pathway or process explanation",
        "conservation or transferability across systems",
        "hypothesis-testing experiment design"
      ],
      "must_not": [
        "ignore short conceptual section",
        "treat old and current papers as one stable format",
        "split one mechanism/evidence block into isolated slide fragments",
        "infer lecture deck year from reference years inside slide text",
        "silently resolve conflicts between lecture-deck guidance and formal-paper format"
      ],
      "generic_contribution": "Validates mechanism-heavy KP construction, section routing, and evidence-based essay planning where mechanisms must be tied to experiments and consequences.",
      "transferable_rules": [
        "For mechanism-heavy source sets, build knowledge points around mechanism -> evidence/experiment -> consequence rather than slide count.",
        "When current papers contain sections with different answer styles, separate prep logic by section.",
        "Use old answer-all short-question papers as coverage and mark-schema evidence when recent papers use a different major-answer format.",
        "Predict examiner operations such as evidence interpretation, causal mechanism, comparison, or experimental inference rather than topic labels alone."
      ],
      "future_target_diagnostic_questions": [
        "Does the target source set require experimental evidence to support mechanism claims?",
        "Are short conceptual prompts and major essay prompts mixed in the current paper?",
        "Are older papers structurally different from current papers?",
        "Should a KP be split because it contains several mechanisms, or merged because one mechanism spans several slides?"
      ],
      "non_transferable_content": [
        "benchmark-specific pathways",
        "named organisms or systems",
        "named examples",
        "topic recurrence claims"
      ],
      "workflow_steps_tested": [
        "target_grouping_regime_split",
        "question_type_gate",
        "exam_format_diagnosis",
        "knowledge_point_optimisation",
        "archetype_mapping",
        "question_type_outputs",
        "example_essay_mode",
        "cross_subject_regression"
      ],
      "anti_patterns_guarded_against": [
        "splitting one mechanism/evidence block into isolated slide fragments",
        "merging a whole topic area into one huge KP",
        "treating sections with different answer modes as the same question type",
        "using old-regime answer-all questions as current blueprint evidence"
      ]
    },
    {
      "target_group_key": "Benchmark_MixedEssay_DataProblem",
      "lecture_source_examples": [
        "examples/private_sources/mixed_essay_data_problem.pptx"
      ],
      "past_paper_glob": "mixed_essay_data_problem*",
      "expected_regimes": [
        {
          "name": "old_essay_only",
          "years": ["2016", "2019"],
          "format": "essay-only paper",
          "evidence_use": "old_regime_coverage_only"
        },
        {
          "name": "current_mini_essay_plus_problem_data",
          "years": ["2024", "2025"],
          "format": "current paper contains mini-essay and data/problem sections",
          "evidence_use": "current_blueprint"
        }
      ],
      "required_archetypes": [
        "mini-essay",
        "problem/data interpretation",
        "phenotype or output inference",
        "graph or table interpretation",
        "intervention data interpretation",
        "experimental design",
        "mechanism-to-application reasoning"
      ],
      "must_not": [
        "treat as pure essay",
        "ignore data/problem questions",
        "output only topic labels",
        "apply one year's word limit to later years without evidence",
        "invent graph values from image-only figures",
        "treat exam-only names as lecture-confirmed KPs without source verification"
      ],
      "generic_contribution": "Validates mixed-format routing where a current paper contains both mini-essay and data/problem sections.",
      "transferable_rules": [
        "Do not treat mixed-format papers as pure essay source sets.",
        "Data/problem sections require graph-reading, phenotype/output inference, mechanism inference, limitation, and follow-up-test archetypes.",
        "If figures, graphs, or tables are image-only, flag visual inspection before claiming exact values.",
        "Adapt the workbook prediction area by detected question type, not by target-group name."
      ],
      "future_target_diagnostic_questions": [
        "Does the current paper contain both essay and data/problem sections?",
        "Does one section require interpretation of figures, graphs, tables, outputs, or experimental conditions?",
        "Are exact data values visible in extracted text, or only in images?",
        "Should the far-right workbook area show data-operation logic instead of essay prompts?"
      ],
      "non_transferable_content": [
        "benchmark-specific variables",
        "named examples",
        "specific topic recurrence claims"
      ],
      "workflow_steps_tested": [
        "question_type_gate",
        "exam_format_diagnosis",
        "archetype_mapping",
        "question_type_outputs",
        "excel_generation",
        "qa",
        "cross_subject_regression"
      ],
      "anti_patterns_guarded_against": [
        "treating a mixed mini-essay plus data/problem paper as pure essay",
        "outputting only topic names without data-operation logic",
        "inventing graph values from image-only figures",
        "applying one year's word limit to later years without evidence"
      ]
    },
    {
      "target_group_key": "Benchmark_ProcessChain_Scenario",
      "lecture_source_examples": [
        "examples/private_sources/process_chain_scenario.pptx"
      ],
      "past_paper_glob": "process_chain_scenario*",
      "expected_regimes": [
        {
          "name": "old_answer_all_short_answer",
          "years": ["2016", "2017", "2018"],
          "format": "answer-all concise responses",
          "evidence_use": "concept_and_short_answer_schema_only"
        },
        {
          "name": "current_answer_one_major_response",
          "years": ["2023", "2024", "2025"],
          "format": "current paper requires major answer or split major-answer section",
          "evidence_use": "current_split_blueprint"
        }
      ],
      "required_archetypes": [
        "process chain",
        "scenario response",
        "actor/component comparison",
        "clinical, applied, or real-world explanation",
        "defect-to-output reasoning",
        "recognition or decision-step contrast"
      ],
      "must_not": [
        "pool old short-answer papers with current major-answer blueprint",
        "output isolated vocabulary instead of process chains",
        "ignore scenario structure",
        "invent missing paper sections",
        "invent the exact transition year between old and recent regimes"
      ],
      "generic_contribution": "Validates regime-shift handling where old concise answer-all papers coexist with newer major-answer papers, and validates process-chain KP segmentation.",
      "transferable_rules": [
        "Separate old short-answer papers from current essay or major-answer blueprint evidence when the paper structure differs.",
        "Build process-heavy KPs as stimulus/input -> actors/components -> signals/rules -> location/context -> mechanism -> outcome -> application.",
        "Use old papers for definitions, concise schemas, examples, and coverage when current paper structure differs.",
        "Flag missing paper sections instead of inventing missing stems or answer keys."
      ],
      "future_target_diagnostic_questions": [
        "Is there a gap between old short-answer format and recent essay or major-answer format?",
        "Do KPs need to be process chains rather than isolated terms?",
        "Do questions rotate scenario contexts while preserving the same examiner operation?",
        "Is any referenced paper section missing from the supplied sources?"
      ],
      "non_transferable_content": [
        "benchmark-specific actors",
        "named examples",
        "specific scenario content",
        "topic recurrence claims"
      ],
      "workflow_steps_tested": [
        "target_grouping_regime_split",
        "question_type_gate",
        "exam_format_diagnosis",
        "knowledge_point_optimisation",
        "past_paper_statistics",
        "pattern_detection",
        "question_type_outputs",
        "qa",
        "cross_subject_regression"
      ],
      "anti_patterns_guarded_against": [
        "pooling old short-answer papers with current major-answer blueprint",
        "outputting isolated vocabulary instead of process-chain explanations",
        "inventing missing paper sections",
        "inventing the exact transition year between regimes"
      ]
    }
  ]
}

---

## Source File: `benchmarks__example_essay_language_linter_fixtures.json`

---

{
  "suite_name": "example_essay_language_linter_fixtures",
  "purpose": "Validate complete Example Essay language quality against the shared language contract.",
  "cases": [
    {
      "id": "metacommentary_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "This essay will discuss how measurement reliability works. It will first explain bias and then explain random error before considering examples."
    },
    {
      "id": "source_trace_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Slides 4-6 should be read as the main paragraph. Slide 4 first establishes the reliability problem, then Slide 5 develops calibration and Slide 6 closes with replication."
    },
    {
      "id": "lecture_route_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "The lecture establishes spinal timing and the next module adds brainstem control. This route is useful for organising the answer, but it mainly describes how the source was taught."
    },
    {
      "id": "exam_guidance_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "The final exam thesis should be that locomotion is layered control. In an exam answer, this should be framed as spinal rhythm plus sensory and brainstem modulation."
    },
    {
      "id": "citation_stack_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Reliability is important because repeated observations can vary across instruments (Smith, 2020) (Jones, 2021) (Patel, 2022). The paragraph lists authority but does not explain which source proves which mechanism."
    },
    {
      "id": "citation_strength_overclaim_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "The review supports inflammation as the single cause of the syndrome, so all other mechanisms can be treated as secondary. This overstates source strength and collapses a multi-hit mechanism into one cause."
    },
    {
      "id": "author_led_citation_prose_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Martinez et al. identified a pathway regulator that changes the interpretation of the mechanism. The content may be relevant, but the author name has become the sentence subject instead of staying inside a parenthetical citation."
    },
    {
      "id": "channel_catalogue_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Central pattern generation can involve persistent Na currents, low-threshold Ca currents, NMDA-dependent plateaus, HCN conductance and Ca-dependent K currents. Adding this conductance catalogue makes the paragraph sound technical, but it does not explain whether the exam question needs cellular conductance detail or a circuit-level distinction between central rhythm generation and sensory adjustment."
    },
    {
      "id": "descriptive_list_without_analysis_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Renshaw cells inhibit motor neurons during spinal output. Ia interneurons mediate reciprocal inhibition between antagonist muscles. Ib interneurons regulate force-sensitive feedback from tendon organs. The paragraph lists named interneurons but never explains what distinction the list proves for the question."
    },
    {
      "id": "compression_scope_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Because spinal networks can generate rhythmic motor output in reduced preparations, sensory feedback is unnecessary for locomotion. This compression removes the distinction between basic rhythm generation and feedback-dependent adjustment to load, speed and phase."
    },
    {
      "id": "mechanical_compression_trace_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "This version has been compressed by 30% while preserving the main points. The target word count is lower, so the paragraph removes some evidence and keeps only the broad conclusion about spinal rhythm generation."
    },
    {
      "id": "negative_opener_before_positive_claim_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "The spinal cord is not a passive relay between brain and muscle. It is the lowest level of the motor hierarchy, transforming sensory input, descending command and motor-neuron feedback into organised motor output. That delayed positive claim should have opened the paragraph directly."
    },
    {
      "id": "fragmented_evidence_sequence_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "The strongest evidence for spinal CPGs is that rhythmic flexor-extensor alternation can persist after sensory reafference from the limb has been removed. In Graham Brown's decerebrate cat experiments, descending influence was reduced, the limb was fixed, and dorsal roots were cut. Rhythmic alternation between flexor tibialis anterior and extensor gastrocnemius still emerged. The result is correct, but the paragraph states the claim, detours into setup, and then restates the claim instead of attaching the result to the setup."
    },
    {
      "id": "repeated_not_but_framing_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Locomotor control is not a single spinal reflex but a layered timing problem. The spinal network is not merely a relay but a generator of core rhythmic output. Sensory input is not the origin of the rhythm but the mechanism that tunes load, phase and terrain adaptation, so the paragraph repeats the same contrast form instead of stating the positive control architecture directly."
    },
    {
      "id": "claim_restart_after_setup_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Spinal timing circuits generate rhythmic locomotor output without requiring sensory feedback. In reduced preparation experiments, descending input was limited and peripheral feedback was removed to test whether the spinal network retained intrinsic timing. Spinal timing circuits generate rhythmic locomotor output without requiring sensory feedback, which shows why the setup should have been connected to the result instead of restarting the claim."
    },
    {
      "id": "descriptive_analytic_imbalance_bad",
      "expected": "fail",
      "has_lecture_anchor": true,
      "text": "Renshaw cells receive motor-neuron collateral input. Ia inhibitory interneurons inhibit antagonist motor pools. Ib interneurons receive tendon-organ force feedback. Commissural interneurons cross the midline. Propriospinal interneurons link spinal segments. Axo-axonic interneurons act on afferent terminals. The paragraph names components but gives too little analysis of what control problem these components solve."
    },
    {
      "id": "intro_part_list_bad",
      "expected": "fail",
      "function": "introduction",
      "has_lecture_anchor": true,
      "text": "This essay will first explain spinal rhythm generation, second describe proprioceptive feedback, third discuss brainstem command and finally summarise vestibular control. The introduction lists the later parts instead of giving a thesis about distributed locomotor control."
    },
    {
      "id": "claim_mechanism_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "Measurement reliability depends on separating systematic bias from random error. Bias shifts observations in a consistent direction, whereas random error widens the spread of repeated measurements, so calibration and replication solve different problems. This distinction matters because a precise instrument can still be wrong if it is miscalibrated, while an unbiased but noisy instrument may require repeated observations before the underlying signal is clear."
    },
    {
      "id": "comparison_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "The two models answer different parts of the same control problem. A feedback model explains how output is corrected after sensory evidence shows a mismatch, whereas a feedforward model explains how an expected demand can be prepared before error occurs. The contrast is therefore not whether one model replaces the other, but which timing assumption best explains the behaviour being tested."
    },
    {
      "id": "evidence_mechanism_interpretation_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "The perturbation experiment supports a specific control claim rather than a general statement that feedback is important. A sudden balance disturbance activates a rapid corrective pathway, showing that sensory evidence can alter motor output when the ongoing pattern is mechanically unsafe. The limitation is equally important: the result supports feedback-dependent correction, not the claim that sensory input creates the basic rhythm from zero."
    },
    {
      "id": "ppt_anchored_cpg_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "A central pattern generator is best treated as a spinal or brainstem network, not a single pacemaker cell. Its recurrent circuitry can produce timed flexor-extensor sequences without sensory reafference, whereas sensory input entrains and adjusts that rhythm to load, speed and phase. The exam-relevant point is therefore layered control: movement has a central timing source, but useful locomotion remains feedback-tuned rather than sensory-independent."
    },
    {
      "id": "linear_evidence_sequence_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "The strongest evidence for spinal CPGs is that rhythmic flexor-extensor alternation persists when limb-derived sensory reafference is removed. In Graham Brown's decerebrate cat experiments, descending influence was reduced, the limb was fixed, and dorsal roots were cut, yet alternating activity still emerged between flexor tibialis anterior and extensor gastrocnemius. The result separates rhythm generation from rhythm adjustment because the core timing survives without the sensory events that normally tune phase and load."
    },
    {
      "id": "parenthetical_citation_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "The extra source should sharpen the mechanism without making the paper itself the topic. A pathway regulator changes the interpretation because it separates the upstream trigger from the downstream response, so the sentence stays focused on the biological claim and places source attribution at the end (Martinez et al., 2021)."
    },
    {
      "id": "direct_positive_claim_good",
      "expected": "pass",
      "has_lecture_anchor": true,
      "text": "The spinal cord is the lowest level of the motor hierarchy, transforming sensory input, descending command and motor-neuron feedback into organised motor output. This framing makes reflexes part of local sensorimotor computation: afferent signals, interneuron relays and motor-neuron feedback are routed into responses that are fast, task-dependent and coordinated."
    },
    {
      "id": "balanced_conclusion_good",
      "expected": "pass",
      "function": "conclusion",
      "has_lecture_anchor": true,
      "text": "Overall, rhythmic movement depends on spinal timing circuits, pattern-formation pathways, proprioceptive phase gating, brainstem initiation and vestibular stabilisation. Analytically, this organisation makes locomotion a distributed control problem: central circuits provide usable timing only because sensory and descending systems continuously tune that timing to mechanical support, behavioural demand and balance."
    }
  ]
}

---

## Source File: `benchmarks__kp_essay_style_linter_fixtures.json`

---

{
  "suite_name": "kp_essay_style_linter_fixtures",
  "purpose": "Validate that default workbook KP explanations are concept-first essay-style synthesis rather than page/slide narration or writing instructions.",
  "cases": [
    {
      "id": "energy_storage_page_trace_bad",
      "column": "explanation",
      "expected": "fail",
      "text": "Pages 8-9 should be read as one connected exam paragraph. Page 8 first establishes the operating problem. Page 9 then develops the degradation pressure and Page 10 then closes with a performance implication."
    },
    {
      "id": "metabolism_style_meta_bad",
      "column": "explanation",
      "expected": "fail",
      "text": "Glycolytic control is the central idea for this block. In an essay answer, it should be written as a pathway sequence. The first part of the sequence establishes substrate entry, and the later pages add the regulatory examples."
    },
    {
      "id": "metabolism_soft_meta_bad",
      "column": "explanation",
      "expected": "fail",
      "text": "Glycolysis should be understood as a connected metabolic process rather than a list of isolated reactions. This knowledge block is mainly an argument about metabolic control and is best written as a pathway summary."
    },
    {
      "id": "measurement_style_slide_sequence_bad",
      "column": "explanation",
      "expected": "fail",
      "text": "KP01 covers pages 15-24. The slide sequence should be read as a connected overview of measurement reliability, with the remaining linked pages providing examples of calibration, bias and repeated observations."
    },
    {
      "id": "prep_column_turn_pages_bad",
      "column": "prep",
      "expected": "fail",
      "text": "Turn pages 15-24 into one paragraph."
    },
    {
      "id": "energy_storage_concept_first_good",
      "column": "explanation",
      "expected": "pass",
      "text": "Battery degradation is best framed as an interaction between electrode chemistry, ion transport and operating conditions rather than as a single failure mode. High current, repeated cycling and temperature stress can accelerate side reactions or structural change, reducing the active material available for reversible charge storage. This matters because performance loss is mechanistic: operating choices alter microscopic processes, and those processes accumulate into measurable capacity fade."
    },
    {
      "id": "measurement_concept_first_good",
      "column": "explanation",
      "expected": "pass",
      "text": "Measurement reliability depends on separating systematic bias from random error. Bias shifts observations in a consistent direction, while random error widens the spread of repeated measurements, so calibration and replication solve different problems. The distinction matters because a precise instrument can still be wrong if it is miscalibrated, whereas an unbiased but noisy instrument may require more repeated observations before the underlying signal is clear."
    },
    {
      "id": "metabolism_concept_first_good",
      "column": "explanation",
      "expected": "pass",
      "text": "Metabolic regulation matches pathway flux to cellular energy demand and substrate availability. Enzymes at irreversible or highly regulated steps respond to signals such as ATP, ADP, AMP, NADH or covalent modification, so carbon flow is redirected when the energetic state changes. This control prevents wasteful cycling and enables tissues to prioritise ATP production, biosynthesis or fuel storage according to physiological context."
    }
  ]
}

---

## Source File: `benchmarks__method_long_answer_suite.json`

---

{
  "suite_name": "method_long_answer_suite",
  "target_group_key": "Benchmark_Method_Long_Answer",
  "target_code": "TEST00001",
  "purpose": "Validate routing for current answer-one project/scenario long-answer regimes without relying on a course name or subject-specific recurrence.",
  "hard_rules": [
    "Do not edit, rename, delete, or overwrite source lecture or past-paper files.",
    "Do not treat exemplars, annotations, or student notes as factual course evidence.",
    "Do not insert unverified citations.",
    "Do not write full long answers into one Excel cell.",
    "Do not use old-format papers as current-regime blueprint evidence."
  ],
  "source_examples": {
    "lecture_folder": "examples/private_sources/method_long_answer",
    "formal_papers": [
      "examples/private_sources/past_papers/method_long_answer_2023.pdf",
      "examples/private_sources/past_papers/method_long_answer_2024.pdf",
      "examples/private_sources/past_papers/method_long_answer_2025.pdf",
      "examples/private_sources/past_papers/method_long_answer_2021.pdf",
      "examples/private_sources/past_papers/method_long_answer_2015.pdf"
    ]
  },
  "expected_regimes": [
    {
      "name": "current_answer_one_project_scenario_long_answer",
      "years": ["2023", "2024", "2025"],
      "evidence_use": "current_blueprint_and_answer_style",
      "required_detection": [
        "answer-one long-answer/project regime",
        "question split into weighted parts",
        "rotating scenario or system",
        "reused examiner operations across different scenario content"
      ]
    },
    {
      "name": "old_or_different_format_coverage_only",
      "years": ["2015", "2021"],
      "evidence_use": "concept_pool_only",
      "required_detection": [
        "not same-regime direct predictor",
        "old-regime evidence used only for coverage or method concept bank"
      ]
    }
  ],
  "recent_project_mappings": [
    {
      "year": "2023",
      "scenario_id": "Scenario A",
      "expected_operations": [
        "design intervention or alteration",
        "prepare or isolate target material",
        "measure functional specificity",
        "quantify interaction or response",
        "select method for structural or system-level determination"
      ]
    },
    {
      "year": "2024",
      "scenario_id": "Scenario B",
      "expected_operations": [
        "choose supporting intervention",
        "prepare or isolate target material",
        "assess integrity",
        "quantify interaction or response",
        "design linker or interface test",
        "determine interaction interface"
      ]
    },
    {
      "year": "2025",
      "scenario_id": "Scenario C",
      "expected_operations": [
        "explain state-change mechanism",
        "prepare or isolate target material",
        "measure unfolding or state transition",
        "quantify association state",
        "interpret condition-sensitive alteration",
        "determine high-resolution or system-level structure"
      ]
    }
  ],
  "required_archetypes": [
    "design preparation strategy",
    "choose and justify characterisation methods",
    "assess stability, state, or integrity",
    "quantify interaction or response strength",
    "interpret engineered or natural alteration",
    "determine interaction interface",
    "determine high-resolution or system-level structure",
    "compare method families",
    "quantify functional activity or specificity",
    "explain state-change or support mechanism",
    "identify in vivo, deployment, or practical caveats"
  ],
  "behavioural_tests": [
    {
      "question": "How would you characterise a condition-sensitive functional response?",
      "must_include_paragraphs": [
        "mechanistic principle and state exposure",
        "preparation of relevant material",
        "method to measure unfolding, transition, or response state",
        "method to identify contact or causal residues where suitable",
        "caveats and controls"
      ],
      "must_not": [
        "broad topic essay",
        "unverified citation",
        "method list without readout interpretation"
      ]
    },
    {
      "question": "How would you prepare a tagged target and determine association state?",
      "must_connect": [
        "capture or enrichment principle",
        "lysis or extraction and clarification",
        "binding, wash, and elution",
        "tag removal if relevant",
        "native or separation method for association state",
        "purity, concentration, or stability checks where relevant",
        "expected elution, band, trace, or signal readout"
      ]
    },
    {
      "question": "How would you choose a method for structural or system-level determination?",
      "must_select_by": [
        "target size or scale",
        "sample stability",
        "preparation feasibility",
        "flexibility or heterogeneity",
        "concentration or amount required",
        "complexity",
        "resolution need",
        "question aim"
      ],
      "must_not": [
        "blindly choose a method without justification"
      ]
    }
  ],
  "output_acceptance": [
    "paragraph plan generated before final answer",
    "each paragraph follows question goal -> lecture principle -> scenario application -> readout -> interpretation -> control",
    "answers all question parts",
    "respects mark weighting",
    "uses compressed academic English and avoids filler",
    "extra reading is omitted unless verified and directly useful",
    "QA flags unsupported/image-only files, weak OCR, unverified extra reading, claims not found in supplied lecture material, and old-regime evidence used only for coverage"
  ],
  "generic_contribution": "Validates long-answer project/scenario routing for method-heavy exams.",
  "transferable_rules": [
    "Route method-design scenario exams to long_answer_project, not essay_theory.",
    "Predict recurring examiner operations rather than repeated scenario content.",
    "Every model answer must include method principle, scenario application, expected readout, interpretation, and control or limitation.",
    "Use older different-format papers only for method/concept coverage unless comparability is proven."
  ],
  "future_target_diagnostic_questions": [
    "Does the paper introduce a scenario or system and ask the student to design or justify methods?",
    "Are examples rotating while examiner operations recur?",
    "Does the question require expected readouts and interpretation?",
    "Would a broad essay fail because the required answer is a compact experimental argument?"
  ],
  "non_transferable_content": [
    "scenario labels",
    "named systems from source materials",
    "specific factual examples",
    "exact operation sequence as content prediction for another target group"
  ],
  "workflow_steps_tested": [
    "question_type_gate",
    "exam_format_diagnosis",
    "knowledge_point_optimisation",
    "archetype_mapping",
    "pattern_detection",
    "question_type_outputs",
    "long_answer_project_mode",
    "extra_reading_and_exemplars",
    "excel_generation",
    "qa",
    "cross_subject_regression"
  ],
  "anti_patterns_guarded_against": [
    "writing a generic essay for a project/scenario question",
    "predicting repeated scenario systems instead of recurrent examiner operations",
    "listing methods without explaining readouts and interpretation",
    "using old papers as current-regime blueprint"
  ]
}

---

## Source File: `benchmarks__past_paper_prediction_suite.json`

---

{
  "suite_name": "past_paper_prediction_suite",
  "purpose": "Validate generic past-paper prediction behaviour without private paper content.",
  "hard_rules": [
    "Past-paper prediction must produce question-family preparation targets, not exact future stems.",
    "Question-level records must precede archetype scoring.",
    "Old or structurally different regimes may support coverage but must not control current blueprint prediction.",
    "Question-type outputs must be type-specific and student-facing confidence must use bands, not fake precision."
  ],
  "target_groups": [
    {
      "target_group_key": "Benchmark_MCQ_NegativeMarking",
      "target_code": "Benchmark_MCQ",
      "lecture_source_examples": [],
      "past_paper_paths": [],
      "expected_regimes": [
        "mcq_heavy_with_negative_marking"
      ],
      "required_archetypes": [
        "mcq_discriminator_axis",
        "mcq_scoring_policy",
        "wrong_option_diagnosis"
      ],
      "must_not": [
        "claim official answers when no answer key exists",
        "treat keyword frequency as sufficient preparation",
        "omit the expected-value guessing threshold when negative marking is detected"
      ],
      "generic_contribution": "Validates MCQ-heavy preparation where high-yield concepts must be paired with distractor logic and scoring policy.",
      "transferable_rules": [
        "For MCQ regimes, infer discriminator axes, common false statements, calculation traps, and scoring policy.",
        "If negative marking is detected, compute or state the positive expected-value threshold from visible scoring rules.",
        "Do not invent official answer keys."
      ],
      "future_target_diagnostic_questions": [
        "Does the paper specify wrong-answer penalties or multiple-response scoring?",
        "Are there enough option-level records to infer distractor families?",
        "Is an answer key present, or must answers remain lecture-inferred?"
      ],
      "non_transferable_content": [
        "specific concepts",
        "option wording",
        "course identity",
        "real paper years"
      ],
      "workflow_steps_tested": [
        "ExtractPastPaperQuestions",
        "ClassifyQuestionType",
        "InferQuestionArchetype",
        "GeneratePrepArtifact",
        "RunDeliverableQA"
      ],
      "anti_patterns_guarded_against": [
        "raw topic hotness",
        "official-answer hallucination",
        "ignoring negative marking"
      ]
    },
    {
      "target_group_key": "Benchmark_ShortAnswer_VariantSpace",
      "target_code": "Benchmark_SAQ",
      "lecture_source_examples": [],
      "past_paper_paths": [],
      "expected_regimes": [
        "short_answer_family_reuse"
      ],
      "required_archetypes": [
        "bounded_short_answer_variant",
        "mark_scaled_schema",
        "source_linked_kp"
      ],
      "must_not": [
        "generate unbounded question lists",
        "create variants without source-linked knowledge points",
        "claim official mark allocation without mark scheme evidence"
      ],
      "generic_contribution": "Validates short-answer preparation as bounded variant generation from archetype, slot grammar, lecture KP, and mark scale.",
      "transferable_rules": [
        "Generate bounded variants only from question family, slot grammar, source-linked KP, and visible mark scale.",
        "Provide concise exam answer and reference expansion as separate layers.",
        "Flag missing lecture evidence rather than filling gaps from memory."
      ],
      "future_target_diagnostic_questions": [
        "Which short-answer families recur?",
        "Which slots vary across years?",
        "Which KPs can fill each slot with source support?"
      ],
      "non_transferable_content": [
        "named examples",
        "specific answer points",
        "source-set identity"
      ],
      "workflow_steps_tested": [
        "ExtractPastPaperQuestions",
        "InferQuestionArchetype",
        "MapKPToArchetype",
        "GeneratePrepArtifact",
        "RunDeliverableQA"
      ],
      "anti_patterns_guarded_against": [
        "unbounded guessing",
        "answer-schema hallucination",
        "topic-only prediction"
      ]
    },
    {
      "target_group_key": "Benchmark_Method_LongAnswer",
      "target_code": "Benchmark_LongAnswer",
      "lecture_source_examples": [],
      "past_paper_paths": [],
      "expected_regimes": [
        "scenario_project_long_answer"
      ],
      "required_archetypes": [
        "method_block_library",
        "readout_interpretation",
        "control_limitation"
      ],
      "must_not": [
        "predict exact rotating scenario",
        "write generic essay for scenario method prompt",
        "omit readout or control logic"
      ],
      "generic_contribution": "Validates long-answer project preparation as reusable method/readout/control blocks rather than exact scenario prediction.",
      "transferable_rules": [
        "Treat the surface scenario as a rotating slot when the method operation is stable.",
        "Prepare method choice, expected readout, interpretation, control, and limitation.",
        "Use old different-format papers for coverage only unless comparability is proven."
      ],
      "future_target_diagnostic_questions": [
        "Does the paper present a new scenario while asking stable method operations?",
        "Which readouts and controls recur?",
        "Can old papers support only coverage rather than current blueprint?"
      ],
      "non_transferable_content": [
        "named systems",
        "specific methods not present in target sources",
        "real question stems"
      ],
      "workflow_steps_tested": [
        "ClassifyQuestionType",
        "InferQuestionArchetype",
        "GeneratePrepArtifact",
        "RunDeliverableQA"
      ],
      "anti_patterns_guarded_against": [
        "scenario memorisation",
        "essay routing for project answers",
        "method list without interpretation"
      ]
    },
    {
      "target_group_key": "Benchmark_Essay_CoveragePlan",
      "target_code": "Benchmark_Essay",
      "lecture_source_examples": [],
      "past_paper_paths": [],
      "expected_regimes": [
        "answer_one_from_several_essay_options"
      ],
      "required_archetypes": [
        "essay_coverage_plan",
        "argument_skeleton",
        "evidence_bank"
      ],
      "must_not": [
        "claim exact future essay title",
        "prepare every lecture block to equal depth when coverage optimisation is requested",
        "merge short-answer recurrence into essay-theme prediction without Section B fit"
      ],
      "generic_contribution": "Validates essay preparation as coverage planning across lecture blocks, command verbs, argument skeletons, evidence banks, diagrams, comparison axes, and limitations.",
      "transferable_rules": [
        "For answer-one essay sections, optimise for at least one high-quality answer among visible option slots.",
        "Predict lecture-block themes and command verbs, not exact future stems.",
        "Keep short-answer evidence separate from essay evidence unless the same block also fits essay option structure."
      ],
      "future_target_diagnostic_questions": [
        "How many essay options are offered and how many are answered?",
        "Which lecture blocks form coherent examinable themes?",
        "Which evidence and diagram banks transfer across practice variants?"
      ],
      "non_transferable_content": [
        "lecture names",
        "specific essay titles",
        "lecturer identity"
      ],
      "workflow_steps_tested": [
        "SplitExamRegime",
        "InferQuestionArchetype",
        "MapKPToArchetype",
        "GeneratePrepArtifact",
        "RunDeliverableQA"
      ],
      "anti_patterns_guarded_against": [
        "exact-stem prediction",
        "coverage overexpansion",
        "mixed evidence streams"
      ]
    }
  ]
}

---

## Source File: `references__best_usage_guide.md`

---

# Best Usage Guide

This guide describes the source pack and run mode that give the Skill the strongest evidence base.

## Best Source Pack

For the strongest result, provide:

- lecture slides, official notes, lecturer-provided notes, or other readable ordered course notes;
- formal past papers from the relevant exam regime;
- answer keys, mark schemes, or official guidance when available;
- practical, data, graph, protocol, case, or calculation materials when those question types are possible;
- essay or long-answer prompts if complete essay or long-answer output is requested;
- extra reading recommendations, books, papers, DOI records, PubMed records, publisher pages, or textbook chapters;
- any user weak areas, time budget, and preferred output depth.

Missing sources do not automatically stop the run. They stop only the conclusions that require them.

## Choosing The Correct Preset

Start from the requested artifact and choose the minimum valid route. The authoritative mode and preset table is in `references/user_interaction_protocol.md`; this guide only explains how to prepare the strongest source pack and how to run planning helpers.

## Strategy Rules

The exam strategy controls the output strategy:

- general-revision default: exam-informed Academic Exam-Ready Notes in a Word walkthrough artifact;
- explicit lecture-order walkthrough: lecture-first Word walkthrough with conceptual modules;
- essay or problem-essay: module-level Example Essays, adaptation maps, paragraph banks, and source-boundary checks;
- MCQ: student-facing Point Cards only by default, with traps folded into the card rather than exposed as separate audit tables;
- short answer: module logic, highlighted keywords, and natural Example Answers rather than visible mark-schema tables;
- data/problem/practical/scenario/project long answer: question analysis, answer order, reusable method/readout/interpretation/control/limitation blocks, Example Answer, and adaptation rules;
- mixed format: one walkthrough foundation may be used, but each add-on report keeps its own question-type route.

## Evidence Rules

Use lecture and official notes for factual course logic. Use formal papers for exam structure and archetypes. Use practical and answer materials for operations and answer style. Use external readings only after verification. Use examples and feedback as transferable style or workflow evidence unless the same factual claim is independently verified from target sources.

## Planning Commands

Create a plan:

```bash
python scripts/plan_workflow.py --config path/to/skill_config.json --output internal_qa/workflow_plan.json
```

Check readiness:

```bash
python scripts/input_readiness_check.py --config path/to/skill_config.json --output internal_qa/input_readiness.json
```

Render a plan preview:

```bash
python scripts/render_workflow_plan.py --plan internal_qa/workflow_plan.json --output internal_qa/workflow_plan.md
```

Use these helpers to make the run auditable. Do not publish helper JSON, rendered previews, manifests, lineage files, or source maps into the student-facing output unless an audit package was requested.

---

## Source File: `references__cross_subject_regression_protocol.md`

---

# Cross-Subject Regression Protocol

Benchmark fixtures are used only to test generic Skill behaviour. A benchmark name, course name, example topic, lecturer, year, or recurring content pattern must never trigger production logic.

Regression asks whether the workflow obeys general evidence and output rules when faced with different source shapes. It does not ask whether the workflow can repeat the same old example.

Hard rule:

```text
Target source-set evidence = factual content + direct prediction evidence.
Old or structurally different target evidence = coverage/schema evidence unless comparability is proven.
External examples = transferable workflow lessons only.
Style/layout exemplars = wording, structure, density, formatting, and answer organisation only.
Benchmark fixtures = tests only; never production rules.
```

## Benchmark Review Schema

Every benchmark or external example must be converted into an `ExampleReviewRecord` before it can influence workflow design:

```yaml
ExampleReviewRecord:
  example_id:
  source_role: benchmark_fixture
  source_materials:
    - lecture_slides
    - lecture_notes
    - formal_past_papers
    - practical_materials
    - mocks_or_quizzes
    - answer_keys
    - marking_guidance
    - exemplar_answers
    - image_examples
  example_scope:
  what_worked:
    - reusable workflow behaviour demonstrated by the example
  why_it_worked:
    - source or output condition that made the behaviour valid
  what_failed:
    - failure observed, or no failure observed
  why_it_failed:
    - cause, or not applicable because no failure was observed
  transferable_principle:
  non_transferable_content:
    - concrete topic/content/example/lecturer/year/detail that must not be reused
  anti_overfit_rule:
  affected_protocols:
    - protocol path or protocol name
  affected_scripts:
    - script path or linter name
  validation_check:
  regression_fixture:
  promotion_status: candidate | accepted | rejected | blocked
  confidence: high | medium | low
```

Benchmarks may contribute only condition-based rules and tests. A target-specific fixture requirement belongs in the fixture; the production rule must be expressed in generic source features such as official definitions, contrast pairs, criteria lists, named teaching examples, `Why X?` blocks, workflows, calculations, and graph or method operations.

## Required Regression Axes

Each benchmark run should validate the generic behaviour it claims to teach.

Source handling:

- files are classified by role and trust level before analysis;
- unreadable or weak-OCR material is flagged rather than inferred;
- old or structurally different papers are separated from current prediction evidence;
- external examples are recorded as transferable workflow lessons, not content evidence.

Question-type routing:

- MCQ, short answer, essay, data/problem, and project/scenario long answer are separated;
- essay-only logic is not applied to MCQ or problem/data questions;
- mixed-format papers keep separate section logic.

Exam-strategy inference:

- answer-all versus answer-one rules are detected;
- section structure, mark weights, word limits, and timing are parsed;
- current-regime predictions are not driven by old-regime format;
- confidence is reported without fake precision.

Knowledge-point construction:

- KPs are built from examinable reasoning blocks rather than slide count;
- adjacent source pages are merged only when they teach one examinable mechanism, process, comparison, method, data operation, or scenario;
- source order is preserved in the compatibility lecture walkthrough and used diagnostically in Academic Exam-Ready Notes;
- page/slide coverage is kept in images/source maps, not narrated inside student prose.

Language quality:

- student-facing explanations use `claim -> mechanism/process/evidence -> consequence`;
- complete Example Essays use paragraph functions, not slide summaries;
- examples support wider claims instead of becoming disconnected case descriptions;
- repeated low-value detail is compressed;
- necessary academic mechanisms are preserved;
- contrast language is explicit;
- citations are minimal, sufficient, and verified.

Output layout:

- student-facing outputs keep evidence/provenance fields out unless an audit package is requested;
- original slide/page images remain visible and aspect-ratio-preserved when included;
- the add-on report adapts to question type;
- complete Example Essays are in DOCX output, not spreadsheet cells.

QA:

- predictions are labelled conservatively by question type, including predicted essay themes for essay/problem-essay outputs;
- source uncertainty is flagged;
- unsupported claims are omitted or flagged;
- benchmark/example leakage is flagged;
- generated prose is linted when tooling exists.

## Example Essay DOCX Regression

When an Example Essay DOCX directory is supplied to the regression checker, validate:

- complete essays are present in the requested DOCX output, either inside `Essay_Module_Example_Essays.docx` or as separate `.docx` files when separate files are requested;
- internal QA artefacts such as `example_essay_manifest.json` and `example_essay_source_audit.json` exist in a separate internal QA directory unless the user explicitly asks for an audit package;
- no generated Example Essay exists only as a spreadsheet row;
- DOCX formatting passes the route-specific contract: Example Essay artifacts use Arial, 2.5 cm margins, 1.5 line spacing, justified body, centered title, and left-aligned subtitles/headings; exam-prep notes and compatibility lecture walkthroughs use compact margins, compact line spacing, left-aligned body text, and lecture page breaks;
- yellow-highlighted runs map to uploaded Extra Reading Book chapter/section anchors;
- green-highlighted runs map to read lecture-slide citation originals and include author-year in-text citation;
- every body paragraph has source anchors;
- language checks pass for compression, claim-led paragraphs, citation discipline, and example-as-evidence use.

## Benchmark Pass/Fail Output

Regression output must report both:

- benchmark fixture pass/fail; and
- generic contribution pass/fail.

```yaml
RegressionResult:
  benchmark_id:
  fixture_status: pass | fail
  generic_contribution_status: pass | fail
  validated_transferable_rules:
    - rule:
      evidence:
      checks_passed:
  leakage_checks:
    benchmark_identity_used_as_trigger: false
    benchmark_content_used_as_fact: false
    external_example_used_as_prediction: false
  qa_flags:
    - flag
```

## Automatic Fail Conditions

Fail regression if:

- production logic branches on benchmark identity;
- benchmark factual content appears in a new source set's factual answer or prediction evidence without independent target-source verification;
- a benchmark lacks generic contribution metadata;
- a benchmark lacks non-transferable-content metadata;
- old or structurally different papers drive current-regime predictions without comparability evidence;
- generated student-facing prose contains slide/page narration as the main explanation;
- complete Example Essays are exported only as spreadsheet rows;
- Example Essay DOCX formatting or source-highlighting checks fail;
- extra-reading or citation-source content is used without verification.

## Success Condition

The regression suite passes when benchmark examples improve only generic workflow behaviour:

- evidence separation;
- exam-regime split;
- question-type routing;
- KP granularity;
- source-order coverage;
- output layout adaptation;
- Example Essay language quality;
- citation and extra-reading discipline;
- no factual leakage from examples into new work.

---

## Source File: `references__essay_generation_protocol.md`

---

# Essay Generation Protocol

Example Essay generation is a DOCX-first branch used when the user explicitly asks for essay preparation, complete Example Essays, model essays, full essay-style answers, or complete essay documents. KP explanations and single essay-style paragraphs do not trigger this branch unless the user asks for essay prep or full Example Essays.

The protocol applies across biological and non-biological science-style essays. The factual source base changes by subject; the writing discipline does not.

Use `language_quality_contract.md` as the source of truth for prose quality. This file defines Example Essay orchestration, source grounding, and planning.

Use `essay_tutor_workflow_protocol.md` when the user asks for complete essay planning, assessed-style drafting, citation-controlled essay writing, or figure/table/data support. That protocol controls essay-specific intake, DeepResearch, subtitle-level planning, plan approval, candidate-source labelling, and visual/data gates before this file controls drafting and DOCX generation.

## Core Principle

An Example Essay is not a longer summary of lecture slides. It is a controlled answer to a question:

```text
question demand -> relevant source scope -> lecture/source logic -> paragraph function -> concise evidence-backed argument
```

Every paragraph must earn its place by advancing the answer. Do not pad to reach a word count.

## Required Internal Pipeline

Run this orchestration sequence for complete Example Essay generation:

```yaml
ExampleEssayMode:
  essay_specific_intake:
  input_readiness_report:
  question_analysis:
  source_scope_detection:
  lecture_or_material_reading:
  ppt_or_source_logic_reconstruction:
  deep_research:
  detailed_essay_plan:
  plan_approval_gate:
  citation_detection:
  citation_original_source_resolution_and_reading:
  classic_experiment_fallback_if_slide_citations_absent:
  extra_reading_scope_matching:
  knowledge_inventory:
  paragraph_plan:
  first_draft:
  citation_and_extra_reading_integration:
  compression_budget_estimate:
  expression_efficiency_compression_pass:
  accuracy_preservation_pass:
  positive_claim_framing_pass:
  logic_linearity_pass:
  descriptive_analytic_balance_pass:
  analytic_argument_pass:
  micro_extra_reading_enhancement_pass:
  highlight_plan:
  source_to_run_mapping:
  high_score_example_essay:
  docx_generation:
  docx_format_linting:
  render_or_visual_qa:
  source_audit_json:
  examiner_fit_checklist:
```

The final user-facing answer should expose requested artefacts and keep internal helper files out, while the essay itself must visibly follow the internal plan.

Optional visual aids may be planned only after the essay or notes text is source-backed. Generated schematics are revision aids, not evidence, citations, official figures, or replacements for written analysis. Follow `visual_aid_generation_protocol.md`; skip the visual-aid layer when generation is unavailable or when the concept does not benefit from a schematic.

Do not:

- write from memory;
- draft a complete final essay before a detailed plan is approved unless the user explicitly asks to skip the approval loop or directly requests generation;
- write from a predicted theme or practice variant alone without verifying the supplied lecture/source scope;
- write from a past-paper stem without reading the relevant lecture/source material;
- copy citations printed in slides without resolving and reading the original source when source-derived content is used;
- skip citation discovery merely because the user did not provide a citation list;
- add extra reading without locating the relevant chapter, section, paper, DOI, PubMed record, publisher page, or textbook source;
- hide all source logic in diagnostics while outputting an ungrounded essay;
- produce several complete essays in one Word document;
- use benchmark/example content as factual content for a new source set.

## Source Grounding

Before planning or drafting, read the supplied lecture slides, official lecture notes, formal questions, practical materials, marking criteria, exemplars, extra reading recommendations, and recommended books relevant to the question.

Source priority:

1. Relevant lecture slides and official notes.
2. Formal question wording and official exam guidance.
3. Practical materials, mocks, answer keys, and exemplars for format and answer-style support.
4. Original sources cited by relevant lecture material, only after they are resolved and read.
5. Verified classic or landmark experiments found by academic search when relevant lecture slides contain no usable citations.
6. Uploaded extra-reading books, only matched chapters or sections.
7. Other peer-reviewed papers, textbooks, DOI/PubMed/publisher pages, or Google Scholar results when no official reading is supplied or citation resolution requires it.

If relevant lecture/source material cannot be identified or read, do not generate a polished essay. Emit a QA flag and ask for the missing material.

Plan-stage citation rule:

- Treat unverified external sources as `candidate_source` during planning.
- Use exact author-year, DOI, PMID, article title, journal, or "recent review" claims only after verification.
- Candidate sources may shape the search plan, but they must not enter the final draft, reference list, highlight map, or DOCX until metadata and claim relevance are verified.

## Example And Exemplar Use

Examples from other essays, images, courses, or benchmark runs teach structure only:

- paragraph function;
- density;
- opening strategy;
- comparison strategy;
- citation placement;
- compression method;
- sector/system-level abstraction;
- answer organisation;
- DOCX layout.

They do not supply factual content, topic recurrence, citation authority, lecturer preference, or prediction evidence.

## Question Analysis

Classify the question before planning:

- describe;
- explain;
- compare/contrast;
- evaluate;
- mechanism;
- experimental evidence;
- scenario/application;
- data/problem;
- sector/system-level analysis;
- cross-topic synthesis.

Infer likely scope from the question and supplied evidence:

- one detailed knowledge point;
- one lecture or practical block;
- several lectures inside one module;
- a whole source set;
- a cross-module synthesis.

```yaml
EssayQuestionDeconstruction:
  question:
  command_verb:
  expected_scope:
  included_sources:
  excluded_sources:
  question_archetype:
  required_core_claims:
  required_mechanisms_or_processes:
  required_evidence_or_examples:
  useful_comparisons:
  optional_extra_reading:
  expected_answer_shape:
```

## Source Logic Reconstruction

Extract factual content and teaching/argument sequence separately.

For lecture-heavy biological material, common logic patterns include:

```text
biological problem -> molecular/cellular constraint -> mechanism -> evidence/example -> consequence
evidence/experiment -> mechanism tested -> interpretation -> limitation
```

For method, practical, or project material:

```text
problem -> method principle -> experimental design -> readout -> interpretation -> control -> limitation
```

For non-biological science or sector-level essays:

```text
sector/system problem -> theoretical frame -> examples as evidence -> implementation mechanism -> wider implication
```

Slide/source order informs the storyline, but paragraph order is determined by question command word and examiner expectation.

## PPT-Anchored Detail Control

Example Essays must be lecture-first and PPT/source-anchored. Citation / Extra Reading Papers, recommended books, lecture-cited originals, and academic papers may sharpen only a mechanism, evidence point, comparison, limitation, or interpretation slot that is already present in the relevant lecture/source logic.

Do not add a named molecular, cellular, channel, receptor, pathway, assay, circuit, gene, material, equation, or method detail merely because it is true or academically impressive. A detail is admissible only if it passes all five tests:

1. PPT/source anchor: the relevant lecture/source contains the parent mechanism, model, evidence point, or comparison slot.
2. Question relevance: the detail helps answer the exact essay question, not a broader review topic.
3. Precision-only: the detail makes an existing claim more precise without changing the level, scope, or direction of the claim.
4. Efficiency: the detail increases examinable mechanism per word and does not create a catalogue, second argument, or review-style digression.
5. Accuracy: the final compressed wording preserves causal strength, scope qualifiers, lecture distinctions, and evidence boundaries.

Reject details that are:

- true but not anchored in the lecture/PPT/source logic;
- more detailed than the question or source level requires;
- a list of molecules, channels, receptors, genes, examples, or methods without analytic use;
- a new subtopic introduced by Extra Reading;
- a detail that requires a new explanatory sentence before it is intelligible.

Use a `DetailAdmissionMatrix` internally when adding or rejecting detail:

```yaml
DetailAdmissionMatrix:
  paragraph_id:
  ppt_core_claim:
  ppt_mechanism_slot:
  question_function:
    - thesis
    - mechanism
    - evidence
    - interpretation
    - limitation
    - synthesis
  candidate_detail:
  source_class:
    - lecture
    - recommended_book
    - extra_reading_paper
    - lecture_cited_original_paper
    - verified_classic_source
    - rejected
  admission_decision:
    - keep
    - compress
    - reject
  reason:
  risk_flags:
    - no_ppt_anchor
    - true_but_unnecessary
    - review_article_drift
    - list_without_analysis
    - mechanism_level_shift
    - compression_risks_inaccuracy
    - citation_stack
    - extra_reading_replaces_ppt_logic
```

High detail is not automatically high quality. The standard is: PPT/source-anchored, citation-supported, analytically interpreted mechanism per word.

Extra Reading and molecular/mechanism detail must not make the essay longer by default. Treat them as substitutions for vague wording, not additions on top of already complete lecture-derived prose. A detail that requires its own explanatory sentence, creates a second argument, or changes a paragraph from answer prose into review prose should be rejected or moved into an explicitly requested supplementary note.

## Knowledge Inventory

Before writing, classify material:

```yaml
EssayKnowledgeInventory:
  must_use:
    - source-backed claims without which the answer is incomplete
  should_use_if_space:
    - useful mechanisms, examples, data points, comparisons, or caveats
  optional_extra_reading:
    - verified extensions that improve precision or sophistication
  exclude:
    - irrelevant details
    - repeated low-value case facts
    - unsupported claims
    - excessive background
    - content outside question scope
```

Prioritise:

```text
question-relevant core claims > source objectives/summaries > repeated mechanisms > named evidence/examples > background definitions > extra reading
```

## Paragraph Plan

Every complete Example Essay must be planned paragraph-by-paragraph.

For standalone essay planning, the plan must also specify main-body subtitles and the specific content, key claim, evidence need, and analytic angle for each subtitle. A plan that contains only `Introduction`, `Main Body`, `Discussion`, and `Conclusion` is insufficient.

```yaml
EssayParagraphPlan:
  paragraph_number:
  function: thesis | mechanism | comparison | example | evidence | application | limitation | synthesis
  core_claim:
  source_content_used:
  evidence_or_example_used:
  extra_reading_used:
  why_this_paragraph_is_needed:
  link_back_to_question:
```

Each body paragraph must contain:

- one clear claim;
- one mechanism, process, comparison axis, evidence operation, or implementation logic;
- one or two examples/evidence items where useful;
- a link back to the question.

Default paragraph logic:

```text
Claim -> mechanism/process/evidence -> scope or limitation -> consequence -> link back.
```

## Expression Efficiency And Study-Time Density

Run citation and Extra Reading integration before final compression. If the essay is compressed first and then enriched, density, paragraph function, and source balance can drift.

Compression is not a word-count operation. It is an exam-preparation efficiency operation: maximise useful examinable knowledge per word while preserving mechanism accuracy.

Before compressing, estimate the safe compression budget. Do not apply a requested percentage mechanically. A 30% reduction is valid only if the removable material is genuinely redundant after the source skeleton, evidence, citation-supported details, and analytic limitations are protected.

Use a `CompressionBudgetEstimate` internally:

```yaml
CompressionBudgetEstimate:
  current_word_count:
  requested_reduction:
    type: percent | words | unspecified
    value:
  protected_source_skeleton:
    - core source claim, mechanism, evidence, comparison, limitation, or synthesis item that cannot be deleted
  protected_academic_details:
    - named evidence, citation-supported mechanism detail, or examiner-relevant distinction that should be kept or compressed but not removed
  removable_redundancy:
    - repeated framing
    - duplicated source/evidence restatement
    - overlong transition
    - low-value background
    - repeated synthesis list
  safe_reduction_range:
    min:
    max:
  unsafe_threshold:
  decision:
    - compress_within_safe_range
    - partial_compression_only
    - reject_requested_reduction
  reason:
```

Compression targets must be content-derived. If a requested reduction would remove a protected item, use the largest safe reduction instead and record that the requested target exceeds the safe compression budget.

A sentence should stay only if it performs at least one of these functions:

- states the paragraph claim;
- explains a required mechanism, process, method, or control problem;
- gives evidence that changes the strength or scope of the claim;
- interprets what an experiment, example, dataset, or figure proves;
- states a limitation, contrast, or boundary condition;
- adds a verified named detail that sharpens a PPT/source-derived mechanism slot;
- links the paragraph back to the question.

Remove:

- repeated definitions;
- repeated claim restatements;
- A-B-A-C logic where the paragraph states a claim, detours into setup, restates the same claim, and only then adds the consequence;
- repeated case descriptions;
- firm/example-level details that do not support the question;
- lecture-route or source-route narration;
- exam-guidance sentences that tell the student what to write instead of writing the answer;
- vague metacommentary such as `this essay will explore`;
- decorative transitions;
- unnecessary historical background;
- unsupported statistics;
- overlong citation stacks;
- examples that are not converted into a wider argument.

Keep:

- mechanisms;
- causal links;
- named evidence where it proves the point;
- analytical interpretation of what the evidence shows and what it does not show;
- necessary definitions;
- scope limitations;
- examiner-relevant contrasts;
- verified citations for non-obvious claims.

Do not compress by simply shortening every sentence. Compress by deciding what function each sentence performs.

Protected material may still be made more concise, but it must remain present. For example, a named interneuron set, citation-supported cell identity, experiment condition, or timing result can be compressed into a tighter clause when it is examiner-relevant; it must not be deleted merely to hit a percentage target.

## Accuracy-Preserving Compression

After compression, run an accuracy preservation pass. The compressed essay must preserve:

1. Causal strength: `supports`, `implicates`, `is consistent with`, and `contributes to` must not become `proves` unless the source proves causality.
2. Scope qualifiers: do not collapse specific phrases such as `core rhythm`, `normal locomotion`, `basic output`, `precision movement`, `clinical recovery`, `under these assay conditions`, or `in this model` into one broad claim.
3. Negative distinctions: `not necessary for generating the core rhythm` must not become `not necessary for locomotion`.
4. Model boundaries: a mechanism that adjusts, gates, entrains, stabilises, or modulates output must not be rewritten as the primary generator unless the source says so.
5. Evidence interpretation: experiments, examples, and figures must retain what they show and what they do not show.

Reject compressed wording when it changes the claim scope, removes a required qualifier, or turns a support/modulation claim into a generation/proof claim.

Also reject compressed drafts when the final answer has lost one of the protected source-skeleton items identified in the compression budget. Shorter wording is not acceptable if it reduces mechanism density, removes necessary evidence, or converts a discussion paragraph into a descriptive summary.

## Analytic Argument Pass

After the accuracy pass, run a pass focused on analytic value. A paragraph fails if it contains more than two consecutive descriptive sentences without an analytic sentence.

A valid analytic sentence must do at least one of the following:

- explain why the mechanism solves a control, causal, methodological, clinical, or sector-level problem;
- state what an experiment proves or fails to prove;
- compare two models, mechanisms, pathways, or methods;
- define the scope of a claim;
- link a molecular, cellular, circuit, method, or source detail to system-level function;
- explain why the detail matters for the essay question.

Use this pattern:

```text
description -> description -> analysis
```

For the full essay, aim for roughly 50% descriptive material and 50% analytic material. Descriptive material gives the required mechanism, evidence, source-backed detail, example, or result. Analytic material states the consequence, boundary, interpretation, comparison, or reason the detail matters for the question. If the draft reads as a fact catalogue, add analysis by linking each important detail to its function; do not add a detached "discussion" sentence after a list.

Run a positive-claim framing pass:

- prefer direct positive claims over `X is not... It is...`;
- use `not`, `but`, `rather than`, and `however` only when they mark an examiner-relevant boundary or a genuine model contrast;
- do not repeat `not...but` or `rather than` framing across a paragraph when one direct positive claim would carry the same logic;
- if the rejected idea is not needed, delete it and state the correct mechanism directly;
- if the rejected idea is needed, place it after the positive claim as a compact boundary.

Run a logic-linearity pass:

- keep each paragraph in a single forward sequence;
- avoid `A -> B -> A`, where a claim is stated, interrupted by setup, and then restated;
- reject A-B-A-C ordering when the same claim is restarted after experimental setup, source context, or an example before the consequence appears;
- for experiments, prefer `claim -> setup and result -> interpretation`, not `claim -> setup -> repeated result`;
- combine setup and result with a connector such as `yet`, `showing that`, `therefore`, or `which means` when it improves flow.

Do not leave named components as a list. Rewrite list-like content into an answer function: which problem each component solves, what distinction it supports, or what consequence follows.

Reject and rewrite:

- lecture/source-route narration, such as sentences whose main function is to state what a lecture, chapter, source, or section introduces next;
- exam-guidance phrasing, such as telling the student what the final thesis should be;
- repeated negative framing where several sentences say only what the answer is not;
- broad importance claims that do not specify the mechanism, consequence, or limitation;
- examples or experiments that stop at description without interpretation;
- citation-derived claims that overstate support as single-cause proof.

For evidence-heavy material, each major experiment, dataset, case, or example must be reduced to its answer function:

```text
evidence -> mechanism tested -> interpretation -> limitation or scope
```

Use stronger causal verbs only when the verified source directly warrants them. Otherwise prefer calibrated verbs such as `supports`, `implicates`, `is consistent with`, `contributes to`, or `suggests`.

## Micro Extra Reading Enhancement Pass

Run this pass after the essay has a coherent draft and before final highlight planning, source-to-run mapping, and DOCX generation.

Purpose:

- do not rewrite the essay;
- do not add new paragraphs;
- do not add separate Extra Reading expansion blocks;
- add only short verified named details to unhighlighted sentences whose parent mechanism is explicit in the lecture/PPT/source logic;
- increase molecular, circuit, method, chemical, or pathway precision without changing the lecture-derived argument, level, scope, or exam function.

The correct question is not "Can extra reading add more content?". The correct question is:

```text
Is there an unhighlighted mechanism, evidence, or interpretation sentence whose parent mechanism is explicitly present in the PPT/source logic, and whose generic slot can be made more precise by one verified named detail without changing the level, scope, or exam function of the sentence?
```

Eligible sentence functions:

- mechanism;
- evidence;
- interpretation;
- application when it contains a mechanism or method readout.

Do not apply this pass to thesis, transition, broad synthesis, or conclusion sentences unless the sentence contains a specific generic mechanism slot whose precision is required by the question.

Detect generic slots such as:

```text
receptor
channel
transporter
enzyme isoform
kinase or phosphatase
transcription factor or partner
response element
morphogen or ligand
cofactor or allosteric ligand
chemical species or transport form
protein domain
cellular compartment
afferent, interneuron, projection, or circuit class
assay readout or experimental marker
pathway intermediate
```

Candidate insertion rules:

```yaml
MicroExtraReadingInsertion:
  original_sentence:
  original_phrase:
  inserted_phrase:
  parent_ppt_or_source_slot:
  question_function:
  source_class: recommended_book | extra_reading_paper | citation_original_source | classic_experiment_source
  source_anchor:
  highlight_colour: yellow | green
  word_count_delta:
  claim_delta: precision_only
  qa_status: micro_detail_verified | rejected
```

Accept an insertion only when all conditions are true:

- the sentence already has a lecture or official-source anchor;
- the parent PPT/source mechanism slot is identified explicitly;
- the inserted phrase is supported directly by a verified source anchor;
- the inserted phrase is compact enough to remain a phrase or short clause inside the original sentence;
- the insertion replaces vague wording or tightens an existing sentence rather than increasing essay length by standalone expansion;
- the insertion names one concrete object, step, source, species, domain, compartment, readout, or module;
- the insertion preserves the grammar and argument direction of the original sentence;
- the addition improves causal precision, assay precision, or mechanistic specificity;
- the essay remains inside the Extra Reading density limit.

Use these low-risk insertion patterns:

```text
generic noun -> specific appositive
generic transport or pathway claim -> named chemical form or step
generic signal phrase -> named receptor, kinase, ligand, domain, or module
generic readout -> named assay marker, flux, compartment, or experimental endpoint
```

Highlight and source mapping are mechanical:

- uploaded recommended book or textbook chapter = yellow;
- verified Citation / Extra Reading Paper = green;
- verified lecture-cited original paper or verified classic source = green;
- ordinary lecture or official-source material = no highlight;
- exemplar-only or remembered detail = reject.

Reject an insertion when:

- no parent PPT/source slot exists;
- no exact source anchor exists;
- author-year, DOI, PubMed, publisher, chapter, or section verification is missing where required;
- the phrase requires a new explanatory sentence;
- the phrase is long enough to become a new explanation or second argument;
- the phrase is added only to increase Extra Reading or molecular-detail volume;
- it starts a new subtopic;
- it replaces lecture logic with external-source logic;
- it makes a stronger claim than the source supports;
- it duplicates a molecule, method, or named detail already nearby;
- it creates a molecular, channel, receptor, gene, pathway, method, or case catalogue without analytic use;
- it creates citation stacking;
- it turns a concise exam answer into a review-style answer.

Highlight span must be minimal. Highlight only the inserted phrase or short inserted clause. Do not highlight a whole lecture-derived sentence merely because one inserted term came from Extra Reading.

QA flags for this pass:

```text
micro_detail_verified
micro_detail_parent_slot_missing
micro_detail_rejected_unverified
micro_detail_insert_missing_source_anchor
micro_detail_too_expansive
micro_detail_claim_delta_not_precision_only
true_but_not_needed_detail
unnecessary_channel_catalogue
unnecessary_receptor_catalogue
descriptive_list_without_analysis
compression_changed_claim_scope
compression_removed_required_qualifier
compression_target_exceeds_safe_budget
protected_source_skeleton_removed
mechanical_compression_trace
highlight_span_too_broad
source_type_colour_mismatch
lecture_logic_replaced_by_extra_reading
academic_paper_author_year_unverified
recommended_book_section_not_found
```

## High-Quality Essay Language Rules

Use the following style discipline for every Example Essay:

1. Start with the answer. The first paragraph should define the problem or thesis, not announce that the essay will discuss a topic.
2. If there is a debate or competing model, state the dispute first, then introduce each model in logical order.
3. A paragraph should move from claim to evidence and then to implication. Do not list facts and leave the inference unstated.
4. Use examples as proof of a broader mechanism or sector/system pattern. Do not let examples become disconnected mini-case studies.
5. Make contrasts explicit. Avoid ambiguous `rather than` sentences unless both sides of the contrast are named precisely.
6. Prefer direct positive wording. Do not add a negative contrast merely to sound sophisticated.
7. Keep the logic order smooth: no claim, detour, repeated claim pattern unless the paragraph is deliberately returning to evaluate the claim.
8. Prefer precise upper-level terms when a list is only illustrative, but keep the list when the listed mechanisms are examiner-relevant.
9. Avoid lecture-route narration and exam-guidance phrasing inside the answer.
10. End paragraphs with a consequence, limitation, or direct answer to the question.
11. End the essay with synthesis, not new evidence or a list of section conclusions.

Strong paragraph shape:

```text
Rhythmic locomotion is centrally generated only in a restricted sense.
The key issue is what initiates repeated flexor-extensor alternation.
The reflex-chain model treats sensory reafference as the trigger for the next phase.
The central-pattern-generator model makes the stronger claim that spinal circuits can generate the core rhythm internally, while sensory input regulates its expression.
The evidence supports central timing but also limits the claim because balance, load regulation, and terrain adaptation still require feedback.
```

This pattern is transferable: define the claim, locate the alternative or limitation, use evidence, then state scope.

## Essay-Level Structure

Introduction:

- state the question's core problem;
- define only terms required for the answer;
- state the thesis;
- preview the organising logic, not a list of all facts, section conclusions, or every later part.

Body paragraphs:

- each paragraph has one function;
- examples support the function;
- citations support non-obvious factual or theoretical claims;
- paragraphs are sequenced by logic, not by slide/page order.

Conclusion:

- answer the question directly;
- synthesise the main mechanisms or comparisons;
- use roughly half factual synthesis and half analytic consequence;
- do not add new examples or unsupported claims;
- do not simply list the conclusion of each body paragraph.

## Comparison Essays

Do not write disconnected blocks:

```text
Paragraph 1: all facts about A.
Paragraph 2: all facts about B.
Paragraph 3: unrelated comment.
```

Prefer comparison axes:

```text
Paragraph 1: shared problem and thesis.
Paragraph 2: axis 1, comparing both sides.
Paragraph 3: axis 2, comparing both sides.
Paragraph 4: evidence or limitation.
Paragraph 5: synthesis.
```

Each axis must be supported by target-source evidence.

## Sector/System-Level Essays

When a question asks for sector-level, system-level, or broader scientific significance:

- state the level of analysis explicitly;
- demote firms/cases/examples to evidence;
- replace excessive case detail with the shared mechanism;
- conclude each section by explaining what the example proves about the wider system.

Strong abstraction pattern:

```text
example detail -> operational mechanism -> wider sector/system implication
```

If the essay starts to read as separate case studies, rewrite the paragraph around the shared mechanism.

## Citation Discipline

Use citations minimally and sufficiently.

Cite:

- non-obvious factual claims;
- theory/framework definitions;
- mechanisms;
- experimental evidence;
- quantitative claims;
- sector-level generalisations;
- source-derived extra-reading additions.

Do not cite:

- obvious transitions;
- the same claim repeatedly;
- unsupported sources copied from another essay;
- a slide citation unless the original source has been resolved and read when source-derived content is used.

Avoid citation stacking. If several sources support the same general claim, keep the most directly relevant source(s). If evidence is insufficient, omit the claim or mark it uncertain in QA.

Match claim strength to source strength. A study, review, or textbook section may support, implicate, refine, or constrain a mechanism without proving it as the sole cause. Do not write causal certainty unless the resolved source directly supports that level of certainty.

Use parenthetical-only academic attribution in normal essay prose. Do not write the paper's authors as the sentence subject when the paragraph's purpose is to explain course content. Render the mechanism, evidence, limitation, or comparison first, then place the verified author-year citation in parentheses. Author-led narration is allowed only when the user explicitly asks for literature history, discovery chronology, or named-author attribution.

Keep public source-basis notes out of the essay body. Any phrase explaining that the answer is a model answer, not a predicted question, built from supplied documents, or based on a particular source set belongs in the chat response or internal QA, not in the final Essay DOCX.

### Citation Fallback When The User Supplies No Citation List

When the user asks for a complete Example Essay but does not provide citations:

1. Read the relevant lecture slides before searching.
2. Detect citations in slide text, notes, reference slides, footers, figure captions, and OCR/visual inspection of relevant image-only slides.
3. Resolve detected citations by DOI, PMID, author-year, title fragment, journal information, or publisher/PubMed/Google Scholar records.
4. Read the original source before using source-derived content. Green-highlight only the source-derived clause or sentence and include a verified author-year citation.
5. If no usable lecture-slide citation exists, perform targeted academic search for several classic experiments or landmark primary studies that directly test the lecture mechanism, model, method, or evidence claim.
6. Select classic experiments using the same standard inferred from lecture-cited sources: direct mechanistic relevance, primary evidence where possible, reliable academic locator, and verified author-year details.
7. Use no more classic-experiment detail than needed to support the lecture-grounded argument. The essay must remain controlled by lecture logic.

Never cite a source just because it is famous. It must support the exact paragraph claim and be verified from a reliable academic source.

## Extra Reading

Use extra reading only if it directly improves the answer to this exact question.

Separate Extra Reading Papers from Extra Reading Books:

- Citation / Extra Reading Papers are citation-bearing academic sources. Use parenthetical author-year attribution, green highlight, and a verified read/source anchor.
- Extra Reading Books are uploaded recommended books or textbook chapters. Use yellow highlight only for the book-derived phrase or clause, with chapter/section anchoring.
- Do not yellow-highlight papers. Do not green-highlight book material unless it is being used as a verified citation source with explicit citation metadata and claim verification.

Allowed use:

- one mechanism deepener;
- one experimental support point;
- one comparison refinement;
- one modern application or method if directly relevant;
- one theoretical frame for a sector/system claim.

Extra reading must not:

- replace lecture/source logic;
- exceed 15% of essay body words unless instructed;
- become padding added only to raise the Extra Reading ratio;
- introduce unrelated mechanisms;
- contradict official sources without explaining the distinction;
- appear without verified author/year/source details.

If no supplied extra reading exists, perform targeted academic search only when it improves accuracy or citation quality. Prefer peer-reviewed papers, textbooks, DOI/PubMed/publisher pages, and official academic sources.

## Highlight And Source Mapping

For DOCX output:

- ordinary lecture/source content is not highlighted;
- uploaded extra-reading book content is yellow-highlighted;
- verified Citation / Extra Reading Papers and read original sources cited by lecture material are green-highlighted and include author-year citations;
- every highlighted run must map to a source anchor in the source map JSON.
- academic paper attribution is parenthetical author-year only in public prose unless an explicit literature-history request makes author-led narration necessary.

Do not highlight content whose source has not been verified.

## Default KP Synthesis

KP explanations are not complete Example Essays, but they must follow the same low-level prose rules:

```text
claim -> mechanism/process/evidence -> consequence
```

Write the answer paragraph itself, not instructions about writing. Do not narrate slides or pages. Do not preserve coverage by page-by-page summary.

For `exam_prep_notes_docx`, use essay-ready paragraph blocks as an add-on layer only. Do not generate full Example Essays unless the user explicitly requests essay preparation, model essays, full essay-style answers, or complete essay documents.

## QA Flags

Add QA flags when needed:

- `essay_question_scope_uncertain`;
- `source_scope_uncertain`;
- `paragraph_plan_missing`;
- `source_logic_not_preserved`;
- `causal_chain_missing`;
- `comparison_axis_missing`;
- `sector_level_abstraction_missing`;
- `essay_exceeds_word_limit`;
- `example_used_as_fact`;
- `citation_original_unreadable`;
- `lecture_slide_citation_absent_classic_experiment_search_required`;
- `classic_experiment_source_unverified`;
- `classic_experiment_not_question_relevant`;
- `extra_reading_unverified`;
- `extra_reading_not_question_relevant`;
- `extra_reading_too_large`;
- `extra_reading_replaces_core_sources`;
- `recommended_reading_missing`;
- `unsupported_claim`;
- `citation_stack_or_overcitation`;
- `case_detail_overload`;
- `lecture_route_narration_present`;
- `exam_guidance_sentence_present`;
- `citation_strength_overclaim`;
- `slide_or_page_narration_present`.
- `ppt_anchor_missing`;
- `true_but_not_needed_detail`;
- `review_article_drift`;
- `unnecessary_channel_catalogue`;
- `unnecessary_receptor_catalogue`;
- `descriptive_list_without_analysis`;
- `compression_changed_claim_scope`;
- `compression_removed_required_qualifier`;
- `compression_target_exceeds_safe_budget`;
- `protected_source_skeleton_removed`;
- `mechanical_compression_trace`;
- `extra_reading_inserted_before_ppt_logic`;
- `extra_reading_replaces_lecture_logic`;
- `citation_added_without_paragraph_function`;
- `word_count_reduced_but_density_not_improved`.

Fail safe by omitting uncertain material rather than inventing mechanisms, citations, mark schemes, dates, names, statistics, or lecturer preferences.

## Output Contract

When explicitly requested, generate:

```yaml
ExampleEssayOutput:
  requested_or_predicted_question:
  question_deconstruction:
  knowledge_inventory:
  paragraph_plan:
  detail_admission_matrix:
  citation_and_extra_reading_integration:
  compression_budget_estimate:
  expression_efficiency_compression_pass:
  accuracy_preservation_pass:
  analytic_argument_pass:
  extra_reading_insert:
  high_score_example_essay:
  paragraph_function_map:
  source_content_used:
  excluded_content:
  examiner_fit_checklist:
    - source_scope_covered:
    - lecture_logic_preserved:
    - ppt_anchor_for_each_extra_detail:
    - no_true_but_unneeded_detail:
    - no_review_article_drift:
    - analytical_sentences_present:
    - protected_source_skeleton_preserved:
    - compression_preserves_claim_scope:
    - compression_inside_safe_budget:
    - compression_improves_expression_efficiency:
    - examples_used_as_evidence:
    - evidence_interpreted_not_listed:
    - causal_logic_clear:
    - comparison_explicit:
    - evidence_use_controlled:
    - citation_density_controlled:
    - extra_reading_controlled:
    - extra_reading_precision_layer_only:
```

Primary file output:

```yaml
ExampleEssayDOCXOutput:
  default_document: Essay_Module_Example_Essays.docx
  optional_separate_output_folder: Example_Essays_DOCX/
  documents:
    - Essay_Module_Example_Essays.docx
    - optional EE01_<short_safe_question_title>.docx
    - optional EE02_<short_safe_question_title>.docx
  user_facing_only:
    - requested final artefacts
  internal_qa_artifacts_not_returned_unless_requested:
    - example_essay_manifest.json
    - example_essay_source_audit.json
    - EE01_source_map.json
    - EE01_qa.json
    - citation_resolution_log.json
```

Never place a complete essay into one spreadsheet cell. Paragraph-row output is an optional audit export only when explicitly requested.

## Success Condition

The workflow passes if every Example Essay:

- answers the exact question;
- is traceable to read source material;
- compresses low-value repetition without losing required academic detail;
- uses examples as evidence for a broader claim;
- interprets evidence through mechanism, scope, and limitation;
- handles citations conservatively;
- separates source-grounded content from extra-reading enrichment;
- follows the required DOCX output contract.

It fails if it lists facts without reconstructing the argument, uses benchmark/example content as fact, or writes a generic essay from general knowledge.

---

## Source File: `references__essay_synthesis_protocol.md`

---

# Essay Synthesis Protocol

This file is the compatibility entry point for earlier workflow prompts that asked for `essay_synthesis_protocol.md`.

Use `references/kp_essay_synthesis_protocol.md` as the legacy/internal protocol for KP-level essay synthesis linting.

Use `references/essay_generation_protocol.md` as the operative protocol for:

- Example Essay Mode;
- lecture-logic extraction;
- knowledge inventory;
- lecturer-intent analysis;
- paragraph planning;
- extra-reading insertion;
- mechanism-heavy essay contribution checks from benchmark fixtures;
- comparison-axis and style-exemplar contribution checks from benchmark fixtures;
- DOCX-first output for explicit Example Essay Mode;
- paragraph-row exports only as optional audit artefacts when explicitly requested.

KP synthesis and full Example Essay Mode are separate:

- KP synthesis writes one compact concept-first paragraph fragment per knowledge point.
- Example Essay Mode writes complete answers only when essay prep or Example Essays are explicitly requested and exports `Essay_Module_Example_Essays.docx` by default, or one standalone DOCX per essay when separate files are requested.

If this file and `kp_essay_synthesis_protocol.md` appear to conflict for KP-level prose linting, follow `kp_essay_synthesis_protocol.md`. If this file and `essay_generation_protocol.md` appear to conflict for full Example Essays, follow `essay_generation_protocol.md`.

---

## Source File: `references__essay_tutor_workflow_protocol.md`

---

# Essay Tutor Workflow Protocol

Use this protocol for `essay_exam_prep`, complete Example Essays, model essays, assessed-style essay drafts, essay plans, citation-controlled essay work, and essay figure/table/data support.

This protocol extends the existing lecture-first Example Essay route. It does not replace `essay_generation_protocol.md`, `example_essay_docx_output_protocol.md`, or `language_quality_contract.md`.

## Core Rule

Complete essay work follows this chain:

```text
EssaySkillConfig
-> EssayInputReadinessReport
-> DeepResearch
-> DetailedEssayPlan
-> PlanApprovalGate
-> SubagentOrRoleResearch
-> Draft
-> CitationFigureTableDataQA
-> DOCXOrFinalOutput
```

Do not draft a complete final essay before the plan is approved unless the user explicitly asks to skip the approval loop or requests direct generation.

For exam-prep package generation, a user request such as "generate the essay pack" or "make the Word document now" counts as approval to execute the planned route after the source-readiness gate passes.

## Essay Intake

Collect the smallest blocking set first. Continue with labelled assumptions when the missing information does not block planning.

Required when available:

| Field | Capture |
| --- | --- |
| Essay topic or exact question | Exact wording, whether the title can change, and whether it is an assessed prompt. |
| Word limit | Upper limit, lower limit, tolerance, and whether references, title, captions, figures, tables, and abstract count. |
| Academic level | Undergraduate, master's, doctoral, professional, or exam-prep level. |
| Course/module context | Module, faculty, lecture block, learning outcomes, and target source set. |
| Required format | Chat plan, Markdown, DOCX, PDF, headings, abstract, figures, tables, or separate essay files. |
| Citation style | APA, Harvard, Vancouver, AMA, IEEE, Chicago, MLA, journal style, or university style. |
| Source base | Lecture slides, official notes, reading list, required papers, uploaded papers, textbooks, practical materials, datasets. |
| Rubric | Marking criteria, feedback, grade descriptors, K/C/U/A/R expectations, or learning outcomes. |
| Stage | Planning only, first draft, revision, final polish, or DOCX generation. |
| AI-use policy | Whether AI-assisted writing is allowed and whether a disclosure is needed. |

Strongly recommended:

- target grade or standard;
- required number and type of sources;
- recency requirement;
- user's intended thesis or preferred argument;
- forbidden sources, theories, or content;
- figure, table, or data-analysis requirements;
- previous feedback;
- preferred example essays for style only.

Ask at most one blocking clarification question at a time. If a field is not blocking, record it under:

```yaml
EssayAssumption:
  field:
  assumed_value:
  risk_if_wrong:
EssayOpenRequirement:
  field:
  why_it_matters:
  when_to_resolve:
```

## DeepResearch Before Planning

Before a full plan, run enough research to avoid a generic outline:

```text
Topic deconstruction
-> key concepts
-> source-scope boundary
-> competing models or mechanisms
-> required lecture/source logic
-> seminal sources
-> recent evidence when relevant
-> methodological limits
-> clinical/theoretical/translation implications
-> critical debates
-> figure/table/data opportunities
-> citation map
```

For course-linked essays, official lecture/source logic remains the skeleton. External search sharpens mechanism, evidence, limitations, or citations only after source scope is clear.

Plan-stage citation rule:

- Use exact author-year, DOI, PMID, title, journal, or "recent review" claims only after verification.
- If a source has not been verified, label it `candidate_source`.
- Candidate sources may guide planning but must not enter the draft, reference list, green highlight, or DOCX until metadata and claim relevance are verified.

## Detailed Essay Plan

Every complete essay plan must go below heading level. The main body must include subtitles or paragraph blocks, not only `Introduction`, `Main Body`, `Discussion`, and `Conclusion`.

Use this shape:

```yaml
DetailedEssayPlan:
  essay_question:
  interpreted_scope:
  excluded_scope:
  working_thesis:
  word_limit_strategy:
  proposed_title:
  source_scope:
    official_sources:
    required_readings:
    external_sources_allowed:
    candidate_sources:
  section_plan:
    introduction:
      function:
      content_sequence:
      key_terms_to_define:
      thesis_move:
    main_body:
      - heading:
        section_function:
        subheadings:
          - subtitle:
            specific_content:
            key_claim:
            evidence_needed:
            analytic_angle:
            candidate_or_verified_citations:
        transition_to_next_section:
    discussion:
      synthesis_paragraph:
      limitations_paragraph:
      future_direction_paragraph:
    conclusion:
      final_answer:
      no_new_evidence_rule:
  citation_strategy:
    intensive_reading_citations:
    broad_support_citations:
    classic_sources:
    recent_sources:
  figure_table_data_strategy:
    figures:
    tables:
    data_analysis:
  critical_thinking_strategy:
    main_body_analytic_targets:
    discussion_analytic_targets:
  assumptions:
  open_questions:
```

## Approval Loop

Use this loop unless the user explicitly asks to skip it:

```text
Plan v0.1
-> user edits
-> Plan v0.2 with concise change log
-> repeat until approval
-> draft from approved plan
```

Rules:

- Revise only requested parts unless the change creates a dependency.
- Preserve approved thesis, section hierarchy, paragraph logic, citation strategy, critical-thinking targets, and visual/data strategy.
- Treat "Approve Plan", "approved", "go ahead", or explicit file-generation instruction as approval.
- If new research contradicts the approved plan, stop and request plan revision instead of silently changing the argument.

## Research Roles

Use real subagents when available and appropriate. Otherwise execute these roles sequentially:

```yaml
QuestionAndRubricAgent:
  command_verb:
  required_scope:
  excluded_scope:
  required_argument:
  examiner_expectation:
  off_topic_risk:

LiteratureRetrievalAgent:
  must_read:
  should_read:
  optional:
  excluded:
  identifier:
  claim_supported:
  verification_status:

MechanismTheoryAgent:
  model:
  mechanism:
  source:
  evidence_strength:
  limitation:
  essay_section:

EvidenceAppraisalAgent:
  claim:
  supporting_sources:
  evidence_type:
  strength:
  limitation:
  allowed_verbs:

CitationAgent:
  citation_key:
  source:
  DOI_or_PMID_or_URL:
  used_for_claim:
  citation_mode:
  in_text_location:
  bibliography_entry:
  verification_status:

FigureTableDataAgent:
  figure_needed:
  figure_type:
  source_backed_claims:
  reuse_permission_status:
  table_needed:
  data_analysis_needed:
  legend_or_caption:
```

Accept role output only after checking that sources exist, identifiers are verified where possible, claims match source scope, and uncertainty is labelled.

## Drafting Standard

Write from the approved plan.

Default paragraph:

```text
Claim -> mechanism/evidence -> interpretation -> scope or limitation -> link back
```

Evidence-heavy paragraph:

```text
Evidence -> mechanism tested -> result -> interpretation -> limitation
```

Comparison paragraph:

```text
Shared problem -> comparison axis -> model A -> model B -> evidence -> evaluation
```

Minimum analytic target:

```yaml
AnalyticMinimum:
  main_body: at_least_30_percent
  discussion: mostly_analytic
  conclusion: synthesis_without_new_evidence
```

Do not solve weak analysis by adding a detached final sentence. Rewrite the paragraph so evidence and interpretation are adjacent.

## Citation Strategy

Use two citation modes:

1. Intensive-reading citation: one sentence, several sentences, or one paragraph focuses on one core paper. Use this for landmark mechanisms, primary experiments, trials, and paper-specific limitations.
2. Broad-support citation: one synthesis sentence cites several verified sources only when every source supports the same claim.

Formatting and metadata:

- Resolve DOI, PMID, ISBN, arXiv, publisher page, or official source where possible.
- Prefer CSL-compatible formatting and verified metadata. Citation.js or similar CSL-compatible tools may be used when available and license-compatible.
- CSL styles may be used for journal or university styles when available.
- Do not scrape citation-generator websites or copy third-party Skill code without license review.

## Figure, Table, And Data Rules

Directly reuse academic paper images only when the licence or permission allows the intended use. Citation alone is not permission.

If licence or permission is unclear, do not reproduce the image. Create an original source-backed schematic instead.

Use:

```yaml
FigureReuseGate:
  source:
  figure_number:
  licence:
  permission_status:
  can_reuse_directly:
  required_attribution:
```

Generated mechanism figures:

- must be original schematics;
- must represent only source-backed claims;
- must not copy lecture, textbook, paper, or private figure layouts;
- must include a legend stating that the image is generated, original, and not reproduced from a published article or course material.

Data figures:

- Use GraphPad Prism when available and appropriate for the graph and analysis.
- Use Prism scripts or PZFX workflows only through official Prism functionality or license-compatible automation.
- If Prism is unavailable, use a reproducible local analysis workflow and state that Prism output was not generated.
- Report test choice, assumptions, effect size, confidence interval where appropriate, and a concise methods sentence.

Academic tables:

- no vertical lines;
- top rule, header rule, bottom rule;
- concise caption above;
- abbreviation/source note below;
- only include information used by the argument.

## Final QA

The essay fails or must be revised when it contains:

- invented citations;
- unverified source metadata used as verified evidence;
- fake statistics;
- unsupported mechanisms;
- lecture/source-route narration inside essay prose;
- mainly descriptive discussion;
- overclaimed causality;
- paper figure reuse without licence or permission;
- generated figures that introduce unsupported content;
- decorative tables;
- a conclusion with new evidence;
- word-limit violation without warning.

---

## Source File: `references__evidence_policy.md`

---

# Evidence Policy

## Source Priority

Use sources in this order:

1. exact lecture slides supplied by the user;
2. official course notes, handouts, practice materials, and exam guidance supplied by the user;
3. exact formal past papers supplied by the user;
4. marking criteria, exemplar answers, and essay tutorials supplied by the user;
5. official university or publisher material;
6. peer-reviewed papers, reviews, textbooks, PubMed, Google Scholar, DOI/publisher pages.

Do not use social media, influencer content, Q&A/content platforms, generic web summaries, or unproven traditional medicine claims.

## Example Essay Evidence Classes

```yaml
EvidenceUse:
  lecture_slide_core:
    meaning: relevant lecture slide content
    highlight: none
    allowed_use: primary essay factual content and answer logic

  extra_reading_book:
    meaning: uploaded textbook/book/chapter material supplied by the user for enrichment
    highlight: yellow
    allowed_use: compact precision layer, usually 5-10% of Example Essay body, with 15% as a hard cap unless the user requests more

  lecture_slide_citation_original:
    meaning: original paper/book/theory cited on relevant lecture slides and read by the Skill
    highlight: green
    allowed_use: brief evidence or mechanism refinement with author-year in-text citation

  classic_experiment_source:
    meaning: verified classic or landmark primary experiment found because relevant lecture slides contain no usable citations
    highlight: green
    allowed_use: brief experimental evidence directly supporting the lecture mechanism, with author-year in-text citation

  docx_format_reference:
    meaning: user-supplied PDF, image, screenshot, or previously generated DOCX showing desired Word layout, highlighting, captions, or citation style
    highlight: none
    allowed_use: transferable formatting and style rules only, not biological content, target facts, or prediction evidence
```

Hard rules:

```text
Lecture slides control the answer logic.
Citation / Extra Reading Papers and Extra Reading Books may refine the answer but must not displace the lecture sequence.
A citation printed on a slide is not enough. The cited original source must be resolved and read before any content from that source is inserted into the essay.
Do not copy author-year citations from slides into the essay unless the cited source has been resolved and the relevant claim verified.
In public essay prose, academic paper author names belong in parenthetical author-year citations, not as the subject of the explanatory sentence, unless the user explicitly requests literature-history narration.
If a cited source cannot be read, omit source-derived details and flag the unresolved citation.
If the user supplies no citations for an Example Essay, actively mine lecture slides for citations before searching externally.
If relevant lecture slides contain no usable citations, find several verified classic experiments or landmark primary studies through academic search. Use them only when they directly support the lecture-grounded paragraph claim.
If Extra Reading Books are uploaded, locate the relevant chapter/section before using them. Do not cite or highlight a whole book vaguely.
If Extra Reading Papers are supplied or discovered, treat them as citation sources: verify metadata and relevant claims, use parenthetical author-year citation, and green-highlight only the paper-derived phrase, clause, or sentence.
Do not yellow-highlight academic papers. Yellow is reserved for uploaded Extra Reading Book chapter/section content.
Formatting reference PDFs are layout/style evidence only and must not supply biological claims.
During essay planning, unverified external sources are candidate sources only. Do not place them in the final draft, reference list, DOCX, or highlight map until metadata and claim relevance are verified.
```

## Example Evidence Use

External examples and benchmark fixtures are not reusable factual evidence for a new target source set. Classify every example source into one of these source-use classes before it can influence workflow design:

- `target_content_evidence_only`: target lecture slides, official notes, formal papers, or guidance that may support factual content for the same target source set.
- `benchmark_regression_example`: named benchmark material used to test whether the Skill behaves correctly on a known fixture.
- `generic_workflow_contribution`: an external example distilled into a transferable workflow rule, output pattern, QA check, or evidence-handling discipline.
- `style_only_exemplar`: exemplar answer, essay draft, handwritten example, or image used only for wording, structure, density, answer organisation, and paragraph logic.
- `non_transferable_content`: topics, named systems, lecturer-specific preferences, exact year recurrence, case details, or subject facts that must not be reused unless independently present in the target source set.

Hard rule:

```text
Do not use an external example as content evidence for a target source set.
An example may only contribute workflow logic, output style, archetype structure, QA checks, or evidence-handling discipline.
```

If a workflow applies a lesson learned from a benchmark, record the structural trigger from target evidence, not the benchmark identity. For example, record `current paper contains mini-essay plus data/problem sections`, not a named-example comparison.

## ExtraReadingVerifier

- Use only peer-reviewed reviews, primary papers, textbooks, official course-recommended readings, PubMed/Google Scholar/DOI/publisher pages.
- Verify author surname and year before using in-text citations.
- Never copy citations from exemplars without independent verification.
- If unverified, place under `Needs verification` and do not insert into essays.

Extra Reading source priority:

1. official recommended reading listed in lecture slides, Canvas reading list, course notes, or lecturer guidance;
2. textbook or book chapter used by the course/module if explicitly supplied;
3. papers, reviews, datasets, methods, or book chapters explicitly named in the lecture slides;
4. if no official book/reading is supplied, ask whether the user has a recommended book or reading list;
5. if unavailable, use peer-reviewed reviews, primary papers, textbooks, PubMed, Google Scholar, DOI pages, or publisher pages.

Extra reading may be inserted into essays only as:

- one precise sentence inside a mechanism paragraph;
- one short named-detail insertion inside an otherwise lecture-derived sentence;
- one comparison point that sharpens the lecture argument;
- one evidence-based example that strengthens the lecture mechanism.

Use a separate enrichment paragraph only when the essay question requires it and the paragraph still advances the lecture-derived argument. It must not replace lecture content, exceed 15% of the essay, introduce an unrelated mechanism, contradict slides without explanation, or appear without verified source anchoring. In explicit Example Essay Mode, uploaded Extra Reading Book content should normally be a compact 5-10% precision layer when relevant chapter/section evidence is found; 10-15% is allowed only when the question genuinely benefits from that detail. Those book-derived words must be yellow-highlighted. Verified paper-derived words are citation content, not book content, and must be green-highlighted with parenthetical author-year citation.

For sentence-level micro-detail insertions, the source rule is stricter: the inserted phrase must be directly supported by a verified chapter, section, original paper, or classic source. Keep the addition compact enough that it remains a phrase or short clause inside the original sentence. Highlight only the inserted phrase. Reject the insertion if it changes the claim, starts a new topic, duplicates nearby detail, requires a new explanatory sentence, or makes the extra-reading detail dominate the lecture-derived claim.

Classic-experiment fallback is not a licence to broaden the answer. Use it only after confirming that relevant lecture slides contain no usable citations, and only for directly relevant experiments with verified author-year/source details. Classic experiments are green-highlighted citation-source content, not yellow-highlighted Extra Reading Book content.

For non-essay long-answer/project answers, extra reading should be one compact refinement only. It may support a named method example, clarify a limitation, justify a technique choice, or add directly relevant method context. It must not become a second answer.

## Exemplar Distillation

Use exemplar answers for:

- answer structure;
- paragraph grammar;
- comparison strategy;
- density and tone;
- strong vs weak answer pattern detection.

Do not use exemplar subject claims as factual authority unless verified from lectures or reliable sources.

For handwritten/image exemplars:

- classify them as `exemplar_image` when possible;
- use them for essay structure, paragraph logic, density, comparison strategy, and academic phrasing only;
- ignore Chinese annotations unless the user explicitly asks to use them;
- treat student Chinese annotations as non-course evidence by default;
- mark `visual_inspection_required` when handwriting or image quality limits extraction;
- never use image exemplar content as factual evidence unless verified from lecture slides, official notes, or reliable academic sources.

## Hard Negatives

Do not:

- pool content prediction evidence across different course/module groups;
- pool old and new exam regimes as if they were one statistical distribution;
- treat topic frequency as sufficient evidence when archetype/slot grammar contradicts it;
- infer lecture deck years from citation/reference years embedded in slide text;
- silently resolve conflicts between current lecture guidance and formal past-paper format;
- invent exact graph values from image-only figures or weak OCR;
- invent missing Paper 1, Section A, answer-key, mark-scheme, or official-answer content;
- invent an exact exam-regime transition year when files are missing between regimes;
- treat every past-paper question as essay;
- let Section A contaminate essay prediction;
- use short-answer papers as direct essay prediction evidence;
- use exemplar answers as factual authority;
- use an external example as content prediction for a target source set;
- write a benchmark-specific instruction outside an explicit regression context;
- apply an example lesson without a matching target evidence condition;
- insert unverified citations;
- present candidate sources as verified essay evidence;
- reuse academic paper figures, tables, or images without licence, permission, user-provided rights, or a clearly allowed private-study boundary;
- skip slide-citation mining when the user does not supply citations for Example Essay generation;
- use classic experiments before checking whether lecture slides contain usable citations;
- use famous experiments that are not directly relevant to the exact paragraph claim;
- insert extra reading that is not directly relevant to the exact essay question;
- let extra reading replace lecture logic;
- use more than one focused extra-reading insert unless the user explicitly requests more;
- overfill essays to reach word count;
- put full essays into single unreadable cells;
- keep source evidence in diagnostics or explicit audit packages;
- expose evidence columns or helper artifacts in student-facing output unless the user explicitly asks for an audit package;
- present predictions as official exam questions;
- apply SBS essay rubric to short-answer/MCQ answers;
- edit, rename, delete, or overwrite source files.

## Essay QA Flags

Use these flags when applicable:

- `essay_question_scope_uncertain`
- `lecturer_intent_low_confidence`
- `paragraph_plan_missing`
- `lecture_logic_not_preserved`
- `causal_chain_missing`
- `comparison_axis_missing`
- `essay_exceeds_word_limit`
- `example_used_as_fact`
- `extra_reading_unverified`
- `extra_reading_not_question_relevant`
- `extra_reading_too_large`
- `extra_reading_replaces_lecture_content`
- `extra_reading_not_integrated`
- `extra_reading_overused`
- `recommended_reading_missing`
- `unsupported_mechanism_claim`
- `example_used_as_content_prediction`
- `example_missing_transferable_contribution`
- `example_non_transferable_content_not_marked`
- `cross_source_content_leakage`
- `benchmark_specific_instruction_outside_regression_context`
- `example_claim_used_without_verification`
- `regime_example_applied_without_format_match`
- `question_type_example_applied_without_question_type_match`
- `citation_detected_on_slide`
- `candidate_source_needs_verification`
- `candidate_source_used_as_verified`
- `citation_original_resolved`
- `citation_original_unreadable`
- `citation_original_used_without_reading`
- `lecture_slide_citation_absent_classic_experiment_search_required`
- `classic_experiment_source_verified`
- `classic_experiment_source_unverified`
- `classic_experiment_not_question_relevant`
- `green_highlight_missing_citation`
- `green_highlight_missing_source_anchor`
- `extra_reading_book_supplied`
- `extra_reading_chapter_found`
- `extra_reading_chapter_not_found`
- `extra_reading_used_without_chapter_anchor`
- `extra_reading_ratio_below_10_percent`
- `extra_reading_ratio_above_15_percent`
- `yellow_highlight_missing_source_anchor`
- `essay_paragraph_missing_lecture_anchor`
- `essay_not_tightly_lecture_grounded`
- `docx_format_lint_failed`
- `figure_reuse_permission_missing`
- `generated_figure_contains_unsupported_claim`

---

## Source File: `references__exam_prep_core_workflow.md`

---

# Exam Prep Core Workflow

This protocol replaces schema-first note dumping with a purpose-first exam-preparation workflow. It applies to ordinary lecture review, practical/data preparation, MCQ preparation, short-answer preparation, long-answer/project/scenario preparation, and essay preparation.

## Purpose

The Skill exists to help a student revise examinable knowledge. The default artifact must therefore explain the course content clearly, not preserve raw slides, administrative metadata, internal planning fields, or every line that was extracted from an upload.

The core output is always:

```text
Lecture_Knowledge_Walkthrough.docx
```

Question-type reports are add-ons. They are never allowed to replace the knowledge walkthrough.

## First-Principles Workflow

```text
1. Classify source roles.
2. Remove non-knowledge noise.
3. Estimate source scale and coverage budget.
4. Read the source set for meaning.
5. Reconstruct lecture/session order and concept modules.
6. Build enough public lecture modules for the source scale.
7. Explain each module in exam-ready direct prose.
8. Run module teaching depth and readability layout gates.
9. Keep question-type overlays separate unless explicitly requested.
10. Run surface, density, noise and layout QA.
```

The model must not be forced to write from slide fragments. The model should use source order to understand prerequisites and teaching sequence, then organise the output by exam-useful conceptual logic.

The public notes should become lecture-first micro-module teaching notes. They must explain what each knowledge point means, how it works, how it is read or used, and what boundary, limitation, calculation or decision follows. They must not preserve coverage by narrating what the course, lecture or source material says.

## Source Role Classification

For every input block, classify it as one of:

- `subject_knowledge`: definitions, mechanisms, structures, methods, experiments, calculations, diagnostic rules, examples, figures, data patterns, limitations.
- `exam_pattern`: past-paper question wording, mark distribution, question type, command verb, recurring operation.
- `practical_operation`: protocol steps, apparatus, reagents, controls, calculations, safety-relevant handling when it changes interpretation.
- `extra_reading`: recommended book chapter, cited paper, review or primary paper.
- `style_or_layout_example`: reference output used only for structure, density, language and layout.
- `non_knowledge_noise`: contact details, staff lists, attendance, course admin, assessment logistics, QR codes, URLs, reading-list logistics, image credits, copyright, acknowledgements, decorative quotes, slide agenda, lecture schedule, generic learning outcomes and generic advice.

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` can become public knowledge prose. `exam_pattern` informs emphasis and add-ons but must not appear as raw exam prediction content in the DOCX unless the user explicitly requests an audit. `non_knowledge_noise` is discarded from student-facing artifacts.

## Hard Public Exclusion List

The default public notes must not contain:

- lecturer names, emails, phone numbers, office locations, staff lists or unit coordinator details;
- SEAtS, Mentimeter, QR code, attendance-code, Blackboard, live session or lecture-room instructions;
- assessment logistics, coursework percentages, exam date/time, closed-book logistics or mark-split admin, except inside a chat-only exam-analysis brief requested by the user;
- bookshop adverts, library-availability notes, URL-only lines, image credits, copyright notices or source filenames;
- decorative quotations, thank-you slides, lecture agendas, contents slides, what-you-will-learn slides, or generic ILOs unless the ILO contains a specific examinable concept;
- raw slide bullets copied line-by-line;
- broken OCR fragments that do not form a biological, chemical, clinical, mathematical or methodological claim.

## Source Scale Budget

The walkthrough must be scaled to the source set. A short post-lab or mock exam should not become the size of a whole-course notebook. A whole-course source pack must not be compressed to the size of a short practical unit.

When the user asks to `analyse this course`, `分析这门课`, or asks for course-level prep analysis without explicitly requesting an audit-only profile, treat the request as a knowledge walkthrough request. A short source inventory, metrics report, or sample-only profile is not a substitute for the public knowledge document.

Before drafting, create an internal budget:

```yaml
SourceScaleBudget:
  source_units_count:
  source_pages_or_slides_estimate:
  source_information_profile_status: measured | estimated | missing | not_applicable
  informative_page_count:
  non_informative_page_count:
  information_mass_units:
  average_information_score:
  page_information_profile:
    - source_id:
      page_index:
      category: knowledge_dense | knowledge_standard | light_context | cover | lecture_plan_or_admin | video_or_media_placeholder | blank
      informative: true | false
      information_score:
      exclusion_reason:
  source_types:
  conceptual_module_target_range:
  examinable_unit_target_range:
  target_public_units_min:
  target_words_min:
  explanation_depth:
    - concise
    - standard
    - expanded
  minimum_visible_coverage_floor:
  compression_reason:
```

Budget rules:

- Small practical/mock/post-lab packs can be concise when the examinable domain is narrow.
- Medium lecture packs need enough modules to cover all conceptual areas, not only the first few lectures.
- Broad course packs need expanded coverage. A 10-20 lecture source pack normally requires many more examinable units than a short practical pack, even after compression.
- Do not use Experimental Biology or any short practical unit as a size cap for larger courses.
- Do not use page count alone. First profile each slide/page when practical. Covers, title-only separators, lecture plans, reading/admin pages, pure video placeholders and blanks can be excluded from `informative_page_count`, but the exclusion ledger must record why.
- Increase coverage when the source contains distinct mechanisms, methods, calculations, disease examples, pathways, data operations, labelled diagrams/tables, speaker-note detail, graph logic, or named experimental evidence.
- If `informative_page_count` and `information_mass_units` are available, they set the main floor. Raw page/slide count remains audit context unless no reliable information profile exists.
- If `target_public_units_min` or `target_words_min` is below the derived floor, the budget is invalid. A polished short document is still a failed release if it falls below the source-scale floor.
- If a high-quality reference DOCX is supplied, use it for density and layout calibration only. A larger or denser target course must exceed the reference's visible knowledge prose unless the information profile proves the target is smaller or sparse.
- If source material is large but the output is short, record a `coverage_floor_failure` and regenerate from the distillation pass.

Indicative internal floors, to be adapted by evidence density:

- 1-10 pages/slides: at least 8 public units and about 420 visible words.
- 11-80 pages/slides: at least 12-25 public units and 1k-3k visible words.
- 81-200 pages/slides: at least 50 public units and about 5.8k visible words.
- 201-500 pages/slides: at least 105 public units and about 14k visible words.
- 501-800 pages/slides: at least 150 public units and about 20k visible words.
- 801+ pages/slides: at least 180 public units and about 25k visible words, or multiple deliverable volumes.

These are not student-visible promises. They prevent accidental over-compression.

## Lecture-First Reconstruction

Before writing, reconstruct the public lecture plan:

```yaml
PublicLectureNotesPlan:
  public_lecture_sections:
    - lecture_title:
      modules:
        - module_title:
          knowledge_functions:
          explanation:
          blocks:
```

The public document starts with the title and then lecture/session headings. `Course Knowledge Map` is internal-only. Do not list uploaded file titles or source inventories in the public document.

Use micro-module headings beneath each lecture. A module heading should name the exact mechanism, readout, calculation, distinction, example function or limitation. If a broad lecture theme contains several separable operations, split it before drafting.

## Examinable Knowledge Unit

Each public unit must be one coherent explanation:

```yaml
ExaminableKnowledgeUnit:
  title:
  priority: high | medium | low
  source_support:
  explanation:
  optional_equation_or_example:
  common_confusion_or_boundary:
```

The `explanation` must be a connected paragraph or a short sequence of explanatory paragraphs. It must answer the useful questions: what is this, why does it work, how does the mechanism/calculation/experiment proceed, and what follows from it. It must use exam-ready direct prose rather than source narration. Public text such as `The course frames`, `The source material identifies`, `The lecture material uses` or `The source states` is a release failure.

Do not write a unit as:

```text
Definition: ...
Mechanism: ...
Logic: ...
Example: ...
```

Do not write a unit as a raw list of source bullets.

## Compression Rules

The default walkthrough is selective. It should not attempt to preserve every extracted phrase.

Keep:

- central definitions and distinctions;
- causal mechanisms and process order;
- experimental evidence and what it proves;
- formulas, units and worked calculations;
- assay/protocol logic and interpretation rules;
- named examples only when they teach a reusable concept;
- diagrams/figures only when they help explain a knowledge point.

Discard:

- administrative lines;
- duplicate slide titles;
- generic aims and learning outcomes unless rewritten into a real knowledge claim;
- one-word fragments, orphaned labels, page numbers and source artefacts;
- named people, institutions or citation debris unless the identity is examinable content.

Compression must preserve coverage of the main examinable mechanisms. It may remove repetition; it may not remove entire lecture blocks, mechanisms, calculations, experiments or conceptual families without an explicit source-role reason.

## Question-Type Add-ons

After the walkthrough is clear, add only the requested or detected add-on:

- `mcq_exam_prep`: common discriminators, high-value facts, trap logic and compact answer rules.
- `short_answer_exam_prep`: likely answerable knowledge units, concise model answers and highlighted mark-producing terms.
- `long_answer_project_scenario_prep`: method/readout/control/limitation blocks and worked example answers.
- `essay_exam_prep`: module-level essay plans or full module-level Example Essays when essay mode is requested.

Past-paper prediction is a chat brief used before generation. It must not become a prediction file by default.

## Output Shape

Default DOCX structure:

```text
Title
Lecture 1: source/session-specific heading
  topic-specific module heading
  connected notes
Lecture 2: source/session-specific heading
  topic-specific module heading
  connected notes
...
```

Within a module, use headings that name the concept, such as:

```text
Membrane transport is required because lipid bilayers exclude polar solutes
Electrochemical gradients combine concentration and voltage
Aquaporin selectivity comes from pore size, charge and NPA motifs
```

Do not use headings such as:

```text
Contents
Aim
Lecture objective
Definition
Key point
Evidence used
Source coverage
```

## QA Gate

Fail and rewrite if any of these are true:

- the output is much shorter than the source scale budget without a defensible compression reason;
- more than a small minority of visible lines are copied slide bullets;
- the output contains course admin or staff/contact/logistics text;
- the output contains Course Knowledge Map, source role summary, extraction limitation, strategy or prediction sections;
- a section is mostly names without explanations;
- labels and bullets replace connected explanation;
- the model preserved broken OCR instead of reconstructing meaning;
- figures create large blank areas without improving readability;
- add-on exam analysis appears before the knowledge has been made clear.

---

## Source File: `references__exam_prep_notes_protocol.md`

---

# Exam Prep Notes Protocol

`exam_prep_notes_docx` is the default route for revision, ordinary notes, general exam preparation and requests to go through course material. It produces:

```text
Lecture_Knowledge_Walkthrough.docx
```

The route is lecture-first, knowledge-only and source-backed. It is not an audit report, source inventory, prediction report, strategy report, slide dump or fixed-length summary.

## Pipeline

```text
SourceRoleMap
-> NonKnowledgeNoiseFilter
-> SourceDistillationPass
-> LectureSessionMap
-> SourceScaleBudget
-> PublicLectureNotesPlan
-> PublicModuleDepthPass
-> ExamReadyDirectProsePass
-> ReadabilityLayoutPass
-> KnowledgeSurfaceContract / NonKnowledgeGate
-> RouteStyleRenderer
```

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` may become public prose. `exam_pattern` can shape internal emphasis only. `non_knowledge_noise` is discarded before public drafting.

## Public Plan Contract

Ordinary notes must render only this public contract:

```yaml
PublicLectureNotesPlan:
  title:
  target_group_key:
  source_scale_budget:
  output_language_profile:
    output_language: English
    allow_bilingual: false
  route_docx_style_profile:
    route: exam_prep_notes_docx
    margin_cm: 2.0
    line_spacing: 1.05-1.15
    body_alignment: left
    title_alignment: left
    heading_alignment: left
    image_alignment: center
    text_color: black
    theme_colours_allowed: false
    blue_heading_styles_allowed: false
  public_lecture_sections:
    - lecture_title:
      lecture_scope:
      modules:
        - module_title:
          knowledge_functions:
            - definition_boundary | mechanism_process | method_readout | graph_data_interpretation | calculation_unit_worked_example | named_example | limitation_trap
          explanation:
          blocks:
            - block_type:
              label:
              content:
```

`knowledge_functions` is a depth gate. Each module needs at least two relevant functions so the output teaches more than a shallow topic label.

The public plan is a micro-module teaching plan. A lecture can remain broad, but module titles should identify the exact operation, distinction, readout, calculation or boundary being taught. Do not use generic module titles such as `Overview`, `Introduction`, `Key concepts` or `Background` as final public headings.

## Public Structure

Default public structure:

```text
Title
Lecture 1: source/session-specific knowledge heading
Concept-specific module heading
Connected explanation
Useful equation, worked example, graph/data rule, named example, comparison or limitation
Lecture 2: ...
```

Do not render `Course Knowledge Map`, `Source Role Summary`, `Source Scope`, `Extraction Limitation`, `Conceptual Course Map`, `Examinable Knowledge Units`, `Predicted Essay Theme`, `Study Order`, `Section A Strategy`, `Section B Strategy`, `How To Answer`, `A strong answer should`, or `Use This Module`.

## Module Depth

A public module should follow the chain:

```text
concept -> why it matters -> mechanism/method/calculation/readout -> interpretation -> limitation or boundary
```

Use `ExaminableKnowledgeUnit` and `CourseModule` only as internal planning vocabulary if needed; do not expose those labels. `SurfaceLabelDecision`, `LabelDecision` and `semantic_sparse` label policy mean labels are visible only when they improve equations, worked examples, controls, comparisons or tables. Avoid `rigid_template_bucket` headings, `colon-slot fragmentation`, repeated `Definition:`/`Workflow:` labels and `shorthand arrow chains` as the main explanation.

Module teaching depth must be checked before release:

- a definition module must state the boundary or distinction, not just the term;
- a mechanism module must explain the process and consequence;
- a method module must state the readout, control or interpretation;
- a graph/data module must state axes or pattern and the inference;
- a calculation module must separate formula, units, substitution and result interpretation;
- an example module must state what the example demonstrates;
- a limitation module must state the trap, false inference or boundary.

## Language

Default public output is English. Translate source-language mixtures into English unless the user explicitly requests Chinese or bilingual output. Technical terms may stay in English even in non-English outputs.

Write exam-ready direct prose. Do not narrate the source route in the public document. Forbidden source narration includes `The course frames`, `The source material identifies`, `The lecture material uses`, `The source states`, `The lecture introduces`, `The material describes`, and equivalent wording. Rewrite these as direct claims about the knowledge itself.

Use the transferable Example Essay language rules for notes: start with the claim or problem, keep mechanism and interpretation adjacent, avoid repeated negative framing, avoid A-B-A restatement, use examples as evidence, and attach every named detail to a function or consequence.

## Source Scale

Use the source-adaptive coverage budget before drafting. `source_units_count`, informative page counts, information-mass estimates and `minimum_visible_coverage_floor` set the lower bound for modules and words. `coverage_floor` failure blocks release.

If a broad source pack produces a short overview, regenerate from source distillation. A concise answer is acceptable only when the source pack is genuinely small or sparse and the internal budget proves it.

## Style

Ordinary notes use black Arial, 2.0 cm margins, compact 1.05-1.15 spacing, left-aligned body text, left-aligned headings and centered images. Example Essay outputs keep the separate essay style controlled by `EssayAdaptiveBudget`: 2.5 cm margins, 1.5 spacing and justified body text.

Readability layout means controlled segmentation, not empty spacing. Split dense explanations into short paragraphs or blocks when the content contains parallel criteria, workflow steps, graph rules, formulas, controls, limitations or worked examples. Keep formulas and worked calculations separated from long prose. Use source visuals only when readable and materially useful; generated visuals remain optional revision aids, not evidence.

## Add-ons

MCQ, short-answer, long-answer, practical/data and essay add-ons come after the base notes. Predictions, strategy sections and answer-advice reports must remain separate from ordinary notes unless the user explicitly requests that separate report.

## QA Gate

Block and regenerate if the public notes contain raw slide bullets, source_route_narration, source narration, ai_process_or_provenance, source maps, QA flags, source anchors, evidence scores, confidence bands, internal manifests, helper JSON, unsupported claims, inventory-only prose, missing module teaching depth, over-dense readability layout, non-black/theme-colour text, blue heading styles, justified ordinary-note body text, non-compact spacing, or any forbidden heading listed above.

---

## Source File: `references__example_analysis_protocol.md`

---

# Example Analysis Protocol

This protocol defines how the Skill learns from examples without turning examples into content triggers.

Examples include:

- user-uploaded model essays;
- screenshots of writing advice;
- ChatGPT shared conversations;
- handwritten or annotated answers;
- non-biological science essays;
- existing generated workbooks or DOCX essays;
- benchmark fixtures;
- answer keys and reasoned solutions;
- formative feedback and marking criteria.

## Core Rule

Examples can teach structure, language, diagnosis, and QA. They cannot supply factual claims, predicted topics, lecturer preferences, citations, or source-set identity.

## Example Learning Rule

Examples are not templates to copy. Every example must first be analysed into an `ExampleReviewRecord`; only the stripped, generic, condition-based lesson may be promoted into protocols, schemas, scripts, or regression fixtures.

No example-derived rule may enter production unless it has:

- what worked;
- why it worked;
- what failed, or the explicit statement `no failure observed`;
- why it failed, or the explicit statement `not applicable because no failure was observed`;
- non-transferable content;
- one transferable principle;
- one anti-overfit rule;
- a destination;
- one validation check;
- one regression fixture or fixture update.

## ExampleReviewRecord

Every reusable lesson must be stored conceptually as:

```yaml
ExampleReviewRecord:
  example_id:
  source_role:
  example_scope:
  what_worked:
  why_it_worked:
  what_failed:
  why_it_failed:
  transferable_principle:
  non_transferable_content:
  anti_overfit_rule:
  affected_protocols:
  affected_scripts:
  validation_check:
  regression_fixture:
  promotion_status: candidate | accepted | rejected | blocked
  confidence: high | medium | low
```

## LanguageDelta Record

Language-only improvements should be stored as:

```yaml
LanguageDelta:
  delta_id:
  bad_pattern:
  improved_pattern:
  reasoning:
  applies_to:
  linter_signal:
  severity: high | medium | low
```

## Analysis Steps

1. Classify the example source and trust boundary.
2. Write one review record per example, including what worked and what failed.
3. Strip target-specific content, names, dates, citations, question stems, headings, and topic details into `non_transferable_content`.
4. Convert only the remaining condition into a transferable principle.
5. Assign the rule to the relevant protocol, schema, script, linter, or regression fixture.
6. Add a validation check that can fail future outputs.
7. Run the rule-promotion gate before treating the lesson as production behavior.

## Example Learning Pipeline

```text
example_inventory
-> example_review_ledger
-> transferable_rule_synthesis
-> rule_promotion_gate
-> example_transfer_linter
-> regression_fixture_update
```

## Rule Promotion Gate

Before promotion, the Skill must:

1. Identify the source feature or output failure the example demonstrates.
2. State whether the example is good, bad, or mixed.
3. Explain why the example worked or failed.
4. Remove source-specific content.
5. Rewrite the lesson as a generic condition-based rule.
6. Add a positive regression.
7. Add a negative regression.
8. Add a linter or schema check where practical.
9. Confirm the promoted rule does not contain the example identity.

Fail the gate if the rule says or implies:

- copy this structure;
- make future output like this example;
- preserve the same module list;
- use the same topic labels;
- transfer target-specific content;
- turn a benchmark fixture into general production logic.

## No Direct Example-To-Skill Rule

Production rules must not contain the example's course name, lecturer name, target title, module-specific topic name, named drug, named gene, named organism, exact heading, fixture ID, or target-specific required module list.

Example-specific checks may live in regression fixtures. Production linters and schemas must operate on generic source features such as:

- official definitions;
- contrast pairs;
- criteria, features, stages, or classes lists;
- named teaching examples;
- `Why X?` source blocks;
- diagrams, tables, equations, graphs, workflows, and calculations;
- method workflows;
- graph or data interpretation operations.

## Generalised Coverage Rule From Examples

When examples expose missing lecture-note density, the transferable rule is not the example's topic list. The general rule is that each source heading, official definition, contrast pair, criteria list, named example, diagram, equation, graph, calculation, method workflow, and summary point must be captured as an atomic knowledge item before exam overlay changes priority, order, or density.

## Language Delta Scope

Scan external essays, formative feedback, answer-style exemplars, reasoned answer keys, and generated outputs for language deltas.

Do not derive language deltas from formal past-paper pages, formal papers with answer appendices, lecture slides, practical protocols, reading lists, or marking criteria. Those sources can teach format, method, evidence role, or assessment structure, but page numbers and question instructions from them are not student-answer prose.

## Common Transferable Lessons

- Compress repetition without removing mechanism.
- Open paragraphs with claim or problem.
- Explain examples as evidence for a broader argument.
- Convert evidence-heavy examples into evidence, mechanism, interpretation, and limitation.
- Remove lecture-route narration and exam-guidance phrasing from final essay prose.
- Calibrate citation strength so support or implication is not written as single-cause proof.
- State the debate before comparing models.
- Separate old-regime evidence from current-regime prediction.
- Treat answer keys as answer-schema evidence, not independent factual authority.
- Treat practical protocols as method/readout/control evidence.
- Use formative feedback as writing and marking guidance, not prediction evidence.

## Hard Negatives

Do not:

- infer a target topic because an example used that topic;
- copy a citation from an example;
- write source-set-specific course names into production logic;
- merge official answers, student answers, and generated answers into one trust class;
- treat a model answer as proof that the same question will recur.

---

## Source File: `references__example_essay_docx_output_protocol.md`

---

# Example Essay DOCX Output Protocol

## Trigger

Use this protocol when Essay Exam Prep or Example Essay Mode is explicitly requested by the user, such as `essay preparation`, `Example Essay`, `model essay`, `full essay-style answer`, or an equivalent request for complete essay answers/documents.

Do not trigger this DOCX protocol for MCQ, short-answer, long-answer/project/scenario, prediction-only, or ordinary lecture-walkthrough requests.

The normal default revision workflow is `exam_prep_notes_docx`. Essay prep is a DOCX add-on built on top of the Academic Exam-Ready Notes artifact unless the user explicitly opts out. `knowledge_walkthrough_docx` remains available only when the user explicitly requests a lecture-first walkthrough.

## Primary Output

Default essay-prep output is one module-level Word document:

- `Essay_Module_Example_Essays.docx`

It should contain the selected examinable modules, one or more full Example Essays where support is sufficient, adaptation maps, and reusable paragraph banks.

If the user explicitly asks for separate essay files, each Example Essay may instead be exported as one standalone `.docx` file.

If separate essay files are requested and N Example Essays are generated, produce N Word documents:

- `EE01_<short_safe_question_title>.docx`
- `EE02_<short_safe_question_title>.docx`
- `EE03_<short_safe_question_title>.docx`

Also produce:

- internal QA artefacts for validation, such as `example_essay_manifest.json`, `example_essay_source_audit.json`, source maps, QA JSON, and citation-resolution logs.

Do not place a complete essay into one Excel cell. Do not create an Excel workbook as the ordinary essay-prep output. Excel paragraph-row output is allowed only as an internal or explicitly requested audit artefact.

Do not create the complete DOCX essay before the detailed essay plan is approved unless the user explicitly requests direct generation or has already requested execution of the planned essay package.

Final user-facing output may include the requested final artefacts, such as `Essay_Module_Example_Essays.docx`, separate Example Essay DOCX files, or another explicitly requested final format. Do not return or package helper JSON, source maps, manifests, source-audit files, render previews, or citation-resolution logs unless the user explicitly asks for an audit package.

## Word Document Formatting

Apply these settings to every generated DOCX. Leave all other Word settings at their defaults unless the user specifies otherwise.

Page:

- Top margin: 2.5 cm.
- Bottom margin: 2.5 cm.
- Left margin: 2.5 cm.
- Right margin: 2.5 cm.

Font:

- Arial.
- Font size: Word default unless the user specifies a size.
- Title: Arial, bold allowed, centered.
- Essay-question subtitle: Arial, plain, not bold, not italic, not enlarged, left aligned.
- Section heading: Arial, bold allowed, left aligned.
- Body: Arial.

Paragraph:

- Line spacing: 1.5.
- Paragraph spacing before: 0 pt.
- Paragraph spacing after: 0 pt.
- Body alignment: justified.
- Title alignment: centered.
- Subtitle / section heading alignment: left.
- No empty spacer paragraphs.

Structure:

- Title paragraph.
- Optional subtitle paragraph containing only the exact essay question or user-approved topic wording. Do not add decorative `Question:`, `Essay Topic:`, bold, italic, enlarged text, or spacer paragraphs around it.
- Numbered section headings if useful, matching the reference style:
  - `1 Introduction`
  - `2 Main mechanism / argument`
  - `2.1 Subsection`
  - `3 Evaluation / synthesis`
  - `4 Conclusion`
- Body paragraphs written as continuous essay prose.
- Figure captions only if figures are explicitly included or requested.

## No Public Preamble In Final DOCX

The final Essay DOCX must begin with the title, optional exact question/topic subtitle, then essay content. Do not insert a public preamble, disclaimer, source-basis note, diagnostic label, or task label into the Word document.

Forbidden visible DOCX text includes:

- `Model answer built from...`
- `This is not a predicted exam question`
- `Exam-style question`
- `Question:` before the subtitle;
- `Essay Topic:` before the subtitle;
- standalone `Example essay` / `Example Essay` labels;
- source-basis or confidence disclaimers that belong in the chat response or internal QA.

If a source-basis note is useful, put it in the short chat response or internal audit artefact, not inside the student-facing essay DOCX.

## Essay Language Contract

Every generated essay must pass the shared prose-quality rules in `language_quality_contract.md` and the orchestration checks in `essay_generation_protocol.md`.

Required paragraph logic:

```text
claim -> mechanism/process/evidence -> scope or limitation -> consequence -> link back
```

Language rules:

- Start with the answer, not with generic metacommentary.
- Aim for roughly balanced descriptive and analytic prose across the full essay.
- Prefer direct positive claims; use negative framing only when it marks a necessary boundary.
- Compress repeated or low-value detail without deleting required academic mechanisms.
- Remove lecture-route narration and exam-guidance phrasing from the essay body.
- Use examples as evidence for a broader claim, not as disconnected case descriptions.
- Convert evidence-heavy examples into `evidence -> mechanism -> interpretation -> limitation`.
- Keep paragraph logic linear. Avoid claim, setup, repeated-claim ordering when the result can be attached to the setup.
- Make contrasts explicit and non-ambiguous.
- Keep citations minimal and sufficient; support theory, mechanisms, data, experiments, or non-obvious generalisations.
- Calibrate citation strength; do not write support, association, or mechanistic plausibility as sole-cause proof.
- Do not cite-stack.
- Keep academic paper author names inside parenthetical in-text citations in normal explanatory prose. Write the content claim first; do not make authors the sentence subject unless the user explicitly asks for literature-history narration.
- Omit unsupported claims rather than inventing citations.
- Conclude by synthesis, not by adding new content or listing every body-part conclusion.

## Highlighting Rules

Use Word highlight, not font colour.

Highlight mapping:

- Extra Reading Books content: yellow highlight.
- Citation / Extra Reading Papers content: green highlight.
- Lecture-slide citation original-source content: green highlight.
- Verified classic-experiment fallback content: green highlight.

Implementation mapping:

- Extra Reading Books: `WD_COLOR_INDEX.YELLOW`
- Citation / Extra Reading Papers, cited original papers / theories / experiments from lecture-slide citations, plus verified classic-experiment fallback sources: `WD_COLOR_INDEX.BRIGHT_GREEN`

Rules:

- Yellow highlight is applied only to content derived from Extra Reading Books or chapters uploaded by the user.
- Green highlight is applied only to content derived from verified Citation / Extra Reading Papers, original citation sources identified from lecture slides and then read or verified, or verified classic-experiment fallback sources used because lecture slides contained no usable citations.
- If a sentence uses a lecture-slide cited original source, include an author-year in-text citation and highlight the full cited-source-derived clause or sentence green, including the citation.
- If a sentence uses a Citation / Extra Reading Paper, include an author-year in-text citation and highlight the paper-derived phrase, clause, or sentence green, including the citation.
- Citation-source clauses must use parenthetical author-year attribution. Do not render author-led prose such as `Author et al. showed...` as the public sentence shape unless the user explicitly requests discovery history or literature attribution.
- If a sentence uses Extra Reading Books, highlight the extra-reading-derived phrase or sentence yellow.
- If a paragraph contains both lecture content and extra-reading content, highlight only the extra-reading portion yellow.
- If a paragraph contains both lecture content and cited-original-paper content, highlight only the cited-original-paper portion green.
- Do not highlight ordinary lecture-slide content.
- If content could belong to both Extra Reading and cited original-source categories, prefer the more specific mapping:
  - source from lecture-slide cited original paper = green;
  - source from verified Citation / Extra Reading Paper = green;
  - source from uploaded Extra Reading Book = yellow.
- Do not use green highlight for citations copied from secondary sources unless the original cited source was read.
- Do not use yellow highlight for generic textbook knowledge unless it came from the uploaded Extra Reading material.
- Do not use yellow highlight for academic papers, even if the user calls them extra reading. Verified papers are citation sources and must use green.

## Highlight Relevance Gate

Highlighting does not justify inclusion. A yellow or green phrase may appear only if the sentence also passes the PPT/source-anchor and question-relevance gate.

Reject highlighted content when:

- it is accurate but not needed for the essay question;
- it creates a molecular, channel, receptor, gene, pathway, method, case, or example list not present in the PPT/source logic;
- it increases Extra Reading ratio by replacing rather than sharpening lecture-derived claims;
- it makes revision harder without improving answer precision;
- it has no paragraph function beyond raising citation or Extra Reading density.

## Micro-Detail Highlighting

When the Micro Extra Reading Enhancement Pass inserts a short named detail into an otherwise lecture-derived sentence, the DOCX must preserve the source boundary at run level.

Rules:

- highlight only the inserted phrase or shortest source-derived clause;
- do not highlight the full sentence if most of the sentence is lecture-derived synthesis;
- yellow is valid only for an inserted phrase from an uploaded recommended book or matched textbook chapter/section;
- green is valid only for an inserted phrase from a verified lecture-cited original source or verified classic/academic source;
- ordinary lecture-derived precision receives no highlight;
- unverified remembered details and exemplar-only details are rejected, not highlighted.

Micro-detail insertions must remain short in function, not by a fixed word count. The addition should read as a phrase or short clause inside the original sentence. If the detail needs a new explanatory sentence, introduces a second argument, or dominates the lecture-derived sentence, it is not a micro-detail insertion and must go through normal paragraph planning.

Each micro-detail run in the source map should record:

```yaml
micro_detail_insert: true
original_phrase:
inserted_phrase:
parent_ppt_or_source_slot:
question_function:
source_type:
source_anchor:
highlight:
word_count:
claim_delta: precision_only
qa_status:
```

Fail or flag the essay if:

- a micro-detail insertion has no source anchor;
- a micro-detail insertion has no parent PPT/source slot;
- a micro-detail insertion is long enough to become a new explanation or second argument;
- a micro-detail insertion has a source type that does not match its highlight colour;
- a micro-detail insertion changes the original claim instead of making it more precise;
- a highlighted span is broader than the source-derived insertion;
- the insertion pushes Extra Reading above the allowed ratio.
- the insertion is true but not needed for the question.

## Compression Budget Source Map

When an Example Essay is compressed after citation and Extra Reading integration, the source map should preserve the internal compression budget so QA can distinguish safe concision from content loss.

```yaml
compression_budget:
  current_word_count:
  requested_reduction:
    type: percent | words | unspecified
    value:
  protected_source_skeleton:
    - source-grounded claim, mechanism, evidence, limitation, comparison, or synthesis item
  protected_academic_details:
    - citation-supported named detail or examiner-relevant distinction
  removable_redundancy:
    - repeated framing
    - duplicated restatement
    - overlong transition
    - low-value background
  safe_reduction_range:
    min:
    max:
  unsafe_threshold:
  decision: compress_within_safe_range | partial_compression_only | reject_requested_reduction
  reason:
```

Fail or flag the essay if a requested compression target is followed after the budget says it is unsafe, a protected source-skeleton item disappears, or final visible prose leaks process language such as percentage-compression decisions.

## Extra Reading Ratio

If relevant Extra Reading Books are uploaded:

- integrate Extra Reading content into the essay;
- treat Extra Reading as a precision layer, not a quota;
- default to short integrated phrase or clause insertions when they sharpen a lecture-derived mechanism, evidence point, comparison, or limitation;
- target roughly 5-10% of total essay body word count when enough relevant material passes the anchor and question-relevance gates;
- allow 10-15% only when the question genuinely needs external detail and the added material remains lecture-anchored and analytically interpreted;
- count only yellow-highlighted words as Extra Reading content;
- do not include more than 15% unless the user explicitly requests more external material;
- do not add separate Extra Reading expansion paragraphs or pad the essay to reach a ratio;
- if no relevant chapter can be found, flag `extra_reading_chapter_not_found` and do not invent.

If Extra Reading Books are not uploaded:

- do not fabricate extra reading;
- set `extra_reading_status = not_supplied`.

## Citation-Source Integration

If the user does not provide citations for Example Essay generation, the workflow must perform citation discovery:

1. inspect relevant lecture slides for citation information;
2. resolve and read lecture-slide cited originals where possible;
3. if no usable slide citation exists, search for several classic experiments or landmark primary studies directly tied to the lecture mechanism.

If the relevant lecture slides contain citations:

- parse all citations on slides used by the essay;
- resolve them to original papers, books, theories, or experiments where possible;
- read the original source before adding source-derived content;
- insert author-year in-text citations;
- highlight source-derived content green;
- record the citation in the source audit.

If a citation cannot be resolved or the original source cannot be read:

- do not use content from that citation;
- do not add a green-highlighted sentence;
- add QA flag `citation_original_unreadable`;
- list the unresolved citation in `example_essay_source_audit.json`.

If the relevant lecture slides contain no usable citations:

- perform targeted academic search using lecture terms, mechanism names, model systems, methods, and named experiments;
- prefer primary experimental papers with DOI/PubMed/publisher records;
- use authoritative reviews only for orientation unless the paragraph claim is review-level;
- record `lecture_slide_citation_absent_classic_experiment_search_required` internally;
- insert only verified, read classic-experiment content, with author-year citation and green highlight.

## Source Hierarchy

Essay content must be built in this order:

1. Relevant lecture slides.
2. Official lecture notes / official course handouts.
3. Formal exam question wording or predicted practice question prompt.
4. Lecture-slide cited original sources, only after reading them.
5. Verified classic experiments found because no usable lecture-slide citation exists.
6. Citation / Extra Reading Papers, only after metadata and relevant claims are verified.
7. Uploaded Extra Reading Books, only relevant chapters/sections.
8. Other peer-reviewed or textbook sources only if explicitly allowed or needed for citation resolution.

Extra Reading and citation-source content must enrich the lecture answer, not replace it.

Candidate sources identified during plan-stage DeepResearch are not reference-list sources until their metadata and claim relevance are verified.

## Lecture Grounding

No Example Essay may be drafted before the relevant lecture slides have been read, mapped, and converted into a lecture-logic plan.

Every body paragraph must have:

- at least one lecture-slide anchor or official course-material anchor;
- one clear claim;
- mechanism or evidence development;
- a link back to the essay question.

The final essay must visibly follow lecture logic:

- the essay begins from the biological problem or principle established by the lecture;
- body paragraphs follow the mechanism / evidence / consequence sequence taught by the lecture;
- named examples are those emphasised in the lecture;
- experimental evidence is placed where the lecture uses it to support a claim;
- conclusions synthesise the lecture argument rather than adding unrelated external material.

## Fail Conditions

Fail DOCX generation or mark the essay as non-compliant if:

- no relevant lecture slides were read;
- a body paragraph has no lecture-slide or official course anchor;
- public preamble, source-basis disclaimers, `Model answer built from...`, `This is not a predicted exam question`, `Exam-style question`, `Question:`, `Essay Topic:`, or standalone `Example essay` labels appear in the visible DOCX;
- Extra Reading content exceeds 15% without user instruction;
- yellow-highlighted content lacks an Extra Reading source anchor;
- an academic paper or Citation / Extra Reading Paper is yellow-highlighted instead of green-highlighted;
- green-highlighted content lacks an in-text citation;
- green-highlighted content is not linked to a read original citation source;
- classic-experiment fallback content was used without verification or without direct relevance to the paragraph claim;
- margins, font family, line spacing, title alignment, subtitle alignment, or body justification fail the DOCX linter;
- paragraph spacing is non-zero, the question/topic subtitle is bold, italic, enlarged, or separated by empty spacer paragraphs;
- the essay is generic and not traceable to lecture logic;
- the essay contains slide/page narration, repeated filler, unsupported claims, citation stacking, or examples used as standalone case detail rather than evidence for the answer;
- the essay contains lecture-route narration, exam-guidance phrasing, or citation-strength overclaiming;
- the essay contains true-but-not-needed detail, review-style drift, or a channel/receptor/gene/pathway catalogue without analytic use;
- compression changes claim scope, causal strength, model boundaries, or experimental interpretation;
- a citation printed on a slide is copied into the essay without resolving and reading the original source;
- a candidate source appears as a verified citation without metadata and claim verification;
- a reused published figure, table image, chart, or adapted visual lacks licence or permission;
- an uploaded formatting PDF or style exemplar is used as biological content.

## User-Facing Output Contract

When the user asks for Example Essays, return paths in this form:

```text
Generated:
- Example_Essays_DOCX/EE01_<title>.docx
- Example_Essays_DOCX/EE02_<title>.docx
```

The user should not need to manually reformat the Word documents.

---

## Source File: `references__excel_output_protocol.md`

---

# Legacy Excel Compatibility Protocol

This file is retained only for migration checks, internal QA, and backwards-compatible lint fixtures. It does not define an ordinary student-facing output route.

Current public exam-prep outputs are Word-first:

- `Lecture_Knowledge_Walkthrough.docx`;
- `MCQ_Exam_Analysis_Report.docx`;
- `ShortAnswer_Exam_Analysis_Report.docx`;
- `LongAnswer_Project_Scenario_Report.docx`;
- `Essay_Module_Example_Essays.docx`.

Do not generate Excel workbooks, prediction workbooks, confidence-band files, archetype-registry files, or essay-theme-plan-only files as ordinary student-facing outputs.

If a legacy workbook is explicitly requested for audit or migration, keep it outside the public student-output folder unless the user asks for an audit package. It must not contain unsupported claims, hidden-source inference, benchmark-specific content, or complete essays stored only in spreadsheet cells.

Legacy audit labels may include:

- Essay / Problem-Essay: `Predicted Essay Theme / Scope / Practice Angle`
- Short Answer: `Likely Short-Answer Form / Mark-Producing Answer Schema`
- MCQ: `Likely Statement Trap / Discriminator / One-line Rule`
- Problem/Data: `Likely Data-Problem Archetype / Graph-Reading Operation / Mechanism Inference`
- Long-Answer Project: `Likely Project Operation / Method-Readout-Interpretation / Control`

These labels are audit labels, not public route names. For current output generation, convert the same analysis into the matching DOCX add-on report.

---

## Source File: `references__gap_closure_loop_protocol.md`

---

# Gap Closure Loop Protocol

The Skill is not complete after one rewrite. It is complete when the example-analysis and QA loop no longer finds high or medium gaps.

## Loop

```text
collect examples
-> classify source roles
-> extract ExampleReviewLedger and LanguageDelta records
-> run rule-promotion gate
-> update protocols/scripts only after promotion passes
-> generate or lint representative outputs
-> import external review notes when available
-> produce gap report
-> repeat until high/medium gaps are closed
```

## Gap Severity

High:

- unsupported factual claims can reach a student-facing answer;
- live-assessment or contract-cheating boundary is unclear;
- course/benchmark identity can trigger production behaviour;
- formal past papers and examples are pooled incorrectly;
- Example Essay DOCX fails required formatting or source-grounding rules.

Medium:

- answer keys lack provenance separation;
- practical/data/problem papers do not get a question-type-specific prep strategy;
- language contract violations persist in generated prose;
- legacy or spreadsheet inputs are ignored without a clear QA flag;
- external review recommendations are not converted into validation checks.

Low:

- naming, documentation, or CLI ergonomics issues that do not change output correctness.

## Completion Condition

The loop can stop only when:

- `gap_report` has no high gaps;
- `gap_report` has no medium gaps unless explicitly accepted with rationale;
- `github_ready_check.py --ci` passes;
- installed Skill copy matches the repository copy;
- Git working tree contains only intentional changes ready for commit.

## External Review

Chrome ChatGPT Pro/Extended review, if available, is an external review artefact. It is not a runtime dependency.

If external review is unavailable, record that fact and continue with local evidence, local examples, and automated checks.

---

## Source File: `references__github_release_protocol.md`

---

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

---

## Source File: `references__input_processing_protocol.md`

---

# Input Processing Protocol

## FileRole Enum

Classify every file before analysis:

- `lecture_slide`
- `lecture_note`
- `annotated_lecture_slide`
- `student_typed_note`
- `student_handwritten_note`
- `structured_revision_note`
- `ai_generated_note`
- `formal_past_paper`
- `formal_past_paper_with_answers`
- `example_paper`
- `practice_paper`
- `practice_answer_key`
- `mock_exam`
- `answer_key`
- `practical_protocol`
- `exemplar_answer`
- `exemplar_image`
- `marking_criteria`
- `essay_guidance`
- `extra_reading_book`
- `extra_reading_chapter`
- `citation_original_source`
- `classic_experiment_source`
- `citation_reference_list`
- `reading_list`
- `docx_format_reference`
- `source_policy`
- `output_protocol`
- `visual_aid_spec`
- `generated_visual_aid`
- `helper_script`
- `unsupported_binary`
- `unknown`

Each file record must include:

- file path;
- normalized `target_group_key`;
- course/module code if detectable;
- course/module name if detectable;
- year if detectable;
- exam regime if detectable;
- source trust level;
- extraction status;
- allowed evidence use.
- source feature flags, such as answer key, example paper, practical protocol, essay guidance, problem/data/case, and recommended reading.

The Skill accepts any readable course-note source: slides, official notes, lecturer-provided PDF/DOCX notes, student typed notes, handwritten notes, annotated screenshots, flashcards, structured revision notes, and AI-generated summaries. Acceptance for intake is not the same as authority for factual claims.

Ordered course-note processing uses:

```text
CourseContentSource -> OrderedContentItem -> SourceFragment -> AtomicKnowledgeLedger -> KnowledgePoint -> PrepArtifact
```

Student handwritten annotations, typed notes, flashcards, and unknown-provenance summaries may be used as interpretation hints, definition candidates, and gap cues, but must not be treated as authoritative course facts unless supported by slide text, official notes, official course material, verified textbooks, or verified academic sources. AI-generated notes have no factual authority and may only help with structure after independent verification.

## Source Trust Levels

- `official_course`: lecture slides, official notes, official past papers, official marking criteria, official exam guidance.
- `course_adjacent`: lecturer-provided practice, mocks, answer keys, exemplars, tutorial material.
- `student_or_unknown`: student notes, downloaded material with unclear provenance, unclear file origin.
- `external_verified`: peer-reviewed, textbook, DOI/PubMed/publisher/official sources verified during the run.
- `unsupported`: unreadable or unsupported content.

## Evidence Use

- `factual_course_content`
- `formal_prediction_evidence`
- `formal_prediction_and_answer_key_evidence`
- `coverage_evidence_only`
- `answer_rationale_evidence`
- `answer_style_only`
- `format_rule`
- `practical_method_evidence`
- `reading_recommendation`
- `extra_reading`
- `lecture_slide_core`
- `lecture_slide_citation_original`
- `classic_experiment_source`
- `student_note_hint`
- `definition_candidate`
- `exam_emphasis_hint`
- `visual_explanation_only`
- `docx_format_reference`
- `excluded`

## AnalysisContext

Every source must also be classified by `AnalysisContext` before it is used downstream.

```yaml
AnalysisContext:
  target_current_regime:
    meaning: same target source set, current formal evidence; allowed for blueprint and prediction
  target_old_or_different_regime:
    meaning: same target source set but old/different format; allowed for concept coverage and answer schema only
  target_auxiliary:
    meaning: practice/mock/tutorial/answer key from same target source set; allowed for coverage and style depending on role
  cross_target_example:
    meaning: non-target material; transferable workflow logic only
  style_exemplar:
    meaning: exemplar answer/image; style/structure/density only unless factual claims are verified
  layout_exemplar:
    meaning: visual formatting example only; may update route style profile and DOCX style lint rules, never factual content
  benchmark_fixture:
    meaning: regression test case only
  unsupported_or_unreadable:
    meaning: do not use for factual or predictive claims
```

Hard rule:

```text
Only `target_current_regime` may directly control current blueprint prediction.
Only target lecture slides, official notes, lecturer-provided course notes, verified official materials, and independently verified academic sources may directly control factual content.
Cross-target examples must be converted into transferable workflow contributions, not content evidence.
```

## AllowedUseMatrix

| Analysis Context | Factual content | Prediction blueprint | Coverage | Style | Layout | Regression |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `target_current_regime` | yes | yes | yes | yes | yes | no |
| `target_old_or_different_regime` | yes if lecture/official | no unless comparability is proven | yes | limited | no | no |
| `target_auxiliary` | limited | no unless official says representative | yes | yes | no | no |
| `cross_target_example` | no | no | no | principle only | possible | no |
| `style_exemplar` | no unless verified | no | no | yes | no | no |
| `layout_exemplar` | no | no | no | no | yes | no |
| `benchmark_fixture` | no | no | no | no | no | yes |
| `unsupported_or_unreadable` | no | no | no | no | no | no |

## ExampleReviewRecord Schema

Every non-target example used by a protocol or benchmark must be represented as a review record before any lesson is promoted:

```yaml
ExampleReviewRecord:
  example_id:
  source_role:
  source_materials:
    - lecture_slides
    - lecture_notes
    - formal_past_papers
    - practice_materials
    - answer_keys
    - practical_protocols
    - marking_guidance
    - exemplar_answers
    - handwritten_or_image_examples
  example_scope:
  what_worked:
    - reusable behaviour demonstrated by the example
  why_it_worked:
    - source or output condition that made the behaviour valid
  what_failed:
    - failure observed, or no failure observed
  why_it_failed:
    - cause, or not applicable because no failure was observed
  transferable_principle:
  non_transferable_content:
    - topic/content/lecturer/year detail that must not be reused
  anti_overfit_rule:
  affected_protocols:
    - protocol path or protocol name
  affected_scripts:
    - script path or linter name
  validation_check:
  regression_fixture:
  promotion_status: candidate | accepted | rejected | blocked
  confidence: high | medium | low
```

Promotion is blocked unless the review record explains both useful and failed behaviours, strips non-transferable content, names the destination, and includes a validation check. Examples may improve workflow logic and QA only; they cannot support target facts or predictions.

## Target Group Key And Regime Split

All question-pattern inference must stay inside the same target course/module group. Normalize every filename before comparison:

1. remove year/date tokens;
2. remove terms such as `mock`, `practice`, `with answers`, `answer key`, `guide answers`, `modified syllabus`, `CADMUS`, `PP1/PP2`, dates, `combined`, copies, and version suffixes;
3. collapse whitespace and punctuation;
4. retain the normalized course/module group as `target_group_key`.

Never use content from one `target_group_key` to predict the content of another target group. External examples may be used only as `ExampleReviewRecord` entries that teach reusable workflow logic, output structure, QA checks, or evidence-handling discipline after non-transferable content is blocked.

Within the same target group, split formal papers into `exam_regime` groups when any of these change materially:

- section structure;
- answer-all vs answer-one/choose-one rule;
- timing or submission mode;
- mark weights;
- MCQ/short-answer/essay/case-study balance;
- data/figure/calculation requirements.

Old-regime papers may support concept coverage and possible slot fillers, but they must not be averaged into current-regime blueprint or archetype recurrence.

## Extraction Rules

- PDF: extract page-by-page text; record image count and warn that diagram/image text may need visual inspection.
- PPTX/PPTM/PPSX: extract slide XML text and notes XML when possible; record that diagrams and embedded images may not be text-extracted.
- PPT: use legacy binary-string extraction only as approximate text; require original-file inspection for diagrams and exact wording.
- DOCX: extract paragraphs and table text.
- XLSX/XLSM: extract sheet names and text-like cell values; treat existing analysis spreadsheets as prior work with provenance, not source truth.
- TXT/Markdown/YAML/Python: read as text.
- Images: mark as image evidence; inspect manually or with OCR when it affects the answer.
- Image exemplars: classify as `exemplar_image` when context indicates handwritten essays, model answers, example answers, or essay drafts. Evidence use is `answer_style_only`; status must include visual-inspection limits. Do not OCR repeatedly by default.
- A user-uploaded textbook, book chapter, monograph, or long PDF supplied as additional reading must be classified as `extra_reading_book` unless it is clearly a lecture slide or past paper.
- A standalone chapter or chapter extract supplied as additional reading must be classified as `extra_reading_chapter`.
- A PDF or paper resolved from a citation on a lecture slide must be classified as `citation_original_source`.
- A classic or landmark primary experiment found because relevant lecture slides contain no usable citations must be classified as `classic_experiment_source` after verification and reading.
- A bibliography/reference-list file supplied to resolve slide citations may be classified as `citation_reference_list`.
- A user-uploaded formatting PDF, screenshot, or previously generated DOCX supplied as a formatting reference must be classified as `docx_format_reference` or `layout_exemplar`. Use it only to derive transferable layout rules such as margin density, spacing, alignment, heading hierarchy, page-break policy, and label discipline; never use it as factual or prediction evidence.
- A reasoned answer key must be classified by provenance where possible: official/lecturer, paper-with-answer, student, generated, or unknown. Use it for answer schema, rationale, distractor traps, and marking expectations, not direct prediction.
- A practical protocol must be routed to practical/data/problem logic: aim, method principle, steps, readout, interpretation, control, limitation.
- A reading list, course handbook, programme/advisement document, or suggestions file may identify reading recommendations or administrative constraints; it must not replace lecture content.
- Essay style examples must be classified as `style_exemplar` or `exemplar_answer` and used only for paragraph structure, density, and tone unless factual claims are independently verified from target materials.
- Unsupported files: never infer hidden content.

## Atomic Source Decomposition

For `exam_prep_notes_docx`, extraction does not stop at broad KnowledgePoints. Before baseline notes are written, every readable slide/page/source block must be decomposed into `AtomicKnowledgeUnit` records inside an internal `AtomicKnowledgeLedger`.

Protected atomic units include:

- intended learning outcomes;
- slide/page headings and major note headings;
- definition-style text;
- contrast pairs;
- criteria, feature, stage, class, or component lists;
- named mechanisms, methods, drugs, diseases, examples, cases, and target classes;
- `Why X?` source blocks;
- labelled diagrams, tables, equations, graphs, calculations, and workflows;
- limitations, misconceptions, and take-home points.

Administrative units, exam timing, mark splits, reading-list logistics, course-admin pages, and repeated duplicates may be excluded from the student view, but the ledger must record the exclusion reason. Knowledge units must be bound to final modules or named submodules before public generation.

### Extra Reading Book Extraction

For Extra Reading Books:

- extract table of contents if available;
- extract chapter headings;
- extract section headings;
- index searchable keywords;
- map chapters to lecture KPs using lecture terms, pathway names, diseases, methods, model systems, and essay question terms;
- read only relevant chapters/sections before inserting yellow-highlighted content into Example Essays.

### Extra Reading Paper Extraction

For Extra Reading Papers:

- extract title, authors, year, DOI, PMID, journal or publisher record where available;
- verify the paper from DOI, PubMed, publisher, Google Scholar, or another reliable academic locator before using it;
- map the paper to the exact lecture mechanism, method, model, evidence point, limitation, comparison, or essay question function it can sharpen;
- classify verified/read paper-derived content as `extra_reading_paper`;
- insert paper-derived content only with parenthetical author-year citation and green highlight;
- do not treat papers as Extra Reading Books and do not yellow-highlight them.

### Lecture-Slide Citation Extraction

For lecture-slide citations:

- extract citations from slide text, notes, reference slides, footers, and figure captions;
- if citations appear only inside slide images, perform targeted OCR or visual inspection on relevant slides;
- parse author-year, DOI, PMID, title fragments, journal names, and reference-list entries;
- classify resolved/read source files as `citation_original_source`;
- do not use source-derived content until the cited original source has been resolved and read.

If the user asks for Example Essay generation but supplies no citation list:

- treat citation discovery as mandatory, not optional;
- inspect relevant lecture slides first for author-year, DOI, PMID, title fragments, journal names, reference-list entries, figure-caption citations, and notes citations;
- emit academic search queries for unresolved slide citations;
- if no usable slide citations exist, create a classic-experiment search plan from lecture terms, named mechanisms, model systems, methods, and evidence claims;
- require several candidate classic experiments or landmark primary studies where possible, but insert only those that have been verified and read;
- classify verified fallback sources as `classic_experiment_source`;
- flag `lecture_slide_citation_absent_classic_experiment_search_required` internally when this fallback path is used.

## ExamFormat Fields

For each formal paper or guidance source, parse:

- course/module code if detectable;
- year;
- duration;
- sections;
- answer_all_or_answer_one;
- question_count_by_section;
- mark_weight_by_section;
- page_limit;
- word_limit;
- character_limit;
- figure_rule;
- citation_rule;
- calculator_rule;
- answer_book_or_blackboard;
- formatting_penalty;
- late_penalty.

Different year constraints directly change answer strategy; do not merge years without recording differences.

## KnowledgePoint Schema

```yaml
KnowledgePoint:
  kp_id:
  lecture_id:
  module_id:
  lecturer:
  title:
  concept_type: mechanism | pathway | experiment | disease | comparison | definition | method | figure | model_system | controversy_or_limitation
  source_anchor:
    file:
    slide_or_page_range:
  examinability: high | medium | low
  likely_question_types: []
  prerequisite_kps: []
  linked_kps: []
  essay_style_paragraph:
  mcq_statement_candidates: []
  short_answer_possible_questions: []
  essay_theme_candidates: []
  compatible_archetypes: []
  essay_function:
    - thesis_support
    - mechanism_paragraph
    - comparison_axis
    - example_evidence
    - cross_module_link
    - optional_extra_detail
  mechanism_chain:
    condition:
    regulator_or_sensor:
    molecular_action:
    output_change:
    biological_consequence:
  lecturer_emphasis:
    learning_objective: true/false
    summary_slide: true/false
    repeated_example: true/false
    named_as_key_point: true/false
  essay_priority: must_use | useful | optional | exclude
  paragraph_fit:
    possible_topic_sentence:
    possible_link_back_to_question:
  task_dimensions:
    factual:
    mechanistic:
    structural:
    quantitative:
    comparative:
```

Do not split by every slide. Split by examinable causal block. A valid KP should work as an MCQ concept, a short-answer mark cluster, an essay paragraph, or one component of an essay plan.

Protected source-backed items override ordinary compression. Treat each of the following as a protected KnowledgePoint or protected sub-item in the source baseline:

- intended learning outcome;
- slide/page heading or major notes heading;
- official definition;
- contrast pair;
- criteria, features, stages, classes, components, or steps list;
- named example used to teach a concept;
- `Why X?` source section;
- labelled diagram, table, graph, equation, calculation, or workflow;
- summary or take-home point;
- term, operation, or concept appearing in formal past papers.

Protected items may be grouped only when the final baseline still names and explains each item. They may not be hidden only in traps, omitted as low-value detail, or reduced to one checklist phrase.

For essay-capable KPs, do not treat all slide facts equally. Prioritise the facts that can form a causal paragraph:

```text
condition or biological problem -> regulator/sensor/molecular feature -> molecular action -> output change -> biological consequence
```

## Lecture-Order Coverage

For compatibility lecture walkthroughs and DOCX add-ons, analysis must proceed from the first slide/page to the last slide/page in source order where lecture order matters.

For `exam_prep_notes_docx`, source order is a diagnostic input, not a binding output order. Use it to infer prerequisites, source intent, and causal development; then organise the final notes by course-section logic, KnowledgePoint dependency, and supported exam emphasis.

Do not:

- analyse only high-yield slides;
- skip middle lecture sections without a QA flag;
- reorder KPs by predicted importance in the compatibility lecture-first walkthrough;
- merge several unrelated mechanisms into one huge KP;
- split one mechanism/evidence block into isolated slide fragments.

Allowed:

- group several consecutive slides/pages into one KP when they form one mechanism, process chain, experimental-evidence block, data-operation block, or essay paragraph block;
- mark a block low examinability, but still preserve its position;
- place detailed evidence in diagnostics or an explicit audit package while keeping the student-facing output clean.

---

## Source File: `references__interactive_setup_protocol.md`

---

# Interactive Setup Protocol

Use setup mode when the request is broad, multi-file, or underspecified.

## Required fields

| Field | Purpose |
| --- | --- |
| `task_type` | Notes, essay, model answer, question drill, prediction, walkthrough, or workbook. |
| `exam_target` | Course, exam board, module, paper, or assessment. |
| `source_roles` | Which files are lectures, readings, past papers, examples, marking guides, or drafts. |
| `allowed_sources` | Whether external research is allowed. |
| `output_format` | Chat, Markdown, DOCX, workbook, table, or JSON. |
| `quality_checks` | Source coverage, citation discipline, language, formatting, and gap checks. |

## Setup behavior

- Ask only for missing fields that change the output.
- Infer harmless formatting preferences from the user's request.
- Treat unsupported content as a gap.
- Confirm file output before creating files.

---

## Source File: `references__knowledge_surface_protocol.md`

---

# Knowledge Surface Protocol

This protocol controls the last public-rendering layer for all student-facing outputs. It sits after evidence extraction, source structuring, planning, and route-specific drafting.

The problem it prevents is not factual inaccuracy alone. It prevents the Skill from exposing planning scaffolds, source-route narration, AI process notes, rigid bucket labels, colon-slot fragments, or shorthand flow charts as if they were revision content.

```text
AtomicKnowledgeLedger -> PublicKnowledgeUnit -> KnowledgeSurfaceContract -> NonKnowledgeGate -> SurfaceFormGate -> LabelDecision -> Student DOCX
```

## Core Rule

Student-facing output must contain knowledge only.

A public sentence, heading, bullet, table row, figure caption, or note is allowed only if it performs one of these functions:

- defines a term or boundary;
- explains a mechanism, pathway, process, method, assay, calculation, graph, data readout, diagnostic rule, or comparison;
- gives a source-backed example or experimental result and interprets what it shows;
- states a limitation, caveat, exception, or scope boundary that changes understanding;
- connects concepts in a way that improves biological, clinical, methodological, or quantitative understanding.

A public item is forbidden when its main function is to describe the Skill, the source route, the AI workflow, the exam-prediction workflow, the evidence audit, or how the student should use the document.

## KnowledgeSurfaceContract

Use this object before any public DOCX is written:

```yaml
KnowledgeSurfaceContract:
  contract_id:
  route:
  allowed_public_functions:
    - definition
    - mechanism
    - process
    - method_workflow
    - assay_readout
    - calculation
    - graph_data_rule
    - diagnostic_rule
    - comparison
    - example_interpretation
    - limitation_or_scope
    - synthesis
  forbidden_public_functions:
    - source_route_narration
    - ai_process_or_provenance
    - audit_trace
    - generic_study_advice
    - exam_meta_or_prediction_trace
    - rigid_template_bucket
    - colon_slot_fragmentation
    - shorthand_arrow_chain
    - evidence_justification_trace
    - decorative_transition
  label_policy:
    mode: semantic_sparse
  density_policy:
    mode: source_adaptive
  layout_policy:
    body_alignment: left
    image_alignment: centered
    title_alignment: left
    heading_alignment: left
    line_spacing: 1.05-1.15
    image_scaling: readability_preserving_auto_fit
  qa_status:
```

The contract is route-independent. `exam_prep_notes_docx`, `knowledge_walkthrough_docx`, `mcq_exam_prep`, `short_answer_exam_prep`, `long_answer_project_scenario_prep`, and `essay_exam_prep` all pass through it.

## Explanatory Knowledge Unit

A public knowledge point should be written as a coherent explanatory unit, not as a shredded list of slots.

Every major point should answer four questions when the source material supports them:

```text
What is the concept or method?
Why does it work biologically, chemically, clinically, quantitatively, or experimentally?
How does the mechanism or calculation proceed?
What consequence, readout, limitation, or diagnostic meaning follows?
```

The output should normally use one topic-specific heading followed by one or more connected paragraphs. Bullets are allowed only when they list naturally parallel items after an explanatory lead sentence. Bullets must not be used to replace the explanation.

Bad public surface:

```text
Binding logic: at pH 7, CM Sephadex is negatively charged.
Protein charge: cytochrome c is positive.
Elution mechanism: NaCl competes.
Failure mode: wrong pH prevents elution.
```

Good public surface:

```text
CM Sephadex works as a cation exchanger because its carboxymethyl groups are deprotonated at the working pH and carry negative charge. Cytochrome c remains net positive under the same condition because it has many basic residues and a high pI, so electrostatic attraction holds the protein on the resin during loading and washing. NaCl elutes cytochrome c by raising ionic strength, competing for charged sites and shielding charge interactions; if pH or salt is wrong, the target can either flow through during loading or remain bound during elution.
```

## Non-Knowledge Classes

### 1. Source-route narration

Reject wording whose main purpose is to report where a claim came from or how slides/pages were ordered.

Forbidden visible patterns include:

```text
This slide shows...
The first slide shows...
The second slide shows...
The slide says...
The slide mentions...
The notes say...
According to page...
PPT page...
English explanations extracted from...
```

Rewrite by deleting the source-route wrapper and keeping only the knowledge.

Bad:

```text
The second slide shows the opposite side of the body.
```

Good:

```text
The crossed extensor reflex activates contralateral extensors and inhibits contralateral flexors so the unstimulated limb supports body weight.
```

### 2. AI process or provenance

Reject public text that describes AI activity, prompt instructions, extraction method, or generation evidence.

Forbidden visible patterns include:

```text
AI generated this...
I extracted...
I used the image/text to...
Generated from ChatGPT...
This document was produced by...
Only knowledge points are included...
I did not include how-to-answer content...
```

Public notes must not state what the AI did or chose not to do. The output itself must simply be the knowledge.

### 3. Audit trace and evidence justification

Reject public source maps, coverage notes, confidence notes, quality caveats, ELM warnings, internal QA flags, run manifests, citation logs, source anchors, and statements explaining why the Skill trusted or rejected material.

Keep these only in internal QA or in an explicitly requested audit package.

### 4. Generic study advice and answer coaching

Reject public prose such as:

```text
How to use this document
How to answer
A strong answer should...
Use this module...
Recommended approach
Exam strategy
Integrated reasoning
```

If the sentence contains real knowledge, rewrite only the knowledge. If it is pure advice, delete it.

### 5. Rigid template buckets and colon-slot fragmentation

The Skill must not mechanically render every point as:

```text
Definition:
Principle:
Mechanism:
Application:
Limitation:
Graph logic:
Interpretation:
```

It must also not replace those labels with a new set of equally fragmented labels:

```text
Components:
Workflow:
Exclusion logic:
Binding logic:
Protein charge:
Elution mechanism:
Formula:
Logic:
Reason:
Safety:
Failure mode:
```

These labels are allowed only when the label is genuinely needed for readability and the labelled block is the natural content type. They are not a required sequence. A high density of different `Label: sentence` lines is a public-surface failure even when each individual label seems plausible.

Preferred public heading style is semantic and topic-specific:

```text
Beer-Lambert conversion from A440 to product concentration
Initial rate is the concentration slope at the start of the reaction
PCR-RFLP turns a SNP into a fragment-pattern difference
pKa controls whether resin functional groups carry charge
```

The reader should see the concept first, not the planning bucket.

### 6. Shorthand arrow chains

Do not use arrow chains as final public explanation when a mechanism or workflow needs understanding.

Bad:

```text
CM Sephadex at pH 7 -> COO- resin -> cytochrome c positive -> binding -> NaCl -> elution
```

Good:

```text
At pH 7, CM Sephadex is negatively charged because its carboxyl groups are deprotonated. Cytochrome c is net positive under the same condition, so it binds to the resin by electrostatic attraction. A high NaCl concentration weakens that attraction by increasing ionic strength, competing for charged sites and shielding charges, allowing cytochrome c to elute.
```

If the user explicitly requests a workflow summary, use compact bullets with explanatory clauses rather than arrows.

## LabelDecision

Every visible label must pass this decision:

```yaml
SurfaceLabelDecision:
  label:
  function:
  decision: keep | merge_into_heading | merge_into_sentence | delete
  reason:
```

Keep labels for equations, worked examples, tables, comparisons, diagnostic rules, and calculations when they prevent ambiguity. Delete or merge labels that merely expose the internal scaffold.

Allowed label examples:

```text
Equation
Worked example
Diagnostic pattern
Control
Comparison
Table
```

## Notes And Walkthrough Rendering

`exam_prep_notes_docx` and `knowledge_walkthrough_docx` should use explanatory knowledge modules.

Allowed public structure:

```text
Title
Lecture Title
Topic-specific module heading
Connected explanatory prose
Optional equation, worked example, method workflow, comparison, or limitation block when useful
```

Forbidden public structure:

```text
How To Use This Document
What This Lecture Is About
What This Module Explains
The first slide shows...
The notes are organised by...
Definition / Principle / Limitation repeated for every point
Components / Workflow / Logic repeated as pseudo-explanation
Arrow chains used as the main explanation
Coverage note
Evidence used
AI process note
Course Knowledge Map
Predicted Essay Theme
Section A Strategy
```

`Course Knowledge Map` and equivalent course-map top matter are internal-only for ordinary notes and walkthroughs.

## DOCX Layout Surface

For `exam_prep_notes_docx` and `knowledge_walkthrough_docx`:

- body text, titles, lecture headings and all subheadings are left aligned;
- images are centered;
- default line spacing is compact, 1.05-1.15;
- body text uses black Arial in a readable size;
- route images are scaled automatically to the available content area, preserving aspect ratio and avoiding upscaling that reduces readability;
- large blank areas inside Word pages should be reduced by fitting images to page context and by avoiding unnecessary page breaks;
- image readability has priority over page-count minimisation.

## Practical And Data Notes

For practical/data/problem material, preserve equations, units, workflows, graph rules and numerical anchors, but write them as explanations rather than as the same mini-template.

Bad:

```text
Formula: Resin-COOH ⇌ Resin-COO- + H+
Logic: below pKa, resin loses negative charge
Formula: Resin-amine + H+ ⇌ Resin-amine-H+
Logic: below pKa, amine is positive
```

Good:

```text
pKa marks the pH at which an ionisable group is half protonated and half deprotonated. For a carboxyl resin group, Resin-COOH ⇌ Resin-COO- + H+: the protonated COOH form is neutral, whereas the deprotonated COO- form is negatively charged. Below the carboxyl pKa, high H+ favours COOH and the resin loses negative charge; above the pKa, COO- dominates and the resin can bind positively charged proteins. For an amine resin, the protonated form is positive, so it binds anions below its pKa and loses positive charge when deprotonated above its pKa.
```

Use labelled blocks only for genuinely separate items such as `Equation`, `Worked example`, `Diagnostic pattern`, or `Control`.

## Example Essay Surface

Example Essays are not notes. They require continuous essay prose, adaptive length, citations/highlights where source class requires them, and a conclusion.

Use this internal budget object:

```yaml
EssayAdaptiveBudget:
  question:
  command_verb:
  lecture_scope:
    - single_concept
    - one_lecture
    - multi_lecture
    - whole_module
    - cross_module
  core_source_skeleton_words:
  mechanism_detail_target_ratio: 0.10-0.15
  extra_reading_target_ratio: 0.10-0.15
  estimated_total_word_range:
  conclusion_required: true
  compression_policy: expression_efficiency_not_fixed_count
```

Rules:

- Do not hard-code 500-1000 words.
- Word count follows question demand, lecture scope, amount of examinable source content, and required evidence.
- Add molecular, cellular, receptor, channel, pathway, morphogen, assay, circuit, gene, or method detail only when it sharpens a lecture/source mechanism slot.
- Add Extra Reading or academic-paper detail only when it is verified, source-anchored, question-relevant, and analytically interpreted.
- Treat 10-15% mechanism-detail and 10-15% Extra Reading as target bands, not padding quotas. If insufficient verified material exists, do not fabricate or inflate.
- The conclusion is mandatory unless the user explicitly asks for a fragment rather than a complete essay.
- The conclusion must synthesise the answer and should not introduce new evidence.

## Highlight Surface Rules For Essays

Highlighting is a source-bound rendering rule, not a style choice.

- Uploaded Extra Reading Books or matched textbook chapters: yellow highlight.
- Verified Citation / Extra Reading Papers: green highlight with parenthetical author-year citation.
- Lecture-slide cited original papers after resolution/reading: green highlight with parenthetical author-year citation.
- Verified classic experimental sources used as fallback: green highlight with parenthetical author-year citation.
- Ordinary lecture material: no highlight.

Fail the essay if:

- academic paper content is not green-highlighted;
- uploaded book/chapter Extra Reading content is not yellow-highlighted;
- green-highlighted content lacks a parenthetical author-year citation;
- highlighted content is broader than the source-derived phrase or clause;
- the highlight exists only to increase the Extra Reading ratio.

## Publish Gate

Before publishing any public DOCX, run this sequence:

```text
1. Surface function scan: every visible item must be knowledge-bearing.
2. Non-knowledge scan: reject source-route narration, AI process, audit trace, study advice, and exam-meta leakage.
3. Explanatory-form scan: reject colon-slot fragmentation and shorthand arrow chains when they replace explanation.
4. Label-decision scan: delete or merge rigid template labels unless the label is semantically necessary.
5. Route-style scan: notes use black Arial, left-aligned headings, left-aligned body text, centered images, compact 1.05-1.15 spacing, and readability-preserving image fit.
6. Essay-specific scan: adaptive budget, conclusion, source-class highlights, citation colour, and word-count efficiency.
```

If any scan fails, rewrite the public surface rather than adding a disclaimer.

---

## Source File: `references__knowledge_walkthrough_docx_protocol.md`

---

# Knowledge Walkthrough DOCX Protocol

`knowledge_walkthrough_docx` is a compatibility route for users who explicitly ask for a lecture/source-order walkthrough. It writes the same artifact:

```text
Lecture_Knowledge_Walkthrough.docx
```

The route uses the same `PublicLectureNotesPlan`, validator, exam-ready direct prose gate, module teaching depth gate, readability layout gate and DOCX renderer as `exam_prep_notes_docx`. The only difference is that the style profile route is `knowledge_walkthrough_docx` and source/session order is treated as the primary ordering signal.

## Contract

Required public shape:

```yaml
PublicLectureNotesPlan:
  title:
  target_group_key:
  source_scale_budget:
  output_language_profile:
  route_docx_style_profile:
    route: knowledge_walkthrough_docx
    margin_cm: 2.0
    line_spacing: 1.05-1.15
    body_alignment: left
    title_alignment: left
    heading_alignment: left
    image_alignment: center
    text_color: black
    theme_colours_allowed: false
    blue_heading_styles_allowed: false
  public_lecture_sections:
    - lecture_title:
      modules:
        - module_title:
          knowledge_functions:
          explanation:
          blocks:
```

Legacy `course_modules`, `legacy_lectures`, `Course Knowledge Map` and knowledge-card scaffolds are internal-only compatibility inputs. They must be converted into `public_lecture_sections` before public DOCX writing or the run fails.

## Student Surface

The public document starts with the title and then lecture headings. It does not include a source role summary, source scope, extraction limitation, course map, prediction, study order, answer strategy, Section A/B strategy, or `How To Use This Document`.

Each module must explain at least two knowledge functions from definition/boundary, mechanism/process, method/readout, graph/data interpretation, calculation/unit/worked example, named example, and limitation/trap. The output should teach concept -> why it matters -> how it works -> interpretation -> boundary.

A walkthrough module must still be a micro-module teaching note, not a record of what the source says. Use direct knowledge claims and block release for wording such as `The course frames`, `The lecture states`, `The source material identifies`, `The source states`, or equivalent source narration. If a source-order section contains several separable operations, split it into smaller module headings.

## Language And Style

Default public output is English unless the user explicitly asks for Chinese or bilingual notes. Lecture walkthroughs use the ordinary notes style: black Arial, 2.0 cm margins, compact 1.05-1.15 line spacing, left-aligned body and headings, centered images, no theme colours and no blue heading styles.

## QA Gate

Block and regenerate if the DOCX contains raw slide bullets, source_route_narration, source narration, ai_process_or_provenance, internal QA fields, evidence scores, confidence bands, strategy/prediction content, inventory-only prose, missing module teaching depth, over-dense readability layout, repeated rigid labels, colon-slot fragmentation, shorthand arrow chains, non-black text, non-Arial text, justified body text or non-compact spacing.

---

## Source File: `references__kp_essay_synthesis_protocol.md`

---

# KP Essay Synthesis Protocol

This protocol governs knowledge-point explanation prose for legacy workbook compatibility and internal prose linting. It is not full Example Essay Mode and not the default revision DOCX route. Current public exam-prep outputs should use Academic Exam-Ready Notes and question-type DOCX add-ons.

Use `language_quality_contract.md` for shared prose-quality rules. This file adds workbook-specific constraints: no source tracing in explanation cells, no how-to-write language, and no page/slide narration.

## Core Separation

Internal source coverage and final student-facing prose are different products.

Internal coverage may preserve:

- slide/page order;
- page ranges;
- extracted slide text;
- OCR quality notes;
- raw bullet fragments;
- source anchors;
- coverage audit records;
- diagnostic flags.

The visible explanation cell must not describe that coverage. It must state the scientific argument directly.

Hard rule:

```text
Source coverage is satisfied by slide images, page ranges, coverage audit, and internal diagnostics. The explanation cell is not responsible for mentioning every page. Never preserve coverage by narrating page-by-page content in prose.
```

## Workbook Explanation Definition

The workbook explanation is:

- a concept-level paragraph, not a source trace;
- written for revision as a reusable essay paragraph fragment;
- normally 80-180 words;
- up to 240 words only for genuinely complex multi-mechanism KPs;
- direct academic English prose;
- factual only from target source evidence or verified sources;
- free of instructions to the student;
- free of page-by-page or slide-by-slide narration.

The paragraph itself is the output. Do not write commentary about how the student should write the paragraph.

## Required Paragraph Structure

Every KP synthesis should follow this structure unless the source material clearly requires a different order:

1. Topic sentence: state the scientific problem, principle, or argument.
2. Causal or mechanistic development: explain how actors, processes, compartments, signals, cells, or methods relate.
3. Named lecture examples: include only the most useful examples, not every extracted bullet.
4. Consequence or link-back: state why the mechanism matters for explanation, prediction, application, physiology, pathology, design, exam argument, or experimental interpretation.

Allowed source-order use:

```text
Use slide/page order to understand lecture logic, prerequisites, and transitions. Do not expose slide/page order as the prose structure.
```

## Domain Templates

Choose the best template by evidence in the target sources, not by benchmark identity.

### Neural / Control Systems

```text
behaviour or control problem -> circuit, sensory, or control mechanism -> functional or clinical consequence
```

Example logic: posture, gaze, reflexes, voluntary movement, sensory feedback, control hierarchy, lesion effects.

### Metabolism

```text
substrate, compartment, enzyme, or regulator -> flux or energetic state -> physiological consequence
```

Example logic: ATP/NADH balance, substrate routing, enzyme regulation, compartmentalisation, fed/fasted or stress state.

### Immune Response

```text
trigger, antigen, or damage signal -> cell, receptor, or cytokine interaction -> effector response -> disease, protection, diagnosis, or therapy implication
```

Example logic: PRR/PAMP/DAMP recognition, antigen presentation, cytokine networks, effector differentiation, immune pathology, vaccination or therapy.

### Plant / Agricultural Systems

```text
agricultural/environmental problem or trait -> plant mechanism, gene, hormone, physiology, or breeding tool -> evidence or named example -> crop or food-security consequence
```

Example logic: yield, climate stress, photosynthesis, flowering, hormones, genetic variation, breeding, transformation, crop resilience.

### Experimental / Data KPs

```text
question or problem -> method or evidence principle -> readout or inference -> limitation or consequence
```

Example logic: assay principle, graph interpretation, control, expected result, biological inference, limitation.

### Comparison KPs

```text
shared problem -> comparison axis -> contrast in mechanism or examples -> synthesis
```

Do not write all facts for one side followed by all facts for the other. Compare directly on the chosen axis.

## Mandatory KP Essay Synthesis Pass

Run this pass after Knowledge-point optimisation and before student-facing prose is written:

```yaml
KPEssaySynthesisPass:
  input:
    - KP title
    - source page range
    - slide images
    - extracted text where reliable
    - lecture/module order
    - exam format and question type
    - confidence flags
  steps:
    - use slide/page order only to infer lecture logic
    - compress raw extracted text into examinable claims
    - choose a paragraph archetype from the domain templates
    - draft direct student-facing prose
    - run a de-slide rewrite pass
    - run the essay-style linter or an equivalent banned-pattern check
    - write only the cleaned synthesis into the student-facing explanation section
  output:
    - clean explanation paragraph
    - diagnostics for omitted/uncertain/low-OCR evidence
```

## De-Slide Rewrite Pass

Before publishing student-facing prose, remove:

- page numbers used as prose structure;
- slide numbers used as prose structure;
- `first establishes`, `then develops`, `then closes`;
- `KP covers pages`;
- `slide sequence should be read as`;
- `remaining linked pages`;
- `central idea for this block`;
- `central examinable idea in this knowledge block`;
- `should be understood as`;
- `best written as`;
- `is mainly an argument about`;
- instructions such as `In an essay answer...`;
- any phrase that explains how to transform pages into a paragraph rather than providing the paragraph.

Rewrite by asking:

```text
If the page numbers disappeared, what scientific argument remains?
What is the mechanism, model, process, or operation?
Which named example genuinely improves the claim?
What consequence makes this examinable?
```

## Bad-To-Target Examples

Bad:

```text
Pages 25-27 should be read as one connected paragraph. Page 25 first establishes the operating problem. Page 26 then develops the degradation risk.
```

Target:

```text
Battery degradation is best framed as an interaction between electrode chemistry, ion transport and operating conditions rather than as a single failure mode. High current, repeated cycling and temperature stress can accelerate side reactions or structural change, reducing the active material available for reversible charge storage. The examinable argument is that performance loss is mechanistic: operating choices alter microscopic processes, and those processes accumulate into measurable capacity fade.
```

Bad:

```text
KP covers pages 15-24. The slide sequence should be read as an overview of measurement reliability, with remaining linked pages adding examples.
```

Target:

```text
Measurement reliability depends on separating systematic bias from random error. Bias shifts observations in a consistent direction, while random error widens the spread of repeated measurements, so calibration and replication solve different problems. This distinction matters because a precise instrument can still be wrong if it is miscalibrated, whereas an unbiased but noisy instrument may require more repeated observations before the underlying signal is clear.
```

Bad:

```text
The central idea for this block is reaction-rate control. In an essay answer, use these pages to explain the first part of the sequence and then add the later pages.
```

Target:

```text
Reaction-rate control links microscopic collision conditions to macroscopic yield, selectivity and safety. Temperature, concentration, catalysts and surface area alter the probability that particles collide with sufficient energy and the correct orientation, so changing a process condition changes both rate and sometimes product distribution. The examinable point is that rate is not a descriptive constant; it is a mechanistic consequence of controllable variables.
```

## Exam-Facing Prep Rule

`Exam-Facing Prep` must contain actual preparation products:

- predicted practice questions;
- answer operations;
- comparison axes;
- data/problem prompts;
- mark-producing schemas;
- MCQ discriminator axes;
- short-answer skeletons;
- method/readout/control prompts.

It must not say `Turn pages X-Y into one paragraph`, `use these pages`, or similar coverage-to-writing instructions.

## Factual Safety

Do not invent biological content to make prose smoother. If extracted text is insufficient, inspect available slide images or source evidence where possible. If the evidence still does not support a confident paragraph, write a conservative claim and flag low confidence internally rather than adding unsupported mechanisms, examples, dates, names, statistics, or citations.

Exemplars may guide style, paragraph density, and logic only. Do not copy exemplar factual claims or treat them as authority unless verified from the target source materials or reliable sources.

## Acceptance Criteria

The workflow passes this protocol if:

- concept-first synthesis quality is preserved across source sets;
- page-trace and module-overview anti-patterns no longer narrate pages/slides in the explanation column;
- at least 95% of KP explanation cells contain direct essay-style synthesis without banned phrases;
- explanation cells do not tell the student how to write;
- explanation cells provide the paragraph itself;
- prep cells contain practice questions, answer schemas, or exam operations, not `turn pages into a paragraph`;
- coverage remains preserved through page ranges, slide images, KP grouping, and audit/diagnostic outputs;
- full Example Essay generation remains opt-in only.

---

## Source File: `references__language_quality_contract.md`

---

# Language Quality Contract

This contract is the shared prose-quality standard for lecture walkthrough explanations, question-type reports, Example Essays, long-answer model answers, and any essay-style revision output.

The contract is subject-independent. Biological, chemical, quantitative, clinical, methodological, and sector-level essays use different factual evidence, but the same language discipline.

## Academic Exam-Ready Notes Prose Policy

For `exam_prep_notes_docx`, write notes as exam-ready academic synthesis, not as tutor narration or slide commentary.

This standard applies to every student-facing output. Example Essays, ordinary notes, knowledge walkthroughs, question-type reports and practical/data add-ons all need exam-ready direct prose. The format changes by route, but the visible language must state the knowledge itself rather than describe the route by which the model found it.

Use internal planning functions such as these to decide content, but do not force them into public headings:

- `Core Exam Claim`;
- `Key Definitions`;
- `Exam-Ready Knowledge Synthesis`;
- `Criteria / Components / Steps`;
- `Mechanism / Process Logic`;
- `Canonical Example`;
- `Exam Use`;
- `Common Error / Trap`;
- `Must Master`.

Ordinary Academic Exam-Ready Notes render compact public points and knowledge-bearing blocks. Public labels stay in default English unless the user explicitly requests another language or mixed-language output; schema field names and Skill package files remain English.

Avoid:

- `In this section we will learn...`;
- `This slide explains...`;
- `The notes are trying to say...`;
- `You should understand...`;
- `The course frames...`;
- `The lecture material uses...`;
- `The source material identifies...`;
- `The source states...`;
- source-route narration such as page, slide, or upload-order commentary inside the answer body.

The public paragraph shape is:

```text
examinable claim or problem -> mechanism/process -> source-backed example when useful -> scope or limitation -> concrete application when it adds knowledge
```

Do not preserve the original notes' order when that order is weaker than the exam logic, but do preserve the source-first baseline coverage of protected definitions, contrast pairs, criteria lists, named examples, diagrams, tables, equations, calculations, and workflow items before applying exam overlay.

For ordinary notes, use micro-module teaching prose. Each module should answer the useful student questions: what is it, how does it work, how do I read or use it, what calculation or decision follows, and what mistake does this prevent. A module that only names what exists is not exam-ready.

## Core Paragraph Shape

Every substantive paragraph should have a visible function:

```text
claim or problem -> mechanism/process/evidence -> scope or limitation -> consequence -> link back
```

Acceptable variants:

- `debate -> model A -> model B -> evidence -> evaluation`;
- `evidence -> mechanism -> interpretation -> limitation`;
- `question demand -> method principle -> readout -> interpretation -> control`;
- `shared problem -> comparison axis -> contrast -> synthesis`;
- `sector/system problem -> example evidence -> implementation mechanism -> wider implication`.

Across a complete Example Essay, keep descriptive and analytic material in balance. A good default is roughly half descriptive content and half analytic content:

- descriptive content states the relevant fact, mechanism, source-backed detail, experiment condition, pathway, case, or observed result;
- analytic content explains why the detail matters, what it proves or fails to prove, which boundary it sets, which mechanism it distinguishes, or how it answers the question.

Do not solve weak analysis by adding a decorative sentence at the end. Integrate analysis into the factual sequence so that evidence and interpretation stay adjacent.

## Required Rules

- Start with the answer or problem, not with metacommentary.
- Prefer direct positive claims. Use negative framing only when the false model is examiner-relevant and the contrast must be stated.
- Preserve necessary mechanisms when compressing language.
- Remove repeated definitions, repeated claims, decorative transitions, and low-value case details.
- Remove lecture-route narration and exam-guidance phrasing from the answer body.
- Add words only when they add mechanism, evidence, interpretation, limitation, or a required contrast.
- Add named biological, chemical, quantitative, clinical, methodological, or sector-specific detail only when it sharpens a lecture/source-derived mechanism slot or evidence function.
- When writing essay/problem-essay prediction outputs, phrase the prediction as an examinable theme with scope and operation, not as a guaranteed future question.
- Use examples as evidence for a wider claim.
- Convert experiments, data, and examples into evidence, mechanism, interpretation, and limitation when the question is evidence-heavy.
- Make contrasts explicit; do not rely on ambiguous `rather than` phrasing.
- Do not open with a negative-only sentence and then restate the correct claim in the next sentence. Write the correct claim first, adding the rejected model only as a compact boundary when needed.
- Use `not...but` and `rather than` sparingly. One necessary contrast can clarify a model boundary; repeated contrast framing usually signals that the paragraph should be rewritten as a direct positive claim.
- Keep logic linear. Avoid `A -> B -> A` sequencing where a claim is stated, interrupted by setup, and then restated. Combine setup and result when possible, especially for experiment evidence.
- Reject `A -> B -> A -> C` sequencing: do not state a claim, insert setup or example context, restart the same claim, and only then give the consequence. Attach the result to the setup and move directly to interpretation.
- Separate model, mechanism, evidence, and implication when a question asks for evaluation.
- Use citations only for non-obvious facts, theories, mechanisms, methods, evidence, data, or broad generalisations.
- Calibrate citation strength. Use `supports`, `implicates`, `is consistent with`, or `contributes to` unless the verified source directly proves causality.
- Avoid citation stacking; one precise citation is usually better than several weakly connected citations.
- Keep academic paper author names inside parenthetical in-text citations. Do not make a paper's authors the subject of an ordinary explanatory sentence unless the user explicitly requests literature-history narration.
- Do not invent statistics, dates, mechanisms, source names, quotations, or citations.
- If the user supplies no Example Essay citations, cite only sources found by slide-citation mining or verified classic-experiment fallback; never cite from memory.
- Conclude by synthesis. Do not add new evidence in the conclusion.
- Openings and conclusions should state the problem, thesis, or synthesis. They must not list every later section or repeat each body paragraph's conclusion.

## Banned Patterns

Reject or rewrite paragraphs that:

- narrate pages or slides instead of giving the argument;
- narrate the lecture/source route instead of giving the answer;
- say how the student should write instead of writing the answer;
- include exam-guidance sentences such as telling the student what the final thesis should be;
- open with an unnecessary `X is not...` sentence when the next sentence gives the real claim;
- use repeated `not... but`, `not simply`, `rather than`, or `however` structures when direct positive wording would be clearer;
- sequence evidence as claim, setup, repeated claim instead of claim, setup plus result, interpretation;
- restart the same claim after a setup sentence, producing A-B-A-C logic instead of a forward A-B-C argument;
- use an introduction or conclusion as a list of parts rather than as a synthesis;
- list examples without explaining what they prove;
- repeat the question using different words without adding mechanism;
- overuse broad claims such as `this is important` without specifying consequence;
- hide uncertainty behind confident language;
- turn supporting or associative evidence into a single-cause claim;
- use a citation copied from lecture slides without verifying the original source when source-derived content is included.
- turn academic-paper attribution into author-led prose when a parenthetical author-year citation would support the same content more cleanly;
- include a list of named channels, receptors, genes, cell classes, methods, examples, firms, or pathways without explaining what the list proves or distinguishes;
- use true but unneeded detail that makes the answer more encyclopedic but less exam-efficient;
- compress wording so that a modulating, gating, entraining, stabilising, supporting, or associative mechanism becomes the primary generator or proof.

## Compression Standard

Compression is not sentence shortening. It is function filtering.

Compression must be budgeted from the content, not from an arbitrary percentage. Before shortening a complete answer, identify:

- the protected source skeleton: core claims, mechanisms, evidence, comparisons, limitations, and synthesis items required by the question;
- protected academic details: named evidence, citation-supported mechanism detail, and examiner-relevant distinctions;
- removable redundancy: repeated framing, duplicated restatement, overlong transitions, and low-value background.

Compress only the removable redundancy first. Protected material may be tightened, but it must not disappear unless the question, source scope, or user request changes.

For each sentence, ask:

```text
Does it state the claim?
Does it explain the mechanism/process?
Does it provide evidence or an example that changes the answer?
Does it interpret what that evidence proves and what it does not prove?
Does it define the scope, limitation, or contrast?
Does it link back to the question?
```

Delete or merge sentences that do none of these.

Compression must preserve causal strength, scope qualifiers, negative distinctions, model boundaries, and evidence interpretation. Do not rewrite `not necessary for generating the core rhythm` as `not necessary for locomotion`, or `supports a mechanism` as `proves the mechanism`, unless the source warrants the stronger claim.

If the user asks for a percentage reduction that would delete protected source skeleton or citation-supported detail, reject that target and use the largest safe reduction. The final answer should not mention internal compression targets or word-count budgeting.

## Detail-Level Discipline

Named detail is valuable only when it improves the answer's function. Do not include a list of channels, receptors, nuclei, genes, cell classes, molecules, methods, firms, case names, equations, or pathways unless the lecture/source logic or exact question requires that level.

When a list is illustrative, compress it to a higher-level mechanism. When a list is examiner-relevant, keep only the items that distinguish mechanisms, evidence, limitations, or consequences.

Extra Reading and named mechanism detail should normally replace vague wording inside an existing lecture-derived sentence. They should not be added as separate expansion sentences unless the question requires that detail and the paragraph still gains mechanism or evidence density per word.

For every named detail, ask:

- Does this detail map to a PPT/source mechanism slot?
- Does it distinguish this mechanism from another?
- Does it explain an experiment, method readout, clinical consequence, sector consequence, or limitation?
- Would deleting it make the answer less accurate, or only less encyclopedic?

## Analytic-Over-Descriptive Standard

A paragraph fails if it contains more than two consecutive descriptive sentences without an analytic sentence. A complete essay also fails when the sentence-level balance is strongly descriptive-dominant. The target is approximately 40-60% analytic sentences, with enough descriptive material to keep the answer factual and enough analytic material to make the answer argumentative.

A valid analytic sentence must do at least one of the following:

- explain why the mechanism solves a control, causal, methodological, clinical, or sector-level problem;
- state what an experiment, example, dataset, or figure proves or fails to prove;
- compare two models, pathways, cases, mechanisms, or methods;
- define the scope or boundary of a claim;
- link a named detail to system-level function or the essay question.

## Example Use

Examples, case studies, firms, organisms, diseases, methods, figures, calculations, or datasets should be treated as evidence slots.

Allowed:

```text
The example demonstrates the mechanism because...
```

Forbidden:

```text
Example A happened. Example B happened. Example C happened.
```

## Citation Discipline

Use the smallest citation set that supports the claim. Do not cite:

- obvious lecture framing;
- generic background;
- every sentence in a paragraph;
- unsupported material copied from another essay.

Use citations for:

- original papers cited by lecture slides and actually read;
- verified classic experiments or landmark primary studies found because relevant lecture slides contain no usable citations;
- Citation / Extra Reading Papers with verified metadata and relevant claim support;
- Extra Reading Books matched to a chapter or section;
- online academic sources verified by DOI, PubMed, publisher page, textbook, or equivalent academic source.

Academic paper details require parenthetical author-year citation and green highlight in Example Essay DOCX output. Uploaded Extra Reading Book details require chapter/section anchoring and yellow highlight. Public source-basis preambles, prediction disclaimers, and decorative question labels are not essay prose and must be removed from final Word output.

## Completion Standard

Language quality is acceptable only when:

- no high-severity language linter failures remain;
- no medium-severity gap remains without an explicit reason;
- the source audit supports factual claims;
- Example Essay DOCX formatting and source-highlight rules pass;
- no benchmark or course identity is used as a production trigger.

---

## Source File: `references__long_answer_example_protocol.md`

---

# Long-Answer Example Protocol

Use this protocol when the exam uses non-essay, paragraph-style, project/scenario-based long answers. The output should read as a high-score experimental, practical, or scenario argument, not as a broad essay.

Trigger only when exam-format parsing or the user's request shows project, scenario, method-design, readout-interpretation, research-proposal, data/problem, or control/limitation structure.

## A. Source Digestion Before Writing

Before planning or drafting:

- read the relevant lecture/practical/source pages in source order;
- inspect rendered images when diagrams, structures, gels, spectra, tables, graphs, or handwritten exemplars matter;
- preserve source logic before segmenting: what problem is introduced, which method or mechanism follows, what readout it produces, and what limitation or control is required;
- use exemplars only for answer structure, paragraph logic, density, and wording style;
- ignore student annotations as factual course content unless the user explicitly asks to use them as notes;
- do not use exemplar subject claims as facts unless verified from official course material or reliable academic sources.

For method-heavy project exams, separate:

```text
method principle -> scenario application -> expected readout -> interpretation -> limitation/control
```

Do not transfer method families, systems, techniques, case studies, or recurrence claims from an example unless the target sources contain them.

## B. Knowledge Inventory

Construct this inventory before writing:

```yaml
LongAnswerKnowledgeInventory:
  must_use_core:
    - source points directly required by the question
  should_use_if_space:
    - supporting source points that improve precision
  method_or_process_principle:
    - examinable principle of each method/process
  scenario_application:
    - how the method/process applies to the given case
  readout_and_interpretation:
    - what the output would show and how it answers the question
  controls_or_limitations:
    - caveats, controls, alternatives, or weaknesses
  cross_source_links:
    - legitimate links to other source blocks in the same target set
  verified_extra_reading:
    - compact refinement only
  exclude:
    - true but non-useful facts for this question
```

Prioritise content that directly answers the command verb. Exclude methods or details that are true but not justified by the scenario.

## C. Pattern Inference

Test, do not assume:

- one lecturer gives one question;
- one module gives one question;
- one lecture gives one question;
- one knowledge point gives one question;
- cross-module synthesis;
- method-design slots;
- data/readout-interpretation slots;
- comparison-choice slots;
- scenario/problem slots;
- limitation/control slots.

Do not write by lecturer or source block in isolated sections unless the question itself is split that way.

## D. Paragraph Planning

Plan every long answer before drafting:

```yaml
LongAnswerParagraphPlan:
  paragraph_no:
  question_part:
  paragraph_function:
    - strategy_framing
    - core_mechanism_or_process
    - method_principle
    - method_application
    - readout_interpretation
    - comparison_choice
    - limitation_control
    - extra_reading_refinement
    - concluding_integration
  claim_or_goal:
  source_content_used:
  scenario_facts_used:
  method_or_mechanism:
  expected_readout:
  interpretation:
  control_or_limitation:
  extra_reading_use:
  excluded_content:
  word_budget:
```

Follow question parts and mark weighting. Higher-mark parts need more explanation, readout interpretation, and controls.

## E. Required Answer Logic

Default logic:

```text
question goal -> source principle -> scenario-specific application -> expected evidence/readout -> interpretation -> limitation/control
```

Every sentence must do one of these jobs:

- answer the command verb;
- justify method choice;
- connect source knowledge to the scenario;
- interpret a readout;
- add a necessary caveat or control;
- compare alternatives when the question requires a choice.

Do not write generic topic summaries, unconnected method lists, or broad essay introductions.

## F. Compact Academic Language

Useful sentence functions:

Purpose framing:

- `The central problem is to determine whether...`
- `The first step is to establish...`

Scenario anchoring:

- `Given that the question specifies..., the answer should focus on...`
- `This method is appropriate here because...`

Principle-to-application:

- `[Method] works by [principle], so in this scenario it can test...`

Readout interpretation:

- `A change in [signal/readout] would indicate...`
- `If the hypothesis is correct, the expected result is...`

Contrast:

- `This approach is preferable to [alternative] because...`
- `This alone would not prove..., so it should be combined with...`

Limitation/control:

- `The main limitation is...`
- `A suitable control would be...`
- `This should be checked because...`

Avoid decorative openings, repeated vague phrases, and padding. A word limit is a maximum, not a target.

## G. Extra Reading

Extra reading must be a compact refinement, not a second answer.

Source hierarchy:

1. recommended reading explicitly listed in lecture slides, handouts, or guidance;
2. books recommended by the lecturer or course handbook;
3. papers named in lecture slides;
4. peer-reviewed reviews or primary papers from PubMed, Google Scholar, DOI, or publisher pages;
5. standard textbooks.

If recommended reading is not present in uploaded material, ask whether the user has a recommended reading list. If the user says no, unknown, or gives no usable list, use verified academic papers or textbooks only when needed.

Extra reading may appear only as:

- one short paragraph;
- two to four integrated sentences;
- one named method example;
- one method-limitation clarification;
- one directly relevant modern/application context.

Reject unrelated detail, unverified citations, multiple extra-reading paragraphs, or any external point that changes the source-grounded answer.

## H. Transferable Long-Answer Operations

Apply these operation types only when exam-format parsing confirms scenario, project, method-design, readout-interpretation, or control/limitation structure:

- design a strategy;
- choose and justify methods;
- assess quality, state, performance, or validity;
- quantify a relationship or parameter;
- interpret an intervention or mutation/effect;
- determine an interaction, interface, pathway, structure, or causal relation;
- compare methods by suitability;
- quantify activity, performance, or specificity;
- explain a mechanism under scenario constraints;
- identify in vivo, clinical, environmental, engineering, or practical caveats.

For every operation, include:

- source principle;
- scenario-specific choice;
- expected readout;
- interpretation;
- limitation/control.

## I. QA Flags

Add or use these flags when relevant:

- `long_answer_project_scope_uncertain`;
- `paragraph_plan_missing`;
- `method_principle_missing`;
- `scenario_fact_not_used`;
- `expected_readout_missing`;
- `interpretation_missing`;
- `control_or_limitation_missing`;
- `generic_essay_written_for_project_question`;
- `old_regime_used_as_current_blueprint`;
- `extra_reading_unverified`;
- `example_used_as_fact`.

Fail safe by omitting uncertain mechanisms, citations, or lecturer preferences rather than inventing them.

---

## Source File: `references__modular_entrypoints_protocol.md`

---

# Modular Entry Points Protocol

This Skill must support both complete end-to-end execution and independent module execution. A user may ask for one module only, several modules chained together, or the full workflow.

## Hard Rule

Do only the requested scope unless the next module is required to make the requested output valid.

Examples:

- If the user asks only for source inventory, do not generate exam-analysis briefs or DOCX reports.
- If the user asks only for DOCX linting, do not rewrite essays.
- If the user asks only for Example Essay DOCX generation and already supplies a valid document plan, do not rerun past-paper prediction.
- If the user asks for the complete default revision workflow, route to `exam_prep_notes_docx` and run only its dependencies.
- If the user explicitly asks for a lecture-order walkthrough, route to `knowledge_walkthrough_docx` and run only its dependencies.

## Module Contract

Every module must define:

- trigger;
- minimum inputs;
- outputs;
- dependencies;
- standalone-use behaviour;
- composition behaviour when used inside the full workflow.

Modules must write their results in a reusable format when practical: JSON, DOCX, or a concise direct answer. Diagnostics should state which modules were run and which were intentionally skipped.

## Independent Modules

### 1. Source Inventory

Trigger:

- user asks to inventory, classify, extract, inspect, OCR, or list supplied files.

Minimum inputs:

- source files or a folder path.

Outputs:

- source inventory JSON/table;
- file roles;
- target group keys;
- extraction status;
- trust/evidence-use classification;
- QA flags for unreadable or unsupported files.

Standalone behaviour:

- stop after inventory unless the user requests analysis.

### 2. Automatic Example Analysis

Trigger:

- user supplies examples, answer keys, feedback, screenshots, existing analysis files, benchmark outputs, or asks to improve Skill logic from examples.

Minimum inputs:

- source inventory or example folder path.

Outputs:

- example category counts;
- `ExampleReviewLedger` records;
- `LanguageDelta` records;
- non-transferable content notes;
- protocol/script gap list.

Standalone behaviour:

- do not use example factual content for target predictions;
- run rule-promotion gating before updating production protocols, schemas, scripts, or regression fixtures.

### 3. Target Grouping / Regime Split

Trigger:

- user asks to group papers, detect regimes, compare years, or separate old/current formats.

Minimum inputs:

- source inventory or formal paper files.

Outputs:

- target-group-key grouping;
- exam-regime split;
- evidence-use labels for each regime;
- conflicts or missing years.

Standalone behaviour:

- do not generate predictions unless requested.

### 4. Question-Type Gate / Exam-Format Diagnosis

Trigger:

- user asks what type of exam it is, how questions are structured, or what preparation product fits.

Minimum inputs:

- formal papers, guidance, or source inventory.

Outputs:

- question family classification;
- section/mark/time/answer-rule summary;
- output-mode recommendation.

Standalone behaviour:

- return diagnosis and recommended next modules.

### 5. Lecture Segmentation

Trigger:

- user asks to split lectures/modules, identify lecture order, or map slides.

Minimum inputs:

- lecture slides/notes.

Outputs:

- lecture/module map;
- slide ranges;
- lecturer/module markers where available;
- title/agenda/recommended-reading exclusion candidates.

Standalone behaviour:

- do not infer exam predictions unless requested.

### 6. Knowledge-Point Optimisation

Trigger:

- user asks to create, merge, refine, or audit knowledge points.

Minimum inputs:

- lecture segmentation and source text/images.

Outputs:

- KP records;
- source anchors;
- merged slide/page ranges;
- prerequisite/linked KPs;
- examinability and likely question types.

Standalone behaviour:

- do not generate question-type reports unless requested.

### 7. KP Essay Synthesis

Trigger:

- user asks to rewrite KP explanations, remove page-by-page narration, make essay-style synthesis, or lint student-facing prose.

Minimum inputs:

- KP records or student-facing explanation drafts plus source anchors.

Outputs:

- concept-first synthesis paragraphs;
- essay-style linter report;
- rewrite diagnostics.

Standalone behaviour:

- only rewrite/lint the requested KP explanations.

### 8. Archetype / Past-Paper / Pattern Analysis

Trigger:

- user asks for predictions, examiner patterns, recurrence, archetypes, or past-paper mapping.

Minimum inputs:

- formal papers and KP map.

Outputs:

- question archetypes;
- past-paper mapping;
- hotness/retention/recency separated from confidence;
- pattern evidence and contradictions.

Standalone behaviour:

- do not generate a DOCX report unless requested.

### 9. Question-Type Output Generation

Trigger:

- user asks for MCQ traps, short-answer schemas, essay prompts, data/problem prompts, or long-answer plans.

Minimum inputs:

- exam-format diagnosis and KPs.

Outputs:

- MCQ Point Cards with explanation, exam-use pattern, traps, and must-remember rules;
- short-answer module logic and point cards with highlighted keywords and example answers;
- predicted essay themes by lecture scope, with optional practice variants;
- data/problem operations;
- long-answer project method/readout/control plans.

Standalone behaviour:

- output only the requested question-type product.

### 10. Academic Exam-Ready Notes DOCX Generation

Trigger:

- user asks for revision, exam-prep notes, to go through the material generally, or requests the default full workflow without a narrower artifact.

Minimum inputs:

- at least one readable course-note source, with factual-authority limits applied.

Outputs:

- Academic Exam-Ready Notes in `Lecture_Knowledge_Walkthrough.docx`;
- internal manifest or QA JSON outside the public output folder unless an audit package is requested.

Standalone behaviour:

- if supplied with a valid `ExamPrepNotesPlan`, generate/lint the DOCX without rerunning upstream modules.
- reconstruct course sections, map lecture sessions, and use supported exam emphasis before writing.

### 10b. Compatibility Knowledge Walkthrough DOCX Generation

Trigger:

- user explicitly asks for lecture knowledge in source order.

Minimum inputs:

- lecture slides or official notes.

Outputs:

- one student-facing lecture-first Word walkthrough.

Standalone behaviour:

- if supplied with a valid `KnowledgeWalkthroughPlan`, generate/lint the DOCX without rerunning upstream modules.
- preserve lecture order while splitting each lecture by conceptual function rather than slide/page number.

### 11. Question-Type DOCX Add-On Generation

Trigger:

- user asks for MCQ, short-answer, essay, practical/data, long-answer, project, scenario, or method-focused exam preparation beyond the base notes.

Minimum inputs:

- lecture slides or official notes;
- knowledge points;
- exam-format evidence when the requested add-on depends on past-paper structure.

Outputs:

- the matching student-facing DOCX add-on report;
- diagnostics JSON;
- optional audit package only when requested.

Standalone behaviour:

- if supplied with valid intermediate JSON/KP records, build the requested DOCX add-on without rerunning upstream modules.

### 12. Example Essay DOCX Mode

Trigger:

- user explicitly asks for complete Example Essays, model essays, full essay-style answers, or essay Word documents.

Minimum inputs:

- essay question(s);
- relevant lecture slides or lecture-source inventory;
- optional slide-cited original sources;
- optional Extra Reading Books.

Outputs:

- one standalone DOCX per essay;
- internal manifest JSON, source audit JSON, source maps, and QA JSON for validation;
- optional ZIP only if requested or needed as the final delivery format.

User-facing output should include the requested final artefacts. Keep internal validation files out of the public output folder unless the user explicitly requests an audit package.

Standalone behaviour:

- if a valid `ExampleEssayDocumentPlan` is supplied, generate/lint DOCX files without rerunning prediction.
- if no lecture slides are supplied or identifiable, do not draft a polished essay; request the missing lecture evidence or flag the blocker.

### 13. Citation Resolver

Trigger:

- user asks to detect/resolve citations from lecture slides or prepare green-highlight source material.

Minimum inputs:

- relevant slide text/images;
- optional uploaded source PDFs/books.

Outputs:

- citation candidates JSON;
- resolution log;
- read-status notes.

Standalone behaviour:

- do not insert citation-derived essay content unless the source is resolved and read.

### 14. Extra Reading Matcher

Trigger:

- user asks to integrate Extra Reading Books or locate relevant chapters.

Minimum inputs:

- essay question or KP terms;
- uploaded book/chapter files.

Outputs:

- chapter/section match log;
- selected anchors;
- insert plan;
- QA flag if no relevant chapter is found.

Standalone behaviour:

- stop after matching unless the user asks to write or update an essay.

### 15. QA / Linting

Trigger:

- user asks to check, validate, lint, audit, or verify an output.

Minimum inputs:

- DOCX directory, source maps, diagnostics, or generated artefacts.

Outputs:

- lint reports;
- pass/fail status;
- offending rows/runs/paragraphs;
- QA flags.

Standalone behaviour:

- do not rewrite files unless explicitly requested.

### 16. Cross-Subject Regression

Trigger:

- user asks to run regression, validate benchmark behaviour, or check Skill quality across outputs.

Minimum inputs:

- regression suite and optionally generated DOCX folders.

Outputs:

- regression report JSON;
- DOCX/prose lint results where supplied.

Standalone behaviour:

- do not make content predictions.

### 17. Gap Closure Report

Trigger:

- user asks to keep improving until no major gaps remain, or asks for final Skill readiness.

Minimum inputs:

- lint reports, regression results, source-audit reports, external review notes, or generated outputs.

Outputs:

- high/medium/low gap report;
- pass/fail completion decision;
- required follow-up edits.

Standalone behaviour:

- do not claim completion while high or medium gaps remain unresolved.

### 18. GitHub Ready QA

Trigger:

- user asks to push, publish, release, or update GitHub.

Minimum inputs:

- repository checkout.

Outputs:

- GitHub-ready QA report;
- identity-trigger scan;
- public safety scan;
- synced installed-Skill check.

Standalone behaviour:

- do not commit or push if GitHub-ready QA fails.

## Full Workflow Composition

When the user requests the complete exam-prep workflow, run modules in this order:

1. Source Inventory.
2. Automatic Example Analysis when examples, answer keys, feedback, existing analyses, or external review notes are supplied.
3. Target Grouping / Regime Split.
4. Question-Type Gate / Exam-Format Diagnosis.
5. Course-Section Reconstruction.
6. Lecture Session Mapping.
7. Knowledge-Point Optimisation.
8. KP Essay Synthesis when a paragraph-style explanation layer is requested.
9. Archetype / Past-Paper / Pattern Analysis.
10. Academic Exam-Ready Notes DOCX Generation for the default revision output.
11. Question-Type DOCX Add-On Generation.
12. Optional Visual-Aid Planning.
13. QA / Linting.
14. Cross-Subject Regression when benchmark inputs or generated outputs are supplied.
15. Gap Closure Report when modifying the Skill itself.
16. GitHub Ready QA before commit or push.

If the user also explicitly requests complete Example Essays, run Example Essay DOCX Mode as a separate branch after lecture-source grounding and question selection:

1. Lecture Slide Scope Detection.
2. Lecture Slide Reading.
3. Lecture Logic Reconstruction.
4. Citation Resolver.
5. Extra Reading Matcher when books are supplied.
6. Essay Plan.
7. DOCX Generation.
8. DOCX Format Linting.
9. Render/Structural QA.
10. Source Audit.
11. Complete Example Essay Language Linting.

## Reuse Of Intermediate Outputs

If the user supplies a valid intermediate artefact, prefer using it directly:

- source inventory JSON can feed target grouping;
- lecture segmentation can feed KP optimisation;
- KP map can feed synthesis, exam-analysis selection, or DOCX report generation;
- student-facing prose drafts can feed the essay-style linter;
- ExampleEssayDocumentPlan can feed DOCX generation;
- DOCX + source map can feed DOCX format linter;
- source audit can feed regression;
- automatic example analysis can feed gap closure;
- gap reports can feed GitHub-ready QA.

Do not recompute upstream analysis unless the supplied artefact is missing, stale, incompatible, or the user asks for a full rerun.

## Reporting

Every run should state:

- modules run;
- modules skipped;
- input artefacts used;
- output artefacts generated;
- QA/lint status;
- blockers if a requested module cannot run.

Keep this report concise in the final user response.

---

## Source File: `references__operational_ontology_protocol.md`

---

# Operational Ontology Protocol

The Skill uses an operational ontology to control workflow, evidence permissions, and output generation. The ontology is not a topic taxonomy and not an embedding index. It is an object-link-action model:

```text
SkillConfig -> WorkflowPlan -> SourceDocument -> SourceFragment -> AtomicKnowledgeLedger -> CourseSection -> KnowledgePoint -> SourceBaselineNotesPlan -> KnowledgeOnlyStudentView -> PublicOutputPoint -> ExamOverlayPass -> PrepArtifact -> QAFlag
```

## Purpose

The ontology exists to make exam preparation evidence-bound and auditable:

- the user request becomes a plan before execution;
- source files become typed objects before they influence output;
- links encode what a source is allowed to support;
- actions write back objects, links, artifacts, and QA flags;
- validators block unsupported claims, wrong-regime evidence, unverified citations, and helper artifacts in public output.

## Internal Lakehouse Layers

Treat each exam-prep run as a small auditable data product, not a one-off response. The internal layers are:

```text
Bronze layer
Raw source inventory:
SourceDocument, extraction status, source hash, raw extracted text, slide/page images.

Silver layer
Normalized fragments:
SourceFragment, FragmentPartition, PastPaperQuestion, AssessmentRegime, ExamBlueprint.

Gold layer
Validated semantic objects:
CourseSection, LectureSession, LectureConceptModule, KnowledgePoint,
AtomicKnowledgeLedger, SourceBaselineNotesPlan, KnowledgeOnlyStudentView,
ExamEmphasisProfile, ExamOverlayPass, ExaminerOperation, QuestionArchetype, SlotGrammar,
PublicOutputPoint, PublicPointBlock, OutputLanguageProfile, RouteDocxStyleProfile,
RenderDecision, PointCoverageBinding, EvidenceClaim, ReadingSource, MethodBlock, QuestionTypeAddOn, VisualAidSpec,
GeneratedVisualAid, QAFlag.

Serving layer
Student-facing artifacts:
Academic Exam-Ready Notes DOCX rendered from public points, Lecture Knowledge Walkthrough DOCX, question-type DOCX reports,
Essay Module Example Essays DOCX, direct answer, plus hidden
diagnostics, lineage, and source audit when requested.
```

Student-visible output may only be generated from Gold objects whose support links pass validation.

## Object Layer

Use `ontology/ontology.json` as the machine-readable contract for object types.

Core objects:

- `UserExamPrepRequest`, `UserConstraint`, `SourceCoverageMap`, `GateResult`, `WorkflowPlan`, and `OutputView`: interaction-layer objects that select mode, plan actions, expose source coverage, and prevent hidden blockers.
- `LectureModule` and `KnowledgeWalkthroughPlan`: compatibility lecture-review objects that preserve lecture order while converting slides or notes into conceptual modules.
- `CourseSection`, `LectureSession`, `LectureConceptModule`, `AtomicKnowledgeLedger`, `AtomicKnowledgeUnit`, `SourceBaselineNotesPlan`, `KnowledgeOnlyStudentView`, `PublicOutputPoint`, `PublicPointBlock`, `OutputLanguageProfile`, `RouteDocxStyleProfile`, `RenderDecision`, `PointCoverageBinding`, `ExamEmphasisProfile`, `ExamOverlayPass`, and `ExamPrepNotesPlan`: default Academic Exam-Ready Notes objects that reconstruct source-backed course structure, decompose source blocks into protected atomic items, protect source-first baseline coverage, filter public output to knowledge-only content, keep default English labels unless the user explicitly requests another language, select compact route style, run the knowledge-only rendering gate, then apply exam overlay before writing. The same `RouteDocxStyleProfile` and knowledge-only gate also control the compatibility lecture walkthrough route so it cannot silently fall back to essay-style formatting or generic advice sections.
- `QuestionTypeAddOn`, `VisualAidSpec`, and `GeneratedVisualAid`: final-layer add-on objects that may extend notes without becoming factual authority.
- `SourceDocument`: every uploaded or discovered file, with role, trust level, allowed evidence use, and extraction status.
- `ExampleReviewLedger`, `TransferableRuleSet`, `NonTransferableContentBlocklist`, and `ExampleTransferQA`: internal example-learning objects that require good/bad analysis, block example-specific content, and gate rule promotion before production changes.
- `SourceFragment`: slide, page, question, figure, table, protocol step, chapter, or section.
- `FragmentPartition`: metadata partition used to prune irrelevant fragments before expensive reasoning or generation.
- `AssessmentRegime` and `ExamBlueprint`: current versus old exam structures.
- `PastPaperQuestion`: question-level record extracted from a paper.
- `KnowledgePoint`: examinable reasoning block, not a raw topic label.
- `ExaminerOperation`: task verb, input format, cognitive operation, answer shape, and marking logic.
- `QuestionArchetype`: recurrent question-family skeleton with slot grammar.
- `EvidenceClaim`: answer claim with source anchors and support strength.
- `ReadingSource`: recommended book, paper, DOI/PubMed/publisher record, or verified academic source.
- `PracticalOperation`, `MethodBlock`, `MCQScoringPolicy`, `ShortAnswerVariant`, and `EssayCoveragePlan`: type-specific preparation objects. Essay outputs that use academic paper evidence must run citation rendering QA so author-year attribution stays parenthetical in normal public prose.
- `PrepArtifact`: student-facing or internal output.
- `QAFlag`: blocking or warning condition.
- `WorkflowRun`: modules run, modules skipped, outputs created, and QA summary.
- `RunManifest`: persisted run-level source hashes, actions, object-store paths, artifact list, and QA summary.
- `LineageEvent`: append-only action event linking input objects, output objects, artifacts, and QA flags.

## Fragment Partitioning

Build `FragmentPartition` objects when the run contains multiple source roles, multiple years/regimes, any past-paper prediction, any Example Essay source audit, or any large source set.

Partition metadata should include:

```yaml
FragmentPartition:
  partition_id:
  source_id:
  fragment_ids: []
  source_role:
  analysis_context:
  target_group_key:
  exam_regime:
  year:
  lecture_or_module:
  question_type:
  concept_type:
  command_verbs: []
  input_format:
  image_count:
  extraction_confidence:
  allowed_evidence_use: []
  source_hash:
```

Use partitions as a pruning layer:

- MCQ prep reads MCQ-compatible KPs, MCQ past-paper questions, definition/classification/mechanism/calculation partitions, and visible scoring-policy evidence.
- Example Essay mode reads the relevant lecture scope, citation candidates, verified reading, and essay-relevant evidence partitions; it does not read unrelated answer keys by default.
- Data/problem prep reads graph, table, protocol, case, calculation, readout, control, and limitation partitions.
- QA/lint-only requests read output artifacts and lineage before rerunning upstream analysis.
- Source-inventory-only requests stop at Bronze unless the user asks for deeper processing.

## Link Layer

Links must encode evidence permission, not only semantic similarity.

Allowed examples:

```text
SourceDocument CONTAINS SourceFragment
SourceDocument PARTITIONED_AS FragmentPartition
FragmentPartition GROUPS_FRAGMENT SourceFragment
SourceFragment SUPPORTS_KP KnowledgePoint
SourceFragment SUPPORTS_LECTURE_MODULE LectureModule
SourceFragment SUPPORTS_COURSE_SECTION CourseSection
LectureSession HAS_LECTURE_CONCEPT_MODULE LectureConceptModule
KnowledgePoint MAPS_KP_TO_EXAM_EMPHASIS ExamEmphasisProfile
AtomicKnowledgeLedger LEDGER_DECOMPOSES_FRAGMENT SourceFragment
AtomicKnowledgeLedger LEDGER_HAS_ATOMIC_UNIT AtomicKnowledgeUnit
AtomicKnowledgeLedger LEDGER_BINDS_KP KnowledgePoint
SourceBaselineNotesPlan BASELINE_USES_ATOMIC_LEDGER AtomicKnowledgeLedger
SourceBaselineNotesPlan BASELINE_COVERS_KP KnowledgePoint
ExamOverlayPass OVERLAY_USES_BASELINE SourceBaselineNotesPlan
KnowledgeOnlyStudentView VIEW_FILTERS_BASELINE SourceBaselineNotesPlan
KnowledgeOnlyStudentView VIEW_APPLIES_OVERLAY ExamOverlayPass
KnowledgeOnlyStudentView VIEW_SELECTS_PUBLIC_POINT PublicOutputPoint
ExamPrepNotesPlan PLAN_HAS_PUBLIC_POINT PublicOutputPoint
PublicOutputPoint PUBLIC_POINT_HAS_BLOCK PublicPointBlock
PublicOutputPoint PUBLIC_POINT_COVERS_ATOMIC_UNIT AtomicKnowledgeUnit
PublicPointBlock PUBLIC_BLOCK_COVERS_ATOMIC_UNIT AtomicKnowledgeUnit
OutputView OUTPUT_VIEW_USES_LANGUAGE_PROFILE OutputLanguageProfile
PrepArtifact PREP_ARTIFACT_USES_DOCX_STYLE_PROFILE RouteDocxStyleProfile
RenderDecision RENDER_DECISION_HIDES_INTERNAL_FIELD ExamPrepNotesPlan
RenderDecision RENDER_DECISION_RENDERS_BLOCK PublicPointBlock
PointCoverageBinding POINT_COVERAGE_BINDS_PUBLIC_POINT PublicOutputPoint
ExamPrepNotesPlan PLAN_USES_SOURCE_BASELINE SourceBaselineNotesPlan
ExamPrepNotesPlan PLAN_USES_EXAM_OVERLAY ExamOverlayPass
KnowledgePoint SUPPORTS_CLAIM EvidenceClaim
PastPaperQuestion INSTANTIATES QuestionArchetype
QuestionArchetype USES_OPERATION ExaminerOperation
KnowledgePoint COMPATIBLE_WITH QuestionArchetype
ReadingSource ENRICHES_KP KnowledgePoint
PrepArtifact GENERATED_FROM_KP KnowledgePoint
PrepArtifact GENERATED_FROM_LECTURE_MODULE LectureModule
PrepArtifact GENERATED_FROM_EXAM_PREP_NOTES_PLAN ExamPrepNotesPlan
GeneratedVisualAid GENERATED_FROM_VISUAL_AID_SPEC VisualAidSpec
PrepArtifact GENERATED_FROM_MCQ_POLICY MCQScoringPolicy
PrepArtifact GENERATED_FROM_SHORT_ANSWER_VARIANT ShortAnswerVariant
PrepArtifact GENERATED_FROM_ESSAY_COVERAGE_PLAN EssayCoveragePlan
PrepArtifact GENERATED_FROM_METHOD_BLOCK MethodBlock
PrepArtifact GENERATED_FROM_PRACTICAL_OPERATION PracticalOperation
QAFlag BLOCKS PrepArtifact
WorkflowRun HAS_MANIFEST RunManifest
WorkflowRun EMITS_LINEAGE LineageEvent
```

Forbidden examples:

```text
cross_target_example SUPPORTS_FACTUAL_CLAIM EvidenceClaim
old_or_different_regime CONTROLS_CURRENT_BLUEPRINT ExamBlueprint
unverified_external_source SUPPORTS_CLAIM EvidenceClaim
unreadable_source SUPPORTS_KP KnowledgePoint
generated_visual_aid SUPPORTS_CLAIM EvidenceClaim
```

## Action Layer

Every workflow step should be expressible as an action that reads objects and writes objects, links, or QA flags:

```text
CreateSourceInventory
ParseUserExamPrepRequest
BuildSourceCoverageMap
SelectOutputView
RecordGateResult
PlanWorkflow
ExtractFragments
BuildFragmentIndex
AnalyzeExamplesIntoTransferableRules
SynthesizeTransferableRules
RunRulePromotionGate
LintExampleTransfer
BuildLectureModules
BuildKnowledgeWalkthroughPlan
ReconstructCourseSections
MapLectureSessions
BuildLectureConceptModules
BuildAtomicKnowledgeLedger
BuildSourceBaselineNotesPlan
RunBaselineCoverageFloorQA
BuildExamEmphasisProfile
ApplyExamOverlayPass
RunOverlayCoverageQA
BuildKnowledgeOnlyStudentView
SelectOutputLanguageProfile
SelectRouteDocxStyleProfile
BuildPublicOutputPoints
BindAtomicItemsToPublicPoints
LintPublicOutputPoints
LintOutputLanguageRequestPolicy
BuildExamPrepNotesPlan
BuildQuestionTypeAddOns
PlanVisualAid
GenerateVisualAid
NormalizeTargetGroup
SplitExamRegime
ExtractPastPaperQuestions
ClassifyQuestionType
InferQuestionArchetype
SegmentKnowledgePoints
BuildPracticalOperations
BuildMethodBlocks
BuildMCQScoringPolicy
GenerateShortAnswerVariants
BuildEssayCoveragePlan
MapKPToArchetype
VerifyReadingSource
RunCitationRenderingGate
GeneratePrepArtifact
GenerateExamPrepNotesDocx
LintExamPrepNotes
LintExamPrepDocxStyle
CreateWorkflowRun
ValidateOntologyRuntime
WriteRunManifest
RunDeliverableQA
ApproveStudentOutput
```

Actions may use helper scripts, but production behaviour must be controlled by object properties, link types, and validation rules rather than benchmark names or source-set identity.

## Query Discipline

Student-facing artifacts should be generated from eligible ontology queries, not direct raw-file concatenation.

Workflow plan preview query:

```text
request scope + selected preset + target + actions + skipped modules + blockers + publish gate
```

Knowledge walkthrough query:

```text
lecture order + lecture overview + module map + lecture modules + key logic + common confusions + lecture recap
```

Student output filter query:

```text
internal objects + selected output mode + allowed visible fields + forbidden visible fields
```

Academic Exam-Ready Notes query:

```text
course knowledge map + lecture mapping + atomic ledger + source baseline + knowledge-only student view + output language profile + route DOCX style profile + public output points + public point blocks + point coverage bindings + render decisions + exam overlay + internal knowledge cards + question-type add-ons + optional visual aids + forbidden student fields
```

Essay theme query:

```text
current regime + essay archetype + compatible KPs + lecture scope + confidence band + QA flags
```

MCQ prep query:

```text
MCQ archetype + discriminator axes + distractor families + scoring policy + confidence band
```

Practical/data query:

```text
input type + required operation + expected inference + limitation/control + follow-up
```

Extra-reading insertion query:

```text
verified reading source + matched KP + matched chapter/section + sentence-budget decision
```

## Runtime Object Store

When an implementation persists ontology outputs, use JSONL or JSON under an internal QA directory, not in the public student deliverable folder:

```text
internal_qa/ontology_objects/source_documents.jsonl
internal_qa/ontology_objects/workflow_plans.jsonl
internal_qa/ontology_objects/source_fragments.jsonl
internal_qa/ontology_objects/fragment_partitions.jsonl
internal_qa/ontology_objects/past_paper_questions.jsonl
internal_qa/ontology_objects/question_archetypes.json
internal_qa/ontology_objects/evidence_claims.jsonl
internal_qa/ontology_links/links.jsonl
internal_qa/run_manifest.json
internal_qa/lineage_events.jsonl
internal_qa/input_readiness.json
internal_qa/workflow_plan.md
```

These files are helper artifacts. They must not be mixed into the final user-facing output unless the user explicitly requests an audit package.

## Validation Gates

Fail or block student-facing output when:

- a claim has no source anchor;
- an ontology object has no writer action;
- the requested output mode has no selected `OutputView`;
- a major generation path has no `WorkflowPlan`;
- student-facing output exposes internal evidence, confidence, source-anchor, discriminator, task-verb, or examiner-operation fields;
- a knowledge walkthrough follows slide/page order instead of conceptual module order;
- the source coverage map hides a blocking gap;
- a source role is not allowed to support the claim;
- old-regime evidence controls current-regime prediction;
- external examples provide factual or prediction content;
- a citation or extra-reading source is not verified/read where required;
- output mode does not match the detected question type;
- a prediction claims exact future wording, guarantee, or fake numerical precision;
- a student-facing artifact has no valid Gold-object lineage;
- a blocking QA flag is unresolved;
- a publish action has no run manifest or lineage event;
- public output contains helper artifacts.

## Control-Plane Invariants

Use these as hard publish gates:

```text
No object -> no link.
No valid link -> no claim.
No verified claim -> no student-facing synthesis.
No lineage -> no reproducible publish.
No QA pass -> no publish.
```

Do not implement distributed compute, warehouses, or platform-specific services. The transferable idea is local metadata, pruning, validation, lineage, and reproducibility.

---

## Source File: `references__past_paper_prediction_protocol.md`

---

# Past Paper Prediction Protocol

Past-paper analysis is not a guessing workflow. It is a constrained preparation-allocation workflow:

```text
past papers -> current exam regime -> question-level records -> archetype registry -> slot grammar -> KP compatibility -> internal confidence band -> chat-only Exam Analysis Brief -> output-route selection
```

The prediction target is a question family and preparation action, not exact future wording.
Do not package this analysis as a separate prediction file or workbook in ordinary student-facing output.

## Theoretical Model

Each question should be encoded as a record:

```text
q = (topic, subtopic, format, command verb, representation, marks, source block)
```

Then group questions by family:

```text
fixed examiner operation + replaceable slot grammar + reusable mark-scheme skeleton
```

For internal ranking, use separate explainable metrics:

```text
InternalScore =
  2.0 * BlueprintFit
+ 2.0 * ArchetypeReuse
+ 1.5 * MarkSchemeReuse
+ 1.0 * KPRecurrence
+ 1.0 * Recency
+ 1.0 * LectureCentrality
+ 0.8 * CoverageGap
+ 0.7 * AssessmentEase
- 1.2 * SaturationPenalty
- 2.0 * RegimeMismatchPenalty
```

Do not expose fake precision to students. For small paper sets, output confidence bands:

- `High`: stable current regime, repeated archetype, compatible lecture centrality, no recent contradiction.
- `Medium`: recurring family or KP, but question form or regime fit is uncertain.
- `Low`: plausible fresh coverage, weak past-paper evidence, or old-regime support only.

Student-facing priority should consider expected value, not just frequency:

```text
priority = probability_band * mark_value * student_weakness * transferability / prep_time
```

When student weakness or prep time is unknown, omit those terms and state that the ranking is evidence-only.

## Question-Level Extraction

Past papers must be converted into `PastPaperQuestion` records before statistical or archetype inference.

Required fields:

```yaml
PastPaperQuestion:
  source_file:
  target_group_key:
  year:
  paper_id:
  section:
  question_no:
  subquestion_no:
  raw_stem:
  marks:
  answer_rule:
  question_type:
  command_verbs: []
  input_format:
  negative_marking:
    present:
    correct_value:
    wrong_value:
    unanswered_value:
  candidate_options:
    count:
    option_texts: []
  extracted_confidence:
  review_flag:
```

If extraction is weak, emit `review_flag` rather than inventing missing sections, marks, options, answers, or diagrams.

## Question-Type Targets

| Question type | Correct prediction object | Incorrect prediction object |
| --- | --- | --- |
| MCQ | concept discriminators, traps, calculation/recognition modes, scoring policy | exact option text or official answer without answer key |
| Fill blank | term bank, cloze variants, exact wording anchors from source | hidden official blanks not visible in sources |
| Short answer | bounded question-family variants and mark-producing schemas | all possible questions |
| Long-answer project/problem | transferable method/readout/control blocks | exact rotating scenario |
| Essay/problem essay | lecture block, command verb, argument skeleton, evidence bank | exact title or guaranteed stem |

## MCQ Scoring Policy

For MCQ regimes, extract scoring rules when visible:

```yaml
MCQScoringPolicy:
  mode: single_best | multiple_true_false | statement_judgement
  option_count:
  correct_value:
  wrong_value:
  unanswered_value:
  positive_ev_threshold:
  action_rule:
```

If unanswered value is zero, correct value is `c`, and wrong penalty magnitude is `d`, the internal expected-value threshold is:

```text
p > d / (c + d)
```

Examples:

- 4-option single-best with `+1` and `-1/3`: threshold `0.25`.
- Statement marking with `+1/3` for correct true and `-1` for wrong true: threshold `0.75`.

Do not output official answer values unless the paper or answer key states them.

## Short-Answer Variant Space

Short-answer preparation should generate bounded variants, not infinite questions:

```text
archetype + slot grammar + lecture KP + mark scale -> ShortAnswerVariant
```

Variant types:

- define;
- list;
- compare;
- explain mechanism;
- draw/label;
- calculate;
- interpret graph;
- design experiment.

Each variant must have a source-linked KP, required mark points, concise exam answer, reference expansion, allowed examples, and confidence band.

## Long-Answer Method Blocks

For scenario/project/problem long answers, prepare reusable method blocks:

```text
question goal -> method choice -> readout -> interpretation -> control -> limitation
```

The biological, chemical, clinical, engineering, or data scenario may rotate. The stable object is the operation.

Method blocks should record:

- method family;
- principle;
- when to use;
- expected readout;
- interpretation logic;
- required control;
- main limitation;
- compatible question parts;
- source anchor.

## Essay Coverage Plan

For essay sections with several options where the student answers one, optimise coverage rather than pretending exact titles can be known.

Use:

```yaml
EssayCoveragePlan:
  lecture_scope_type: one_lecture_one_theme | one_lecture_two_themes | two_lectures_one_theme | cross_lecture_synthesis | uncertain
  likely_command_verbs: []
  argument_skeleton:
  paragraph_claims: []
  evidence_bank: []
  diagram_bank: []
  comparison_axes: []
  limitations: []
  coverage_role: core | backup | optional
  confidence: High | Medium | Low
```

If a section presents several essay options and the student answers one, prepare enough lecture blocks to make at least one high-quality answer likely. Do not force equal-depth preparation for every possible block unless the user asks for exhaustive coverage.

## Exam-Informed Notes Control

When formal past papers are supplied with a general notes or revision request, past-paper analysis feeds `exam_prep_notes_docx` before notes are generated:

```text
formal papers -> current regime split -> PastPaperQuestion records -> question families -> KP compatibility -> ExamEmphasisProfile -> ExamOverlayPass -> Academic Exam-Ready Notes
```

The `ExamEmphasisProfile` feeds the `ExamOverlayPass`, which may control density, ordering, and visible star priority labels for source-backed KnowledgePoints after the `SourceBaselineNotesPlan` has passed coverage QA. It may also decide whether MCQ, short-answer, long-answer, practical/data, or essay add-ons are useful after the base notes.

The `ExamEmphasisProfile` and `ExamOverlayPass` must not control:

- deletion, hiding, or over-compression of protected source-backed baseline modules;
- exact future wording;
- unsupported official answers;
- fake numerical prediction;
- content outside supplied or verified source scope;
- public recurrence counts, confidence bands, or past-paper year mappings.

If no formal papers exist, generate notes from official source centrality, conceptual dependency, learning-objective emphasis, and source coverage only. Do not invent exam frequency.

## Lecturer Style

Lecturer or source-block style is a weak auxiliary variable.

It cannot raise confidence above `Medium` unless all conditions are met:

1. same current exam regime;
2. repeated over at least two formal papers;
3. aligned with lecture objectives, summaries, or central lecture blocks;
4. not contradicted by recent papers.

Never infer lecturer preference from one question alone unless labelled `Low`.

## Hard Failures

Fail or rewrite prediction output when it contains:

- `this exact question will appear`;
- `guaranteed`;
- precise probabilities from a small paper set, such as `72.4%`;
- lecturer preference inferred from one question without a `Low` label;
- external example content used as target prediction;
- old-regime paper controlling current-regime blueprint;
- short-answer variants with no source-linked KP;
- MCQ answer claimed official without an answer key;
- essay stem presented as official instead of a practice variant;
- generated `all possible questions` without bounded slot grammar.

---

## Source File: `references__practical_data_problem_protocol.md`

---

# Practical, Data, And Problem Protocol

Use this protocol when supplied materials include practical protocols, problem papers, case studies, numerical assessments, spotters, figures, graphs, tables, or answer keys with worked reasoning.

## Evidence Boundary

- Practical protocols are method/readout/control evidence.
- Problem papers and case studies define operation grammar.
- Answer keys and worked solutions teach mark-producing reasoning and traps.
- Example papers and mocks define format and practice style, not topic recurrence.
- Image-only figures require visual inspection before exact values are claimed.

## Question Operation Shape

For every practical/data/problem question, infer:

```text
input type -> required operation -> expected inference -> limitation/control -> follow-up action
```

Input types:

- graph;
- table;
- figure;
- image/spotter;
- experimental protocol;
- case/scenario;
- calculation;
- sequence/structure;
- method comparison.

## Preparation Products

Generate outputs matched to operation type:

- graph/table: axis reading, trend, anomaly, mechanism, limitation;
- calculation: formula, substitution, units/measurement convention, sanity check;
- protocol: aim, principle, steps, controls, expected readout, failure modes;
- case/scenario: key facts, mechanism, differential explanation, decision point;
- spotter/image: diagnostic features, distractors, confidence limits;
- method comparison: suitability criteria, readout, resolution, cost/risk, limitation.

## Answer-Key Alignment

When an answer key or worked solution is supplied:

1. Identify whether it is official, lecturer-provided, student-generated, or generated by an assistant.
2. Extract answer schema, not just final answers.
3. Record distractor traps and common wrong operations.
4. Do not treat answer-key content as independent factual authority unless verified against lecture/practical sources.

## DOCX Report Output

The student-facing practical/data/problem report should show the concrete operation:

```text
Read the graph -> identify trend -> infer mechanism -> state limitation -> propose control
```

Do not output only a topic label for practical/data/problem exams.

---

## Source File: `references__protected_source_coverage_protocol.md`

---

# Protected Source Coverage Protocol

This protocol prevents two opposite failures: public notes that omit examinable source content, and public notes that expose internal audit scaffolds. It is used before `KnowledgeSurfaceContract` rendering.

```text
SourceFragment -> SlideAtomicLedger -> ProtectedSourceUnit -> PublicOutputPoint -> SourceToOutputBinding -> ZeroMentionLint
```

## Core Principle

Official course material must be decomposed before it is compressed. Past papers may change density, ordering and priority, but they must not define the factual boundary of ordinary notes.

## SlideAtomicLedger

Use `SlideAtomicLedger` for lecture slides, practical notes, mocks, postlab documents, answer keys and diagram-heavy sources.

```yaml
SlideAtomicLedger:
  ledger_id:
  source_id:
  source_role:
  slide_or_page_units:
    - unit_id:
      locator:
      raw_heading:
      unit_type:
      protected_status:
      expected_public_mentions:
      bound_public_point_ids:
      qa_flags:
```

Protected units include:

- learning outcomes;
- lecture, slide, page or practical-problem headings;
- official definitions;
- contrast pairs;
- criteria, stages, classes and component lists;
- named examples and named experiments;
- diagram labels, table rows and graph axes that teach content;
- equations, calculations, units and workflows;
- “Why X?” explanatory blocks;
- summary or take-home points;
- formal-past-paper terms and operations.

## ProtectedSourceUnit

```yaml
ProtectedSourceUnit:
  unit_id:
  source_id:
  locator:
  unit_kind:
    - definition
    - term
    - contrast_pair
    - criteria_item
    - mechanism_step
    - method_step
    - equation
    - calculation_rule
    - graph_data_rule
    - diagram_label
    - table_entry
    - named_example
    - experimental_result
    - practical_operation
    - past_paper_term
    - summary_point
  required_visibility:
    - public_knowledge
    - internal_audit_only
    - excluded_admin
    - duplicate_bound_elsewhere
  expected_public_mentions:
  coverage_status:
```

Protected units must either appear in public knowledge output or be explicitly classified as duplicate, administrative, unreadable, unsupported, or internal-audit-only. Silence is not a valid outcome.

## PastPaperTermMustAppear

When a formal past paper, mock, practical problem or answer key uses a term, calculation, graph operation, reagent, method or diagnostic distinction that is also supported by course material, it becomes a protected public mention.

Rules:

- Past-paper terms increase protection and density; they do not invent new course facts.
- A past-paper term may be grouped under a broader module, but it must remain name-visible if the term itself is testable.
- Old-regime past-paper terms can support coverage only when the term is course-backed and not obsolete.
- If the public output contains the broader topic but omits the tested term, fail `zero_mention_lint`.

## SourceToOutputBinding

Every protected public unit must bind to a visible output point.

```yaml
SourceToOutputBinding:
  binding_id:
  protected_unit_id:
  public_point_id:
  public_block_id:
  mention_text:
  binding_quality:
    - exact_named
    - grouped_but_named
    - paraphrased_with_equivalent_term
    - missing
```

Acceptable binding:

- `exact_named`: the official term or equation appears.
- `grouped_but_named`: the term is inside a list or compact paragraph, but still visible.
- `paraphrased_with_equivalent_term`: allowed only for prose explanations where the source term is not the examinable term.

Unacceptable binding:

- only implied by a broad topic title;
- only present in a hidden audit map;
- only mentioned in `Common Error`, `Exam Use`, `Must Master`, or source notes that are suppressed from public output;
- merged into generic wording so the tested term disappears.

## ZeroMentionLint

Run `zero_mention_lint` after public rendering.

Fail when:

- a protected official term has zero visible mentions;
- a past-paper-backed term is omitted from public notes;
- a diagram/table/equation is referenced only as “the graph/figure” without its knowledge content;
- a calculation appears without units or conversion logic;
- a method workflow appears without principle, readout or interpretation;
- a named example is deleted because a broad module title seemed to cover it.

## Density Rules

Protected source coverage is not a licence to make unreadable notes. Use compact grouping only when all protected names and operations remain visible.

Allowed compression:

```text
PCR-RFLP turns a SNP into a fragment-pattern difference: amplify the target, digest with an enzyme whose site changes between alleles, then separate fragments by agarose gel electrophoresis.
```

Forbidden compression:

```text
PCR diagnostics are important.
```

## Public Surface Interaction

This protocol controls coverage. `knowledge_surface_protocol.md` controls what is allowed to be visible. A protected unit that contains audit or source-route text must be rewritten as knowledge rather than copied.

Example:

- Source text: `The second slide shows the opposite side of the body.`
- Protected knowledge: crossed extensor reflex.
- Public rewrite: `The crossed extensor reflex activates contralateral extensors and inhibits contralateral flexors so the unstimulated limb supports body weight.`

## Route Integration

- `exam_prep_notes_docx`: required for every ordinary notes run.
- `knowledge_walkthrough_docx`: required when lecture-first walkthrough is generated.
- `practical_data_problem_protocol.md`: required for calculations, graph interpretation, protocols and postlab materials.
- `essay_exam_prep`: use protected source skeleton before adding extra reading or compression.

## Publish Gate

Before public output is approved:

1. Build or conceptually maintain `SlideAtomicLedger`.
2. Mark protected units.
3. Bind each protected unit to public output.
4. Run zero-mention lint.
5. Run knowledge-surface lint so the coverage does not expose audit/provenance text.

---

## Source File: `references__question_type_protocol.md`

---

# Question Type Protocol

## QuestionType Enum

Classify before prediction:

- `mcq_single_best`
- `mcq_multiple_true_false`
- `mcq_statement_judgement`
- `fill_blank`
- `short_answer_define`
- `short_answer_list`
- `short_answer_explain`
- `short_answer_compare`
- `short_answer_experiment`
- `data_problem`
- `practical_protocol`
- `spotter_image`
- `numerical_problem`
- `case_study`
- `essay_theory`
- `essay_compare_contrast`
- `essay_experimental_design`
- `essay_scenario`
- `essay_disease_mechanism`
- `long_answer_project`
- `mixed_or_uncertain`

Never apply SBS K/C/U/A/R to MCQ, fill-blank, short-answer, or problem-based questions. Apply K/C/U/A/R only to essay-based theory answers.

## Question-Type Add-On Layer

For `exam_prep_notes_docx`, question-type logic is an add-on layer after the base Academic Exam-Ready Notes. It must not replace the base notes and must not cause essay-only logic to leak into MCQ, short-answer, practical/data, project, scenario, or long-answer routes.

MCQ add-on output:

```yaml
MCQAddOn:
  testable_statement:
  possible_wrong_or_distractor_statement:
  common_trap:
  must_remember_rule:
```

Do not claim an official answer unless an answer key or official solution is supplied.

Short-answer add-on output:

```yaml
ShortAnswerAddOn:
  bounded_example_question:
  concise_example_answer:
  required_terms_in_answer_text:
  avoid_this_mistake:
```

Bold required terms inside the answer text. Do not expose `common omissions`.

Essay add-on output:

```yaml
EssayAddOn:
  essay_ready_paragraph_blocks:
    mechanism:
    process:
    comparison:
    evidence:
    limitation:
```

Complete Example Essays are generated only when the user explicitly asks for essay preparation, model essays, full essay-style answers, or complete essay documents.

## MCQ Statement-Level Map

For MCQ-heavy exams, predict discriminator axes and distractor families, not long model answers and not exact stems.

MCQ extraction schema:

```yaml
MCQPattern:
  target_group_key:
  exam_regime:
  year:
  question_no:
  question_mode: definition | classification | mechanism | calculation | exception_not | graph_figure | application
  correct_concept:
  discriminator:
  distractor_families: []
  trap:
  compatible_kps: []
  source_question:
```

MCQ pattern categories:

- `definition`: terms likely to be confused.
- `classification`: category boundaries.
- `mechanism`: causal direction and sequence.
- `calculation`: formula, measurement convention, order of magnitude.
- `exception_not`: common incorrect statements.
- `graph_figure`: curve shape, graph reading, diagram logic.
- `application`: correct explanation in a new scenario.

For MCQ-heavy exams, create a statement/discriminator map:

- likely true statements;
- likely false/distractor statements;
- common contrast pairs;
- numbers/locations/names likely to be tested;
- mechanism-order traps;
- definition traps;
- exceptions;
- lecture-only wording that should be memorised.
- one-sentence rule;
- wrong-option diagnosis.

Internal `MCQ_HighFrequency` fields may include:

- Lecture;
- Knowledge point;
- Why high frequency;
- Likely MCQ statement;
- Correct answer / truth value if knowable;
- Common trap;
- Source slide/page;
- Confidence.

The default student-facing MCQ report is a Point Card report only. Convert the internal map into `MCQStudentPointCard` objects:

```yaml
MCQStudentPointCard:
  priority: ★★★ | ★★ | ★
  point: string
  knowledge_explanation: string
  how_exam_tests_it: string
  common_traps: []
  must_remember: string
```

Do not include practice questions, answer keys, contrast tables, separate trap banks, source anchors, confidence, evidence, examiner-operation labels, or discriminator-axis labels in the default MCQ high-yield report. Fold wrong-option logic into `common_traps`.

If no answer key exists, do not invent official answers. Mark answers as `inferred_from_lecture`.

If a visible MCQ regime includes negative marking, multiple-response marking, or statement-level scoring, extract an `MCQScoringPolicy`:

```yaml
MCQScoringPolicy:
  mode: single_best | multiple_true_false | statement_judgement
  option_count:
  correct_value:
  wrong_value:
  unanswered_value:
  positive_ev_threshold:
  action_rule:
```

If unanswered answers score zero, correct answers score `c`, and wrong answers lose `d`, the internal positive expected-value threshold is:

```text
p > d / (c + d)
```

This policy supports answer strategy. It must not be used to invent official answers.

Internal MCQ analysis may contain:

- term-pair contrast table;
- formula flashcards;
- wrong-option diagnosis;
- one-sentence rules;
- exception list;
- `NOT / incorrect` scan habits.

Do not output `X will be tested` when the stronger claim is `X is a likely discriminator boundary`.

## Short-Answer Mark-Point Generator

For short-answer questions, predict `question archetype -> mark-producing answer schema`, not only topic labels.

Do not generate unbounded lists of possible questions. Generate bounded variants from:

```text
archetype + slot grammar + source-linked KP + mark scale
```

Short-answer extraction schema:

```yaml
ShortAnswerPattern:
  target_group_key:
  exam_regime:
  year:
  question_no:
  marks:
  stem_type:
  task_verbs: []
  input_format:
  primary_kp:
  supporting_kps: []
  operation: []
  answer_schema: []
  archetype_id:
```

Short-answer prediction output must say how a KP can be asked. For example:

- explain variability between cases;
- compare/rank alternatives;
- calculate or interpret a parameter;
- draw/label a structure;
- list named examples;
- build a stepwise causal chain.

For high-reuse families, a variant record should include:

```yaml
ShortAnswerVariant:
  family_id:
  kp_id:
  variant_type: define | list | compare | explain_mechanism | draw_label | calculate | interpret_graph | design_experiment
  likely_stem_template:
  required_mark_points:
  concise_exam_answer:
  reference_expansion:
  allowed_examples:
  source_anchor:
  confidence: High | Medium | Low
```

Internally, generate two answer layers when useful:

1. `Exam Answer`
   - concise student-style answer;
   - directly answers the question;
   - uses lecture wording where possible;
   - English only.

2. `Reference Expansion`
   - more acceptable points than required;
   - alternative acceptable examples;
   - extra detail if useful;
   - source anchors.

If marks are visible, infer minimum scoring points from marks and wording, but do not claim exact official allocation unless a mark scheme exists. If wording says `list three`, provide at least three core answers plus additional acceptable examples. If the answer is not found in supplied lecture slides/notes, explicitly flag `Not found in supplied lecture material.`

Extra reading may appear only under `Optional extra-reading refinement` unless lecture content is insufficient.

Generate mark-length skeletons only when the user explicitly asks for length variants or when a visible prompt requires them:

- 2-mark version: one-line definition or two named points.
- 4-mark version: definition plus two to three linked explanatory points.
- 6-mark version: mechanism with causal sequence and named examples.
- 8/10-mark version: full schema including comparison, diagram, data interpretation, or scenario conclusion.

Do not claim exact official mark allocation unless an official mark scheme is present.

The default student-facing short-answer report must be simplified into module logic plus point cards:

```yaml
ShortAnswerModuleSection:
  module_name: string
  module_core_logic: string
  high_yield_points: []
  point_cards: list[ShortAnswerPointCard]

ShortAnswerPointCard:
  priority: ★★★ | ★★ | ★
  point: string
  common_question_form: string
  exam_explanation_with_highlighted_keywords: string
  example_answer: string
```

Do not show mark-producing schema, required terms, optional examples, reference expansion, common omissions, task verb, confidence, evidence, or source anchor as separate student-facing fields. Bold required terms inside the explanation. Put the scoring logic into a natural `example_answer`.

## Practical / Data / Problem Outputs

Route practical protocols, problem papers, case studies, numerical assessments, spotters, graphs, figures, and worked solutions through `practical_data_problem_protocol.md`.

Practical/data/problem extraction schema:

```yaml
ProblemOperationPattern:
  target_group_key:
  exam_regime:
  year:
  question_no:
  input_type: graph | table | figure | image | protocol | case | calculation | structure | sequence | method_comparison
  required_operation:
  expected_inference:
  answer_schema: []
  controls_or_limitations: []
  follow_up_action:
  answer_key_alignment:
    provenance: official | lecturer | paper_with_answer | student | generated | unknown
    reusable_rationale:
    non_authoritative_content: []
```

Preparation output must be operation-first:

```text
input -> operation -> inference -> limitation/control -> follow-up
```

Do not output only topic names for problem/data/practical exams. If an answer key exists, extract answer logic and traps; do not treat it as independent factual authority unless verified against lecture or practical material.

## Long-Answer Project / Scenario Outputs

Use `long_answer_project` when the formal paper is non-essay but requires paragraph-style project, scenario, method-design, or research-proposal answers. This is separate from ordinary essay theory.

Long-answer project extraction schema:

```yaml
LongAnswerProjectPattern:
  target_group_key:
  exam_regime:
  year:
  question_no:
  project_context:
  named_systems_or_examples: []
  question_parts:
    - part_label:
      mark_weight:
      command_verbs: []
      required_operation:
      likely_lecture_blocks: []
      output_expected:
  core_archetype:
  slot_grammar:
  required_answer_mode:
  cross_module_links: []
```

Method-driven long-answer project archetypes:

Apply these archetypes only when exam-format parsing confirms scenario, project, method-design, readout-interpretation, or control/limitation structure. Do not transfer subject-specific systems, techniques, or recurrence claims unless supplied in the target sources.

- design purification strategy;
- choose and justify characterisation methods;
- assess folding, secondary, tertiary, or quaternary structure;
- quantify binding affinity or dimerisation affinity;
- interpret mutation effect;
- determine interaction interface;
- determine atomic or high-resolution structure;
- compare structural biology methods;
- quantify enzyme activity or substrate specificity;
- explain chaperone or folding mechanism;
- identify in vivo or biotechnological caveats.

For each long-answer archetype, require:

- lecture principle;
- scenario-specific method choice;
- expected readout;
- interpretation;
- limitation/control.

When the surface system or case rotates but the operation remains stable, prepare a reusable `MethodBlock` library:

```yaml
MethodBlock:
  method_family:
  principle:
  when_to_use:
  expected_readout:
  interpretation_logic:
  required_control:
  main_limitation:
  compatible_question_parts:
  source_anchor:
```

When a user explicitly asks for a model answer or Example Essay for a project/scenario exam, route to `long_answer_example_protocol.md` and generate a `High-score example long answer`, not a generic essay. The answer must be structured by question parts, mark weights, method logic, readouts, interpretation, and controls.

Do not let old short-answer or coverage-only papers control the current long-answer project blueprint. They may support concept coverage only unless exam-format parsing proves the same regime.

## Essay / Problem-Essay Outputs

For essay and problem-essay prediction, the default prediction object is a theme-level scope, not an exact question stem. Generate a full Example Essay only when the user explicitly asks for an Example Essay, model essay, essay-style answer, essay paragraph, or similar.

Theme-level prediction means:

- predict the likely examinable theme or theme family;
- state the lecture scope that supports it;
- state whether the scope is roughly one lecture with one main theme, one lecture with two separable themes, two adjacent lectures forming one theme, or a cross-lecture synthesis;
- state the examiner operation likely to be rewarded, such as explain mechanism, compare pathways, evaluate evidence, interpret experiment, or apply to disease/scenario;
- provide optional practice angles only as practice variants, not as predicted official wording.

If a recent formal paper has an answer-one essay section with several broad options, infer option slots and theme families. Keep short-answer or fill-blank sections separate: repeated Section A terms can support factual coverage, but they must not inflate essay-theme prediction unless the same lecture block also fits Section B wording and lecture centrality.

Essay/problem-essay theme schema:

```yaml
EssayThemePrediction:
  target_group_key:
  exam_regime:
  theme_id:
  theme_title:
  lecture_scope:
    scope_type: one_lecture_one_theme | one_lecture_two_themes | two_lectures_one_theme | cross_lecture_synthesis | uncertain
    lecture_titles_or_blocks: []
    source_anchor_pages_or_slides: []
  core_examiner_operation:
  why_examinable:
    - formal_paper_pattern
    - lecture_centrality
    - learning_objective_or_summary
    - mechanism_or_evidence_density
    - coverage_gap_or_rotation_slot
  compatible_kps: []
  possible_practice_angles: []
  not_claimed:
    - exact_exam_wording
    - guaranteed_question
    - lecturer_identity_trigger
  confidence: High | Medium | Low
```

Use `Predicted essay theme` only inside the chat-only exam-analysis brief or an explicit audit/selection note. If a practice stem is useful, label it `Practice variant from predicted theme`.

For answer-one essay sections with several options, add an `EssayCoveragePlan`. The aim is to prepare enough lecture blocks for at least one high-quality answer, not to claim exact future titles or force equal-depth preparation for every source block unless requested.

When Essay Exam Prep or Example Essay Mode is triggered, follow `essay_generation_protocol.md` and package the student-facing result as `Essay_Module_Example_Essays.docx` unless the user explicitly asks for separate essay files.

For complete essay planning, assessed-style essay drafting, or a user-supplied essay topic not already constrained by a lecture source pack, first apply `essay_tutor_workflow_protocol.md`. The plan must collect essay constraints, run DeepResearch, produce a subtitle-level plan, and pass the plan-approval gate unless the user explicitly requests direct generation.

If the exam-format gate classifies the target as `long_answer_project`, follow `long_answer_example_protocol.md` instead of the essay-generation protocol.

For every essay output, require:

- Question deconstruction;
- Essay intake constraints where relevant;
- Detailed essay plan with subtitle-level main-body content;
- Lecture anchors;
- Knowledge inventory;
- Lecturer-intent analysis;
- Paragraph plan;
- Extra-reading insertion decision;
- High-score example essay when explicitly requested;
- Paragraph function map;
- Figure plan;
- Extra reading;
- Exclusion list;
- K/C/U/A/R self-check.

Use K/C/U/A/R only for essay-based theory answers.

Every essay paragraph must have internal planning metadata:

- paragraph number;
- paragraph text;
- function;
- source anchor;
- K/C/U/A/R contribution;
- why included;
- what was excluded.

Do not write slide-by-slide summaries. Each paragraph must serve the question command verb.

For the default essay-prep DOCX add-on, include module-level Example Essays, adaptation maps, and paragraph banks. Do not create a prediction workbook or put complete essays into spreadsheet rows.

The essay must be built from paragraph functions, not from slide order alone. Slide order informs lecture logic; paragraph order is determined by the command word, expected scope, and lecturer intent.

If the question has a 1000-word maximum and no minimum, maximise relevance per word. Do not pad. Omit background that does not answer the question.

Required essay paragraph pattern:

```text
Claim -> mechanism -> evidence/example -> biological consequence -> link back to question.
```

Required output structure for direct-chat Example Essays:

```text
Question Analysis
Paragraph Plan
Extra Reading Insert
Example Essay
Examiner-Fit Checklist
```

---

## Source File: `references__scientific_precision_protocol.md`

---

# Scientific Precision Protocol

This protocol controls the precision layer for scientific, biomedical, clinical, quantitative, methodological and sector-level writing. It prevents high-density output from becoming a list of true but unstructured details.

```text
EvidenceClaim -> EntityPrecisionPass -> CategoryMatchedSentenceRule -> EvidenceLadderRule -> MechanismPerDetailRule -> ClaimStrengthCalibration -> Student prose
```

## Purpose

High-scoring notes and essays need more than correct facts. They need the correct entity type, the correct evidence strength, and a clear reason why each named detail matters.

A named detail may enter public prose only when it performs a function:

- sharpens a source-backed mechanism;
- distinguishes one model, pathway, method, cell type, molecule, case or sector mechanism from another;
- explains what an experiment, assay, graph, figure or dataset shows;
- defines a scope boundary or limitation;
- links a molecular/cellular/method detail to the question-level answer.

## Entity Precision Pass

Before final prose, collapse aliases and classify named entities.

```yaml
EntityPrecisionRecord:
  entity:
  aliases:
  entity_category:
    - gene
    - transcript
    - protein
    - receptor
    - channel
    - ligand_or_morphogen
    - cell_type
    - circuit_element
    - anatomical_structure
    - pathway
    - assay
    - method
    - chemical_species
    - disease_or_patient_group
    - company_or_case
    - regulatory_body
    - quantitative_parameter
  source_anchor:
  allowed_claim_type:
  student_visible_decision:
```

Rules:

- Do not mix entity categories inside one sentence unless the relation between categories is explicit.
- Do not use a gene name as if it were the protein, receptor, pathway or disease phenotype unless the source supports that wording.
- Collapse synonyms before writing so the output does not look like a catalogue of separate items.
- When a term is ambiguous, state the precise level or omit the detail.

## Category-Matched Sentence Rule

Each sentence should match grammar to the category it names.

Examples:

- A gene can encode a protein, carry a mutation, contain an expansion or alter expression.
- A protein can bind, aggregate, mislocalise, phosphorylate, transport, catalyse or interact.
- A receptor or channel can gate, signal, open, close, desensitise or change downstream output.
- An assay can measure, detect, compare or validate; it cannot by itself prove disease causality.
- A patient cohort or model can support, implicate or test a mechanism; it does not automatically prove universal human causation.
- A company or case can illustrate a sector mechanism; it does not become the sector mechanism itself.

Reject sentences that list entities from different categories without stating their causal or evidential relation.

## Evidence Ladder Rule

When several evidence streams support one mechanism, write them as an evidence ladder rather than a flat list.

```text
source observation -> model or assay result -> mechanism tested -> interpretation -> scope or limitation
```

For scientific essays, common ladders include:

```text
patient evidence -> cell model -> animal model -> treatment logic -> calibrated conclusion
lecture experiment -> assay readout -> mechanism -> limitation
genetic lesion -> molecular consequence -> cellular phenotype -> system-level effect
```

For sector/system essays, common ladders include:

```text
market problem -> platform mechanism -> firm example -> sector implication -> limitation
```

The ladder should preserve claim strength. Association stays association; rescue or perturbation can support causality only within its model and conditions.

## Mechanism-Per-Detail Rule

Every named detail must earn its word count.

Accept a named detail only when at least one is true:

- it changes the causal mechanism;
- it names the specific object measured or manipulated;
- it explains why an experiment supports or limits a claim;
- it distinguishes one answer option, model, pathway, method or disease subtype from another;
- it directly improves revision accuracy or exam transfer.

Reject the detail when:

- it is true but not needed for the question;
- it creates a gene/channel/receptor/pathway/company catalogue;
- it requires a new explanatory paragraph not supported by the question scope;
- it shifts the answer away from the lecture/source mechanism;
- it is used only to increase molecular, mechanism or extra-reading volume.

## Claim Strength Calibration

Use calibrated verbs:

| Source situation | Preferred wording | Avoid |
|---|---|---|
| correlation, association or altered abundance | associated with, linked to, consistent with | proves, causes |
| perturbation changes a model readout | supports, contributes to, is required under these conditions | universally proves |
| rescue experiment restores a phenotype | supports a causal role in that model | proves sole cause |
| review-level synthesis | suggests, implicates, supports a model | demonstrates directly |
| company/case example | illustrates, shows a route, exemplifies | proves sector-wide rule |

## ScientificPrecisionGate

Run this gate before final notes, long answers and Example Essays.

```yaml
ScientificPrecisionGate:
  entity_precision_pass:
  alias_collapse_pass:
  category_matched_sentence_pass:
  evidence_ladder_pass:
  mechanism_per_detail_pass:
  claim_strength_pass:
  qa_flags:
```

Fail or rewrite when:

- a sentence mixes entity categories without relation;
- a detail has no mechanism or evidence function;
- a claim overstates the source;
- a named list replaces explanation;
- extra reading replaces lecture logic;
- academic-paper content lacks parenthetical author-year citation where required;
- a biological, clinical, method or sector example is used as direct factual authority for a new target source set without verification.

## Route Integration

- `exam_prep_notes_docx`: apply to public points and calculation/method/graph explanations.
- `knowledge_walkthrough_docx`: apply to conceptual walkthrough prose and synthesis blocks.
- `essay_exam_prep`: apply after paragraph planning and again after compression.
- `long_answer_project_scenario_prep`: apply to method/readout/interpretation/control paragraphs.
- `mcq_exam_prep` and `short_answer_exam_prep`: apply to point cards so distractors and concise answers do not blur entities or claim strength.

Scientific precision is not a request to add more detail. It is a filter that keeps only the detail that improves the answer's mechanism, evidence or decision value.

---

## Source File: `references__scoring_and_pattern_protocol.md`

---

# Scoring And Pattern Protocol

## Core Model

The primary prediction object is not a repeated topic. It is:

```text
fixed examiner operation + replaceable knowledge slots + reusable mark-scheme skeleton
```

When formal past papers are supplied, build this from question-level records rather than prose impressions:

```text
PastPaperQuestion -> QuestionArchetype -> SlotGrammar -> compatible KnowledgePoint -> confidence band -> PrepArtifact
```

Use three layers:

1. `Exam blueprint`: section structure, required/optional questions, marks, timing, question-type balance, data/figure/calculation/case-study frequency, and fixed Q-slot themes.
2. `Question archetype`: task verb + input format + cognitive operation + expected output + mark-scheme structure.
3. `Slot grammar`: replaceable variables within an archetype, such as molecule set, functional group, disease/drug/channel example, graph parameter, circuit component, assay, figure type, or calculation value.

The workflow must ask:

- Is the target exam blueprint stable?
- Which archetypes are reused?
- Which variables rotate inside those archetypes?
- Which untested or partly tested KPs can fill the same slots?
- What preparation action follows?

KP posterior/hotness is auxiliary and must not override a stronger archetype/regime signal.

For essay/problem-essay exams, the student-facing prediction object is narrower and safer than an exact stem:

```text
examinable theme + lecture scope + likely examiner operation + possible practice angles
```

Use this when a formal paper asks broad essay or problem-essay questions and lecture content naturally groups into themes. A valid theme is a coherent lecture block, not a raw topic label: it should normally correspond to one lecture with one main theme, one lecture with two separable themes, two adjacent lectures forming one theme, or a cross-lecture synthesis supported by formal-paper wording. Do not predict exact question wording unless official wording is already supplied by the user.

When the same current regime combines a short-answer/fill-blank section with a high-weight answer-one essay section, separate the evidence streams. Short-answer recurrence supports the factual coverage matrix. Essay prediction should come from broad Section B option structure, lecture-scope coherence, and examiner operation fit.

## Target-Internal Comparison Rule

Only compare papers within the same normalized `target_group_key` or compatible source group. Do not use MCQ, short-answer, or content patterns from one source group to predict another source group's content.

Allowed external-example use:

- identifying a generic question-writing structure;
- borrowing an output layout or annotation style;
- learning how a good short-answer/MCQ explanation is phrased.

Forbidden external-example use:

- pooling KP frequency;
- claiming a topic is high-yield because it appears in an external example;
- importing another source set's distractor bank as content prediction.

## Example Contribution Transfer

External examples may transfer only operation grammar, workflow discipline, output layout logic, or QA checks. They may not transfer content, lecturer assumptions, repeated topics, or direct prediction evidence into a target source set.

Allowed example transfer:

```text
This benchmark shows that when data figures recur, predict graph-reading operation + mechanism inference + limitation.
```

Forbidden example transfer:

```text
Because one benchmark used a specific molecule, crop, disease, pathway, company, theory, or case study, a new source set should expect that same content.
```

Transferable archetypes must record the condition under which the lesson may be reused:

```yaml
TransferableArchetypePattern:
  source_example_id:
  observed_operation:
  slot_grammar:
  evidence_condition_required:
  output_action:
  forbidden_content_transfer:
```

## Exam-Regime Split

Within a target source group, split papers into separate regimes when exam format changes. Examples of regime-breaking changes include:

- MCQ + short-note becomes short-answer + case-study;
- answer-all becomes answer-one;
- closed-book timed paper becomes take-home essay;
- mark distribution or section weights change substantially.

Old-regime papers may support concept-pool coverage, but they must receive `RegimeMismatchPenalty` for current-regime predictions.

## Coverage Closure

Do not list only repeated KPs. Build an all-examinable matrix:

```text
past-paper archetypes -> slot grammar -> lecture/syllabus KP inventory -> compatible KP-slot pairs -> tested / partially tested / fresh / saturated
```

Each KP must be labelled across five task dimensions:

- `factual`: definition, list, name, identify;
- `mechanistic`: pathway, causal explanation, sequence;
- `structural`: draw, label, topology, molecular/circuit structure;
- `quantitative`: calculate, graph, table interpretation, measurement conventions;
- `comparative`: compare, rank, contrast, choose best.

This matrix is how the Skill expands from seen questions to all plausible examinable variants.

## Not-Past-Paper-Only Rule

The Skill must not restrict coverage to already-examined content.

For every official source-backed KnowledgePoint, assign one internal status:

- `exam-proven`: appears in supplied compatible formal past papers;
- `exam-plausible`: foregrounded by source headings, definitions, examples, diagrams, summaries, ILOs, or method workflows even if not yet tested;
- `supporting-background`: useful context that rarely produces marks alone.

Student-facing output must not display these internal labels. Convert them into star ratings:

- `exam-proven` plus answer-producing content is usually `★★★`;
- `exam-plausible` plus source-foregrounded content is usually `★★` or `★★★`;
- `supporting-background` is usually `★`.

Never omit `exam-plausible` content merely because it has not yet appeared in supplied past papers.

## Paper Comparability

Use:

- `formal_high`: recent formal paper with same or very similar format.
- `formal_medium`: formal paper with same target group but older or materially different constraints.
- `formal_low`: formal paper with different question style; useful for coverage only unless configured otherwise.
- `auxiliary_practice`: practice paper, mock, quiz, answer key, tutorial, exemplar, or problem sheet.
- `excluded`: wrong target group, inaccessible, unsupported, duplicate, or not relevant.

Formal past papers drive retention and examiner-pattern inference. Practice materials support coverage and answer style only unless explicitly configured.

## Primary And Secondary Knowledge Points

For every question:

```yaml
QuestionKnowledgeMapping:
  question_id:
  primary_kp_id:
  secondary_kp_ids: []
  mapping_confidence: High | Medium | Low
  evidence:
  review_queue_reason:
```

Use one primary KP for frequency/retention statistics. Use secondary KPs for answer planning, not to inflate statistics.

## Separate Metrics

Do not collapse these into one opaque score:

- Hotness: how often tested.
- Retention: how many formal years it appears in.
- Recency: whether it appears in recent papers.
- Lecture centrality: learning objectives, summaries, repeated diagrams, key experiments, lecturer emphasis.
- Question-shape fit: suitability for MCQ, short answer, essay, scenario, experiment, disease, comparison.
- Lecturer/module slot fit: whether the KP fits detected lecturer/module/question slots.

PredictionScore may be used only as explainable ranking aid:

- BlueprintFit;
- ArchetypeReuse;
- MarkSchemeReuse;
- KPRecurrence;
- Recency;
- CoverageGap;
- LectureCentrality;
- AssessmentEase;
- SaturationPenalty;
- RegimeMismatchPenalty.

A conceptual ranking formula is allowed:

```text
Score =
  2.0 * BlueprintFit
+ 2.0 * ArchetypeReuse
+ 1.5 * MarkSchemeReuse
+ 1.0 * KPRecurrence
+ 1.0 * Recency
+ 1.0 * LectureCentrality
+ 0.8 * CoverageGap
+ 0.7 * AssessmentEase
- 1.2 * SaturationPenalty
- 2.0 * RegimeMismatchPenalty
```

For small paper sets, do not report precise numeric probabilities such as `72.4%`. Use confidence bands:

- `High confidence`: archetype likely, exact instantiation uncertain.
- `Medium confidence`: KP family likely, question form uncertain.
- `Low confidence`: possible fresh coverage, evidence weak.

Student-facing priority may additionally consider expected value:

```text
priority = confidence_band * mark_value * student_weakness * transferability / prep_time
```

If student weakness or preparation time is unknown, omit those terms and state that the ranking is evidence-only.

## LecturerModuleSlotDetector

Test, do not assume:

1. one lecturer -> one question;
2. one module block -> one question;
3. one lecture -> one question;
4. one detailed knowledge point -> one question;
5. cross-lecture synthesis;
6. disease/application slot;
7. experiment/design slot;
8. scenario slot;
9. figure-required slot.

Output:

```yaml
SlotPatternResult:
  pattern_type:
  supporting_years: []
  contradicted_years: []
  mapped_questions: []
  confidence:
  consequence_for_prediction:
```

For essay writing, add:

```yaml
EssayLecturerIntentResult:
  likely_lecturer:
  evidence_for_lecturer: []
  contradicted_evidence: []
  likely_scope: one_kp | one_lecture | one_module | several_lectures_same_lecturer | cross_module | whole_source_set
  expected_answer_shape:
    - mechanism_detail
    - compare_contrast
    - examples_as_evidence
    - experimental_evidence
    - application_or_disease
    - synthesis
  required_lecture_examples: []
  likely_extra_reading_tolerance: low | medium | high
  confidence: High | Medium | Low
```

Do not infer lecturer preference from one question alone unless labelled `Low` confidence. Combine learning objectives, repeated examples, formal past-paper patterns, module boundaries, and question wording.

Lecturer or source-block style cannot raise confidence above `Medium` unless it is supported in the same current exam regime by at least two formal papers, aligned with lecture objectives or summary material, and not contradicted by recent papers.

For Example Essay Mode, lecturer intent controls paragraph planning. It does not override source accuracy or question wording.

For Essay Problem prediction, add:

```yaml
EssayProblemThemeResult:
  theme_title:
  lecture_scope_type: one_lecture_one_theme | one_lecture_two_themes | two_lectures_one_theme | cross_lecture_synthesis | uncertain
  lecture_blocks: []
  supporting_evidence:
    - formal paper format
    - lecture objective or summary
    - mechanism/process/evidence density
    - compatible past-paper operation
  predicted_theme_not_stem: true
  possible_practice_angles: []
  exact_question_wording_claimed: false
  confidence: High | Medium | Low
```

This result may be ranked, but it must not be rewritten as `this exact question will appear`.

## LongAnswerProjectSlotDetector

For non-essay long-answer/project exams, test whether the current formal regime uses a project/scenario structure instead of a broad essay structure.

The detector must identify:

1. current formal regime versus old coverage-only regime;
2. whether the paper uses one or more project choices;
3. whether each project is split into weighted parts;
4. whether the biological system rotates while examiner operations recur;
5. whether purification, binding/affinity, structural determination, mutation/rational-design, folding/chaperone, enzyme activity, and biophysical-characterisation operations recur.

Output:

```yaml
LongAnswerSlotPatternResult:
  pattern_type:
  supporting_years: []
  contradicted_years: []
  mapped_questions: []
  recurrent_operations: []
  rotated_slots: []
  confidence: High | Medium | Low
  consequence_for_answer_generation:
```

When the recent formal regime is project/scenario-based, older short-answer, take-home, or different-format papers may inform the concept pool only. They must not control current answer style, paragraph structure, or predicted project-question structure.

For method-driven project/scenario papers, consequence for answer generation should normally be:

```text
Generate a compact experimental argument: question goal -> lecture method principle -> scenario-specific application -> expected readout -> interpretation -> limitation/control.
```

Do not write separate lecturer blocks unless the question itself asks for that structure. Recent project/scenario questions may combine several lecturers' material inside one answer.

## Archetype Registry Schema

```yaml
QuestionArchetype:
  archetype_id:
  target_group_key:
  exam_regime:
  question_family: mcq | short_answer | essay | case_study | data_problem | long_answer_project
  task_verbs: []
  input_format:
  cognitive_operation:
  expected_output:
  mark_scheme_structure:
  compatible_kp_families: []
  slots: []
  derived_from_external_example:
  transferable_rule:
  non_transferable_content: []
  format_match_required:
  seen_in:
    - source_group:
      year:
      question_no:
  saturation: fresh | partially_tested | saturated | unknown
  confidence: High | Medium | Low
```

An archetype can be stronger evidence than a repeated isolated KP when the operation, slot grammar, and answer skeleton recur with rotated examples.

## Review Queue

Place mappings or predictions into QA/review when:

- OCR or parsing is weak;
- source mapping is ambiguous;
- one question could map to multiple primary KPs;
- a formal paper has changed format;
- lecturer ownership is unclear;
- lecturer intent is inferred from weak evidence;
- an essay paragraph plan is missing or does not preserve lecture logic;
- a long-answer project paragraph plan is missing;
- a long-answer project answer lacks method principle, scenario application, readout, interpretation, or control/limitation;
- a project/scenario answer has been written as a generic essay;
- a comparison essay lacks shared comparison axes;
- an answer is not found in supplied lecture material;
- a citation is unverified;
- prediction confidence is low.

---

## Source File: `references__student_facing_output_policy.md`

---

# Student-Facing Output Policy

The Skill may use source anchors, evidence claims, confidence bands, examiner-operation labels, recurrence, lecture centrality, scoring logic, and source coverage internally. Student-facing outputs must not expose that audit reasoning unless the user explicitly asks for an audit package.

Student-facing exam-prep outputs must be rewritten as directly usable revision content:

```text
internal reasoning: evidence -> operation -> priority -> output type
student output: priority -> public point -> explanation -> knowledge-bearing blocks
```

Ordinary Academic Exam-Ready Notes are knowledge documents, not exam-format audits. They must not display assessment percentages, exam timing, mark splits, Section A/Section B administrative rules, historical-paper comparability notes, `Coverage note` warnings, source-quality caveats, ELM-check warnings, or provenance/audit explanations. Keep those items internal unless the user explicitly requests an audit package.

## Forbidden Visible Fields

Do not show these fields in ordinary student-facing reports:

- source anchor;
- evidence rationale;
- confidence;
- recurrence count;
- lecture centrality;
- regime match;
- why high-yield;
- examiner operation;
- discriminator axis;
- task verb;
- reference expansion;
- common omissions;
- evidence limit;
- past-paper year mapping;
- prediction score.
- assessment timing;
- mark split;
- current regime;
- older papers;
- no mark scheme;
- coverage note;
- source coverage;
- extraction quality;

Canonical forbidden field IDs:

```text
source_anchor
confidence
evidence
examiner_operation
discriminator_axis
practice_mcq
answer_key
contrast_table
separate_trap_bank
mark_producing_schema
reference_expansion
exam_specificity
core_exam_claim
exam_use
common_error_or_trap
must_master
```

These may appear only in internal QA or an explicit audit package requested by the user.

## Example Essay Visible Boundary

Final Example Essay DOCX files are student-facing essay documents, not audit reports. They must not contain public preambles, source-basis disclaimers, prediction disclaimers, confidence notes, or diagnostic task labels.

Forbidden visible text in final Example Essay DOCX output includes `Model answer built from...`, `This is not a predicted exam question`, `Exam-style question`, decorative `Question:` / `Essay Topic:` subtitle labels, and standalone `Example essay` labels. The document may have a centered title and an optional subtitle containing only the exact essay question or user-approved topic wording.

If source-basis, prediction status, or evidence limitations need to be stated, put them in the chat response or internal QA artefact, not in the Word document.

## Allowed Priority Labels

Use only these visible priority labels when priority is useful:

- `★★★`;
- `★★`;
- `★`.

Meanings:

- `★★★` = answer-producing exam core: standalone definition, mechanism, calculation, graph/data operation, criteria list, method workflow, named source example, or case-study decision point.
- `★★` = supporting examinable knowledge: useful for explanation, comparison, justification, or transfer.
- `★` = background/context: useful framing only; keep brief unless directly tested.

Do not explain why a point is `★★★` by exposing recurrence, confidence, or source-scoring logic. Convert the reason into useful content: what to know, which mechanism or list matters, and which boundary or limitation prevents an error.

## Exam Prep Notes Student Contract

`exam_prep_notes_docx` is the default general-revision route. It emits Academic Exam-Ready Notes in the compatible public artifact `Lecture_Knowledge_Walkthrough.docx`.

Visible structure:

```yaml
ExamPrepNotesStudentContract:
  public_lecture_sections: list[PublicLectureSection]
```

The visible top matter is only the document title. `Course Knowledge Map`, `Source Role Summary`, extraction limitations, prediction sections and generic exam advice stay internal unless the user explicitly requests a separate audit or exam-analysis report.

Compact Public Notes Rule:

- Internally, decompose sources into atomic knowledge items and protect every source-backed definition, criterion, mechanism, method, example, equation, graph, table, and workflow.
- Publicly, render compact lecture-level exam notes. Do not expose the internal card scaffold.
- The public route is lecture-first: each official lecture/session becomes a visible lecture section, with concept-specific modules inside it.
- Group protected atomic items into readable public points using concise paragraphs, bullets, equations, examples, comparisons, and mechanism chains.
- Coverage must be complete; formatting must be compact.
- Compact lecture notes and compatibility walkthroughs use Arial, 2.0 cm margins, compact 1.05-1.15 line spacing, left-aligned body text, black text, and lecture page breaks. Essay-style 2.5 cm margins, 1.5 spacing, and justified body text are reserved for Example Essay outputs.
- A hard knowledge-only rendering gate applies before public DOCX writing. Ordinary notes and compatibility walkthroughs must not render generic advice sections such as `How To Answer`, `How To Use`, `Integrated reasoning`, `Integrated practical reasoning`, `Answer Logic`, `Exam Strategy`, `Recommended Approach`, `A strong answer should`, `Use this module`, or question-type reliability commentary. Keep only the underlying source-backed knowledge, rewritten as knowledge points, definitions, method workflows, calculations, graph/data rules, comparisons, examples, or limitations.
- A public-point consistency gate applies before DOCX writing. Every visible internal KnowledgeCard must map to at least one public point, every public point must reference real source cards, and public point, block, and coverage-binding atomic-unit sets must agree.

Visible public module:

```yaml
PublicLectureSection:
  lecture_title: string
  lecture_scope: string
  modules: list[PublicLectureModule]

PublicLectureModule:
  module_title: string
  knowledge_functions: list[
    definition_boundary | mechanism_process | method_readout | graph_data_interpretation | calculation_unit_worked_example | named_example | limitation_trap
  ]
  explanation: string
  blocks: list[PublicPointBlock]

PublicPointBlock:
  block_type: definition | mechanism | method | graph_data | calculation | example | limitation | comparison | table | explanation
  label: string | null
  content: string | list[string]
```

Internal card fields guide planning and QA. They are not public headings. Ordinary Academic Exam-Ready Notes must not render headings named `Exam Specificity`, `Core Exam Claim`, `Exam Use`, `Common Error / Trap`, or `Must Master`. `Canonical Example` remains an internal planning field; public notes should render the knowledge as an `Example` block, explicit user-requested equivalent, or unlabeled paragraph.

`Exam Use`, `Common Error / Trap`, and `Must Master` may appear only in MCQ reports, short-answer add-ons, explicit trap/checklist outputs, or internal QA. In ordinary notes, useful distinctions should be integrated into `comparison`, `limitation`, or the main explanation.

Allowed visible add-on items:

- testable statement;
- possible wrong or distractor statement;
- common trap;
- must-remember rule;
- bounded example question;
- concise example answer;
- required terms bolded inside answer text;
- `Avoid this mistake`;
- essay-ready paragraph block;
- generated schematic caption.

Question-type add-ons must come after the base notes. They do not replace the base notes and must not expose source anchors, recurrence, confidence, internal scoring, or past-paper year mapping.

## MCQ Student Contract

MCQ reports are point-card reports. They must not contain practice questions, answer keys, contrast tables, or a separate trap bank by default.

Visible MCQ Point Card:

```yaml
MCQStudentPointCard:
  priority: ★★★ | ★★ | ★
  point: string
  knowledge_explanation: string
  how_exam_tests_it: string
  common_traps: list[string]
  must_remember: string
```

Forbidden by default:

- practice MCQ;
- answer key;
- contrast table;
- separate trap bank;
- source anchor;
- confidence;
- evidence;
- examiner operation;
- discriminator axis.

If the user explicitly asks for practice questions, generate a separate practice pack rather than adding them into the MCQ high-yield report.

## Short-Answer Student Contract

Short-answer reports have two levels:

- module-level logic, so the student understands how related points connect;
- point-level cards, so the student can write a direct answer.

Visible module section:

```yaml
ShortAnswerModuleSection:
  module_name: string
  module_core_logic: string
  high_yield_points: list[string]
  point_cards: list[ShortAnswerPointCard]
```

Visible point card:

```yaml
ShortAnswerPointCard:
  priority: ★★★ | ★★ | ★
  point: string
  common_question_form: string
  exam_explanation_with_highlighted_keywords: string
  example_answer: string
```

Do not display these as separate fields:

- mark-producing schema;
- required terms;
- optional examples;
- reference expansion;
- common omissions;
- task verb;
- confidence;
- source anchor.

Required terms should be bolded inside the explanation. Mark logic should be absorbed into the `Example Answer` as a natural paragraph, not exposed as a scoring table. Do not split the student answer mechanically into 2/4/6/8-mark versions unless the user specifically asks for that format.

## Long-Answer Student Contract

Long-answer outputs are exam-response playbooks, not general study coaching.

Visible structure:

```yaml
LongAnswerStudentItem:
  topic: string
  core_exam_problem: string
  likely_question_forms: list[string]
  answer_order: list[string]
  reusable_answer_blocks:
    mechanism_block: string
    method_or_readout_block: string
    interpretation_block: string
    control_or_limitation_block: string
  example_answer: string
  adaptation_rules: list[string]
  must_include: list[string]
  avoid_overwriting: list[string]
```

Do not show evidence, source, confidence, recurrence, or why the operation is likely.

## Essay Student Contract

Essay outputs are module-level packs only when the user explicitly asks for essay preparation or complete Example Essays.

Visible structure:

```yaml
EssayModulePack:
  module_name: string
  essay_title: string
  core_thesis: string
  full_example_essay: string
  adaptation_map: list[string]
  key_paragraph_bank: list[string]
  essential_terms: list[string]
  likely_stem_variants: list[string]
```

The useful student-facing pair is:

```text
Full Example Essay + how to adapt it to specific essay questions
```

Do not generate Essay Module Packs as the default revision product.

## Visual Aid Student Boundary

Generated visual aids may be embedded or attached only as revision schematics. The visible caption must state that the image is generated for revision and is not an official course figure.

Do not use a generated image as evidence, a citation, an official answer, or a replacement for written explanation. If the platform cannot generate images, omit the visual-aid section from the student-facing output.

---

## Source File: `references__subagent_protocol.md`

---

# Subagent Protocol

Use subagents when available for large multi-source exam-analysis jobs. Keep tasks independent and bounded.

## Recommended Roles

- `source-inventory agent`: inventories files, extracts text, classifies roles, and reports extraction gaps.
- `target-grouper agent`: normalizes target group keys, detects years, detects exam regimes, and blocks cross-source content pooling.
- `lecture-map agent`: splits lectures/modules and builds a knowledge-point map with slide anchors.
- `past-paper-pattern agent`: classifies paper formats, separates direct prediction evidence from coverage evidence, maps questions to lectures, and detects blueprint stability.
- `question-archetype-mapper agent`: extracts task verb, input format, cognitive operation, expected output, mark-scheme structure, and slot grammar.
- `mcq-distractor-analyser agent`: creates discriminator axes, distractor families, contrast pairs, formula traps, and exception lists.
- `short-answer-schema-planner agent`: creates bounded answer variants, highlighted keywords, and Example Answer logic.
- `coverage-closure agent`: maps every KP into compatible archetype slots and labels tested, partially tested, fresh, or saturated variants.
- `question-output agent`: drafts MCQ Point Cards, short-answer reports, long-answer/project/scenario reports, or essay module packs for a specific question type.
- `docx-output agent`: builds or reviews the student-facing walkthrough or question-type DOCX layout.
- `ExampleReviewAgent`: creates one `ExampleReviewRecord` per external example, records what worked and what failed, strips non-transferable content, writes an anti-overfit rule, declares the destination, and adds validation and regression checks before promotion.
- `RegressionAgent`: runs benchmark fixtures separately and reports both fixture pass/fail and generic contribution pass/fail against `cross_subject_regression_protocol.md`. It must explain what reusable workflow rule each benchmark validates.
- `docx-verifier agent`: reviews generated DOCX reports for formatting, readability, missing anchors, and unsupported claims.

Essay-specific roles when `essay_exam_prep` or complete essay drafting is active:

- `question-and-rubric agent`: extracts command verb, required scope, excluded scope, examiner expectation, and off-topic risks.
- `literature-retrieval agent`: finds required readings, seminal papers, recent papers, reviews, and candidate sources with DOI/PMID/URL status.
- `mechanism-theory agent`: maps mechanisms, models, source support, evidence strength, and limitations to essay sections.
- `evidence-appraisal agent`: calibrates claim strength and allowed verbs for each major source-backed claim.
- `citation agent`: verifies metadata, citation placement, source-to-claim fit, in-text citations, and reference-list entries.
- `figure-table-data agent`: checks figure reuse permission, generated schematic scope, academic table value, and data-analysis requirements.
- `critical-thinking agent`: checks analytic/descriptive balance, discussion quality, limitation use, and model comparison.

## Delegation Rules

- Do not give the same source group to multiple agents unless independent validation is needed.
- Do not ask a subagent to invent content; require source anchors and uncertainty labels.
- Give each agent a clear output schema and prohibit file edits unless the agent is explicitly assigned a write task.
- Keep DOCX generation in one owner to avoid conflicting writes.

## Useful Parallel Split

For a large source set:

1. Run source inventory locally or in one subagent.
2. Run target grouping and regime split before any cross-paper comparison.
3. In parallel, assign lecture mapping to one agent and past-paper pattern/archetype analysis to another.
4. After both return, run coverage closure and question-type outputs locally or split by MCQ/short-answer/essay.
5. Build the DOCX walkthrough and requested add-on reports locally.
6. Use one verifier agent only if time and tools allow.

## Required Verification

Before accepting subagent output:

- check that source paths exist;
- check that claims have anchors or are labelled uncertain;
- check that all comparisons are within the same `target_group_key` or compatible target group;
- check that old-regime papers are not used as current-regime blueprint evidence;
- check that archetype and slot grammar claims are separated from KP hotness claims;
- check that old/non-comparable papers were not used as direct essay predictions;
- check that the output matches the requested question type.
- check that visual source material preserves aspect ratio and remains readable when included;
- check that the main walkthrough preserves first-to-last lecture order.
- check that every external example is labelled with transferable contribution and non-transferable content;
- check that benchmark content has not been used as target factual or prediction evidence;
- check that a benchmark lesson is applied only after structural trigger evidence is found in target sources;
- check that subagent outputs distinguish fixture pass/fail from generic contribution pass/fail.
- for essay roles, check that candidate sources are not treated as verified citations until metadata and claim relevance are confirmed.

---

## Source File: `references__user_interaction_protocol.md`

---

# User Interaction Protocol

## Intake

Capture the user's target exam, subject, course, source set, deadline, output format, and quality target before generating major outputs.

## Source roles

Keep these roles separate unless the user explicitly asks for synthesis:

- lecture notes
- textbook or assigned readings
- past papers
- marking guides
- example answers
- user drafts
- external sources requested by the user

## Output views

Choose the narrowest view that satisfies the request:

- source walkthrough
- revision notes
- essay plan
- model answer
- question drill
- gap report
- prediction memo
- DOCX deliverable

## Blocking conditions

Stop and ask for missing information when the required source, target exam, output format, or citation policy is unclear and a reasonable assumption would affect correctness.

## Final-response rule

Answer directly. Include only the support detail needed for correctness. Do not expose internal QA notes unless the user asks for them.

---

## Source File: `references__visual_aid_generation_protocol.md`

---

# Visual Aid Generation Protocol

Generated images are optional revision aids. They are never factual authorities, official course figures, or substitutes for reading supplied sources.

Use this protocol only after the text content is already source-backed and the selected route would benefit from a schematic.

For essay-specific figure, table, or data decisions, also apply `essay_tutor_workflow_protocol.md`.

## When To Use

Use a visual aid only when all conditions hold:

- the platform supports image generation or diagram generation;
- the concept benefits from visual structure;
- every represented claim is already supported by accepted sources;
- the schematic can be made without copying a lecture, textbook, article, or private figure.

Usually useful:

- mechanism pathway;
- process sequence;
- spatial relation;
- comparison framework;
- method workflow;
- data-interpretation logic.

Usually not useful:

- definition-only content;
- pure essay thesis;
- unsupported student-note claim;
- content that would require copying a supplied figure.

## Hard Boundaries

Do not:

- introduce new facts through an image;
- reproduce copyrighted lecture, textbook, article, or private figures;
- create exact diagrams from supplied slides;
- imply the image is official course material;
- use visual style to increase confidence in a weak claim;
- use generated images as citation, evidence, or answer authority.
- reproduce academic paper, textbook, lecture, or private figures unless licence or permission allows the intended use. Citation alone is not permission.

If generation is unavailable, skip the visual aid silently in student-facing output and attach the internal flag `visual_aid_skipped_platform_unavailable` when an audit package is requested.

## Figure Reuse Gate

Before reusing any published figure, table image, chart, or adapted visual, record:

```yaml
FigureReuseGate:
  source:
  figure_or_table_number:
  licence:
  permission_status:
  can_reuse_directly:
  required_attribution:
```

If permission or licence is unclear, do not reproduce the image. Create an original schematic or an academic table from cited claims instead.

## VisualAidSpec

Create an internal spec before generation:

```yaml
VisualAidSpec:
  visual_aid_id:
  kp_id:
  aid_type: mechanism_pathway | process_sequence | spatial_relation | comparison_framework | method_workflow | data_interpretation_logic
  source_backed_claims: []
  visual_elements: []
  caption:
  alt_text:
  generation_prompt:
  forbidden_elements: []
  qa_flags: []
```

The prompt must be schematic and generic. It should describe relationships and labels, not ask for a copy of a supplied figure.

## Caption Contract

Use this caption or a close equivalent:

```text
Generated schematic for revision. It illustrates the source-backed mechanism; it is not an official course figure.
```

If a subject-specific caption is needed, keep the official-figure boundary explicit.

## Visual Aid QA

Before embedding or attaching a visual aid, check:

- all labels correspond to source-backed claims;
- no unsupported mechanism, direction, number, date, citation, source name, or official answer appears;
- no private or copyrighted source figure has been copied;
- licence or permission exists for any reused published visual;
- the caption states the image is generated for revision;
- the visual does not replace the written explanation.

Block or rewrite the visual aid when any check fails.

## Tables And Data Figures

Tables must be argument-useful, not decorative. Use academic styling: no vertical lines, top rule, header rule, bottom rule, caption above, and abbreviation/source note below.

For user-supplied data, use GraphPad Prism when available and appropriate for the final graph. If Prism is unavailable, use a reproducible local analysis workflow and state that Prism output was not generated. Report test choice, assumptions, effect size and confidence interval where appropriate, and a concise methods sentence.

---

## Source File: `references__visual_workbook_acceptance.md`

---

# Visual Output Regression Acceptance Criteria

This file is a generic regression acceptance note. It does not define production triggers and contains no transferable factual content.

## Generic Contribution Summary

Observed benchmark behaviour:

- older papers may contain answer-all short-answer/problem-style evidence;
- recent papers may use answer-one essay/problem-essay formal evidence;
- student-facing outputs are most usable when lecture order, original visual/source context, student-facing explanation, and question-type preparation are kept aligned.

Transferable rule:

- compare answer rule, section structure, question family, timing, and mark weighting across years before pooling papers;
- if old papers have a different answer regime, use them for coverage/schema evidence only;
- for visually taught slide-based courses, preserve first-to-last source order and align source image, explanation, and exam-facing preparation output.

Non-transferable content:

- all benchmark-specific topics, examples, year patterns, lecturers, and recurrence claims.

## Regression Acceptance Criteria

Expected generic behaviour:

1. Classify older answer-all short-answer/problem-style papers as coverage/schema evidence when current papers use a different format.
2. Do not use old-format papers as direct current prediction evidence.
3. Use only high-comparability recent formal papers as current formal evidence.
4. Detect answer-one rules when present.
5. Detect essay/problem-essay themes as operation slots, not as guaranteed recurring factual topics.
6. Generate the Word-first walkthrough or question-type DOCX add-on requested by the selected route.
7. Create the requested output folder or report a safe fallback path.
8. Save student-facing DOCX output separately from diagnostics/QA files.
9. The student-facing DOCX output must preserve source order where relevant, keep explanation and question-type preparation visibly connected, and exclude evidence/provenance columns or helper artifacts unless an audit package is explicitly requested.

---

## Source File: `requirements.txt`

---

openpyxl
python-docx
pypdf
PyMuPDF

---

## Source File: `schemas__analysis_context.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/analysis_context.schema.json",
  "title": "AnalysisContext",
  "type": "object",
  "required": [
    "context_id",
    "source_id",
    "context_type",
    "allowed_evidence_use",
    "factual_claim_support_allowed",
    "current_prediction_allowed",
    "unit_name_production_trigger_allowed"
  ],
  "properties": {
    "object_type": { "const": "AnalysisContext" },
    "context_id": { "type": "string" },
    "source_id": { "type": "string" },
    "target_group_key": { "type": "string" },
    "source_role": { "type": "string" },
    "context_type": {
      "enum": [
        "target_unit_current_regime",
        "target_unit_old_or_different_regime",
        "target_unit_auxiliary",
        "cross_unit_example",
        "style_exemplar",
        "layout_exemplar",
        "benchmark_fixture",
        "unsupported_or_unreadable"
      ]
    },
    "comparability_status": {
      "enum": ["current", "comparable_with_limits", "old_or_different", "style_only", "layout_only", "test_only", "unusable", "unknown"]
    },
    "allowed_evidence_use": {
      "type": "array",
      "items": {
        "enum": [
          "factual_course_content",
          "current_exam_blueprint",
          "coverage_schema",
          "question_format_evidence",
          "answer_style_only",
          "layout_only",
          "regression_test_only",
          "no_claim_support"
        ]
      }
    },
    "factual_claim_support_allowed": { "type": "boolean" },
    "current_prediction_allowed": { "type": "boolean" },
    "unit_name_production_trigger_allowed": { "const": false },
    "blocked_uses": { "type": "array", "items": { "type": "string" } },
    "qa_flags": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": false
}

---

## Source File: `schemas__atomic_knowledge_ledger.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/atomic_knowledge_ledger.schema.json",
  "title": "AtomicKnowledgeLedger",
  "type": "object",
  "required": ["ledger_id", "target_group_key", "units", "coverage_floor", "qa_status"],
  "properties": {
    "object_type": { "const": "AtomicKnowledgeLedger" },
    "ledger_id": { "type": "string", "minLength": 1 },
    "target_group_key": { "type": "string", "minLength": 1 },
    "units": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "unit_id",
          "source_id",
          "lecture_id",
          "slide_or_page_range",
          "raw_heading",
          "raw_text_summary",
          "unit_type",
          "student_visibility",
          "bound_module_id",
          "coverage_status"
        ],
        "properties": {
          "unit_id": { "type": "string", "minLength": 1 },
          "source_id": { "type": "string", "minLength": 1 },
          "lecture_id": { "type": "string" },
          "slide_or_page_range": { "type": "string" },
          "raw_heading": { "type": "string" },
          "raw_text_summary": { "type": "string" },
          "unit_type": {
            "enum": [
              "definition",
              "term",
              "contrast_pair",
              "criteria_item",
              "mechanism_step",
              "method_step",
              "equation",
              "calculation_rule",
              "graph_readout",
              "diagram_label",
              "table_entry",
              "named_example",
              "disease_case",
              "drug_case",
              "limitation",
              "misconception",
              "administrative",
              "decorative",
              "duplicate",
              "unreadable_visual"
            ]
          },
          "student_visibility": {
            "enum": [
              "include_in_notes",
              "internal_audit_only",
              "exclude_admin",
              "duplicate_covered_elsewhere",
              "requires_visual_inspection"
            ]
          },
          "bound_module_id": { "type": ["string", "null"] },
          "coverage_status": {
            "enum": [
              "covered",
              "grouped_but_named",
              "audit_only",
              "excluded_with_reason",
              "missing"
            ]
          }
        },
        "additionalProperties": false
      }
    },
    "coverage_floor": {
      "type": "object",
      "required": ["protected_units_total", "visible_units_bound", "missing_units"],
      "properties": {
        "protected_units_total": { "type": "integer", "minimum": 0 },
        "visible_units_bound": { "type": "integer", "minimum": 0 },
        "missing_units": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "qa_status": { "enum": ["pass", "warn", "block"] }
  },
  "additionalProperties": false
}

---

## Source File: `schemas__evidence_claim.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/evidence_claim.schema.json",
  "title": "EvidenceClaim",
  "type": "object",
  "required": ["claim_id", "claim_text", "support_level", "verification_status", "source_anchors", "claim_strength"],
  "properties": {
    "object_type": { "const": "EvidenceClaim" },
    "claim_id": { "type": "string" },
    "claim_text": { "type": "string" },
    "support_level": { "type": "string" },
    "verification_status": { "type": "string" },
    "source_anchors": { "type": "array" },
    "claim_strength": { "type": "string" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__exam_emphasis_profile.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/exam_emphasis_profile.schema.json",
  "title": "ExamEmphasisProfile",
  "type": "object",
  "required": [
    "profile_id",
    "target_group_key",
    "current_regime",
    "visible_question_types",
    "compatible_knowledge_points",
    "emphasis_level",
    "limitation_flags"
  ],
  "properties": {
    "profile_id": { "type": "string" },
    "target_group_key": { "type": "string" },
    "current_regime": { "type": ["string", "null"] },
    "visible_question_types": { "type": "array", "items": { "type": "string" } },
    "repeated_question_families": { "type": "array", "items": { "type": "string" } },
    "compatible_knowledge_points": { "type": "array", "items": { "type": "string" } },
    "answer_operations": { "type": "array", "items": { "type": "string" } },
    "emphasis_level": { "enum": ["high", "medium", "low", "unknown"] },
    "limitation_flags": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__exam_prep_notes_plan.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/exam_prep_notes_plan.schema.json",
  "title": "PublicLectureNotesPlan",
  "type": "object",
  "required": [
    "object_type",
    "title",
    "target_group_key",
    "source_scale_budget",
    "output_language_profile",
    "route_docx_style_profile",
    "public_lecture_sections"
  ],
  "properties": {
    "object_type": { "const": "PublicLectureNotesPlan" },
    "notes_plan_id": { "type": "string" },
    "title": { "type": "string", "minLength": 1 },
    "target_group_key": { "type": "string", "minLength": 1 },
    "source_scale_budget": { "$ref": "#/$defs/SourceScaleBudget" },
    "output_language_profile": { "$ref": "#/$defs/OutputLanguageProfile" },
    "route_docx_style_profile": { "$ref": "#/$defs/RouteDocxStyleProfile" },
    "public_lecture_sections": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/PublicLectureSection" }
    }
  },
  "not": {
    "anyOf": [
      { "required": ["course_knowledge_map"] },
      { "required": ["course_modules"] },
      { "required": ["legacy_course_sections"] },
      { "required": ["legacy_public_output_points"] },
      { "required": ["knowledge_cards"] },
      { "required": ["exam_overlay_pass"] },
      { "required": ["question_type_addons"] }
    ]
  },
  "$defs": {
    "SourceScaleBudget": {
      "type": "object",
      "required": [
        "source_units_count",
        "readable_source_blocks",
        "protected_knowledge_units_total",
        "excluded_non_knowledge_units_total",
        "target_public_units_min",
        "target_words_min",
        "compression_mode",
        "coverage_floor_status"
      ],
      "properties": {
        "source_units_count": { "type": "integer", "minimum": 0 },
        "readable_source_blocks": { "type": "integer", "minimum": 0 },
        "source_pages_or_slides_estimate": { "type": "integer", "minimum": 0 },
        "source_information_profile_status": { "enum": ["measured", "estimated", "missing", "not_applicable"] },
        "informative_page_count": { "type": "integer", "minimum": 0 },
        "non_informative_page_count": { "type": "integer", "minimum": 0 },
        "information_mass_units": { "type": "number", "minimum": 0 },
        "average_information_score": { "type": "number", "minimum": 0 },
        "page_information_profile": {
          "type": "array",
          "items": { "type": "object", "additionalProperties": true }
        },
        "source_types": { "type": "array", "items": { "type": "string" } },
        "protected_knowledge_units_total": { "type": "integer", "minimum": 0 },
        "excluded_non_knowledge_units_total": { "type": "integer", "minimum": 0 },
        "target_public_units_min": { "type": "integer", "minimum": 0 },
        "target_words_min": { "type": "integer", "minimum": 0 },
        "target_words_max": { "type": "integer", "minimum": 0 },
        "compression_mode": { "enum": ["explain_not_dump", "concise", "standard", "expanded", "multi_volume_required"] },
        "compression_reason": { "type": "string" },
        "coverage_floor_status": { "enum": ["pass", "warn", "block"] }
      },
      "additionalProperties": false
    },
    "OutputLanguageProfile": {
      "type": "object",
      "required": ["output_language"],
      "properties": {
        "output_language": { "type": "string", "minLength": 1 },
        "allow_bilingual": { "type": "boolean", "default": false },
        "allow_non_english": { "type": "boolean", "default": false },
        "preserve_technical_terms": { "type": "boolean", "default": true }
      },
      "additionalProperties": false
    },
    "PublicLectureSection": {
      "type": "object",
      "required": ["lecture_title", "modules"],
      "properties": {
        "lecture_title": { "type": "string", "minLength": 1 },
        "lecture_scope": { "type": "string" },
        "modules": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/PublicLectureModule" }
        }
      },
      "additionalProperties": false
    },
    "PublicLectureModule": {
      "type": "object",
      "required": ["module_title", "knowledge_functions", "explanation", "blocks"],
      "properties": {
        "module_title": { "type": "string", "minLength": 1 },
        "knowledge_functions": {
          "type": "array",
          "minItems": 2,
          "uniqueItems": true,
          "items": {
            "enum": [
              "definition_boundary",
              "mechanism_process",
              "method_readout",
              "graph_data_interpretation",
              "calculation_unit_worked_example",
              "named_example",
              "limitation_trap"
            ]
          }
        },
        "explanation": { "type": "string", "minLength": 160 },
        "blocks": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/PublicLectureBlock" }
        },
        "visual_refs": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "PublicLectureBlock": {
      "type": "object",
      "required": ["block_type", "content"],
      "properties": {
        "block_type": {
          "enum": [
            "definition",
            "mechanism",
            "method",
            "graph_data",
            "calculation",
            "example",
            "limitation",
            "comparison",
            "table",
            "explanation"
          ]
        },
        "label": { "type": "string" },
        "content": {
          "oneOf": [
            { "type": "string", "minLength": 1 },
            { "type": "array", "minItems": 1, "items": { "type": "string", "minLength": 1 } }
          ]
        }
      },
      "additionalProperties": false
    },
    "RouteDocxStyleProfile": {
      "type": "object",
      "required": [
        "route",
        "margin_cm",
        "line_spacing",
        "body_alignment",
        "title_alignment",
        "heading_alignment",
        "image_alignment",
        "body_font_pt",
        "text_color",
        "theme_colours_allowed",
        "blue_heading_styles_allowed"
      ],
      "properties": {
        "route": { "const": "exam_prep_notes_docx" },
        "margin_cm": { "type": "number", "minimum": 1.92, "maximum": 2.08 },
        "line_spacing": { "type": "number", "minimum": 1.05, "maximum": 1.15 },
        "body_alignment": { "const": "left" },
        "title_alignment": { "const": "left" },
        "heading_alignment": { "const": "left" },
        "image_alignment": { "const": "center" },
        "body_font_pt": { "type": "number", "minimum": 9.5, "maximum": 11.5 },
        "title_font_pt": { "type": "number", "minimum": 13.0, "maximum": 16.0 },
        "lecture_heading_font_pt": { "type": "number", "minimum": 12.0, "maximum": 15.0 },
        "module_heading_font_pt": { "type": "number", "minimum": 10.5, "maximum": 13.0 },
        "text_color": { "const": "black" },
        "lecture_page_breaks": { "type": "boolean", "default": false },
        "theme_colours_allowed": { "const": false },
        "blue_heading_styles_allowed": { "const": false }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}

---

## Source File: `schemas__example_essay_plan.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/example_essay_plan.schema.json",
  "title": "ExampleEssayPlan",
  "type": "object",
  "required": ["essays"],
  "properties": {
    "citation_rendering_policy": {
      "type": "object",
      "properties": {
        "academic_paper_author_display": { "enum": ["parenthetical_author_year_only"] },
        "author_led_prose_allowed": { "const": false }
      },
      "additionalProperties": true
    },
    "essays": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["essay_id", "question", "title", "lecture_anchors", "paragraphs"],
        "properties": {
          "essay_id": { "type": "string" },
          "question": { "type": "string" },
          "title": { "type": "string" },
          "subtitle": { "type": ["string", "null"] },
          "target_group_key": { "type": ["string", "null"] },
          "citation_rendering_policy": {
            "type": ["object", "null"],
            "properties": {
              "academic_paper_author_display": { "enum": ["parenthetical_author_year_only"] },
              "author_led_prose_allowed": { "const": false }
            },
            "additionalProperties": true
          },
          "lecture_anchors": { "type": "array" },
          "compression_budget": {
            "type": ["object", "null"],
            "properties": {
              "current_word_count": { "type": ["integer", "number", "null"] },
              "requested_reduction": { "type": ["object", "null"] },
              "protected_source_skeleton": { "type": "array" },
              "protected_academic_details": { "type": "array" },
              "removable_redundancy": { "type": "array" },
              "safe_reduction_range": { "type": ["object", "null"] },
              "unsafe_threshold": { "type": ["integer", "number", "null"] },
              "decision": { "type": ["string", "null"] },
              "reason": { "type": ["string", "null"] }
            },
            "additionalProperties": true
          },
          "paragraphs": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["paragraph_id", "function", "text_runs"],
              "properties": {
                "paragraph_id": { "type": "string" },
                "function": { "type": "string" },
                "is_title": { "type": "boolean" },
                "is_subtitle": { "type": "boolean" },
                "is_heading": { "type": "boolean" },
                "lecture_anchors": { "type": "array" },
                "text_runs": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "required": ["text"],
                    "properties": {
                      "text": { "type": "string" },
                      "source_type": { "type": ["string", "null"] },
                      "source_anchor": { "type": ["string", "null"] },
                      "highlight": { "enum": ["none", "yellow", "green"] },
                      "in_text_citation": { "type": ["string", "null"] },
                      "citation_original_read": { "type": ["boolean", "null"] },
                      "source_read": { "type": ["boolean", "null"] },
                      "micro_detail_insert": { "type": "boolean" },
                      "original_phrase": { "type": ["string", "null"] },
                      "inserted_phrase": { "type": ["string", "null"] },
                      "parent_ppt_or_source_slot": { "type": ["string", "null"] },
                      "question_function": { "type": ["string", "null"] },
                      "claim_delta": { "type": ["string", "null"] },
                      "qa_status": { "type": ["string", "null"] }
                    },
                    "additionalProperties": true
                  }
                }
              },
              "additionalProperties": true
            }
          }
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__example_review_ledger.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/example_review_ledger.schema.json",
  "title": "ExampleReviewLedger",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "object_type",
    "ledger_id",
    "target_group_key",
    "records",
    "non_transferable_content",
    "promotion_summary",
    "qa_status"
  ],
  "properties": {
    "object_type": { "const": "ExampleReviewLedger" },
    "ledger_id": { "type": "string", "minLength": 1 },
    "target_group_key": { "type": "string", "minLength": 1 },
    "records": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "example_id",
          "source_role",
          "example_scope",
          "what_worked",
          "why_it_worked",
          "what_failed",
          "why_it_failed",
          "transferable_principle",
          "non_transferable_content",
          "anti_overfit_rule",
          "affected_protocols",
          "affected_scripts",
          "validation_check",
          "regression_fixture",
          "promotion_status",
          "confidence"
        ],
        "properties": {
          "example_id": { "type": "string", "minLength": 1 },
          "source_role": {
            "type": "string",
            "enum": ["style_exemplar", "feedback", "cross_target_example", "benchmark_fixture", "other_example"]
          },
          "example_scope": { "type": "string", "minLength": 1 },
          "what_worked": { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 1 },
          "why_it_worked": { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 1 },
          "what_failed": { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 1 },
          "why_it_failed": { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 1 },
          "transferable_principle": { "type": "string", "minLength": 1 },
          "non_transferable_content": { "type": "array", "items": { "type": "string", "minLength": 1 }, "minItems": 1 },
          "anti_overfit_rule": { "type": "string", "minLength": 1 },
          "affected_protocols": { "type": "array", "items": { "type": "string", "minLength": 1 } },
          "affected_scripts": { "type": "array", "items": { "type": "string", "minLength": 1 } },
          "validation_check": { "type": "string", "minLength": 1 },
          "regression_fixture": { "type": "string", "minLength": 1 },
          "promotion_status": { "type": "string", "enum": ["candidate", "accepted", "rejected", "blocked"] },
          "confidence": { "type": "string", "enum": ["high", "medium", "low"] }
        }
      }
    },
    "non_transferable_content": { "type": "array", "items": { "type": "string", "minLength": 1 } },
    "promotion_summary": {
      "type": "object",
      "additionalProperties": false,
      "required": ["accepted_count", "candidate_count", "rejected_count", "blocked_count"],
      "properties": {
        "accepted_count": { "type": "integer", "minimum": 0 },
        "candidate_count": { "type": "integer", "minimum": 0 },
        "rejected_count": { "type": "integer", "minimum": 0 },
        "blocked_count": { "type": "integer", "minimum": 0 }
      }
    },
    "qa_status": { "type": "string", "enum": ["pass", "warning", "fail"] }
  }
}

---

## Source File: `schemas__fragment_partition.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/fragment_partition.schema.json",
  "title": "FragmentPartition",
  "type": "object",
  "required": ["partition_id", "source_id", "fragment_ids", "source_role", "analysis_context", "target_group_key", "exam_regime", "year", "question_type", "concept_type", "command_verbs", "input_format", "image_count", "extraction_confidence", "allowed_evidence_use", "source_hash"],
  "properties": {
    "object_type": { "const": "FragmentPartition" },
    "partition_id": { "type": "string" },
    "source_id": { "type": "string" },
    "fragment_ids": { "type": "array", "items": { "type": "string" } },
    "source_role": { "type": "string" },
    "analysis_context": { "type": "string" },
    "target_group_key": { "type": ["string", "null"] },
    "exam_regime": { "type": ["string", "null"] },
    "year": { "type": ["integer", "string", "null"] },
    "question_type": { "type": ["string", "null"] },
    "concept_type": { "type": ["string", "null"] },
    "command_verbs": { "type": "array", "items": { "type": "string" } },
    "input_format": { "type": ["string", "object", "null"] },
    "image_count": { "type": ["integer", "null"] },
    "visual_content_types": { "type": "array", "items": { "type": "string" } },
    "visual_inspection_status": { "type": "string" },
    "visual_inspection_required": { "type": "boolean" },
    "extraction_confidence": { "enum": ["High", "Medium", "Low"] },
    "allowed_evidence_use": { "type": "array", "items": { "type": "string" } },
    "source_hash": { "type": "string" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__gap_report.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/gap_report.schema.json",
  "title": "GapReport",
  "type": "object",
  "required": ["status", "high_gaps", "medium_gaps", "low_gaps", "checks"],
  "properties": {
    "status": { "enum": ["pass", "fail"] },
    "high_gaps": { "type": "array", "items": { "type": "object" } },
    "medium_gaps": { "type": "array", "items": { "type": "object" } },
    "low_gaps": { "type": "array", "items": { "type": "object" } },
    "checks": { "type": "array", "items": { "type": "object" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__gate_result.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/gate_result.schema.json",
  "title": "GateResult",
  "type": "object",
  "required": ["gate_result_id", "gate_name", "outcome", "reason", "blocked_conclusion", "remediation_source", "severity"],
  "properties": {
    "object_type": { "const": "GateResult" },
    "gate_result_id": { "type": "string" },
    "gate_name": { "type": "string" },
    "outcome": { "enum": ["pass", "warn", "block"] },
    "reason": { "type": "string" },
    "blocked_conclusion": { "type": ["string", "null"] },
    "remediation_source": { "type": ["string", "null"] },
    "severity": { "enum": ["blocking", "warning", "info"] }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__input_readiness_report.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/input_readiness_report.schema.json",
  "title": "InputReadinessReport",
  "type": "object",
  "required": [
    "report_id",
    "selected_preset",
    "target_group_key",
    "required_source_classes",
    "available_source_classes",
    "missing_required",
    "blockers",
    "warnings",
    "can_run"
  ],
  "properties": {
    "report_id": { "type": "string" },
    "selected_preset": { "type": "string" },
    "target_group_key": { "type": "string" },
    "required_source_classes": { "type": "array", "items": { "type": "string" } },
    "available_source_classes": { "type": "array", "items": { "type": "string" } },
    "missing_required": { "type": "array", "items": { "type": "string" } },
    "blockers": { "type": "array", "items": { "type": "object" } },
    "warnings": { "type": "array", "items": { "type": "object" } },
    "can_run": { "type": "boolean" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__knowledge_surface_contract.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/knowledge_surface_contract.schema.json",
  "title": "KnowledgeSurfaceContract",
  "type": "object",
  "required": ["contract_id", "route", "allowed_public_functions", "forbidden_public_functions", "label_policy", "density_policy"],
  "properties": {
    "object_type": { "const": "KnowledgeSurfaceContract" },
    "contract_id": { "type": "string" },
    "route": {
      "enum": [
        "exam_prep_notes_docx",
        "knowledge_walkthrough_docx",
        "mcq_exam_prep",
        "short_answer_exam_prep",
        "long_answer_project_scenario_prep",
        "essay_exam_prep"
      ]
    },
    "allowed_public_functions": {
      "type": "array",
      "items": {
        "enum": [
          "definition",
          "mechanism",
          "process",
          "method_workflow",
          "assay_readout",
          "calculation",
          "graph_data_rule",
          "diagnostic_rule",
          "comparison",
          "example_interpretation",
          "limitation_or_scope",
          "synthesis"
        ]
      },
      "minItems": 1
    },
    "forbidden_public_functions": {
      "type": "array",
      "items": {
        "enum": [
          "source_route_narration",
          "ai_process_or_provenance",
          "audit_trace",
          "generic_study_advice",
          "exam_meta_or_prediction_trace",
          "rigid_template_bucket",
          "evidence_justification_trace",
          "decorative_transition"
        ]
      }
    },
    "label_policy": {
      "type": "object",
      "required": ["mode"],
      "properties": {
        "mode": { "enum": ["semantic_sparse", "explicit_user_requested", "calculation_or_table_only"] },
        "allowed_labels": { "type": "array", "items": { "type": "string" } },
        "forbidden_template_labels": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "density_policy": {
      "type": "object",
      "required": ["mode"],
      "properties": {
        "mode": { "enum": ["source_adaptive", "user_fixed", "strict_brief"] },
        "mechanism_detail_target_ratio": { "type": "string", "pattern": "^0\\.10-0\\.15$" },
        "extra_reading_target_ratio": { "type": "string", "pattern": "^0\\.10-0\\.15$" },
        "conclusion_required": { "type": "boolean" }
      },
      "additionalProperties": false
    },
    "surface_label_decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["label", "function", "decision"],
        "properties": {
          "label": { "type": "string" },
          "function": { "type": "string" },
          "decision": { "enum": ["keep", "merge_into_heading", "merge_into_sentence", "delete"] },
          "reason": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "qa_status": { "enum": ["pass", "warn", "fail", "not_run"] }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__knowledge_walkthrough_plan.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/knowledge_walkthrough_plan.schema.json",
  "title": "PublicLectureNotesPlan",
  "type": "object",
  "required": [
    "object_type",
    "title",
    "target_group_key",
    "source_scale_budget",
    "output_language_profile",
    "route_docx_style_profile",
    "public_lecture_sections"
  ],
  "properties": {
    "object_type": { "const": "PublicLectureNotesPlan" },
    "walkthrough_id": { "type": "string" },
    "title": { "type": "string", "minLength": 1 },
    "target_group_key": { "type": "string", "minLength": 1 },
    "source_scale_budget": { "$ref": "exam_prep_notes_plan.schema.json#/$defs/SourceScaleBudget" },
    "output_language_profile": { "$ref": "exam_prep_notes_plan.schema.json#/$defs/OutputLanguageProfile" },
    "public_lecture_sections": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "exam_prep_notes_plan.schema.json#/$defs/PublicLectureSection" }
    },
    "route_docx_style_profile": { "$ref": "#/$defs/RouteDocxStyleProfile" }
  },
  "not": {
    "anyOf": [
      { "required": ["course_knowledge_map"] },
      { "required": ["course_modules"] },
      { "required": ["legacy_lectures"] },
      { "required": ["knowledge_cards"] },
      { "required": ["question_type_addons"] }
    ]
  },
  "$defs": {
    "RouteDocxStyleProfile": {
      "type": "object",
      "required": [
        "route",
        "margin_cm",
        "line_spacing",
        "body_alignment",
        "title_alignment",
        "heading_alignment",
        "image_alignment",
        "body_font_pt",
        "text_color",
        "theme_colours_allowed",
        "blue_heading_styles_allowed"
      ],
      "properties": {
        "route": { "const": "knowledge_walkthrough_docx" },
        "margin_cm": { "type": "number", "minimum": 1.92, "maximum": 2.08 },
        "line_spacing": { "type": "number", "minimum": 1.05, "maximum": 1.15 },
        "body_alignment": { "const": "left" },
        "title_alignment": { "const": "left" },
        "heading_alignment": { "const": "left" },
        "image_alignment": { "const": "center" },
        "body_font_pt": { "type": "number", "minimum": 9.5, "maximum": 11.5 },
        "title_font_pt": { "type": "number", "minimum": 13.0, "maximum": 16.0 },
        "lecture_heading_font_pt": { "type": "number", "minimum": 12.0, "maximum": 15.0 },
        "module_heading_font_pt": { "type": "number", "minimum": 10.5, "maximum": 13.0 },
        "text_color": { "const": "black" },
        "lecture_page_breaks": { "type": "boolean", "default": false },
        "theme_colours_allowed": { "const": false },
        "blue_heading_styles_allowed": { "const": false }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}

---

## Source File: `schemas__language_delta.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/language_delta.schema.json",
  "title": "LanguageDelta",
  "type": "object",
  "required": ["delta_id", "bad_pattern", "improved_pattern", "reasoning", "applies_to", "linter_signal", "severity"],
  "properties": {
    "delta_id": { "type": "string" },
    "bad_pattern": { "type": "string" },
    "improved_pattern": { "type": "string" },
    "reasoning": { "type": "string" },
    "applies_to": { "type": "array", "items": { "type": "string" } },
    "linter_signal": { "type": "string" },
    "severity": { "enum": ["high", "medium", "low"] }
  },
  "additionalProperties": false
}

---

## Source File: `schemas__lineage_event.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/lineage_event.schema.json",
  "title": "LineageEvent",
  "type": "object",
  "required": ["event_id", "run_id", "action_id", "action_type", "input_object_ids", "output_object_ids", "artifact_ids", "qa_flag_ids", "timestamp", "status"],
  "properties": {
    "object_type": { "const": "LineageEvent" },
    "event_id": { "type": "string" },
    "run_id": { "type": "string" },
    "action_id": { "type": "string" },
    "action_type": { "type": "string" },
    "input_object_ids": { "type": "array", "items": { "type": "string" } },
    "output_object_ids": { "type": "array", "items": { "type": "string" } },
    "artifact_ids": { "type": "array", "items": { "type": "string" } },
    "qa_flag_ids": { "type": "array", "items": { "type": "string" } },
    "timestamp": { "type": "string" },
    "status": { "enum": ["pass", "fail", "blocked", "skipped"] }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__ontology_link.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/ontology_link.schema.json",
  "title": "OntologyLink",
  "type": "object",
  "required": ["link_id", "link_type", "from_id", "to_id"],
  "properties": {
    "link_id": { "type": "string" },
    "link_type": { "type": "string" },
    "from_id": { "type": "string" },
    "to_id": { "type": "string" },
    "support_level": { "type": ["string", "null"] },
    "created_by_action": { "type": ["string", "null"] }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__output_view.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/output_view.schema.json",
  "title": "OutputView",
  "type": "object",
  "required": ["view_id", "view_type", "included_sections", "omitted_sections", "reason", "artifact_policy"],
  "properties": {
    "object_type": { "const": "OutputView" },
    "view_id": { "type": "string" },
    "view_type": { "type": "string" },
    "included_sections": { "type": "array", "items": { "type": "string" } },
    "omitted_sections": { "type": "array", "items": { "type": "string" } },
    "reason": { "type": "string" },
    "artifact_policy": { "type": "string" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__prompt_card.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/prompt_card.schema.json",
  "title": "PromptCard",
  "type": "object",
  "required": ["card_id", "preset", "purpose", "minimum_inputs", "output_contract", "hard_stops"],
  "properties": {
    "card_id": { "type": "string" },
    "preset": { "type": "string" },
    "purpose": { "type": "string" },
    "minimum_inputs": { "type": "array", "items": { "type": "string" } },
    "output_contract": { "type": "array", "items": { "type": "string" } },
    "hard_stops": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__qa_flag.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/qa_flag.schema.json",
  "title": "QAFlag",
  "type": "object",
  "required": ["flag_id", "severity", "reason", "blocked_object", "resolution_status"],
  "properties": {
    "object_type": { "const": "QAFlag" },
    "flag_id": { "type": "string" },
    "severity": { "enum": ["blocking", "warning", "info"] },
    "reason": { "type": "string" },
    "blocked_object": { "type": ["string", "null"] },
    "resolution_status": { "type": "string" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__question_type_addon.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/question_type_addon.schema.json",
  "title": "QuestionTypeAddOn",
  "type": "object",
  "required": ["addon_id", "kp_id", "addon_type", "student_visible_items", "qa_flags"],
  "properties": {
    "addon_id": { "type": "string" },
    "kp_id": { "type": "string" },
    "addon_type": { "enum": ["mcq", "short_answer", "long_answer", "practical_data", "essay"] },
    "student_visible_items": { "type": "array", "items": { "type": "string" } },
    "qa_flags": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__run_manifest.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/run_manifest.schema.json",
  "title": "RunManifest",
  "type": "object",
  "required": ["run_id", "created_at", "request_scope", "source_hashes", "actions", "object_store", "artifacts", "qa_summary"],
  "properties": {
    "object_type": { "const": "RunManifest" },
    "run_id": { "type": "string" },
    "created_at": { "type": "string" },
    "request_scope": { "type": "string" },
    "source_hashes": { "type": "object" },
    "actions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["action_id", "action_type", "status", "inputs", "outputs"],
        "properties": {
          "action_id": { "type": "string" },
          "action_type": { "type": "string" },
          "status": { "enum": ["planned", "skipped", "pass", "fail", "blocked"] },
          "inputs": { "type": "array" },
          "outputs": { "type": "array" }
        },
        "additionalProperties": true
      }
    },
    "object_store": { "type": "object" },
    "artifacts": { "type": "array" },
    "qa_summary": { "type": "object" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__run_status.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/run_status.schema.json",
  "title": "RunStatus",
  "type": "object",
  "required": ["run_id", "plan_id", "status", "current_action", "completed_actions", "blocked_actions", "artifacts"],
  "properties": {
    "run_id": { "type": "string" },
    "plan_id": { "type": "string" },
    "status": { "enum": ["planned", "running", "blocked", "failed", "passed"] },
    "current_action": { "type": ["string", "null"] },
    "completed_actions": { "type": "array", "items": { "type": "string" } },
    "blocked_actions": { "type": "array", "items": { "type": "string" } },
    "artifacts": { "type": "array", "items": { "type": "object" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__skill_config.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/skill_config.schema.json",
  "title": "SkillConfig",
  "type": "object",
  "required": ["project", "source_inputs", "source_policy", "output_mode", "qa", "advanced"],
  "properties": {
    "task_type": { "type": "string" },
    "sources": { "type": "array", "items": { "type": ["string", "object"] } },
    "output_format": { "type": "string" },
    "qa_checks": { "type": "array", "items": { "type": "string" } },
    "project": {
      "type": "object",
      "required": ["course_name", "module_code", "target_group_key", "exam_year", "output_folder"],
      "properties": {
        "course_name": { "type": "string" },
        "module_code": { "type": "string" },
        "target_group_key": { "type": "string" },
        "exam_year": { "type": ["string", "number", "null"] },
        "output_folder": { "type": "string" }
      },
      "additionalProperties": true
    },
    "source_inputs": {
      "type": "object",
      "properties": {
        "lecture_slides": { "type": "array", "items": { "type": ["string", "object"] } },
        "official_notes": { "type": "array", "items": { "type": ["string", "object"] } },
        "course_notes": { "type": "array", "items": { "type": ["string", "object"] } },
        "student_notes": { "type": "array", "items": { "type": ["string", "object"] } },
        "ai_generated_notes": { "type": "array", "items": { "type": ["string", "object"] } },
        "formal_past_papers": { "type": "array", "items": { "type": ["string", "object"] } },
        "practical_materials": { "type": "array", "items": { "type": ["string", "object"] } },
        "mocks_quizzes_answer_keys": { "type": "array", "items": { "type": ["string", "object"] } },
        "exemplars_or_feedback": { "type": "array", "items": { "type": ["string", "object"] } },
        "extra_reading_books_or_papers": { "type": "array", "items": { "type": ["string", "object"] } }
      },
      "additionalProperties": true
    },
    "source_policy": {
      "type": "object",
      "required": [
        "allow_online_academic_search",
        "allow_extra_reading_enrichment",
        "require_verified_citations",
        "treat_examples_as_style_only"
      ],
      "properties": {
        "allow_online_academic_search": { "type": "boolean" },
        "allow_extra_reading_enrichment": { "type": "boolean" },
        "require_verified_citations": { "type": "boolean" },
        "treat_examples_as_style_only": { "type": "boolean" }
      },
      "additionalProperties": true
    },
    "output_mode": {
      "type": "object",
      "required": ["preset", "include_audit_package", "student_visible_only"],
      "properties": {
        "preset": {
          "enum": [
            "source_inventory_only",
            "exam_format_diagnosis",
            "exam_prep_notes_docx",
            "knowledge_walkthrough_docx",
            "mcq_exam_prep",
            "short_answer_exam_prep",
            "long_answer_project_scenario_prep",
            "essay_exam_prep",
            "audit_lint_only",
            "github_ready_qa"
          ]
        },
        "include_audit_package": { "type": "boolean" },
        "student_visible_only": { "type": "boolean" }
      },
      "additionalProperties": true
    },
    "qa": {
      "type": "object",
      "required": [
        "strict_publish_gate",
        "require_lineage",
        "run_language_lint",
        "run_workflow_validator",
        "fail_on_blocking_flags"
      ],
      "properties": {
        "strict_publish_gate": { "type": "boolean" },
        "require_lineage": { "type": "boolean" },
        "run_language_lint": { "type": "boolean" },
        "run_workflow_validator": { "type": "boolean" },
        "fail_on_blocking_flags": { "type": "boolean" }
      },
      "additionalProperties": true
    },
    "advanced": {
      "type": "object",
      "required": ["reuse_existing_intermediates", "rebuild_fragment_index", "clean_stale_generated_outputs"],
      "properties": {
        "reuse_existing_intermediates": { "type": "boolean" },
        "rebuild_fragment_index": { "enum": ["auto", "always", "never"] },
        "clean_stale_generated_outputs": { "type": "boolean" }
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__source_coverage_map.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/source_coverage_map.schema.json",
  "title": "SourceCoverageMap",
  "type": "object",
  "required": ["coverage_id", "request_id", "required_source_classes", "available_source_classes", "missing_blocking_sources", "freshness_status", "unreadable_sources", "blocked_conclusions"],
  "properties": {
    "object_type": { "const": "SourceCoverageMap" },
    "coverage_id": { "type": "string" },
    "request_id": { "type": "string" },
    "required_source_classes": { "type": "array", "items": { "type": "string" } },
    "available_source_classes": { "type": "array", "items": { "type": "string" } },
    "missing_blocking_sources": { "type": "array", "items": { "type": "string" } },
    "freshness_status": { "type": "string" },
    "unreadable_sources": { "type": "array", "items": { "type": "string" } },
    "blocked_conclusions": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__source_document.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/source_document.schema.json",
  "title": "SourceDocument",
  "type": "object",
  "required": ["source_id", "path", "file_role", "trust_level", "analysis_context", "allowed_evidence_use", "extraction_status"],
  "properties": {
    "object_type": { "const": "SourceDocument" },
    "source_id": { "type": "string" },
    "path": { "type": "string" },
    "file_role": { "type": "string" },
    "trust_level": { "type": "string" },
    "analysis_context": { "type": "string" },
    "allowed_evidence_use": { "type": "array", "items": { "type": "string" } },
    "extraction_status": { "type": "string" },
    "source_hash": { "type": ["string", "null"] },
    "visual_content_types": { "type": "array", "items": { "type": "string" } },
    "visual_inspection_status": { "type": "string" },
    "visual_inspection_required": { "type": "boolean" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__source_fragment.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/source_fragment.schema.json",
  "title": "SourceFragment",
  "type": "object",
  "required": ["fragment_id", "source_id", "fragment_type", "locator", "text", "image_anchor", "extraction_confidence"],
  "properties": {
    "object_type": { "const": "SourceFragment" },
    "fragment_id": { "type": "string" },
    "source_id": { "type": "string" },
    "fragment_type": { "type": "string" },
    "locator": { "type": "string" },
    "text": { "type": "string" },
    "image_anchor": { "type": ["string", "null"] },
    "extraction_confidence": { "enum": ["High", "Medium", "Low"] }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__student_output_contract.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/student_output_contract.schema.json",
  "title": "StudentOutputContract",
  "type": "object",
  "required": ["contract_id", "output_mode", "allowed_visible_fields", "forbidden_visible_fields"],
  "properties": {
    "contract_id": { "type": "string" },
    "output_mode": {
      "enum": [
        "exam_prep_notes_docx",
        "knowledge_walkthrough_docx",
        "mcq_exam_prep",
        "short_answer_exam_prep",
        "long_answer_project_scenario_prep",
        "essay_exam_prep"
      ]
    },
    "allowed_visible_fields": { "type": "array", "items": { "type": "string" } },
    "forbidden_visible_fields": {
      "type": "array",
      "items": {
        "enum": [
          "source_anchor",
          "confidence",
          "evidence",
          "examiner_operation",
          "discriminator_axis",
          "practice_mcq",
          "answer_key",
          "contrast_table",
          "separate_trap_bank",
          "mark_producing_schema",
          "required_terms",
          "optional_examples",
          "reference_expansion",
          "common_omissions",
          "task_verb",
          "recurrence_count",
          "lecture_centrality",
          "prediction_score",
          "assessment_timing",
          "mark_split",
          "current_regime",
          "older_papers",
          "no_mark_scheme",
          "coverage_note",
          "source_coverage",
          "extraction_quality",
          "exam_specificity",
          "core_exam_claim",
          "exam_use",
          "common_error_or_trap",
          "must_master"
        ]
      }
    },
    "exam_prep_notes_student_contract": {
      "type": "object",
      "properties": {
        "public_lecture_sections": {
          "type": "array",
          "items": { "$ref": "#/properties/public_lecture_section" }
        }
      },
      "additionalProperties": false
    },
    "public_lecture_section": {
      "type": "object",
      "required": ["lecture_title", "modules"],
      "properties": {
        "lecture_title": { "type": "string" },
        "lecture_scope": { "type": "string" },
        "modules": { "type": "array", "items": { "$ref": "#/properties/public_lecture_module" } }
      },
      "additionalProperties": false
    },
    "public_lecture_module": {
      "type": "object",
      "required": ["module_title", "knowledge_functions", "explanation", "blocks"],
      "properties": {
        "module_title": { "type": "string" },
        "knowledge_functions": {
          "type": "array",
          "minItems": 2,
          "items": {
            "enum": [
              "definition_boundary",
              "mechanism_process",
              "method_readout",
              "graph_data_interpretation",
              "calculation_unit_worked_example",
              "named_example",
              "limitation_trap"
            ]
          }
        },
        "explanation": { "type": "string" },
        "blocks": { "type": "array", "items": { "$ref": "#/properties/public_point_block" } }
      },
      "additionalProperties": false
    },
    "public_point_block": {
      "type": "object",
      "required": ["block_type", "content"],
      "properties": {
        "block_type": {
          "enum": [
            "definition",
            "mechanism",
            "method",
            "graph_data",
            "calculation",
            "example",
            "limitation",
            "comparison",
            "table",
            "explanation"
          ]
        },
        "label": { "type": "string" },
        "content": {
          "anyOf": [
            { "type": "string" },
            { "type": "array", "items": { "type": "string" } }
          ]
        }
      },
      "additionalProperties": false
    },
    "mcq_student_point_card": {
      "type": "object",
      "properties": {
        "priority": { "enum": ["★★★", "★★", "★"] },
        "point": { "type": "string" },
        "knowledge_explanation": { "type": "string" },
        "how_exam_tests_it": { "type": "string" },
        "common_traps": { "type": "array", "items": { "type": "string" } },
        "must_remember": { "type": "string" }
      },
      "additionalProperties": false
    },
    "short_answer_point_card": {
      "type": "object",
      "properties": {
        "priority": { "enum": ["★★★", "★★", "★"] },
        "point": { "type": "string" },
        "common_question_form": { "type": "string" },
        "exam_explanation_with_highlighted_keywords": { "type": "string" },
        "example_answer": { "type": "string" }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__unit_example_contribution.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/unit_example_contribution.schema.json",
  "title": "UnitExampleContribution",
  "type": "object",
  "required": [
    "contribution_id",
    "source_unit",
    "source_materials",
    "observed_unit_pattern",
    "generic_skill_contribution",
    "transferable_rule",
    "future_unit_diagnostic_questions",
    "non_transferable_content",
    "affected_workflows",
    "anti_patterns_prevented",
    "validation_checks"
  ],
  "properties": {
    "object_type": { "const": "UnitExampleContribution" },
    "contribution_id": { "type": "string" },
    "source_unit": { "type": "string" },
    "source_materials": { "type": "array", "items": { "type": "string" } },
    "analysis_context": { "$ref": "analysis_context.schema.json" },
    "observed_unit_pattern": { "type": "string" },
    "generic_skill_contribution": { "type": "string" },
    "transferable_rule": { "type": "string" },
    "future_unit_diagnostic_questions": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "non_transferable_content": { "type": "array", "items": { "type": "string" } },
    "affected_workflows": {
      "type": "array",
      "items": {
        "enum": [
          "routing",
          "evidence_policy",
          "source_coverage",
          "exam_prep_notes",
          "knowledge_walkthrough",
          "mcq_exam_prep",
          "short_answer_exam_prep",
          "long_answer_project_scenario_prep",
          "essay_exam_prep",
          "student_surface",
          "scientific_precision",
          "docx_formatting",
          "release_qa"
        ]
      }
    },
    "anti_patterns_prevented": { "type": "array", "items": { "type": "string" } },
    "validation_checks": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "production_trigger_terms_forbidden": { "type": "boolean", "const": true },
    "qa_status": { "enum": ["pass", "warn", "fail", "not_run"] }
  },
  "additionalProperties": false
}

---

## Source File: `schemas__user_constraint.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/user_constraint.schema.json",
  "title": "UserConstraint",
  "type": "object",
  "required": ["constraint_id", "request_id", "time_budget_or_gap", "preferred_output_depth", "requested_artifacts", "allowed_audit_package", "deadline_or_gap"],
  "properties": {
    "object_type": { "const": "UserConstraint" },
    "constraint_id": { "type": "string" },
    "request_id": { "type": "string" },
    "time_budget_or_gap": { "type": ["string", "null"] },
    "preferred_output_depth": { "type": ["string", "null"] },
    "requested_artifacts": { "type": "array", "items": { "type": "string" } },
    "allowed_audit_package": { "type": "boolean" },
    "deadline_or_gap": { "type": ["string", "null"] }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__user_exam_prep_request.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/user_exam_prep_request.schema.json",
  "title": "UserExamPrepRequest",
  "type": "object",
  "required": ["request_id", "raw_request", "requested_mode", "language", "target_group_or_gap", "focus_areas", "source_policy", "user_provided_sources", "academic_integrity_status"],
  "properties": {
    "object_type": { "const": "UserExamPrepRequest" },
    "request_id": { "type": "string" },
    "raw_request": { "type": "string" },
    "requested_mode": { "type": "string" },
    "language": { "type": "string" },
    "target_group_or_gap": { "type": ["string", "null"] },
    "focus_areas": { "type": "array", "items": { "type": "string" } },
    "source_policy": { "type": "string" },
    "user_provided_sources": { "type": "array" },
    "academic_integrity_status": { "type": "string" }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__visual_aid_spec.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/visual_aid_spec.schema.json",
  "title": "VisualAidSpec",
  "type": "object",
  "required": [
    "visual_aid_id",
    "kp_id",
    "aid_type",
    "source_backed_claims",
    "visual_elements",
    "caption",
    "alt_text",
    "generation_prompt",
    "forbidden_elements",
    "qa_flags"
  ],
  "properties": {
    "visual_aid_id": { "type": "string" },
    "kp_id": { "type": "string" },
    "aid_type": {
      "enum": [
        "mechanism_pathway",
        "process_sequence",
        "spatial_relation",
        "comparison_framework",
        "method_workflow",
        "data_interpretation_logic"
      ]
    },
    "source_backed_claims": { "type": "array", "items": { "type": "string" } },
    "visual_elements": { "type": "array", "items": { "type": "string" } },
    "caption": { "type": "string" },
    "alt_text": { "type": "string" },
    "generation_prompt": { "type": "string" },
    "forbidden_elements": { "type": "array", "items": { "type": "string" } },
    "qa_flags": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__workflow_action.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/workflow_action.schema.json",
  "title": "WorkflowAction",
  "type": "object",
  "required": [
    "action_id",
    "action_type",
    "module",
    "depends_on",
    "minimum_inputs",
    "expected_outputs",
    "can_reuse_existing",
    "skip_reason",
    "qa_gate"
  ],
  "properties": {
    "action_id": { "type": "string", "minLength": 1 },
    "action_type": { "type": "string", "minLength": 1 },
    "module": { "type": "string", "minLength": 1 },
    "depends_on": { "type": "array", "items": { "type": "string" } },
    "minimum_inputs": { "type": "array", "items": { "type": "string" } },
    "expected_outputs": { "type": "array", "items": { "type": "string" } },
    "can_reuse_existing": { "type": "boolean" },
    "skip_reason": { "type": ["string", "null"] },
    "qa_gate": {
      "type": "object",
      "required": ["gate_name", "required"],
      "properties": {
        "gate_name": { "type": "string" },
        "required": { "type": "boolean" },
        "checks": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": true
}

---

## Source File: `schemas__workflow_plan.schema.json`

---

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.invalid/everything-exam-preparation/workflow_plan.schema.json",
  "title": "WorkflowPlan",
  "type": "object",
  "required": [
    "object_type",
    "plan_id",
    "request_scope",
    "selected_preset",
    "target_group_key",
    "source_inventory_required",
    "fragment_index_required",
    "actions",
    "skipped_modules",
    "blockers",
    "publish_gate"
  ],
  "properties": {
    "object_type": { "const": "WorkflowPlan" },
    "plan_id": { "type": "string", "minLength": 1 },
    "request_scope": {
      "type": "object",
      "required": ["raw_mode", "normalized_preset", "student_visible_only"],
      "properties": {
        "raw_mode": { "type": "string" },
        "normalized_preset": { "type": "string" },
        "student_visible_only": { "type": "boolean" },
        "include_audit_package": { "type": "boolean" },
        "requested_artifacts": { "type": "array", "items": { "type": "string" } }
      },
      "additionalProperties": true
    },
    "selected_preset": {
      "enum": [
        "source_inventory_only",
        "exam_format_diagnosis",
        "exam_prep_notes_docx",
        "knowledge_walkthrough_docx",
        "mcq_exam_prep",
        "short_answer_exam_prep",
        "long_answer_project_scenario_prep",
        "essay_exam_prep",
        "audit_lint_only",
        "github_ready_qa"
      ]
    },
    "target_group_key": { "type": "string", "minLength": 1 },
    "source_inventory_required": { "type": "boolean" },
    "fragment_index_required": { "type": "boolean" },
    "actions": {
      "type": "array",
      "items": { "$ref": "workflow_action.schema.json" }
    },
    "skipped_modules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["module", "reason"],
        "properties": {
          "module": { "type": "string" },
          "reason": { "type": "string" }
        },
        "additionalProperties": true
      }
    },
    "blockers": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["blocker_id", "severity", "missing_input", "resolution_prompt"],
        "properties": {
          "blocker_id": { "type": "string" },
          "severity": { "enum": ["blocking", "warning", "info"] },
          "missing_input": { "type": "string" },
          "resolution_prompt": { "type": "string" },
          "blocked_modules": { "type": "array", "items": { "type": "string" } }
        },
        "additionalProperties": true
      }
    },
    "publish_gate": {
      "type": "object",
      "required": ["object_validation", "lineage_required", "qa_required"],
      "properties": {
        "object_validation": { "type": "boolean" },
        "lineage_required": { "type": "boolean" },
        "qa_required": { "type": "boolean" },
        "strict_publish_gate": { "type": "boolean" },
        "fail_on_blocking_flags": { "type": "boolean" }
      },
      "additionalProperties": true
    }
  },
  "additionalProperties": true
}

---

## Source File: `skill_manifest.json`

---

{
  "schema_version": 1,
  "skill_id": "everything-exam-preparation",
  "repo": "OctavianYimingZhang/Everything-Exam-Preparation",
  "branch": "main",
  "entrypoint": "SKILL.md",
  "health_commands": [
    "python3 -m compileall -q scripts",
    "python3 scripts/no_identity_trigger_linter.py --forbid-legacy-label",
    "python3 scripts/validate_workflow_planning_contract.py",
    "python3 scripts/example_transfer_linter.py tests/fixtures/example_learning/valid_example_review_ledger.json",
    "python3 scripts/validate_interaction_contract.py",
    "python3 scripts/validate_student_output_contract.py",
    "python3 scripts/notes_exam_ready_language_linter.py --self-test",
    "python3 scripts/module_teaching_depth_linter.py --self-test",
    "python3 scripts/notes_readability_layout_linter.py --self-test",
    "python3 scripts/source_information_profiler.py --self-test",
    "python3 scripts/source_scale_budget_linter.py --self-test",
    "python3 scripts/reference_density_linter.py --self-test",
    "python3 scripts/zero_mention_lint.py --self-test",
    "python3 scripts/knowledge_surface_linter.py --self-test",
    "python3 scripts/scientific_precision_linter.py --self-test",
    "python3 scripts/github_ready_check.py --ci"
  ],
  "post_update_commands": [
    "python3 -m pip install -r requirements.txt"
  ]
}
