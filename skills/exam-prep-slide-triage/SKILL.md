---
name: exam-prep-slide-triage
description: Internal material-analysis Skill for Exam Prep Notes. Use before Notes generation when lecture slides, slide-like PDFs, or PPTX files need page-by-page filtering so non-teaching slides are excluded from detailed explanation while structure, ILO, summary, visual, example, and substantive knowledge slides still support lecture-unit coverage.
---

# Exam Prep Slide Triage

Use this Skill inside the Everything Exam Prep multiple Skill system before generating Exam Prep Notes from slides or slide-like PDFs.

## Core Purpose

Decide whether each slide should be used, merged into the previous knowledge unit, or excluded from Notes analysis. This is not a detail-level grading system. The goal is to stop public Notes from explaining non-knowledge slides in detail while still preserving useful lecture structure.

Slide triage serves Notes material analysis only. It must not narrow MCQ, Short Answer, Long Answer, Worked Solutions, Essay, Question Solving, or Question Organization Specific Research Reports.

## Internal Output

For each slide-like fragment, keep these internal fields:

- `slide_decision`: `use`, `merge_with_previous`, or `exclude`.
- `notes_role`: `knowledge_source`, `structure_marker`, `visual_or_data_support`, `example_or_summary_support`, or `non_teaching_material`.
- `detailed_explanation_allowed`: boolean.
- `triage_reason`: short internal reason.
- provenance: source name, lecture order, slide or page number, likely slide title.

`slide_decision` is about whether the slide should guide Notes coverage. `detailed_explanation_allowed` is about whether the Notes may explain the slide content at length.

## Decision Rules

Use `use` with `notes_role: knowledge_source` and `detailed_explanation_allowed: true` when a slide teaches substantive course knowledge: definitions, concepts, mechanisms, pathways, methods, assays, comparisons, formulae, calculations, direct graph interpretation, direct data interpretation, or conceptual applications.

Use `use` with `detailed_explanation_allowed: false` when a slide is useful for structure but should not be explained at length: intended learning outcomes, agenda, topic boundary, section divider, summary, conclusion, and high-level recap slides. These slides help split topics, preserve lecture order, and audit coverage.

Use `use` with `notes_role: visual_or_data_support` when a visual, table, graph, pathway, scheme, image, or dataset clarifies a nearby knowledge unit. Allow detailed explanation only when the slide itself requires interpretation or teaches a method, mechanism, calculation, or data conclusion.

Use `merge_with_previous` when a slide continues the previous idea, repeats an example, gives a supporting case, or contains a visual or summary that should support the previous knowledge unit without becoming its own Notes section.

Use `exclude` with `notes_role: non_teaching_material` when a slide is administrative, empty, decorative, copyright/license/source-credit material, a reading list or textbook reference without teaching content, a pure transition page with no topic signal, a duplicate with no new knowledge, or generic awareness/social framing that does not explain course knowledge.

## Notes Boundary

Keep ILOs, topic boundaries, non-core visuals, non-essential data, examples, and summary slides available to the Notes generator as structure and coverage evidence. Do not turn them into long public explanations unless they contain substantive knowledge signals.

Excluded slides remain in the internal `slide_triage_audit`. They should not become public Notes sections, detailed paragraphs, visual explanations, or exam-priority claims.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before any public Notes output. This Skill may produce internal slide-triage records, but public Notes generation still needs confirmed Material type/source roles and Notes choice.
