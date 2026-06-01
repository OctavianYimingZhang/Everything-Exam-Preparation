# Input Processing Protocol

## FileRole Enum

Classify every file before analysis:

- `lecture_slide`
- `lecture_note`
- `annotated_lecture_slide`
- `student_typed_note`
- `student_handwritten_note`
- `structured_revision_note`
- `ai_generated_note`
- `formal_past_paper`
- `formal_past_paper_with_answers`
- `example_paper`
- `practice_paper`
- `practice_answer_key`
- `mock_exam`
- `answer_key`
- `practical_protocol`
- `exemplar_answer`
- `exemplar_image`
- `marking_criteria`
- `essay_guidance`
- `extra_reading_book`
- `extra_reading_chapter`
- `citation_original_source`
- `classic_experiment_source`
- `citation_reference_list`
- `reading_list`
- `docx_format_reference`
- `source_policy`
- `output_protocol`
- `visual_aid_spec`
- `generated_visual_aid`
- `helper_script`
- `unsupported_binary`
- `unknown`

Each file record must include:

- file path;
- normalized `target_group_key`;
- course/module code if detectable;
- course/module name if detectable;
- year if detectable;
- exam regime if detectable;
- source trust level;
- extraction status;
- allowed evidence use.
- source feature flags, such as answer key, example paper, practical protocol, essay guidance, problem/data/case, and recommended reading.

The Skill accepts any readable course-note source: slides, official notes, lecturer-provided PDF/DOCX notes, student typed notes, handwritten notes, annotated screenshots, flashcards, structured revision notes, and AI-generated summaries. Acceptance for intake is not the same as authority for factual claims.

Ordered course-note processing uses:

```text
CourseContentSource -> OrderedContentItem -> SourceFragment -> AtomicKnowledgeLedger -> KnowledgePoint -> PrepArtifact
```

Student handwritten annotations, typed notes, flashcards, and unknown-provenance summaries may be used as interpretation hints, definition candidates, and gap cues, but must not be treated as authoritative course facts unless supported by slide text, official notes, official course material, verified textbooks, or verified academic sources. AI-generated notes have no factual authority and may only help with structure after independent verification.

## Source Trust Levels

- `official_course`: lecture slides, official notes, official past papers, official marking criteria, official exam guidance.
- `course_adjacent`: lecturer-provided practice, mocks, answer keys, exemplars, tutorial material.
- `student_or_unknown`: student notes, downloaded material with unclear provenance, unclear file origin.
- `external_verified`: peer-reviewed, textbook, DOI/PubMed/publisher/official sources verified during the run.
- `unsupported`: unreadable or unsupported content.

## Evidence Use

- `factual_course_content`
- `formal_prediction_evidence`
- `formal_prediction_and_answer_key_evidence`
- `coverage_evidence_only`
- `answer_rationale_evidence`
- `answer_style_only`
- `format_rule`
- `practical_method_evidence`
- `reading_recommendation`
- `extra_reading`
- `lecture_slide_core`
- `lecture_slide_citation_original`
- `classic_experiment_source`
- `student_note_hint`
- `definition_candidate`
- `exam_emphasis_hint`
- `visual_explanation_only`
- `docx_format_reference`
- `excluded`

## AnalysisContext

Every source must also be classified by `AnalysisContext` before it is used downstream.

```yaml
AnalysisContext:
  target_current_regime:
    meaning: same target source set, current formal evidence; allowed for blueprint and prediction
  target_old_or_different_regime:
    meaning: same target source set but old/different format; allowed for concept coverage and answer schema only
  target_auxiliary:
    meaning: practice/mock/tutorial/answer key from same target source set; allowed for coverage and style depending on role
  cross_target_example:
    meaning: non-target material; transferable workflow logic only
  style_exemplar:
    meaning: exemplar answer/image; style/structure/density only unless factual claims are verified
  layout_exemplar:
    meaning: visual formatting example only; may update route style profile and DOCX style lint rules, never factual content
  benchmark_fixture:
    meaning: regression test case only
  unsupported_or_unreadable:
    meaning: do not use for factual or predictive claims
```

Hard rule:

