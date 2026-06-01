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
