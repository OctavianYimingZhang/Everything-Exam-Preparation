# Student-Facing Output Policy

The Skill may use source anchors, evidence claims, confidence bands, examiner-operation labels, recurrence, lecture centrality, scoring logic, and source coverage internally. Student-facing outputs must not expose that audit reasoning unless the user explicitly asks for an audit package.

Student-facing exam-prep outputs must be rewritten as directly usable revision content:

```text
internal reasoning: evidence -> operation -> priority -> output type
student output: priority -> public point -> explanation -> knowledge-bearing blocks
```

Ordinary Academic Exam-Ready Notes are knowledge documents, not exam-format audits. They must not display assessment percentages, exam timing, mark splits, Section A/Section B administrative rules, historical-paper comparability notes, `Coverage note` warnings, source-quality caveats, ELM-check warnings, or provenance/audit explanations. Keep those items internal unless the user explicitly requests an audit package.

## Forbidden Visible Fields

Do not show these fields in ordinary student-facing reports:

- source anchor;
- evidence rationale;
- confidence;
- recurrence count;
- lecture centrality;
- regime match;
- why high-yield;
- examiner operation;
- discriminator axis;
- task verb;
- reference expansion;
- common omissions;
- evidence limit;
- past-paper year mapping;
- prediction score.
- assessment timing;
- mark split;
- current regime;
- older papers;
- no mark scheme;
- coverage note;
- source coverage;
- extraction quality;

Canonical forbidden field IDs:

```text
source_anchor
confidence
evidence
examiner_operation
discriminator_axis
practice_mcq
answer_key
contrast_table
separate_trap_bank
mark_producing_schema
reference_expansion
exam_specificity
core_exam_claim
exam_use
common_error_or_trap
must_master
```

These may appear only in internal QA or an explicit audit package requested by the user.

## Example Essay Visible Boundary

Final Example Essay DOCX files are student-facing essay documents, not audit reports. They must not contain public preambles, source-basis disclaimers, prediction disclaimers, confidence notes, or diagnostic task labels.

Forbidden visible text in final Example Essay DOCX output includes `Model answer built from...`, `This is not a predicted exam question`, `Exam-style question`, decorative `Question:` / `Essay Topic:` subtitle labels, and standalone `Example essay` labels. The document may have a centered title and an optional subtitle containing only the exact essay question or user-approved topic wording.

If source-basis, prediction status, or evidence limitations need to be stated, put them in the chat response or internal QA artefact, not in the Word document.

## Allowed Priority Labels

Use only these visible priority labels when priority is useful:

- `★★★`;
- `★★`;
- `★`.

Meanings:

- `★★★` = answer-producing exam core: standalone definition, mechanism, calculation, graph/data operation, criteria list, method workflow, named source example, or case-study decision point.
- `★★` = supporting examinable knowledge: useful for explanation, comparison, justification, or transfer.
- `★` = background/context: useful framing only; keep brief unless directly tested.

Do not explain why a point is `★★★` by exposing recurrence, confidence, or source-scoring logic. Convert the reason into useful content: what to know, which mechanism or list matters, and which boundary or limitation prevents an error.

## Exam Prep Notes Student Contract

`exam_prep_notes_docx` is the default general-revision route. It emits Academic Exam-Ready Notes in the compatible public artifact `Lecture_Knowledge_Walkthrough.docx`.

Visible structure:

```yaml
ExamPrepNotesStudentContract:
  course_knowledge_map: string
  lecture_mapping: list[string]
  exam_ready_knowledge_notes: list[PublicOutputPoint]
  question_type_addons: list[QuestionTypeAddOn]
  optional_visual_aids: list[GeneratedVisualAidCaption]
```

The visible top matter is `Course Knowledge Map`, not `Course-Level Exam Map`. It may state how the knowledge is organised, list knowledge sections, and map lectures/topics to those sections. Generic exam advice stays internal unless the user asks for a question-type add-on.

Compact Public Notes Rule:

