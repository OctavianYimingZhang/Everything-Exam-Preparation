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
7. Explain each module in connected prose.
8. Keep question-type overlays separate unless explicitly requested.
9. Run surface, density, noise and layout QA.
```

The model must not be forced to write from slide fragments. The model should use source order to understand prerequisites and teaching sequence, then organise the output by exam-useful conceptual logic.

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

The `explanation` must be a connected paragraph or a short sequence of explanatory paragraphs. It must answer the useful questions: what is this, why does it work, how does the mechanism/calculation/experiment proceed, and what follows from it.

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
