# Notes Protocol

## Purpose and Source Authority

Reconstruct the teachable course for revision, including material a student may be learning for the first time. Keep Notes broader than a past-paper trend report.

Apply the user's source roles before drafting. Build the coverage ledger from the designated coverage authority. When lecture slides are primary and text notes are reference material, cover every substantive slide knowledge point; use the reference notes only to identify emphasis, concise phrasing, and useful organisation. A reference summary's omissions never justify omitting slide content.

Past papers and recap questions calibrate emphasis and explanation depth. They do not replace the course-coverage ledger.

## Public Notes Boundary

Represent course knowledge through definitions, structures, mechanisms, processes, methods taught as subject matter, equations, evidence, data interpretation, comparisons, applications, and explanatory examples. Integrate the knowledge behind recap or interactive questions into the relevant teaching unit.

Use assessment specifications, past papers, mark schemes, rubrics, and question sets as internal evidence for emphasis or explanation depth. Keep assessment strategy, command-word coaching, answer-planning routes, thesis or paragraph templates, model-answer scaffolds, reproduced question banks, revision schedules, time-allocation plans, and exam-day advice in a separately and explicitly requested Practice or Essay artifact.

Generate only the Notes file for Notes, improvement, continuation, rebuild, or bulk course-document tasks. Do not append exam-preparation schemes to Notes or create an unsolicited companion artifact.

## Coverage and Slide Triage

Build connected knowledge units from definitions, mechanisms, methods, comparisons, calculations, data interpretation, evidence, applications, and explanatory examples. Use learning outcomes, agendas, section dividers, recaps, and summaries for structure. Merge repetition and continuation slides into the nearest complete explanation.

The source processor assigns each slide-like fragment:

- `use`: contributes structure or substantive teaching;
- `merge_with_previous`: continues or duplicates the preceding knowledge unit;
- `exclude`: is administrative, decorative, citation-only, empty, or duplicated without adding teaching content.

Treat automated triage as provisional. Review the complete rendered slide or page before confirming any exclusion, and compare the visuals as well as the extracted text before confirming that repeated material can be merged. Copyright, licence, source-credit, sparse text, or citation-like text can coexist with substantive teaching graphics and never establishes a defensible exclusion by itself. Review `notes_role`, `detailed_explanation_allowed`, `manual_review_required`, `triage_reason`, and the source-level audit before finalising coverage. Keep those decisions and all source locators internal.

## Visual Value Gate

Use a diagram, graph, micrograph, process schematic, compact comparison table, or equation when it materially improves the explanation of a spatial, temporal, structural, quantitative, or causal relationship beyond a clear text or table treatment. Apply this decision to every candidate image; there is no image quota and no requirement to illustrate each page or knowledge unit.

Prefer a suitable original lecture-slide image, crop, or complete slide page when it already teaches the relationship clearly at readable size. Create a new diagram only when the relationship has strong visual value and the supplied course material contains no adequate visual. Pair each retained visual with the definitions, causal links, or interpretation needed to make it self-contained.

Keep essential figure labels close to the surrounding reading size. At the intended embedded width, use a minimum effective label size of about 80% of the body-text size; with the standard 11 pt body this means approximately 9 pt or larger. Calculate raster-label size as `source font px × embedded width in × 72 ÷ source width px`, record the result in the internal figure-typography audit, and reflow, simplify, crop, enlarge, or split a visual when labels would fall below the relative floor.

Do not print source filenames, slide/page locators, `Source:` lines, figure numbers, or figure legends under images unless the user explicitly asks for them. Retain provenance in the internal audit. Use a short public caption only when explicitly requested and set `display_caption: true` for that image block; otherwise supply explicit `alt_text` that identifies the visual's subject and the teaching relationship it shows. Treat a heading alone, `Course visual`, `Course concept diagram`, and bibliographic or source text as invalid accessibility descriptions.

## Writing, Equations, and Tables

Choose paragraphs, learning-point lists, or a combination according to the material. Coherent longer paragraphs are appropriate when they explain a connected concept more clearly; bullet points are appropriate for genuinely list-like, sequential, or contrastive information. Define specialist terms at first use, show causal chains explicitly, and place methods and worked examples inside the knowledge unit they support.

Let source knowledge density, conceptual difficulty, and explanation needs determine document length and detail. Preserve concise treatment for genuinely sparse material and fuller treatment for dense material; do not expand or compress content to meet a uniform word, page, paragraph, or bullet target. Reducing prose must not reduce coverage.

Set important formulae as centred display equations with professional mathematical typography comparable to LaTeX. Render fractions, roots, Greek letters, operators, subscripts, superscripts, and chemical charges as mathematical notation rather than raw markup. Define symbols and units immediately below, carry units through calculations, and explain assumptions and the meaning of the result.

Use tables only when exact comparison or mapping is clearer than prose. Apply light borders, restrained header shading, content-aware column widths, adaptive type size, natural wrapping, suitable cell padding, and alignment based on content. Verify that no column is crowded or clipped.

## Document Design

Use A4, Arial 11 pt body text, 2 cm margins, 1.5 line spacing, a centred main title, left-aligned headings, justified body text, black academic text, restrained hierarchy, and consistent visual placement.

Keep the document in natural continuous flow. An intentional page break may introduce an actual Lecture boundary; knowledge units within the same Lecture flow continuously. Keep a heading with enough following content to identify its section without creating avoidable large blank areas.

Use the user's requested filename and language. Otherwise use English and a clear course-based filename. Use a single main title by default and add supplementary title text when requested.

## Verification Loop

Confirm that every coverage-authority source and every substantive slide fragment is represented, merged with a recorded reason, or excluded with a defensible non-teaching reason. Check heading order, equation notation, table width and wrapping, image resolution, semantic alternative text, source-label suppression, image-value decisions, and page breaks at Lecture boundaries.

Before release, scan all public text, equations, tables, and visual labels for raw notation such as unresolved `_` or `^`, replacement or missing-glyph boxes, malformed roots or fractions, and incorrect chemical or ionic charges. Confirm the figure-typography audit covers every teaching visual and that the rendered labels meet the body-relative size floor. Render the complete DOCX to page images and inspect every page at readable zoom. Record the inspected page count; correct clipping, overflow, crowded tables, broken equations, misplaced images, awkward blank space, orphan headings, isolated final-page content, unexpected blank pages, and font inconsistency; then re-render and repeat until every page passes.
