# Exam Prep Notes Protocol

`exam_prep_notes_docx` is the default route when the user supplies course materials and asks for revision, notes, general exam preparation, or to go through the material without naming a narrower artifact. It produces the compatible public Word artifact:

```text
Lecture_Knowledge_Walkthrough.docx
```

The route is a synthesis route, not an extraction route. Its job is to turn source material into clear examinable knowledge. It must not preserve every slide heading, file title, raw bullet, administrative line, or OCR fragment.

## Route Purpose

The public document should help a student understand the course. It should answer:

- what the concept, method, process, structure or calculation is;
- why it works;
- how the mechanism, experiment, graph, assay or calculation proceeds;
- what readout, consequence, limitation or application follows.

Question-type reports are add-ons. They come after the core knowledge walkthrough is clear.

## First-Principles Pipeline

Run this route in the following order:

```text
SourceRoleMap
-> NonKnowledgeNoiseFilter
-> SourceDistillationPass
-> ConceptualCourseMap
-> ExaminableKnowledgeUnitPlan
-> ConnectedExplanationDraft
-> KnowledgeSurfaceContract / NonKnowledgeGate
-> optional question-type overlay
-> DOCX layout QA
```

Do not let `AtomicKnowledgeLedger`, source coverage, or past-paper emphasis become the public generation driver. Those tools may protect important concepts internally, but they must not force raw slide text into the final DOCX.

## Source Role Map

Every source block must be classified before drafting:

- `subject_knowledge`: definitions, mechanisms, structures, pathways, experiments, methods, calculations, graphs, data patterns, examples, diagnostic rules and limitations.
- `practical_operation`: apparatus, reagents, protocol logic, controls, safety handling, calculations and interpretation rules.
- `exam_pattern`: question form, command verbs, mark operations and recurring discriminators.
- `extra_reading`: verified books, chapters, papers or academic sources that deepen source logic.
- `style_or_layout_example`: reference output used only for structure, density and layout.
- `non_knowledge_noise`: admin, logistics, contact details, attendance systems, URLs, decorative text, OCR debris, file titles and slide artifacts.

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` may become public prose. Past papers shape emphasis and overlays only. Cross-target examples cannot support factual claims for the current course.

## NonKnowledgeNoiseFilter

Remove these before notes are planned:

- lecturer names, emails, phone numbers, office locations, staff lists, unit coordinator details and contributor lists;
- attendance apps, QR codes, room instructions, timetable lines, live-session instructions, platform instructions and links;
- assessment logistics unless the user explicitly requests a separate exam-analysis brief;
- bookshop adverts, library availability lines, URL-only lines, image credits, copyright lines, acknowledgements and decorative quotations;
- slide agendas, contents pages, generic learning outcomes and generic advice unless rewritten into a specific knowledge claim;
- raw slide bullets, duplicated headings, font dumps, page artifacts and extraction debris;
- OCR fragments that do not form a biological, chemical, clinical, mathematical or methodological claim.

If a block contains both knowledge and noise, extract the knowledge claim and discard the noise. Do not copy the block.

## SourceDistillationPass

The source distillation pass rewrites source material into candidate knowledge claims before any public notes are drafted.

For each source lecture, practical, paper or notes block, make internal records of:

```yaml
DistilledKnowledgeCandidate:
  concept:
  function:
  source_support:
  keep_reason:
  discard_reason_if_any:
  merge_with:
  public_unit_candidate: true | false
```

Rules:

- Keep central definitions, distinctions, causal mechanisms, process order, evidence, formulas, units, worked calculations, method logic, interpretation rules and named examples that teach a reusable concept.
- Merge adjacent source fragments when they explain the same concept. For example, a method principle, readout and limitation normally belong in one explanatory unit, not three isolated labels.
- Drop headings that are only source navigation, such as `Introduction`, `Contents`, `Today`, `Summary`, `Part 1`, `Next module`, or file names.
- Convert vague source headings into concept-specific headings. Example: `Lecture 1` is not a public heading; `Internal membranes create organelle-specific chemical environments` can be.
- Never write the public notes directly from extracted bullet text.

## Conceptual Course Map

The `Course Knowledge Map` must be conceptual, not a file list. It should normally contain 4-10 course modules for a broad source pack.

Allowed map form:

```text
The course is organised around membrane structure, transport energetics, signalling, trafficking and disease/application logic.
```

Forbidden map form:

```text
Core knowledge spans Lecture 1; Lecture 2; slides.pptx; Module 3.pdf; practical handout; source file name...
```

A public map may mention source lectures only inside a compact lecture/topic mapping when this helps orientation. It must not be the main knowledge map.

## CourseModule

Construct modules by conceptual function:

```yaml
CourseModule:
  module_title:
  module_function:
  source_lectures:
  core_questions:
  examinable_units:
