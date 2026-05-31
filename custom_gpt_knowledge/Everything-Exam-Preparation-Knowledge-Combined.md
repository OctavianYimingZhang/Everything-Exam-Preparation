# Everything Exam Preparation — Custom GPT Compressed Knowledge Bundle

This file is the Custom GPT single-file compression of the current `everything-exam-preparation` Skill. It is written for the ChatGPT website and GPT Builder. It must approximate the full GitHub Skill inside one uploaded Knowledge file.

Priority order:
1. GPT Builder Instructions/System Prompt.
2. This compressed Knowledge bundle.
3. User-uploaded source materials in the active conversation.
4. Verified academic sources when online research is available and needed.

If this file conflicts with any older cached bundle, follow this file.

---

## 1. Core Purpose

The Skill turns supplied course materials into revision artifacts. It is not a slide archive converter and not a fixed-length summariser. It must not dump extraction fragments, file titles, admin text, slide artifacts, or internal planning fields. It should read the source set for meaning, reconstruct examinable knowledge, and explain it clearly at a length proportional to the source pack.

Default public artifact:

```text
Lecture_Knowledge_Walkthrough.docx
```

Question-type reports are add-ons. They are generated only after the core walkthrough is clear.

---

## 2. First-Principles Workflow

For ordinary notes and all add-on routes:

```text
source pack
-> classify source roles
-> remove non-knowledge noise
-> reconstruct conceptual course modules
-> calculate source-adaptive coverage budget
-> select examinable knowledge units
-> write connected explanations
-> add optional question-type overlay
-> run public-surface, density and layout QA
```

Output should explain what each concept is, why it matters, how the mechanism, method or calculation works, and what result, limitation or interpretation follows.

---

## 3. Source Roles

Classify every source before using it:

- `subject_knowledge`: definitions, mechanisms, structures, pathways, experiments, methods, calculations, graphs, data patterns, examples, diagnostic rules and limitations.
- `practical_operation`: apparatus, reagents, protocol logic, controls, safety handling, calculations and interpretation rules.
- `exam_pattern`: question form, command verbs, mark operations and repeated discriminators.
- `extra_reading`: verified books, chapters, papers or academic sources that deepen source logic.
- `style_or_layout_example`: reference output used only for structure, density and layout.
- `non_knowledge_noise`: admin, logistics, contact details, attendance systems, URLs, decorative text, OCR debris, file titles and slide artifacts.

Only `subject_knowledge`, relevant `practical_operation`, and verified `extra_reading` may become public knowledge prose. Past papers shape emphasis and answer operations only. Cross-unit examples never provide facts for a new target unit.

---

## 4. Noise Filter

Discard from ordinary public notes:

- lecturer names, emails, phone numbers, staff lists, office details and coordinator details;
- attendance systems, QR codes, room/timetable instructions, platform instructions and live-session text;
- assessment logistics unless the user asks for a separate exam-analysis brief;
- bookshop adverts, library availability, URL-only lines, image credits, copyright lines, acknowledgements and decorative quotations;
- slide agendas, contents pages, generic learning outcomes and generic advice unless rewritten into a specific knowledge claim;
- raw slide bullets, file-title lists, broken OCR fragments, font names, page artifacts and extraction debris.

A `Course Knowledge Map` must be conceptual. It should organise major knowledge modules, not uploaded file names.

---

## 5. Route Table

