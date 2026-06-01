# Knowledge Surface Protocol

This protocol controls the last public-rendering layer for all student-facing outputs. It sits after evidence extraction, source structuring, planning, and route-specific drafting.

The problem it prevents is not factual inaccuracy alone. It prevents the Skill from exposing planning scaffolds, source-route narration, AI process notes, rigid bucket labels, colon-slot fragments, or shorthand flow charts as if they were revision content.

```text
AtomicKnowledgeLedger -> PublicKnowledgeUnit -> KnowledgeSurfaceContract -> NonKnowledgeGate -> SurfaceFormGate -> LabelDecision -> Student DOCX
```

## Core Rule

Student-facing output must contain knowledge only.

A public sentence, heading, bullet, table row, figure caption, or note is allowed only if it performs one of these functions:

- defines a term or boundary;
- explains a mechanism, pathway, process, method, assay, calculation, graph, data readout, diagnostic rule, or comparison;
- gives a source-backed example or experimental result and interprets what it shows;
- states a limitation, caveat, exception, or scope boundary that changes understanding;
- connects concepts in a way that improves biological, clinical, methodological, or quantitative understanding.

A public item is forbidden when its main function is to describe the Skill, the source route, the AI workflow, the exam-prediction workflow, the evidence audit, or how the student should use the document.

## KnowledgeSurfaceContract

Use this object before any public DOCX is written:

```yaml
KnowledgeSurfaceContract:
  contract_id:
  route:
  allowed_public_functions:
    - definition
    - mechanism
    - process
    - method_workflow
    - assay_readout
    - calculation
    - graph_data_rule
    - diagnostic_rule
    - comparison
    - example_interpretation
    - limitation_or_scope
    - synthesis
  forbidden_public_functions:
    - source_route_narration
    - ai_process_or_provenance
    - audit_trace
    - generic_study_advice
    - exam_meta_or_prediction_trace
    - rigid_template_bucket
    - colon_slot_fragmentation
    - shorthand_arrow_chain
    - evidence_justification_trace
    - decorative_transition
  label_policy:
    mode: semantic_sparse
  density_policy:
    mode: source_adaptive
  layout_policy:
    body_alignment: left
    image_alignment: centered
    title_alignment: left
    heading_alignment: left
    line_spacing: 1.05-1.15
    image_scaling: readability_preserving_auto_fit
  qa_status:
```

The contract is route-independent. `exam_prep_notes_docx`, `knowledge_walkthrough_docx`, `mcq_exam_prep`, `short_answer_exam_prep`, `long_answer_project_scenario_prep`, and `essay_exam_prep` all pass through it.

## Explanatory Knowledge Unit

A public knowledge point should be written as a coherent explanatory unit, not as a shredded list of slots.

Every major point should answer four questions when the source material supports them:

```text
What is the concept or method?
Why does it work biologically, chemically, clinically, quantitatively, or experimentally?
How does the mechanism or calculation proceed?
What consequence, readout, limitation, or diagnostic meaning follows?
```

The output should normally use one topic-specific heading followed by one or more connected paragraphs. Bullets are allowed only when they list naturally parallel items after an explanatory lead sentence. Bullets must not be used to replace the explanation.

Bad public surface:

```text
Binding logic: at pH 7, CM Sephadex is negatively charged.
Protein charge: cytochrome c is positive.
Elution mechanism: NaCl competes.
Failure mode: wrong pH prevents elution.
```

Good public surface:

```text
CM Sephadex works as a cation exchanger because its carboxymethyl groups are deprotonated at the working pH and carry negative charge. Cytochrome c remains net positive under the same condition because it has many basic residues and a high pI, so electrostatic attraction holds the protein on the resin during loading and washing. NaCl elutes cytochrome c by raising ionic strength, competing for charged sites and shielding charge interactions; if pH or salt is wrong, the target can either flow through during loading or remain bound during elution.
```

## Non-Knowledge Classes

### 1. Source-route narration

Reject wording whose main purpose is to report where a claim came from or how slides/pages were ordered.

Forbidden visible patterns include:

```text
This slide shows...
The first slide shows...
The second slide shows...
The slide says...
The slide mentions...
The notes say...
According to page...
PPT page...
English explanations extracted from...
```

Rewrite by deleting the source-route wrapper and keeping only the knowledge.

