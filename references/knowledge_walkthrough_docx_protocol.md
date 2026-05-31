# Knowledge Walkthrough DOCX Protocol

`knowledge_walkthrough_docx` is the compatibility route when the user explicitly asks to go through lecture knowledge in source order. It produces the same public artifact name:

```text
Lecture_Knowledge_Walkthrough.docx
```

The route is lecture-aware, not slide-dump based. Source order can help preserve prerequisites and teaching logic, but the public document must still be a knowledge explanation, not a page-by-page extraction log.

## Purpose

The student opens this Word file to understand the main knowledge in lecture order. A valid walkthrough should explain what each concept is, why it matters, how the relevant mechanism, method, pathway, calculation or experiment works, and what consequence, limitation or interpretation follows.

The route is not:

- a slide/page paraphrase;
- an audit of uploaded files;
- a source inventory;
- a prediction file;
- an essay package by default;
- a place for course administration, staff details, attendance instructions, platform links or raw extraction text.

## Route Pipeline

```text
SourceRoleMap
-> NonKnowledgeNoiseFilter
-> SourceScaleBudget
-> lecture-order conceptual reconstruction
-> ExaminableKnowledgeUnitPlan
-> connected explanation drafting
-> KnowledgeSurfaceContract / NonKnowledgeGate
-> DOCX layout QA
```

The important change is that `SourceScaleBudget` comes before drafting. A large lecture pack must not be collapsed into a short practical-style summary. A small practical pack can be concise, but a full-course pack needs enough modules and examinable units to cover the source scale.

## Source Scale Budget

Before writing, estimate:

```yaml
SourceScaleBudget:
  source_units_count:
  source_pages_or_slides_estimate:
  readable_source_blocks:
  protected_knowledge_units_total:
  excluded_non_knowledge_units_total:
  target_public_units_min:
  target_words_min:
  compression_mode: explain_not_dump
  coverage_floor_status: pass | warn | block
```

Rules:

- Use more public knowledge units when the source contains more lectures, mechanisms, figures, methods, calculations, pathways, examples or named evidence.
- Do not use a short Experimental Biology-style practical output as the size cap for larger units.
- Keep conceptual grouping, but place multiple examinable units inside each module.
- `source_pages_or_slides_estimate` must drive the minimum size when it is larger than the lecture count. Large course decks should not be allowed to declare a small `target_words_min`: 201-500 slides/pages usually needs at least 105 public units and about 14k visible words; 501-800 needs at least 150 public units and about 20k visible words; 801+ needs at least 180 public units and about 25k visible words or multiple volumes.
- If the output is much shorter than the source scale budget, regenerate from source distillation.

## Student-Facing Structure

Use this public structure:

```text
Title
Course Knowledge Map
Lecture or module heading when source order helps
[★★★ | ★★ | ★] Topic-specific knowledge heading
Connected explanatory prose
Optional equation / worked example / diagnostic pattern / comparison / table when useful
```

The Course Knowledge Map must be conceptual. It must not be a list of filenames, lecture deck names, source titles or upload inventory.

Forbidden visible structures include:

```text
How To Use This Document
What This Lecture Is About
What This Module Explains
Knowledge Walkthrough
Key Logic
Knowledge Points
Must Master
Lecture Recap
Source Coverage
Evidence Used
Extraction Quality
```

If a legacy plan contains these fields, merge real knowledge into the nearest explanatory unit and discard the scaffold label.

## Examinable Knowledge Units

Each visible unit should be one coherent explanation:

```yaml
ExaminableKnowledgeUnit:
  title:
  priority: high | medium | low
  source_support:
  explanation:
  optional_equation_or_example:
  common_confusion_or_boundary:
```

The explanation must be a connected paragraph or a short set of connected paragraphs. It should not be a raw list of slide bullets. It should not be broken into repeated slot labels such as:

```text
Definition:
Components:
Workflow:
Logic:
Interpretation:
Graph logic:
```

Bullets are allowed only when the source content is naturally parallel, such as equation variables, ordered method steps, diagnostic patterns, receptor classes, ion-channel subfamilies or comparison rows. A bullet list needs an explanatory lead sentence.

## Non-Knowledge Removal

Remove these from public output:

- lecturer names, emails, phone numbers, office locations, contributor lists and staff biographies;
- Unit Attendance, SEAtS, Mentimeter, QR codes, room schedules, Blackboard/SoftChalk instructions and live-session logistics;
- assessment percentages, exam dates, mark splits and closed-book logistics unless the user asks for a separate exam-analysis brief;
- library availability, bookshop adverts, URL-only lines, image credits, copyright lines, figure filenames, raw font names and page artefacts;
- decorative quotes, acknowledgements, lecture agenda slides and generic ILOs unless rewritten into specific examinable knowledge;
- public AI provenance, source-route narration, QA flags, evidence scores, confidence bands, manifests and helper JSON.

## Layout Contract

Use the ordinary notes/walkthrough layout:

```yaml
RouteDocxStyleProfile:
  route: knowledge_walkthrough_docx
  margin_cm: 2.0
  line_spacing: 1.5
  body_alignment: justified
  title_alignment: left
  heading_alignment: left
  image_alignment: center
  body_font_pt: 10.5
  heading_font_pt: 12
  text_color: black
  theme_colours_allowed: false
  blue_heading_styles_allowed: false
```

This route must not use inherited Word theme colours or light-blue heading styles. Run the layout normalizer if the generated DOCX inherits coloured heading styles from Word defaults.

## Visuals

Figures are included only when they help explain a knowledge point. They must be centered and scaled to the available content area while preserving readability. Avoid large blank areas by fitting images to nearby explanatory content and avoiding unnecessary page breaks.

## QA Gate

Block and regenerate if any of these appear:

- source-scale coverage floor failure;
- file-title Course Knowledge Map;
- raw slide bullets copied line-by-line;
- course administration, staff/contact/logistics or platform text;
- old scaffold headings such as `What This Lecture Is About` or `Knowledge Points`;
- dense repeated label fragments;
- shorthand arrow chains used as the main explanation;
- non-black visible text, theme-colour headings, blue text, non-Arial text, wrong alignment or non-1.5 line spacing;
- source-route narration such as `this slide shows` or `the notes say`.

When QA fails, regenerate from the distilled knowledge units rather than patching the final DOCX by deleting a few bad lines.
