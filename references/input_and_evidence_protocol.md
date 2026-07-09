# Input and Evidence Protocol

This Skill reads supplied files through rough source hints and open knowledge signals.

Source hints describe provenance and routing context. Notes coverage is calibrated from the knowledge signals and knowledge units found in the material.

Lecture files remain course-facing `knowledge_material` when they are named like lecture files, contain lecture titles, include ILOs or learning objectives, or show module-code lecture context. Textbook references, recommended reading, citations, or embedded book-source captions inside lecture slides do not by themselves turn the lecture file into `extra_reading_source`.

## Source Hints

Use source hints as open, coarse provenance labels. Treat the labels below as examples that can be expanded when the source context requires it:

- `knowledge_material`: course-facing explanation or teaching content.
- `practice_material`: questions, tasks, or exam-style prompts.
- `marking_material`: answer keys, mark schemes, solutions, or examiner feedback.
- `style_reference`: examples that show preferred answer style or layout.
- `extra_reading_source`: academically useful background, methods, evidence, research context, textbook-like, chapter-like, paper-like, DOI/PMID, or reference material.
- `online_material`: web-accessible academic/module material, online readings, official pages, databases, papers, or user-provided links whose use must be confirmed before Online Essay Exam planning.
- `other_material`: readable files whose source role remains mixed or unclear.

Mixed files remain valid. A single file can contain several source roles, many knowledge units, and several knowledge roles. Coverage comes from knowledge signals and knowledge units, not from the hint label.

## Human Review of Source Roles

Material type and source roles are preliminary until the user confirms them through human review. After source scanning, display the **Auto-diagnosis review plan** with the detected Material type/source roles, role counts, question signals, and any Mixed or unclear evidence. Then ask the Material type/source roles question through `request_user_input`.

The options must be concrete to the source pack, such as treating lecture files as `knowledge_material`, treating question files as `practice_material`, using answer keys as `marking_material`, using research files as `extra_reading_source`, treating links or web-accessible sources as `online_material`, or manually correcting Mixed/unclear files. After the user confirms or corrects the roles, update the source hints and use the confirmed roles for routing, coverage, essay-style Extra Reading, Online Essay Exam source permissions, and output decisions.

For Online Essay Exam, material collection has an additional source-permission gate before any plan, evidence map, Notes, report, or draft. Ask whether Online Materials are required, optional, forbidden, or unclear; whether Lecture Materials may be used as primary evidence, background only, forbidden, or unclear; whether Past Papers, rubrics, module handbooks, uploaded readings, and external academic sources may be used; whether citations or references are required; and whether the final output should be a chat draft, DOCX draft, or both. Missing source-permission answers remain plan-changing unresolved items unless explicitly recorded as a user-confirmed default.

## Direct Invocation Gate

When a focused Skill is opened directly and no `exam-prep-index` review state is available, first create the same confirmed review state before public output. Use `scripts/plan_workflow.py` and `scripts/build_review_questions.py` or an equivalent `request_user_input` payload.

An `AcademicTaskContext` v1 payload may satisfy already-confirmed parts of this gate. Preserve its non-empty `original_prompt` and `route_selection`; an explicitly confirmed route must not be re-detected from an empty or reconstructed prompt. Continue to ask only for unresolved source-role, Notes, Mixed-component, Online Essay permission, assessment-blueprint scope, answer-evaluation criteria, or timed-practice duration decisions. `scripts/soleil_adapter.py` produces `TaskRunState` v1 while retaining those unresolved gates.

## Cross-plugin context and course history

Consume only the `relevant_memory` records named in the current `AcademicTaskContext`. Everything University memory may provide prior course mastery or weakness references, but it does not override the current user's explicit route, source permissions, answer, criteria, or duration.

Per-course mastery and weakness history is enabled by default. The user can enable, disable, export, or delete it through `scripts/mastery_history.py`. Disabling prevents new attempt records while preserving existing records until the user exports or deletes them. Answer Evaluation and Timed Practice may update this history only after their own route gates are satisfied.

## Locator provenance

Preserve source name and locator plus available `page_number`, `slide_number`, `time_offset_seconds`, and `time_range` fields from extraction through fragment indexing, assessment blueprints, answer evaluation evidence, timed-practice slots, and public outputs where provenance belongs. Missing locators remain missing; do not infer page, slide, or time values.

The confirmed review state records the fields that affect the route: Exam type or route, Material type and source roles, Notes generation choice for report-style routes, selected component routes for Mixed, route-specific follow-up choices, and Online Materials or Lecture Materials permissions for Online Essay Exam. Treat an explicit fixed-route user instruction as confirmation only for the fields it states; ask for the remaining plan-changing fields before generating Notes, Specific Research Reports, Worked Solutions, Question Solving output, organized question DOCX files, evidence maps, plans, or drafts.

## Intake

For each file, record:

- file name, path, source hint, readable character count, extraction notes;
- text fragments;
- extracted media and cropped PDF visual-region assets when available;
- question signals for Past Paper and Practical Materials when detectable;
- practical worked-solution signals and solution-evidence signals when detectable;
- `knowledge_signals`, `knowledge_roles`, and `knowledge_unit_candidates` when detectable.