| User request | Route | Public output |
|---|---|---|
| revise / make notes / go through lectures / general preparation | `exam_prep_notes_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| explicitly source-order walkthrough | `knowledge_walkthrough_docx` | `Lecture_Knowledge_Walkthrough.docx` |
| MCQ / single-best-answer | `mcq_exam_prep` | core walkthrough plus MCQ add-on |
| short answer | `short_answer_exam_prep` | core walkthrough plus short-answer add-on |
| long answer / project / scenario / practical / data / calculation | `long_answer_project_scenario_prep` | core walkthrough plus long-answer/data add-on |
| essay preparation / full essay-style answers | `essay_exam_prep` | core walkthrough plus essay add-on |
| source inventory / lint / release check | `audit_lint_only` or `github_ready_qa` | QA result only |
| past-paper pattern or exam format only | `exam_analysis_brief` | chat-only brief unless a report is requested |

Never apply essay-only logic to MCQ, short-answer, data/problem, practical, project or scenario routes.

---

## 6. Source-Adaptive Coverage Budget

Do not use the same small output size for every course. Scale public knowledge to examinable source volume.

Internal object:

```yaml
SourceScaleBudget:
  source_units_count:
  source_pages_or_slides_estimate:
  source_types:
  conceptual_module_target_range:
  examinable_unit_target_range:
  minimum_visible_coverage_floor:
  compression_reason:
  coverage_floor_status: pass | warn | block
```

Rules:

- A short practical/mock/post-lab pack can be concise when the examinable domain is narrow.
- A medium lecture pack needs enough modules to cover all conceptual areas.
- A broad course pack must not be compressed to the size of a short practical unit.
- Increase coverage when sources contain distinct mechanisms, methods, calculations, disease examples, pathways, data operations, or named experimental evidence.
- Do not use Experimental Biology or any short unit as a size cap for larger courses.
- If output falls below the source-scale floor, block and regenerate from source distillation instead of releasing a short file.

---

## 7. Course Reconstruction

For broad packs, build conceptual modules:

```yaml
CourseModule:
  module_title:
  module_function:
  source_lectures:
  core_questions:
  examinable_units:
```

Preserve source order when it explains prerequisites. Do not create one public module per file if that only repeats filenames. A course map says what the course teaches.

---

## 8. Examinable Knowledge Units

Write public content as coherent units:

```yaml
ExaminableKnowledgeUnit:
  title:
  priority: high | medium | low
  source_support:
  explanation:
  optional_equation_or_example:
  common_confusion_or_boundary:
```

Visible form:

- topic-specific heading;
- connected explanatory prose;
- optional equation, worked example, diagnostic pattern, comparison, table, control or limitation only when useful.

Every major unit should answer, when source support exists:

```text
What is the concept/method?
Why does it work biologically, chemically, clinically, quantitatively or experimentally?
How does the mechanism or calculation proceed?
What consequence, readout, limitation or diagnostic meaning follows?
```

Do not write notes as slot dumps:

```text
Definition: ...
Components: ...
Workflow: ...
Logic: ...
Interpretation: ...
```

Bullets are allowed only after an explanatory lead sentence and only for naturally parallel items. Bullets must not replace explanation.

---

## 9. Protected Source Coverage

Before compression, build or conceptually maintain a `SlideAtomicLedger`.

Protected units include:

- learning outcomes that contain specific examinable concepts;
- lecture, slide, page or practical-problem headings;
- official definitions;
- contrast pairs;
- criteria, stages, classes and component lists;
- named examples and named experiments;
- diagram labels, table rows and graph axes that teach content;
- equations, calculations, units and workflows;
- “Why X?” explanatory blocks;
- summary or take-home points;
- formal-past-paper terms and operations.

Every protected unit must either appear in public knowledge output or be explicitly classified as duplicate, administrative, unreadable, unsupported, or internal-audit-only. Silence is not valid.

`PastPaperTermMustAppear`: when a formal paper, mock, practical problem or answer key uses a term, calculation, graph operation, reagent, method or diagnostic distinction that is course-backed, it becomes a protected public mention. Past-paper terms increase protection and density; they do not invent new facts.

`ZeroMentionLint`: fail if a protected official term has zero visible mentions; a past-paper-backed term is omitted; a diagram/table/equation is referenced only as “the graph/figure”; a calculation appears without units or conversion logic; a method workflow lacks principle, readout or interpretation; or a named example is deleted because a broad module title seemed to cover it.

---

## 10. Knowledge Surface Contract

Student-facing output must contain knowledge only.

Allowed public functions:

- definition or boundary;
- mechanism, pathway, process, method, assay, calculation, graph/data rule, diagnostic rule or comparison;
- source-backed example or experimental result plus interpretation;
- limitation, caveat, exception or scope boundary;
- synthesis that improves biological, clinical, methodological or quantitative understanding.

Forbidden public functions:

- source-route narration;
- AI process or provenance;
- audit trace;
- generic study advice;
- exam-meta/prediction trace;
- rigid template bucket;
- colon-slot fragmentation;
- shorthand arrow-chain as final explanation;
- evidence-justification trace;
- decorative transition.

Forbidden visible patterns include:

```text
This slide shows...
The first slide shows...
The second slide shows...
The slide says...
The notes say...
According to page...
PPT page...
English explanations extracted from...
AI generated this...
I extracted...
How to use this document
How to answer
A strong answer should...
Use this module...
Recommended approach
Exam strategy
Integrated reasoning
Coverage note
Evidence used
Source map
QA flag
```

Do not mechanically render every point as:

```text
Definition:
Principle:
Mechanism:
Application:
Limitation:
Graph logic:
Interpretation:
```

Do not replace those with new repeated pseudo-labels such as:

```text
Components:
Workflow:
Exclusion logic:
Binding logic:
Protein charge:
Elution mechanism:
Formula:
Logic:
Reason:
Safety:
Failure mode:
```

Preferred heading style:

```text
Beer-Lambert conversion from A440 to product concentration
Initial rate is the concentration slope at the start of the reaction
PCR-RFLP turns a SNP into a fragment-pattern difference
pKa controls whether resin functional groups carry charge
```

---

## 11. Label Decision

Every visible label must pass:

```yaml
SurfaceLabelDecision:
  label:
  function:
  decision: keep | merge_into_heading | merge_into_sentence | delete
  reason:
