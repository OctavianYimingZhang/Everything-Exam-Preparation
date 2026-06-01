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
  public_lecture_sections: list[PublicLectureSection]
```

The visible top matter is only the document title. `Course Knowledge Map`, `Source Role Summary`, extraction limitations, prediction sections and generic exam advice stay internal unless the user explicitly requests a separate audit or exam-analysis report.

Compact Public Notes Rule:

- Internally, decompose sources into atomic knowledge items and protect every source-backed definition, criterion, mechanism, method, example, equation, graph, table, and workflow.
- Publicly, render compact lecture-level exam notes. Do not expose the internal card scaffold.
- The public route is lecture-first: each official lecture/session becomes a visible lecture section, with concept-specific modules inside it.
- Group protected atomic items into readable public points using concise paragraphs, bullets, equations, examples, comparisons, and mechanism chains.
- Coverage must be complete; formatting must be compact.
- Compact lecture notes and compatibility walkthroughs use Arial, 2.0 cm margins, compact 1.05-1.15 line spacing, left-aligned body text, black text, and lecture page breaks. Essay-style 2.5 cm margins, 1.5 spacing, and justified body text are reserved for Example Essay outputs.
- A hard knowledge-only rendering gate applies before public DOCX writing. Ordinary notes and compatibility walkthroughs must not render generic advice sections such as `How To Answer`, `How To Use`, `Integrated reasoning`, `Integrated practical reasoning`, `Answer Logic`, `Exam Strategy`, `Recommended Approach`, `A strong answer should`, `Use this module`, or question-type reliability commentary. Keep only the underlying source-backed knowledge, rewritten as knowledge points, definitions, method workflows, calculations, graph/data rules, comparisons, examples, or limitations.
- A public-point consistency gate applies before DOCX writing. Every visible internal KnowledgeCard must map to at least one public point, every public point must reference real source cards, and public point, block, and coverage-binding atomic-unit sets must agree.

Visible public module:

```yaml
PublicLectureSection:
  lecture_title: string
  lecture_scope: string
  modules: list[PublicLectureModule]

PublicLectureModule:
  module_title: string
  knowledge_functions: list[
    definition_boundary | mechanism_process | method_readout | graph_data_interpretation | calculation_unit_worked_example | named_example | limitation_trap
  ]
  explanation: string
  blocks: list[PublicPointBlock]

PublicPointBlock:
  block_type: definition | mechanism | method | graph_data | calculation | example | limitation | comparison | table | explanation
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