- Internally, decompose sources into atomic knowledge items and protect every source-backed definition, criterion, mechanism, method, example, equation, graph, table, and workflow.
- Publicly, render compact lecture-level exam notes. Do not expose the internal card scaffold.
- Start major modules on new pages only when it improves readability and does not create large blank areas.
- Group protected atomic items into readable public points using concise paragraphs, bullets, equations, examples, comparisons, and mechanism chains.
- Coverage must be complete; formatting must be compact.
- Ordinary notes and compatibility walkthroughs use the Experimental Biology reference surface: Arial, 2.0 cm margins, 1.5 line spacing, left-aligned title/headings, justified body text, black visible text, and centered images. Theme colours, blue heading styles and non-black visible text are never allowed unless the user explicitly asks for colour.
- A hard knowledge-only rendering gate applies before public DOCX writing. Ordinary notes and compatibility walkthroughs must not render generic advice sections such as `How To Answer`, `How To Use`, `Integrated reasoning`, `Integrated practical reasoning`, `Answer Logic`, `Exam Strategy`, `Recommended Approach`, `A strong answer should`, `Use this module`, or question-type reliability commentary. Keep only the underlying source-backed knowledge, rewritten as knowledge points, definitions, method workflows, calculations, graph/data rules, comparisons, examples, or limitations.
- A hard workflow-leakage gate applies before public DOCX writing. Ordinary notes and compatibility walkthroughs must not render selected-route text, workflow plans, source-role maps, source-scale budgets, coverage floor reports, QA gate explanations, internal schema object names, generation-process notes, or statements about what the Skill included or excluded.
- A public-point consistency gate applies before DOCX writing. Every visible internal KnowledgeCard must map to at least one public point, every public point must reference real source cards, and public point, block, and coverage-binding atomic-unit sets must agree.

Final iterative output rules:

- Later user edits override earlier compatible requirements. Before release, build a short internal checklist from the user's last revision instructions and verify the actual DOCX against that checklist.
- Do not overcompress. If the user gives a target character or word range, stay inside it unless protected source content would be lost; if the target is unsafe, use the largest safe compression and say so outside the DOCX.
- Expression efficiency means fewer repeated claims and tighter causal order, not deletion of mechanisms, calculations, controls, worked examples, interpretation rules, limitations or figure/table logic.
- Delete or rewrite sections that only introduce a topic without explaining the examinable mechanism, method, data operation or calculation.
- For bilingual or Chinese-facing outputs with academic English support, academic terms should receive English annotations at first meaningful use, formulas and calculation labels should be in English, and label text before colon-style labels should be English unless the user explicitly asks otherwise.
- If revising from a DOCX and the user says images must not be changed, preserve image objects, order, size and placement as far as the format allows. Do not recreate, crop, recolour or resize images for compression convenience.
- If the user asks to remove sentence-ending full stops, remove Chinese full stops and sentence-final English periods from public body text while preserving decimals, formula notation, file names and necessary scientific abbreviations.
- Render-check the final DOCX when tooling is available. Inspect page images or PDF for missing images, bad table row splits, unreadable tables, large blank gaps, colour drift, blue/theme text, and formatting defects before release.

Visible public point:

```yaml
PublicOutputPoint:
  point_id: string
  lecture_session_id: string
  point_title: string
  priority: ★★★ | ★★ | ★
  point_kind: definition | mechanism | method_workflow | criteria_list | comparison | calculation | graph_or_data_interpretation | canonical_example | compact_background
  main_text: string
  blocks: list[PublicPointBlock]
  covered_atomic_units: list[string]

PublicPointBlock:
  block_type: definitions | key_points | criteria | steps | mechanism | equation | calculation_logic | graph_logic | comparison | example | limitation
  label: string | null
  content: string | list[string]
```

Internal card fields guide planning and QA. They are not public headings. Ordinary Academic Exam-Ready Notes must not render headings named `Exam Specificity`, `Core Exam Claim`, `Exam Use`, `Common Error / Trap`, or `Must Master`. `Canonical Example` remains an internal planning field; public notes should render the knowledge as an `Example` block, explicit user-requested equivalent, or unlabeled paragraph.