```text
Only `target_current_regime` may directly control current blueprint prediction.
Only target lecture slides, official notes, lecturer-provided course notes, verified official materials, and independently verified academic sources may directly control factual content.
Cross-target examples must be converted into transferable workflow contributions, not content evidence.
```

## AllowedUseMatrix

| Analysis Context | Factual content | Prediction blueprint | Coverage | Style | Layout | Regression |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `target_current_regime` | yes | yes | yes | yes | yes | no |
| `target_old_or_different_regime` | yes if lecture/official | no unless comparability is proven | yes | limited | no | no |
| `target_auxiliary` | limited | no unless official says representative | yes | yes | no | no |
| `cross_target_example` | no | no | no | principle only | possible | no |
| `style_exemplar` | no unless verified | no | no | yes | no | no |
| `layout_exemplar` | no | no | no | no | yes | no |
| `benchmark_fixture` | no | no | no | no | no | yes |
| `unsupported_or_unreadable` | no | no | no | no | no | no |

## ExampleReviewRecord Schema

Every non-target example used by a protocol or benchmark must be represented as a review record before any lesson is promoted:

```yaml
ExampleReviewRecord:
  example_id:
  source_role:
  source_materials:
    - lecture_slides
    - lecture_notes
    - formal_past_papers
    - practice_materials
    - answer_keys
    - practical_protocols
    - marking_guidance
    - exemplar_answers
    - handwritten_or_image_examples
  example_scope:
  what_worked:
    - reusable behaviour demonstrated by the example
  why_it_worked:
    - source or output condition that made the behaviour valid
  what_failed:
    - failure observed, or no failure observed
  why_it_failed:
    - cause, or not applicable because no failure was observed
  transferable_principle:
  non_transferable_content:
    - topic/content/lecturer/year detail that must not be reused
  anti_overfit_rule:
  affected_protocols:
    - protocol path or protocol name
  affected_scripts:
    - script path or linter name
  validation_check:
  regression_fixture:
  promotion_status: candidate | accepted | rejected | blocked
  confidence: high | medium | low
```

Promotion is blocked unless the review record explains both useful and failed behaviours, strips non-transferable content, names the destination, and includes a validation check. Examples may improve workflow logic and QA only; they cannot support target facts or predictions.

## Target Group Key And Regime Split

All question-pattern inference must stay inside the same target course/module group. Normalize every filename before comparison:

1. remove year/date tokens;
2. remove terms such as `mock`, `practice`, `with answers`, `answer key`, `guide answers`, `modified syllabus`, `CADMUS`, `PP1/PP2`, dates, `combined`, copies, and version suffixes;
3. collapse whitespace and punctuation;
4. retain the normalized course/module group as `target_group_key`.

Never use content from one `target_group_key` to predict the content of another target group. External examples may be used only as `ExampleReviewRecord` entries that teach reusable workflow logic, output structure, QA checks, or evidence-handling discipline after non-transferable content is blocked.

Within the same target group, split formal papers into `exam_regime` groups when any of these change materially:

- section structure;
- answer-all vs answer-one/choose-one rule;
- timing or submission mode;
- mark weights;
- MCQ/short-answer/essay/case-study balance;
- data/figure/calculation requirements.

Old-regime papers may support concept coverage and possible slot fillers, but they must not be averaged into current-regime blueprint or archetype recurrence.

## Extraction Rules