```

A module title should name the knowledge problem, not the source file. Good examples:

```text
Lipid bilayers create selective permeability and compartment identity
Electrochemical gradients combine concentration and voltage
Taste receptor identity determines signalling pathway and labelled-line coding
```

Bad examples:

```text
Lecture 1
Module 02
1.3 Tools and Techniques
Postlab ANSWERS
```

## ExaminableKnowledgeUnit

Public content must be written as coherent units:

```yaml
ExaminableKnowledgeUnit:
  title:
  priority: high | medium | low
  source_support:
  explanation:
  optional_equation_or_example:
  common_confusion_or_boundary:
```

The visible unit should be a topic-specific heading followed by connected prose. It must not be a slot list. It should normally explain what the point is, why it works, how the mechanism or calculation proceeds, and what follows from it.

Do not write units as:

```text
Definition: ...
Components: ...
Workflow: ...
Logic: ...
Interpretation: ...
```

Use bullets only when the items are naturally parallel, such as formula variables, ordered workflow steps or a real comparison table. A bullet list must have an explanatory lead sentence and should not replace the explanation.

## Density And Compression

The route should be selective. The goal is high-information explanation, not maximum line count.

- A broad first-year course should not create hundreds of tiny visible points.
- A short practical unit may need fewer but deeper units.
- A method/calculation unit should keep formula, units and worked example together.
- A mechanism unit should keep cause, process, evidence and consequence together.
- A disease/drug/example unit should include only details that teach the reusable concept.

Fail if the output looks like copied extraction text with `★★` headings before nearly every slide heading.

## Question-Type Overlay

After the core walkthrough is clear, add the requested or useful overlay:

- MCQ: discriminator rules and compact trap distinctions.
- Short answer: concise model answers and mark-producing terms.
- Long answer / practical / data / project / scenario: method-readout-control-limitation logic and worked examples.
- Essay: plans or full Example Essays only when essay mode is requested. `EssayAdaptiveBudget` controls length.

The overlay must not replace baseline knowledge and must not expose source-route narration, examiner-operation fields, recurrence counts, confidence bands or prediction scores.

## Public DOCX Structure

Default structure:

```text
Title
Course Knowledge Map
Module 1: concept-specific heading
  connected explanatory units
Module 2: concept-specific heading
  connected explanatory units
...
```

Do not render sections named `How To Use This Document`, `What This Lecture Is About`, `What This Module Explains`, `Core Exam Claim`, `Exam Specificity`, `Exam Use`, `Common Error / Trap`, `Must Master`, `Source Coverage`, `Evidence Used`, `Extraction Quality` or equivalent internal fields.

Use `SurfaceLabelDecision`, `LabelDecision` and `semantic_sparse` label policy: labels are kept only when they improve readability for equations, worked examples, diagnostic patterns, controls, comparisons or tables. Otherwise merge the label into the heading or prose. This prevents `colon-slot fragmentation` and `shorthand arrow chains` from becoming the visible document style.

## Public DOCX Layout

For ordinary notes:

```yaml
RouteDocxStyleProfile:
  route: exam_prep_notes_docx
  margin_cm: 2.0
  line_spacing: 1.5
  body_alignment: justified
  title_alignment: left
  heading_alignment: left
  image_alignment: center
  body_font_pt: 10.5
  heading_font_pt: 12
  text_color: black
```

Images must be centered and scaled to the content area while preserving readability. Avoid large blank areas and unnecessary page breaks.

## KnowledgeSurfaceContract

Before public rendering, apply the `KnowledgeSurfaceContract` and run the `NonKnowledgeGate`. Public notes must not contain:

- `source_route_narration`;
- `ai_process_or_provenance`;
- `rigid_template_bucket` headings;
- internal QA or audit fields;
- source maps, run manifests, lineage files or helper JSON;
- source file names as knowledge map content.

## QA Gate

Block and rewrite if any of these appear:

- `Core knowledge spans` followed by a source list;
- many visible sections beginning with source file names, `Lecture:`, `Module 01`, `slides`, `handout` or `presentation`;
- high density of `★★` headings that mirror slide headings;
- administrative, logistics, staff, contact, attendance, platform or assessment material;
- raw slide bullets, OCR fragments, font dumps, image credits or copyright debris;
- dense lists of names without mechanisms;
- repeated `Definition`, `Components`, `Workflow`, `Logic`, `Graph logic`, `Interpretation` or equivalent labels;
- shorthand arrow chains used as the main explanation;
- unsupported claims, fake citations or over-strong scientific claims;
- public AI-process text, source anchors, QA JSON, manifests or lineage files.

When the QA gate fails, regenerate from the `SourceDistillationPass`; do not patch the final DOCX by deleting a few bad lines.