`Exam Use`, `Common Error / Trap`, and `Must Master` may appear only in MCQ reports, short-answer add-ons, explicit trap/checklist outputs, or internal QA. In ordinary notes, useful distinctions should be integrated into `comparison`, `limitation`, or the main explanation.

Allowed visible add-on items:

- testable statement;
- possible wrong or distractor statement;
- common trap;
- must-remember rule;
- bounded example question;
- concise example answer;
- required terms bolded inside answer text;
- `Avoid this mistake`;
- essay-ready paragraph block;
- generated schematic caption.

Question-type add-ons must come after the base notes. They do not replace the base notes and must not expose source anchors, recurrence, confidence, internal scoring, or past-paper year mapping.

## MCQ Student Contract

MCQ reports are point-card reports. They must not contain practice questions, answer keys, contrast tables, or a separate trap bank by default.

Visible MCQ Point Card:

```yaml
MCQStudentPointCard:
  priority: ★★★ | ★★ | ★
  point: string
  knowledge_explanation: string
  how_exam_tests_it: string
  common_traps: list[string]
  must_remember: string
```

Forbidden by default:

- practice MCQ;
- answer key;
- contrast table;
- separate trap bank;
- source anchor;
- confidence;
- evidence;
- examiner operation;
- discriminator axis.

If the user explicitly asks for practice questions, generate a separate practice pack rather than adding them into the MCQ high-yield report.

## Short-Answer Student Contract

Short-answer reports have two levels:

- module-level logic, so the student understands how related points connect;
- point-level cards, so the student can write a direct answer.

Visible module section:

```yaml
ShortAnswerModuleSection:
  module_name: string
  module_core_logic: string
  high_yield_points: list[string]
  point_cards: list[ShortAnswerPointCard]
```

Visible point card:

```yaml
ShortAnswerPointCard:
  priority: ★★★ | ★★ | ★
  point: string
  common_question_form: string
  exam_explanation_with_highlighted_keywords: string
  example_answer: string
```

Do not display these as separate fields:

- mark-producing schema;
- required terms;
- optional examples;
- reference expansion;
- common omissions;
- task verb;
- confidence;
- source anchor.

Required terms should be bolded inside the explanation. Mark logic should be absorbed into the `Example Answer` as a natural paragraph, not exposed as a scoring table. Do not split the student answer mechanically into 2/4/6/8-mark versions unless the user specifically asks for that format.

## Long-Answer Student Contract

Long-answer outputs are exam-response playbooks, not general study coaching.

Visible structure:

```yaml
LongAnswerStudentItem:
  topic: string
  core_exam_problem: string
  likely_question_forms: list[string]
  answer_order: list[string]
  reusable_answer_blocks:
    mechanism_block: string
    method_or_readout_block: string
    interpretation_block: string
    control_or_limitation_block: string
  example_answer: string
  adaptation_rules: list[string]
  must_include: list[string]
  avoid_overwriting: list[string]
```

Do not show evidence, source, confidence, recurrence, or why the operation is likely.

## Essay Student Contract

Essay outputs are module-level packs only when the user explicitly asks for essay preparation or complete Example Essays.

Visible structure:

```yaml
EssayModulePack:
  module_name: string
  essay_title: string
  core_thesis: string
  full_example_essay: string
  adaptation_map: list[string]
  key_paragraph_bank: list[string]
  essential_terms: list[string]
  likely_stem_variants: list[string]
```

The useful student-facing pair is:

```text
Full Example Essay + how to adapt it to specific essay questions
```

Do not generate Essay Module Packs as the default revision product.

## Visual Aid Student Boundary

Generated visual aids may be embedded or attached only as revision schematics. The visible caption must state that the image is generated for revision and is not an official course figure.

Do not use a generated image as evidence, a citation, an official answer, or a replacement for written explanation. If the platform cannot generate images, omit the visual-aid section from the student-facing output.
