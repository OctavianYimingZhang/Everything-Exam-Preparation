# Input And Evidence Protocol

This is the only canonical source-intake and evidence-boundary protocol.

## Source Roles

Classify every supplied item before drafting:

- `subject_knowledge`: lecture slides, official notes, verified course notes, definitions, mechanisms, structures, pathways, methods, calculations, diagrams, examples, data patterns, limitations.
- `practical_operation`: protocols, apparatus, reagents, controls, safety, assay logic, graph/data readouts, calculation operations.
- `exam_pattern`: formal past papers, mocks, mark schemes, answer keys, command verbs, section structure, timing, mark operations.
- `extra_reading`: books, chapters, DOI records, PubMed records, publisher pages, textbooks, peer-reviewed papers, verified academic sources.
- `style_or_layout_example`: exemplar answers, feedback, format references, visual examples, prior outputs used only for organisation, density, and expression style.
- `non_knowledge_noise`: admin, emails, staff lists, room information, attendance systems, URLs with no knowledge content, copyright lines, image credits, decorative quotes, OCR debris.

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` may become public knowledge prose. `exam_pattern` may shape routing, emphasis, and add-on answer operations. `style_or_layout_example` may shape presentation only. `non_knowledge_noise` is discarded.

## Authority And Boundaries

Use course and official sources as the factual baseline. Use past papers to identify exam mode, command operations, and repeated families only when comparable. Use answer keys and exemplars for answer style and operation logic, not new facts. Use extra reading only after verification and only to deepen source-backed logic.

Do not infer hidden content from unreadable files. Do not use benchmark names, old target groups, example topics, or previous project names as production triggers. Unsupported claims become explicit gaps.

## Extraction Objects

The workflow may internally build `SourceDocument`, `SourceFragment`, `FragmentPartition`, `AnalysisContext`, `EvidenceClaim`, `SourceCoverageMap`, and `AtomicKnowledgeLedger`. These are internal control-plane objects. They must not be rendered in student-facing output unless the user explicitly asks for an audit package.

## Visual And Citation Boundaries

Images, diagrams, tables, graphs, and slide visuals must be inspected when they carry examinable information. Generated visual aids are optional revision schematics, not evidence. Slide citations must be resolved before they support factual essay prose; unresolved citations remain gaps or are labelled as unresolved.