- PDF: extract page-by-page text; record image count and warn that diagram/image text may need visual inspection.
- PPTX/PPTM/PPSX: extract slide XML text and notes XML when possible; record that diagrams and embedded images may not be text-extracted.
- PPT: use legacy binary-string extraction only as approximate text; require original-file inspection for diagrams and exact wording.
- DOCX: extract paragraphs and table text.
- XLSX/XLSM: extract sheet names and text-like cell values; treat existing analysis spreadsheets as prior work with provenance, not source truth.
- TXT/Markdown/YAML/Python: read as text.
- Images: mark as image evidence; inspect manually or with OCR when it affects the answer.
- Image exemplars: classify as `exemplar_image` when context indicates handwritten essays, model answers, example answers, or essay drafts. Evidence use is `answer_style_only`; status must include visual-inspection limits. Do not OCR repeatedly by default.
- A user-uploaded textbook, book chapter, monograph, or long PDF supplied as additional reading must be classified as `extra_reading_book` unless it is clearly a lecture slide or past paper.
- A standalone chapter or chapter extract supplied as additional reading must be classified as `extra_reading_chapter`.
- A PDF or paper resolved from a citation on a lecture slide must be classified as `citation_original_source`.
- A classic or landmark primary experiment found because relevant lecture slides contain no usable citations must be classified as `classic_experiment_source` after verification and reading.
- A bibliography/reference-list file supplied to resolve slide citations may be classified as `citation_reference_list`.
- A user-uploaded formatting PDF, screenshot, or previously generated DOCX supplied as a formatting reference must be classified as `docx_format_reference` or `layout_exemplar`. Use it only to derive transferable layout rules such as margin density, spacing, alignment, heading hierarchy, page-break policy, and label discipline; never use it as factual or prediction evidence.
- A reasoned answer key must be classified by provenance where possible: official/lecturer, paper-with-answer, student, generated, or unknown. Use it for answer schema, rationale, distractor traps, and marking expectations, not direct prediction.
- A practical protocol must be routed to practical/data/problem logic: aim, method principle, steps, readout, interpretation, control, limitation.
- A reading list, course handbook, programme/advisement document, or suggestions file may identify reading recommendations or administrative constraints; it must not replace lecture content.
- Essay style examples must be classified as `style_exemplar` or `exemplar_answer` and used only for paragraph structure, density, and tone unless factual claims are independently verified from target materials.
- Unsupported files: never infer hidden content.

## Atomic Source Decomposition

For `exam_prep_notes_docx`, extraction does not stop at broad KnowledgePoints. Before baseline notes are written, every readable slide/page/source block must be decomposed into `AtomicKnowledgeUnit` records inside an internal `AtomicKnowledgeLedger`.

Protected atomic units include:

- intended learning outcomes;
- slide/page headings and major note headings;
- definition-style text;
- contrast pairs;
- criteria, feature, stage, class, or component lists;
- named mechanisms, methods, drugs, diseases, examples, cases, and target classes;
- `Why X?` source blocks;
- labelled diagrams, tables, equations, graphs, calculations, and workflows;
- limitations, misconceptions, and take-home points.

Administrative units, exam timing, mark splits, reading-list logistics, course-admin pages, and repeated duplicates may be excluded from the student view, but the ledger must record the exclusion reason. Knowledge units must be bound to final modules or named submodules before public generation.

### Extra Reading Book Extraction

For Extra Reading Books:

- extract table of contents if available;
- extract chapter headings;
- extract section headings;
- index searchable keywords;
- map chapters to lecture KPs using lecture terms, pathway names, diseases, methods, model systems, and essay question terms;
- read only relevant chapters/sections before inserting yellow-highlighted content into Example Essays.

### Extra Reading Paper Extraction

For Extra Reading Papers:

- extract title, authors, year, DOI, PMID, journal or publisher record where available;
- verify the paper from DOI, PubMed, publisher, Google Scholar, or another reliable academic locator before using it;
- map the paper to the exact lecture mechanism, method, model, evidence point, limitation, comparison, or essay question function it can sharpen;
- classify verified/read paper-derived content as `extra_reading_paper`;
- insert paper-derived content only with parenthetical author-year citation and green highlight;
- do not treat papers as Extra Reading Books and do not yellow-highlight them.

### Lecture-Slide Citation Extraction

For lecture-slide citations:

- extract citations from slide text, notes, reference slides, footers, and figure captions;
- if citations appear only inside slide images, perform targeted OCR or visual inspection on relevant slides;
- parse author-year, DOI, PMID, title fragments, journal names, and reference-list entries;
- classify resolved/read source files as `citation_original_source`;
- do not use source-derived content until the cited original source has been resolved and read.

If the user asks for Example Essay generation but supplies no citation list:

