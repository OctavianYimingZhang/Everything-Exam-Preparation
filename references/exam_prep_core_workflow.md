# Exam Prep Core Workflow

This is the only canonical protocol for default Exam Preparation Notes and lecture-first public DOCX output.

## Purpose

Default route: `exam_prep_notes_docx`. Compatibility source-order route: `knowledge_walkthrough_docx`. Both produce the same public artifact:

```text
Lecture_Knowledge_Walkthrough.docx
```

The output is lecture-first, knowledge-only, source-backed, and source-adaptive. It is not an audit report, strategy report, prediction report, source inventory, slide dump, or fixed-length summary.

## Pipeline

```text
SourceRoleMap
-> NonKnowledgeNoiseFilter
-> SourceDistillationPass
-> LectureSessionMap
-> SourceScaleBudget
-> AtomicKnowledgeLedger
-> ProtectedSourceUnit coverage floor
-> PublicLectureNotesPlan
-> KnowledgeSurfaceContract / NonKnowledgeGate
-> ExamReadyDirectProsePass
-> PublicModuleDepthPass
-> ReadabilityLayoutPass
-> RouteStyleRenderer
-> Deliverable QA
```

Use `SourceScaleBudget`, `coverage_floor`, `source_units_count`, `minimum_visible_coverage_floor`, and protected source coverage to prevent broad source packs from being compressed into shallow notes. Use `ExaminableKnowledgeUnit` internally to preserve definitions, contrast pairs, criteria, named examples, calculations, graphs, methods, assays, diagrams, tables, and limitations.

## Public Plan

The public plan is `PublicLectureNotesPlan` in `schemas/public_lecture_notes_plan.schema.json`. It must contain `public_lecture_sections`, module-level `knowledge_functions`, `output_language_profile`, and `route_docx_style_profile`. The route field is either `exam_prep_notes_docx` or `knowledge_walkthrough_docx`.

Each module must be a micro-module with connected explanation. It should answer: what the concept/method is, how it works, how to read or use it, what calculation or decision follows, and what mistake or limitation it prevents when the source supports that information.

## Student Surface

Student-facing notes must contain knowledge only. Public text may define, explain mechanisms, describe processes, give source-backed examples, interpret data, state limitations, compare concepts, show calculations, or synthesize related points. Public text must not expose source_route_narration, ai_process_or_provenance, audit trace, generic study advice, exam-prediction trace, rigid_template_bucket, colon-slot fragmentation, shorthand arrow chains, source maps, source anchors, confidence, evidence scores, examiner operations, discriminator axes, practice MCQs, answer keys, contrast tables, mark-producing schema, reference expansion, exam_specificity, core_exam_claim, exam_use, common_error_or_trap, or must_master fields.

Forbidden student-visible field identifiers are: `source_anchor`, `source_anchors`, `confidence`, `evidence`, `examiner_operation`, `discriminator_axis`, `practice_mcq`, `answer_key`, `contrast_table`, `separate_trap_bank`, `mark_producing_schema`, `reference_expansion`, `exam_specificity`, `core_exam_claim`, `exam_use`, `common_error_or_trap`, and `must_master`. The readability layout gate must run before release.

Use `LabelDecision` / `SurfaceLabelDecision` with `semantic_sparse` labels only when a heading improves reading. Avoid raw slide bullets. Use exam-ready direct prose and module teaching depth. Remove source narration such as `the slide says`, `the source material identifies`, or `the course frames`.

## DOCX Style

Public notes use black Arial, 2.0 cm margins, compact 1.05-1.15 line spacing, left-aligned title, headings and body, centered images, no theme colours, and no blue heading styles. Example Essay DOCX uses separate essay formatting in `references/essay_exam_prep_protocol.md`.

## Add-ons

MCQ, Short Answer, Long Answer, Practical/Data, and Essay outputs are add-ons. They must not damage the core source baseline or replace the notes with exam strategy. Add-ons are governed by `references/exam_mode_and_addons_protocol.md` and `references/essay_exam_prep_protocol.md`.
