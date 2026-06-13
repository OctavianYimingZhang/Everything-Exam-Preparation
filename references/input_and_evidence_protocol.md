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

## Intake

For each file, record:

- file name, path, source hint, readable character count, extraction notes;
- text fragments;
- extracted media when available;
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
- application signal: clinical use, case use, exam use, answer use, decision use;
- explanatory example signal: examples that clarify a concept, mechanism, method, calculation, data interpretation, evidence use, or answer move.

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

Extra Reading is used when it adds mechanism depth, molecular detail, experimental evidence, research context, method detail, or stronger evaluation.

## Practical Extraction

Text files, Markdown, JSON, YAML, CSV, DOCX, PPTX, and PDF are read when the local runtime can read them. Embedded images from DOCX/PPTX can be exported to an asset folder. Files without automatic text extraction remain listed with an extraction note.
