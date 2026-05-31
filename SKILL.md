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
-> reconstruct conceptual course modules
-> calculate source-adaptive coverage budget
-> select examinable knowledge units
-> write connected explanations
-> add optional question-type overlay
-> run public-surface, density and layout QA
```

The output should explain what each concept is, why it matters, how the mechanism, method or calculation works, and what result, limitation or interpretation follows.

## Source Roles

Before drafting, classify material as:

- `subject_knowledge`: definitions, mechanisms, structures, pathways, experiments, methods, calculations, graphs, data patterns, examples, diagnostic rules and limitations.
- `practical_operation`: apparatus, reagents, protocol logic, controls, safety handling, calculations and interpretation rules.
- `exam_pattern`: question form, command verbs, mark operations and repeated discriminators.
- `extra_reading`: verified books, chapters, papers or academic sources that deepen source logic.
- `style_or_layout_example`: reference output used only for structure, density and layout.
- `non_knowledge_noise`: admin, logistics, contact details, attendance systems, URLs, decorative text, OCR debris, file titles and slide artifacts.

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` may become public knowledge prose. Past papers shape emphasis and answer operations only. Cross-unit examples never provide facts for a new target unit.

## Noise Filter

Discard these from ordinary public notes:

- lecturer names, emails, phone numbers, office locations, staff lists and coordinator details;
- attendance systems, QR codes, live-session instructions, room or timetable instructions and platform instructions;
- assessment logistics unless the user asks for a separate exam-analysis brief;
- bookshop adverts, library availability, URL-only lines, image credits, copyright lines, acknowledgements and decorative quotations;
- slide agendas, contents pages, generic learning outcomes and generic advice unless rewritten into a specific knowledge claim;
- raw slide bullets, file-title lists, broken OCR fragments, font names, page artifacts and extraction debris.

A `Course Knowledge Map` must be conceptual. It should organise the course into major knowledge modules, not uploaded file names.

## Route Table

| User request | Route | Public output |
| --- | --- | --- |
| revise / make notes / go through lectures / general preparation | `exam_prep_notes_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| explicitly source-order walkthrough | `knowledge_walkthrough_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| MCQ / single-best-answer | `mcq_exam_prep` | core walkthrough plus MCQ add-on |
| short answer | `short_answer_exam_prep` | core walkthrough plus short-answer add-on |
| long answer / project / scenario / practical / data / calculation | `long_answer_project_scenario_prep` | core walkthrough plus long-answer/data add-on |
| essay preparation / full essay-style answers | `essay_exam_prep` | core walkthrough plus essay add-on |
| source inventory / lint / release check | `audit_lint_only` or `github_ready_qa` | QA result only |
| past-paper pattern or exam format only | `exam_analysis_brief` | chat-only brief unless a report is requested |

Essay and problem-essay prediction uses the label `Predicted essay theme` for a source-qualified theme, scope and practice angle. It must not present a predicted theme as official future question wording.

## Course Reconstruction

For broad source packs, build conceptual modules:

```yaml
CourseModule:
  module_title:
  module_function:
  source_lectures:
  core_questions:
  examinable_units:
```

Preserve source order when it explains prerequisites. Do not produce one public module per file if that only repeats file names.

## Source-Adaptive Coverage Budget

Never use the same small output size for every course. The amount of public knowledge must scale with the amount of examinable source material.

The reference-quality target is the supplied Experimental Biology style of output: topic-specific headings, dense connected explanations, formulas or worked examples when useful, black Arial text, 2.0 cm margins, 1.5 spacing, left-aligned headings and justified body prose. Use that file only as a style, density and layout exemplar; it is not factual evidence and it is not a length cap.

Before drafting, create:

```yaml
SourceScaleBudget:
  source_units_count:
  source_pages_or_slides_estimate:
  source_types:
  conceptual_module_target_range:
  examinable_unit_target_range:
  minimum_visible_coverage_floor:
  compression_reason:
  coverage_floor_status: pass | warn | block
```

Rules:

- A broad course pack must not be compressed to the size of a short practical or mock paper.
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
- If `target_public_units_min` or `target_words_min` is below the derived source-scale floor, the budget is invalid even if the draft is polished.
- If the first draft feels like a route summary, file inventory, checklist, or brief overview, it is not acceptable. Regenerate from the source-distillation pass until the public document teaches the examinable mechanisms, calculations, methods, examples, boundaries and interpretations in connected prose.
- If the public output falls below the source-scale floor, block the run and regenerate from source distillation instead of releasing a short file.

## Examinable Knowledge Units

Write public content as coherent units:

```yaml
ExaminableKnowledgeUnit:
  title:
  priority: high | medium | low
  source_support:
  explanation:
  optional_equation_or_example:
  common_confusion_or_boundary:
```

The visible unit is a topic-specific heading followed by connected explanatory prose. Bullets are allowed only after an explanatory lead sentence and only for naturally parallel items.

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

- body text is justified;
- titles, lecture headings and subheadings are left aligned;
- images are centered;
- default text line spacing is 1.5;
- text is black Arial in a readable size;
- theme colours, blue heading styles and non-black visible text are forbidden unless the user explicitly asks for colour;
- images are scaled to the content area while preserving aspect ratio and readability;
- large blank areas should be reduced by fitting images to context and avoiding unnecessary page breaks.

Public notes must not contain source-route narration, AI-process text, source maps, QA flags, evidence scores, confidence bands, internal manifests, helper JSON or raw extraction text.

Public notes must also not contain visible workflow explanations such as selected route, workflow plan, source role map, source scale budget, coverage floor status, KnowledgeSurfaceContract, ExaminableKnowledgeUnit, CourseModule, QA gate, generation process, or statements about what the Skill did. Keep those objects internal and render only the resulting knowledge.

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
- file-title course maps instead of conceptual course maps;
- raw slide bullets or broken OCR fragments;
- copied extraction text instead of explanation;
- dense lists of names without mechanisms;
- repeated `Definition`, `Components`, `Workflow`, `Logic`, `Graph logic` or equivalent labels;
- shorthand arrow chains used as the main explanation;
- a broad source pack compressed below the source-adaptive coverage floor;
- unsupported claims, fake citations or over-strong scientific claims;
- unbound protected source units;
- public AI-process text, source anchors, QA JSON, manifests or lineage files;
- non-black visible text, theme-colour headings, non-Arial text, wrong alignment or non-1.5 line spacing.

Targeted checks:

```bash
python3 scripts/no_identity_trigger_linter.py --forbid-legacy-label
python3 scripts/validate_workflow_planning_contract.py
python3 scripts/validate_interaction_contract.py
python3 scripts/validate_student_output_contract.py
python3 scripts/skill_architecture_linter.py --self-test
python3 scripts/zero_mention_lint.py --self-test
python3 scripts/knowledge_surface_linter.py --self-test
python3 scripts/scientific_precision_linter.py --self-test
python3 scripts/github_ready_check.py --ci
```