The assistant should inspect fragments directly. Coarse source hints support routing, while knowledge signals drive notes coverage.

## Open Knowledge Signals

Detect knowledge signals wherever they appear across the supplied material:

- topic boundary: headings, section titles, numbered units, topic transitions;
- learning target: objectives, outcomes, "by the end" statements, task aims;
- concept signal: definitions, named terms, classifications, principles;
- mechanism signal: causal chains, pathways, activation, inhibition, sequence, consequence;
- method signal: protocols, assays, controls, readouts, measurements, steps;
- comparison signal: contrast, versus, whereas, shared and distinguishing features;
- calculation signal: equations, formulas, rates, dose-response measures, numeric interpretation;
- data interpretation signal: figures, graphs, tables, trends, readouts, conclusions from data;
- evidence signal: findings, results, experimental support, DOI/PMID, cited research;
- application signal: clinical use, case use, disciplinary use, decision use, conceptual application, method selection, or interpretation use;
- explanatory example signal: examples that clarify a concept, mechanism, method, calculation, data interpretation, evidence use, or reasoning move.

High density is indicated by many signals in a short span, repeated technical terms, stacked learning targets, or compact topic lists. High-density spans should be expanded into explainable notes rather than treated as simple lists.

## Knowledge Units

A knowledge unit is a connected group of signals that should be explained together.

Knowledge units can be formed by:

- an explicit heading or topic boundary;
- a learning objective followed by related content;
- a concept and its mechanism, method, comparison, evidence, or application;
- a sequence of related fragments that build one explanation.

Each knowledge unit should keep its source grounding and record the explanation it requires. A unit can require several explanation types at once, such as definition plus mechanism plus data interpretation.

For Exam Prep Notes, preserve lecture/source order when building the Notes coverage map. Scoring can still identify density or report priority, but it should not reorder the public Notes away from the course sequence.

Use content triage before writing Notes:

- `core_lecture_content`: substantive lecture material that should be covered.
- `supporting_example`: examples or cases that should be included when they teach reusable reasoning and compressed when repetitive.
- `reading_reference`: reading lists, book references, DOI/PMID pointers, or source citations that should be excluded unless directly needed for examinable course knowledge.
- `admin_or_boilerplate`: housekeeping, licensing, contact, or administrative material that should be excluded unless it changes assessed content.
- `low_exam_relevance_context`: broad contextual framing that should be compressed or excluded unless it teaches a course concept, mechanism, method, or application.

## Extra Reading Intake

Extra Reading can be uploaded directly or mentioned inside course material. Mentions include Source, Sources, References, Recommended reading, Further reading, Textbook, Book, Chapter, DOI, PMID, author-year citation, journal reference, figure source, or reference-list text.

Extra Reading is used for Essay Question and Example Essay enrichment, plus Online Essay Exam enrichment when source permissions allow it, where external evidence, mechanism depth, molecular evidence, counterargument, and evaluation can help earn Extra Reading credit. Do not use Extra Reading for MCQ, short-answer, long-answer, practical/data/problem, worked-solution, or general Notes routes unless the user also confirms an essay-style output.

## Practical Extraction

Text files, Markdown, JSON, YAML, CSV, DOCX, PPTX, and PDF are read when the local runtime can read them. Embedded images from DOCX/PPTX can be exported to an asset folder. PDF figure, table, diagram, graph, pathway, scheme, or image regions can be rendered into cropped assets when those regions show academic value. Page locators can support the written explanation when a reliable local visual crop is not available. Files without automatic text extraction remain listed with an extraction note.

Past Paper and Practical Materials can record `question_signals`. Past Paper signals come from question-paper context plus extractable question wording. For MCQ and Short Answer recurrence reports, mark Past Papers, Mock Papers, and official exam papers distinctly from ordinary Practice Material. Ordinary Practice Material can provide context but does not count toward high-frequency recurrence. Practical question signals come from explicit task, data, calculation, interpretation, or problem wording. Worked-solution signals come from calculation, derivation, estimate, proof, physics/math problem, data-interpretation, unit, uncertainty, graph, table, or problem wording. Solution-evidence signals come from mark schemes, answer keys, solutions, worked answers, or examiner feedback. These signals route separate Exam Type Related Specific Research Reports or Math/Physics/Practical Worked Solutions output. Notes use the same material for knowledge-signal evidence, and worked examples are included when they directly teach a knowledge unit. Question/practice material calibrates report emphasis while lecture/course knowledge units continue to drive full Notes coverage.

Question records should preserve source file, locator, question order, question demand, knowledge terms, answer-operation type, MCQ question pattern or SAQ answer pattern, and practical worked-solution signals. Treat every SAQ subquestion, subpart, and mark-point prompt as an independent question record. Use those records to match target questions and practice questions to lecture knowledge units. For MCQ and Short Answer recurrence clustering, assign each question to the most direct knowledge unit that decides the answer; if a question cannot be assigned uniquely, use the latest clearly matched lecture unit. For strict same-knowledge-point retrieval, require the same matched knowledge unit plus specific shared terms and visible provenance from the supplied material. For Past Paper and Practice Material organization, sort matched questions by lecture knowledge-unit order and assign questions that match several units to the latest matching unit.