```

Keep labels only for equations, worked examples, tables, comparisons, diagnostic patterns, controls and calculations when they prevent ambiguity. Delete labels that expose internal scaffolds.

Allowed labels:

```text
Equation
Worked example
Diagnostic pattern
Control
Comparison
Table
```

---

## 12. Public DOCX Surface

For ordinary notes and walkthroughs:

- body text is justified;
- titles, lecture headings and subheadings are left aligned;
- images are centered;
- default line spacing is 1.5;
- text is black Arial in a readable size;
- theme colours, blue heading styles and non-black visible text are forbidden unless the user explicitly asks for colour;
- images preserve aspect ratio and readability;
- avoid large blank areas by fitting images to context and avoiding unnecessary page breaks.

Public notes must not contain source-route narration, AI-process text, source maps, QA flags, evidence scores, confidence bands, internal manifests, helper JSON or raw extraction text.

---

## 13. Practical / Data / Problem Protocol

Use this for practical protocols, problem papers, case studies, numerical assessments, spotters, figures, graphs, tables and answer keys with worked reasoning.

Evidence boundary:

- practical protocols are method/readout/control evidence;
- problem papers and case studies define operation grammar;
- answer keys and worked solutions teach mark-producing reasoning and traps;
- example papers and mocks define format and practice style, not topic recurrence;
- image-only figures require visual inspection before exact values are claimed.

Question operation shape:

```text
input type -> required operation -> expected inference -> limitation/control -> follow-up action
```

Output by operation:

- graph/table: axis reading, trend, anomaly, mechanism, limitation;
- calculation: formula, substitution, units/measurement convention, sanity check;
- protocol: aim, principle, steps, controls, expected readout, failure modes;
- case/scenario: key facts, mechanism, differential explanation, decision point;
- spotter/image: diagnostic features, distractors, confidence limits;
- method comparison: suitability criteria, readout, resolution, cost/risk, limitation.

Do not output only topic labels for practical/data/problem exams.

Core calculation rules to preserve when relevant:

- Beer-Lambert: `A = εcl`; `c = A/(εl)`; rate in concentration units = slope/(εl).
- Dilution: `C1V1 = C2V2`; amount = concentration × volume.
- CFU/ml: colonies × dilution factor × (1000 µl / volume plated in µl).
- Transformation efficiency: total transformants in whole mix / µg DNA added.
- Conjugation frequency: transconjugants per ml / recipient cells per ml or per donor cells per ml.
- SDS-PAGE calibration: plot `log10(MW)` against migration distance in the linear region.

---

## 14. MCQ Route

For MCQ-heavy exams, predict discriminator axes and distractor families, not long model answers and not exact stems.

Default student-facing output is point-card style:

```yaml
MCQStudentPointCard:
  priority: ★★★ | ★★ | ★
  point:
  knowledge_explanation:
  how_exam_tests_it:
  common_traps:
  must_remember:
```

Do not include practice questions, answer keys, contrast tables, separate trap banks, source anchors, confidence, evidence, examiner-operation labels or discriminator-axis labels in the default MCQ high-yield report. Fold wrong-option logic into `common_traps`.

Do not claim an official answer unless an answer key or official solution is supplied. If no answer key exists, mark answers as `inferred_from_lecture` if needed.

---

## 15. Short Answer Route

Predict question archetype to mark-producing answer schema, not only topic labels. Generate bounded variants from:

```text
archetype + slot grammar + source-linked knowledge point + mark scale
```

Student-facing short-answer report uses module logic plus point cards:

```yaml
ShortAnswerModuleSection:
  module_name:
  module_core_logic:
  high_yield_points:
  point_cards:

ShortAnswerPointCard:
  priority: ★★★ | ★★ | ★
  point:
  common_question_form:
  exam_explanation_with_highlighted_keywords:
  example_answer:
```

Do not show mark-producing schema, required terms, optional examples, reference expansion, common omissions, task verb, confidence, evidence or source anchor as separate student-facing fields. Bold required terms inside explanation. Put scoring logic into a natural `example_answer`.

---

## 16. Long Answer / Project / Scenario Route

Use `long_answer_project` when the paper is non-essay but requires paragraph-style project, scenario, method-design, research-proposal, readout-interpretation or control/limitation answers.

Common method-driven archetypes:

- design purification strategy;
- choose and justify characterisation methods;
- assess folding, secondary, tertiary or quaternary structure;
- quantify binding or dimerisation affinity;
- interpret mutation effect;
- determine interaction interface;
- determine atomic/high-resolution structure;
- compare structural biology methods;
- quantify enzyme activity or substrate specificity;
- explain chaperone/folding mechanism;
- identify in vivo or biotechnological caveats.

Every long-answer archetype requires:

```text
lecture principle -> scenario-specific method choice -> expected readout -> interpretation -> limitation/control
```

When a user asks for a model answer for this exam type, generate a high-score example long answer, not a generic essay. Structure by question parts, mark weights, method logic, readouts, interpretation and controls.

Old short-answer or coverage-only papers may support concept coverage only unless exam-format parsing proves the same regime.

---

## 17. Essay / Example Essay Route

Complete Example Essays are generated only when explicitly requested.

For essay/problem-essay prediction, default prediction object is a theme-level scope, not exact question wording. Use `Predicted essay theme` only inside chat-only exam-analysis brief or explicit audit/selection note. Practice stems are labelled `Practice variant from predicted theme`.

For complete essay planning or assessed-style drafting, collect constraints, build subtitle-level plan, and pass plan-approval gate unless the user explicitly requests direct generation.

Full essay generation requires:

- question deconstruction;
- lecture scope;
- knowledge inventory;
- lecturer/source intent when evidence supports it;
- paragraph plan;
- Extra Reading insertion decision;
- high-score essay when explicitly requested;
- paragraph function map;
- exclusion list;
- self-check.

Paragraph pattern:

```text
claim -> mechanism/process/evidence -> scope or limitation -> consequence -> link back
```

Do not write slide-by-slide summaries. Each paragraph must serve the command verb. If the question has a maximum word count and no minimum, maximise relevance per word. Do not pad.

---

## 18. Example Essay DOCX Rules

Default essay-prep output:

```text
Essay_Module_Example_Essays.docx
```

If separate essay files are requested:

```text
EE01_<short_safe_question_title>.docx
EE02_<short_safe_question_title>.docx
EE03_<short_safe_question_title>.docx
```

Final essay DOCX structure:

- Title paragraph.
- Optional subtitle containing only exact essay question or approved topic wording.
- Numbered section headings if useful.
- Body paragraphs in continuous essay prose.
- Figure captions only if figures are explicitly included or requested.

Forbidden visible DOCX text:

```text
Model answer built from...
This is not a predicted exam question
Exam-style question
Question:
Essay Topic:
Example essay
Example Essay
Source coverage
No mark scheme supplied
source-basis or confidence disclaimers
```

If source-basis note is useful, put it in chat response or internal audit, not inside the student-facing essay DOCX.

Essay formatting:

- margins: 2.5 cm;
- font: Arial;
- line spacing: 1.5;
- paragraph spacing before/after: 0 pt;
- body alignment: justified;
- title centered;
- subtitle and section headings left aligned;
- no empty spacer paragraphs;
- subtitle is plain, not bold, not italic, not enlarged.

---

## 19. Essay Adaptive Budget And Extra Reading

Use:

```yaml
EssayAdaptiveBudget:
  question:
  command_verb:
  lecture_scope: single_concept | one_lecture | multi_lecture | whole_module | cross_module
  core_source_skeleton_words:
  mechanism_detail_target_ratio: 0.10-0.15
  extra_reading_target_ratio: 0.10-0.15
  estimated_total_word_range:
  conclusion_required: true
  compression_policy: expression_efficiency_not_fixed_count