- treat citation discovery as mandatory, not optional;
- inspect relevant lecture slides first for author-year, DOI, PMID, title fragments, journal names, reference-list entries, figure-caption citations, and notes citations;
- emit academic search queries for unresolved slide citations;
- if no usable slide citations exist, create a classic-experiment search plan from lecture terms, named mechanisms, model systems, methods, and evidence claims;
- require several candidate classic experiments or landmark primary studies where possible, but insert only those that have been verified and read;
- classify verified fallback sources as `classic_experiment_source`;
- flag `lecture_slide_citation_absent_classic_experiment_search_required` internally when this fallback path is used.

## ExamFormat Fields

For each formal paper or guidance source, parse:

- course/module code if detectable;
- year;
- duration;
- sections;
- answer_all_or_answer_one;
- question_count_by_section;
- mark_weight_by_section;
- page_limit;
- word_limit;
- character_limit;
- figure_rule;
- citation_rule;
- calculator_rule;
- answer_book_or_blackboard;
- formatting_penalty;
- late_penalty.

Different year constraints directly change answer strategy; do not merge years without recording differences.

## KnowledgePoint Schema

```yaml
KnowledgePoint:
  kp_id:
  lecture_id:
  module_id:
  lecturer:
  title:
  concept_type: mechanism | pathway | experiment | disease | comparison | definition | method | figure | model_system | controversy_or_limitation
  source_anchor:
    file:
    slide_or_page_range:
  examinability: high | medium | low
  likely_question_types: []
  prerequisite_kps: []
  linked_kps: []
  essay_style_paragraph:
  mcq_statement_candidates: []
  short_answer_possible_questions: []
  essay_theme_candidates: []
  compatible_archetypes: []
  essay_function:
    - thesis_support
    - mechanism_paragraph
    - comparison_axis
    - example_evidence
    - cross_module_link
    - optional_extra_detail
  mechanism_chain:
    condition:
    regulator_or_sensor:
    molecular_action:
    output_change:
    biological_consequence:
  lecturer_emphasis:
    learning_objective: true/false
    summary_slide: true/false
    repeated_example: true/false
    named_as_key_point: true/false
  essay_priority: must_use | useful | optional | exclude
  paragraph_fit:
    possible_topic_sentence:
    possible_link_back_to_question:
  task_dimensions:
    factual:
    mechanistic:
    structural:
    quantitative:
    comparative:
```

Do not split by every slide. Split by examinable causal block. A valid KP should work as an MCQ concept, a short-answer mark cluster, an essay paragraph, or one component of an essay plan.

Protected source-backed items override ordinary compression. Treat each of the following as a protected KnowledgePoint or protected sub-item in the source baseline:

- intended learning outcome;
- slide/page heading or major notes heading;
- official definition;
- contrast pair;
- criteria, features, stages, classes, components, or steps list;
- named example used to teach a concept;
- `Why X?` source section;
- labelled diagram, table, graph, equation, calculation, or workflow;
- summary or take-home point;
- term, operation, or concept appearing in formal past papers.

Protected items may be grouped only when the final baseline still names and explains each item. They may not be hidden only in traps, omitted as low-value detail, or reduced to one checklist phrase.

For essay-capable KPs, do not treat all slide facts equally. Prioritise the facts that can form a causal paragraph:

```text
condition or biological problem -> regulator/sensor/molecular feature -> molecular action -> output change -> biological consequence
```

## Lecture-Order Coverage

For compatibility lecture walkthroughs and DOCX add-ons, analysis must proceed from the first slide/page to the last slide/page in source order where lecture order matters.

For `exam_prep_notes_docx`, source order is a diagnostic input, not a binding output order. Use it to infer prerequisites, source intent, and causal development; then organise the final notes by course-section logic, KnowledgePoint dependency, and supported exam emphasis.

Do not:

- analyse only high-yield slides;
- skip middle lecture sections without a QA flag;
- reorder KPs by predicted importance in the compatibility lecture-first walkthrough;
- merge several unrelated mechanisms into one huge KP;
- split one mechanism/evidence block into isolated slide fragments.

Allowed:

- group several consecutive slides/pages into one KP when they form one mechanism, process chain, experimental-evidence block, data-operation block, or essay paragraph block;
- mark a block low examinability, but still preserve its position;
- place detailed evidence in diagnostics or an explicit audit package while keeping the student-facing output clean.