Bad:

```text
The second slide shows the opposite side of the body.
```

Good:

```text
The crossed extensor reflex activates contralateral extensors and inhibits contralateral flexors so the unstimulated limb supports body weight.
```

### 2. AI process or provenance

Reject public text that describes AI activity, prompt instructions, extraction method, or generation evidence.

Forbidden visible patterns include:

```text
AI generated this...
I extracted...
I used the image/text to...
Generated from ChatGPT...
This document was produced by...
Only knowledge points are included...
I did not include how-to-answer content...
```

Public notes must not state what the AI did or chose not to do. The output itself must simply be the knowledge.

### 3. Audit trace and evidence justification

Reject public source maps, coverage notes, confidence notes, quality caveats, ELM warnings, internal QA flags, run manifests, citation logs, source anchors, and statements explaining why the Skill trusted or rejected material.

Keep these only in internal QA or in an explicitly requested audit package.

### 4. Generic study advice and answer coaching

Reject public prose such as:

```text
How to use this document
How to answer
A strong answer should...
Use this module...
Recommended approach
Exam strategy
Integrated reasoning
```

If the sentence contains real knowledge, rewrite only the knowledge. If it is pure advice, delete it.

### 5. Rigid template buckets and colon-slot fragmentation

The Skill must not mechanically render every point as:

```text
Definition:
Principle:
Mechanism:
Application:
Limitation:
Graph logic:
Interpretation:
```

It must also not replace those labels with a new set of equally fragmented labels:

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

These labels are allowed only when the label is genuinely needed for readability and the labelled block is the natural content type. They are not a required sequence. A high density of different `Label: sentence` lines is a public-surface failure even when each individual label seems plausible.

Preferred public heading style is semantic and topic-specific:

```text
Beer-Lambert conversion from A440 to product concentration
Initial rate is the concentration slope at the start of the reaction
PCR-RFLP turns a SNP into a fragment-pattern difference
pKa controls whether resin functional groups carry charge
```

The reader should see the concept first, not the planning bucket.

### 6. Shorthand arrow chains

Do not use arrow chains as final public explanation when a mechanism or workflow needs understanding.

Bad:

```text
CM Sephadex at pH 7 -> COO- resin -> cytochrome c positive -> binding -> NaCl -> elution
```

Good:

```text
At pH 7, CM Sephadex is negatively charged because its carboxyl groups are deprotonated. Cytochrome c is net positive under the same condition, so it binds to the resin by electrostatic attraction. A high NaCl concentration weakens that attraction by increasing ionic strength, competing for charged sites and shielding charges, allowing cytochrome c to elute.
```

If the user explicitly requests a workflow summary, use compact bullets with explanatory clauses rather than arrows.

## LabelDecision

Every visible label must pass this decision:

```yaml
SurfaceLabelDecision:
  label:
  function:
  decision: keep | merge_into_heading | merge_into_sentence | delete
  reason:
```

Keep labels for equations, worked examples, tables, comparisons, diagnostic rules, and calculations when they prevent ambiguity. Delete or merge labels that merely expose the internal scaffold.

Allowed label examples:

```text
Equation
Worked example
Diagnostic pattern
Control
Comparison
Table
```

## Notes And Walkthrough Rendering

`exam_prep_notes_docx` and `knowledge_walkthrough_docx` should use explanatory knowledge modules.

Allowed public structure:

```text
Title
Lecture Title
Topic-specific module heading
Connected explanatory prose
Optional equation, worked example, method workflow, comparison, or limitation block when useful
```

Forbidden public structure:

```text
How To Use This Document
What This Lecture Is About
What This Module Explains
The first slide shows...
The notes are organised by...
Definition / Principle / Limitation repeated for every point
Components / Workflow / Logic repeated as pseudo-explanation
Arrow chains used as the main explanation
Coverage note
Evidence used
AI process note
Course Knowledge Map
Predicted Essay Theme
Section A Strategy
```

`Course Knowledge Map` and equivalent course-map top matter are internal-only for ordinary notes and walkthroughs.

## DOCX Layout Surface

For `exam_prep_notes_docx` and `knowledge_walkthrough_docx`:

