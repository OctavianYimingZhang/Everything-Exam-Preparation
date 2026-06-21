# Input and Evidence Protocol

This Skill reads supplied files through rough source hints and open knowledge signals.

Source hints describe provenance and routing context. Notes coverage is calibrated from the knowledge signals and knowledge units found in the material.

## Source Hints

Use source hints as open, coarse provenance labels. Treat the labels below as examples that can be expanded when the source context requires it:

- `knowledge_material`: course-facing explanation or teaching content.
- `practice_material`: questions, tasks, or exam-style prompts.
- `marking_material`: answer keys, mark schemes, solutions, or examiner feedback.
- `style_reference`: examples that show preferred answer style or layout.
- `extra_reading_source`: academically useful background, methods, evidence, research context, textbook-like, chapter-like, paper-like, DOI/PMID, or reference material.
- `other_material`: readable files whose source role remains mixed or unclear.

Mixed files remain valid. A single file can contain several source roles, many knowledge units, and several knowledge roles. Coverage comes from knowledge signals and knowledge units, not from the hint label.

## Human Review of Source Roles

Material type and source roles are preliminary until the user confirms them through human review. After source scanning, display the **Auto-diagnosis review plan** with the detected Material type/source roles, role counts, question signals, and any Mixed or unclear evidence. Then ask the Material type/source roles question through `request_user_input`.

The options must be concrete to the source pack, such as treating lecture files as `knowledge_material`, treating question files as `practice_material`, using answer keys as `marking_material`, using research files as `extra_reading_source`, or manually correcting Mixed/unclear files. After the user confirms or corrects the roles, update the source hints and use the confirmed roles for routing, coverage, essay-only Extra Reading, and output decisions.

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

## Extra Reading Intake

Extra Reading can be uploaded directly or mentioned inside course material. Mentions include Source, Sources, References, Recommended reading, Further reading, Textbook, Book, Chapter, DOI, PMID, author-year citation, journal reference, figure source, or reference-list text.

Extra Reading is used only for Essay Question and Example Essay enrichment, where external evidence, mechanism depth, molecular evidence, counterargument, and evaluation can help earn Extra Reading credit. Do not use Extra Reading for MCQ, short-answer, long-answer, practical/data/problem, worked-solution, or general Notes routes unless the user also confirms an essay output.

## Practical Extraction

Text files, Markdown, JSON, YAML, CSV, DOCX, PPTX, and PDF are read when the local runtime can read them. Embedded images from DOCX/PPTX can be exported to an asset folder. PDF figure, table, diagram, graph, pathway, scheme, or image regions can be rendered into cropped assets when those regions show academic value. Page locators can support the written explanation when a reliable local visual crop is not available. Files without automatic text extraction remain listed with an extraction note.

Past Paper and Practical Materials can record `question_signals`. Past Paper signals come from question-paper context plus extractable question wording. For MCQ and Short Answer recurrence reports, mark Past Papers, Mock Papers, and official exam papers distinctly from ordinary Practice Material. Ordinary Practice Material can provide context but does not count toward high-frequency recurrence. Practical question signals come from explicit task, data, calculation, interpretation, or problem wording. Worked-solution signals come from calculation, derivation, estimate, proof, physics/math problem, data-interpretation, unit, uncertainty, graph, table, or problem wording. Solution-evidence signals come from mark schemes, answer keys, solutions, worked answers, or examiner feedback. These signals route separate Exam Type Related Specific Research Reports or Math/Physics/Practical Worked Solutions output. Notes use the same material for knowledge-signal evidence, and worked examples are included when they directly teach a knowledge unit. Question/practice material calibrates report emphasis while lecture/course knowledge units continue to drive full Notes coverage.

Question records should preserve source file, locator, question order, question demand, knowledge terms, answer-operation type, MCQ question pattern or SAQ answer pattern, and practical worked-solution signals. Treat every SAQ subquestion, subpart, and mark-point prompt as an independent question record. Use those records to match target questions and practice questions to lecture knowledge units. For MCQ and Short Answer recurrence clustering, assign each question to the most direct knowledge unit that decides the answer; if a question cannot be assigned uniquely, use the latest clearly matched lecture unit. For strict same-knowledge-point retrieval, require the same matched knowledge unit plus specific shared terms and visible provenance from the supplied material. For Past Paper and Practice Material organization, sort matched questions by lecture knowledge-unit order and assign questions that match several units to the latest matching unit.
