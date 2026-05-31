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
5. Reconstruct the course into modules.
6. Build enough examinable knowledge units for the source scale.
7. Explain each unit in connected prose.
8. Add question-type overlays only after the knowledge is clear.
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

Use any supplied high-quality DOCX only as a calibration exemplar for density, layout and paragraph style. The Experimental Biology exemplar demonstrates the target public surface: topic-specific headings, explanatory paragraphs, calculation detail when needed, 2.0 cm margins, black Arial text, 1.5 spacing, left-aligned headings and justified body text. It must not supply factual claims for another course and must not cap larger outputs.

Before drafting, create an internal budget:

```yaml
SourceScaleBudget:
  source_units_count:
  source_pages_or_slides_estimate:
  source_types:
  conceptual_module_target_range:
  examinable_unit_target_range:
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
- Do not use page count alone. Increase coverage when the source contains distinct mechanisms, methods, calculations, disease examples, pathways, data operations, or named experimental evidence.
- If source material is large but the output is short, record a `coverage_floor_failure` and regenerate from the distillation pass.
- If the public draft reads like a workflow explanation, file inventory, source-role report, or high-level revision guide rather than a knowledge document, it fails even if the word count is high.

Indicative internal floors, to be adapted by evidence density:

- 1-3 source units: usually 8-20 examinable units.
- 4-8 source units: usually 20-45 examinable units.
- 9-15 source units: usually 40-80 examinable units.
- 16+ source units or whole-course packs: usually 70+ examinable units or multiple deliverable volumes.

These are not student-visible promises. They prevent accidental over-compression.

## Course Reconstruction

Before writing, reconstruct a compact course map:

```yaml
CourseModule:
  module_title:
  module_function:
  source_lectures:
  core_questions:
  examinable_units:
```

A course map should normally contain conceptual modules, not one line per uploaded slide deck. It should say what the course teaches, not list every file title. For broad courses, use as many conceptual modules as needed to preserve the main knowledge areas; do not force every course into 4-10 modules if that hides content.

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
Course Knowledge Map
Module 1: topic-specific module heading
  connected notes
Module 2: topic-specific module heading
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
Selected route
Workflow plan
Source scale budget
Coverage floor status
Generation process
```

## QA Gate

Fail and rewrite if any of these are true:

- the output is much shorter than the source scale budget without a defensible compression reason;
- more than a small minority of visible lines are copied slide bullets;
- the output contains course admin or staff/contact/logistics text;
- the course map is mostly a list of file titles;
- a section is mostly names without explanations;
- labels and bullets replace connected explanation;
- the model preserved broken OCR instead of reconstructing meaning;
- figures create large blank areas without improving readability;
- add-on exam analysis appears before the knowledge has been made clear.