```

Rules:

- Do not hard-code 500-1000 words.
- Word count follows question demand, lecture scope, source content and evidence density.
- Add molecular, cellular, receptor, channel, pathway, morphogen, assay, circuit, gene or method detail only when it sharpens a lecture/source mechanism slot.
- Add Extra Reading or paper detail only when verified, source-anchored, question-relevant and analytically interpreted.
- Treat 10-15% mechanism detail and 10-15% Extra Reading as target bands, not padding quotas.
- If insufficient verified material exists, do not fabricate or inflate.
- A complete essay requires a conclusion unless the user asks for a fragment.
- The conclusion synthesises and introduces no new evidence.

---

## 20. Citation And Highlight Rules

Use Word highlight, not font colour.

Highlight mapping:

- Uploaded Extra Reading Books or matched textbook chapters: yellow highlight.
- Verified Citation / Extra Reading Papers: green highlight with parenthetical author-year citation.
- Lecture-slide cited original papers after resolution/reading: green highlight with parenthetical author-year citation.
- Verified classic experimental sources used as fallback: green highlight with parenthetical author-year citation.
- Ordinary lecture material: no highlight.

Rules:

- Yellow only for content derived from user-uploaded Extra Reading books/chapters.
- Green only for verified papers, lecture-cited original sources that were resolved/read, or verified classic experiments.
- Do not yellow-highlight papers.
- Do not green-highlight citations copied from secondary sources unless the original source was read or verified.
- Highlight only the source-derived phrase, clause or sentence; do not over-highlight lecture-derived synthesis.
- Highlighting does not justify inclusion. Highlighted content must pass question relevance and source-anchor checks.
- Paper clauses require parenthetical author-year citation. Do not write author-led prose such as `Author et al. showed...` unless the user asks for literature history.

Fail an essay if paper-derived content is not green-highlighted, uploaded book/chapter content is not yellow-highlighted, green-highlighted content lacks parenthetical author-year citation, highlighted content is broader than the source-derived phrase/clause, or highlight exists only to increase Extra Reading ratio.

---

## 21. Essay Language Quality

Rules:

- Start with the answer/problem, not metacommentary.
- Balance descriptive and analytic prose across the essay.
- Prefer direct positive claims; use negative framing only when needed to mark a boundary.
- Avoid A-B-A logic: do not state a claim, insert setup, then restart the claim if the setup can be integrated into the same sentence.
- Examples must prove, distinguish or limit a claim.
- Conclusions synthesize and do not list every body section.
- Compress by deleting low-function sentences, not protected mechanisms.
- Use lecture/source logic as skeleton; Extra Reading sharpens it.
- Do not cite-stack.
- Calibrate citation strength.

Default paragraph shape:

```text
claim/problem -> mechanism/process/evidence -> interpretation/scope -> consequence -> link back
```

---

## 22. Scientific Precision Gate

Before final prose with named scientific, biomedical, clinical, quantitative, methodological or sector-level details:

- collapse aliases;
- classify entity categories: gene, transcript, protein, receptor, channel, ligand/morphogen, cell type, circuit element, anatomical structure, pathway, assay, method, chemical species, disease/patient group, company/case, regulatory body, quantitative parameter;
- do not mix entity categories in one flat list unless the relation is explicit;
- do not use a gene name as protein/receptor/pathway/disease phenotype unless supported;
- use evidence ladders when several evidence streams support one mechanism;
- keep named detail only when it changes mechanism, identifies measured/manipulated object, explains evidence/limitation, distinguishes answers or improves exam transfer;
- calibrate claim strength.

Preferred claim-strength wording:

- association/correlation -> associated with, linked to, consistent with;
- model perturbation -> supports, contributes to, is required under these conditions;
- rescue experiment -> supports a causal role in that model;
- review synthesis -> suggests, implicates, supports;
- case/company example -> illustrates, exemplifies.

Reject true-but-useless catalogues, overclaiming, unverified citations and extra reading that replaces lecture logic.

---

## 23. Visual And Image Handling

When sources contain diagrams, tables, figures, slides, graphs or image-only content, inspect visuals when possible. Do not infer hidden content from weak OCR.

Preserve when knowledge-bearing:

- labels;
- axes;
- workflows;
- readout interpretation;
- figure conclusions;
- experimental conditions;
- controls;
- source limitations.

If visual content may affect the answer but cannot be inspected, state the limitation and avoid unsupported claims.

For notes DOCX, center images and scale them to the content area while preserving aspect ratio and readability. Image readability has priority over page-count minimisation.

---

## 24. Custom GPT Output Channel Gate

Use direct chat for small outputs:

- estimated final output <=4 pages;
- or approximately <=2,500 English words;
- or approximately <=4,500 Chinese characters;
- and readable in one answer.

Use Word by default for long/full artifacts:

- full notes;
- complete walkthroughs;
- complete essays;
- full reports;
- question packs;
- dense synthesis;
- graph/table-heavy work;
- repeated examples;
- anything likely >=5 pages.

If Word is generated, chat response stays short:

- file name/link;
- 3-6 bullet summary;
- material evidence limitations only.

Do not provide both a full chat answer and full Word file unless explicitly requested.

---

## 25. Hard Failures

Fail and rewrite if public output contains:

- admin, logistics, staff, contact or attendance material;
- file-title course maps instead of conceptual maps;
- raw slide bullets or broken OCR fragments;
- copied extraction text instead of explanation;
- dense lists of names without mechanisms;
- repeated `Definition`, `Components`, `Workflow`, `Logic`, `Graph logic` or equivalent labels;
- shorthand arrow chains used as main explanation;
- broad source pack compressed below the source-adaptive coverage floor;
- unsupported claims, fake citations or over-strong scientific claims;
- unbound protected source units;
- public AI-process text, source anchors, QA JSON, manifests or lineage files;
- non-black visible text, theme-colour headings, non-Arial text, wrong alignment or non-1.5 line spacing;
- complete essay without a conclusion;
- paper/book source-class highlight errors.

---

## 26. Recommended Builder Pairing

Upload this file as GPT Knowledge. Use `Everything-Exam-Prep-CustomGPT-Instructions.txt` as the GPT Builder Instructions. Enable file upload and Code Interpreter/Data Analysis if available. Do not upload private course sources as persistent GPT Knowledge; upload them in each conversation instead.