- body text, titles, lecture headings and all subheadings are left aligned;
- images are centered;
- default line spacing is compact, 1.05-1.15;
- body text uses black Arial in a readable size;
- route images are scaled automatically to the available content area, preserving aspect ratio and avoiding upscaling that reduces readability;
- large blank areas inside Word pages should be reduced by fitting images to page context and by avoiding unnecessary page breaks;
- image readability has priority over page-count minimisation.

## Practical And Data Notes

For practical/data/problem material, preserve equations, units, workflows, graph rules and numerical anchors, but write them as explanations rather than as the same mini-template.

Bad:

```text
Formula: Resin-COOH ⇌ Resin-COO- + H+
Logic: below pKa, resin loses negative charge
Formula: Resin-amine + H+ ⇌ Resin-amine-H+
Logic: below pKa, amine is positive
```

Good:

```text
pKa marks the pH at which an ionisable group is half protonated and half deprotonated. For a carboxyl resin group, Resin-COOH ⇌ Resin-COO- + H+: the protonated COOH form is neutral, whereas the deprotonated COO- form is negatively charged. Below the carboxyl pKa, high H+ favours COOH and the resin loses negative charge; above the pKa, COO- dominates and the resin can bind positively charged proteins. For an amine resin, the protonated form is positive, so it binds anions below its pKa and loses positive charge when deprotonated above its pKa.
```

Use labelled blocks only for genuinely separate items such as `Equation`, `Worked example`, `Diagnostic pattern`, or `Control`.

## Example Essay Surface

Example Essays are not notes. They require continuous essay prose, adaptive length, citations/highlights where source class requires them, and a conclusion.

Use this internal budget object:

```yaml
EssayAdaptiveBudget:
  question:
  command_verb:
  lecture_scope:
    - single_concept
    - one_lecture
    - multi_lecture
    - whole_module
    - cross_module
  core_source_skeleton_words:
  mechanism_detail_target_ratio: 0.10-0.15
  extra_reading_target_ratio: 0.10-0.15
  estimated_total_word_range:
  conclusion_required: true
  compression_policy: expression_efficiency_not_fixed_count
```

Rules:

- Do not hard-code 500-1000 words.
- Word count follows question demand, lecture scope, amount of examinable source content, and required evidence.
- Add molecular, cellular, receptor, channel, pathway, morphogen, assay, circuit, gene, or method detail only when it sharpens a lecture/source mechanism slot.
- Add Extra Reading or academic-paper detail only when it is verified, source-anchored, question-relevant, and analytically interpreted.
- Treat 10-15% mechanism-detail and 10-15% Extra Reading as target bands, not padding quotas. If insufficient verified material exists, do not fabricate or inflate.
- The conclusion is mandatory unless the user explicitly asks for a fragment rather than a complete essay.
- The conclusion must synthesise the answer and should not introduce new evidence.

## Highlight Surface Rules For Essays

Highlighting is a source-bound rendering rule, not a style choice.

- Uploaded Extra Reading Books or matched textbook chapters: yellow highlight.
- Verified Citation / Extra Reading Papers: green highlight with parenthetical author-year citation.
- Lecture-slide cited original papers after resolution/reading: green highlight with parenthetical author-year citation.
- Verified classic experimental sources used as fallback: green highlight with parenthetical author-year citation.
- Ordinary lecture material: no highlight.

Fail the essay if:

- academic paper content is not green-highlighted;
- uploaded book/chapter Extra Reading content is not yellow-highlighted;
- green-highlighted content lacks a parenthetical author-year citation;
- highlighted content is broader than the source-derived phrase or clause;
- the highlight exists only to increase the Extra Reading ratio.

## Publish Gate

Before publishing any public DOCX, run this sequence:

```text
1. Surface function scan: every visible item must be knowledge-bearing.
2. Non-knowledge scan: reject source-route narration, AI process, audit trace, study advice, and exam-meta leakage.
3. Explanatory-form scan: reject colon-slot fragmentation and shorthand arrow chains when they replace explanation.
4. Label-decision scan: delete or merge rigid template labels unless the label is semantically necessary.
5. Route-style scan: notes use black Arial, left-aligned headings, left-aligned body text, centered images, compact 1.05-1.15 spacing, and readability-preserving image fit.
6. Essay-specific scan: adaptive budget, conclusion, source-class highlights, citation colour, and word-count efficiency.
```

If any scan fails, rewrite the public surface rather than adding a disclaimer.
