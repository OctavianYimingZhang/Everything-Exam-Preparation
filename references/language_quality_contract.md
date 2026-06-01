# Language Quality Contract

This contract is the shared prose-quality standard for lecture walkthrough explanations, question-type reports, Example Essays, long-answer model answers, and any essay-style revision output.

The contract is subject-independent. Biological, chemical, quantitative, clinical, methodological, and sector-level essays use different factual evidence, but the same language discipline.

## Academic Exam-Ready Notes Prose Policy

For `exam_prep_notes_docx`, write notes as exam-ready academic synthesis, not as tutor narration or slide commentary.

Use internal planning functions such as these to decide content, but do not force them into public headings:

- `Core Exam Claim`;
- `Key Definitions`;
- `Exam-Ready Knowledge Synthesis`;
- `Criteria / Components / Steps`;
- `Mechanism / Process Logic`;
- `Canonical Example`;
- `Exam Use`;
- `Common Error / Trap`;
- `Must Master`.

Ordinary Academic Exam-Ready Notes render compact public points and knowledge-bearing blocks. Public labels stay in default English unless the user explicitly requests another language or mixed-language output; schema field names and Skill package files remain English.

Avoid:

- `In this section we will learn...`;
- `This slide explains...`;
- `The notes are trying to say...`;
- `You should understand...`;
- source-route narration such as page, slide, or upload-order commentary inside the answer body.

The public paragraph shape is:

```text
examinable claim or problem -> mechanism/process -> source-backed example when useful -> scope or limitation -> concrete application when it adds knowledge
```

Do not preserve the original notes' order when that order is weaker than the exam logic, but do preserve the source-first baseline coverage of protected definitions, contrast pairs, criteria lists, named examples, diagrams, tables, equations, calculations, and workflow items before applying exam overlay.

## Core Paragraph Shape

Every substantive paragraph should have a visible function:

```text
claim or problem -> mechanism/process/evidence -> scope or limitation -> consequence -> link back
```

Acceptable variants:

- `debate -> model A -> model B -> evidence -> evaluation`;
- `evidence -> mechanism -> interpretation -> limitation`;
- `question demand -> method principle -> readout -> interpretation -> control`;
- `shared problem -> comparison axis -> contrast -> synthesis`;
- `sector/system problem -> example evidence -> implementation mechanism -> wider implication`.

Across a complete Example Essay, keep descriptive and analytic material in balance. A good default is roughly half descriptive content and half analytic content:

- descriptive content states the relevant fact, mechanism, source-backed detail, experiment condition, pathway, case, or observed result;
- analytic content explains why the detail matters, what it proves or fails to prove, which boundary it sets, which mechanism it distinguishes, or how it answers the question.

Do not solve weak analysis by adding a decorative sentence at the end. Integrate analysis into the factual sequence so that evidence and interpretation stay adjacent.

## Required Rules

- Start with the answer or problem, not with metacommentary.
- Prefer direct positive claims. Use negative framing only when the false model is examiner-relevant and the contrast must be stated.
- Preserve necessary mechanisms when compressing language.
- Remove repeated definitions, repeated claims, decorative transitions, and low-value case details.
- Remove lecture-route narration and exam-guidance phrasing from the answer body.
- Add words only when they add mechanism, evidence, interpretation, limitation, or a required contrast.
- Add named biological, chemical, quantitative, clinical, methodological, or sector-specific detail only when it sharpens a lecture/source-derived mechanism slot or evidence function.
- When writing essay/problem-essay prediction outputs, phrase the prediction as an examinable theme with scope and operation, not as a guaranteed future question.
- Use examples as evidence for a wider claim.
- Convert experiments, data, and examples into evidence, mechanism, interpretation, and limitation when the question is evidence-heavy.
- Make contrasts explicit; do not rely on ambiguous `rather than` phrasing.
- Do not open with a negative-only sentence and then restate the correct claim in the next sentence. Write the correct claim first, adding the rejected model only as a compact boundary when needed.
- Use `not...but` and `rather than` sparingly. One necessary contrast can clarify a model boundary; repeated contrast framing usually signals that the paragraph should be rewritten as a direct positive claim.
- Keep logic linear. Avoid `A -> B -> A` sequencing where a claim is stated, interrupted by setup, and then restated. Combine setup and result when possible, especially for experiment evidence.
- Reject `A -> B -> A -> C` sequencing: do not state a claim, insert setup or example context, restart the same claim, and only then give the consequence. Attach the result to the setup and move directly to interpretation.
- Separate model, mechanism, evidence, and implication when a question asks for evaluation.
- Use citations only for non-obvious facts, theories, mechanisms, methods, evidence, data, or broad generalisations.
- Calibrate citation strength. Use `supports`, `implicates`, `is consistent with`, or `contributes to` unless the verified source directly proves causality.
- Avoid citation stacking; one precise citation is usually better than several weakly connected citations.
- Keep academic paper author names inside parenthetical in-text citations. Do not make a paper's authors the subject of an ordinary explanatory sentence unless the user explicitly requests literature-history narration.
- Do not invent statistics, dates, mechanisms, source names, quotations, or citations.
- If the user supplies no Example Essay citations, cite only sources found by slide-citation mining or verified classic-experiment fallback; never cite from memory.
- Conclude by synthesis. Do not add new evidence in the conclusion.
- Openings and conclusions should state the problem, thesis, or synthesis. They must not list every later section or repeat each body paragraph's conclusion.

## Banned Patterns

Reject or rewrite paragraphs that:

- narrate pages or slides instead of giving the argument;
- narrate the lecture/source route instead of giving the answer;
- say how the student should write instead of writing the answer;
- include exam-guidance sentences such as telling the student what the final thesis should be;
- open with an unnecessary `X is not...` sentence when the next sentence gives the real claim;
- use repeated `not... but`, `not simply`, `rather than`, or `however` structures when direct positive wording would be clearer;
- sequence evidence as claim, setup, repeated claim instead of claim, setup plus result, interpretation;
- restart the same claim after a setup sentence, producing A-B-A-C logic instead of a forward A-B-C argument;
- use an introduction or conclusion as a list of parts rather than as a synthesis;
- list examples without explaining what they prove;
- repeat the question using different words without adding mechanism;
- overuse broad claims such as `this is important` without specifying consequence;
- hide uncertainty behind confident language;
- turn supporting or associative evidence into a single-cause claim;
- use a citation copied from lecture slides without verifying the original source when source-derived content is included.
- turn academic-paper attribution into author-led prose when a parenthetical author-year citation would support the same content more cleanly;
- include a list of named channels, receptors, genes, cell classes, methods, examples, firms, or pathways without explaining what the list proves or distinguishes;
- use true but unneeded detail that makes the answer more encyclopedic but less exam-efficient;
- compress wording so that a modulating, gating, entraining, stabilising, supporting, or associative mechanism becomes the primary generator or proof.

## Compression Standard

Compression is not sentence shortening. It is function filtering.

Compression must be budgeted from the content, not from an arbitrary percentage. Before shortening a complete answer, identify:

- the protected source skeleton: core claims, mechanisms, evidence, comparisons, limitations, and synthesis items required by the question;
- protected academic details: named evidence, citation-supported mechanism detail, and examiner-relevant distinctions;
- removable redundancy: repeated framing, duplicated restatement, overlong transitions, and low-value background.

Compress only the removable redundancy first. Protected material may be tightened, but it must not disappear unless the question, source scope, or user request changes.

For each sentence, ask:

```text
Does it state the claim?
Does it explain the mechanism/process?
Does it provide evidence or an example that changes the answer?
Does it interpret what that evidence proves and what it does not prove?
Does it define the scope, limitation, or contrast?
Does it link back to the question?
```

Delete or merge sentences that do none of these.

Compression must preserve causal strength, scope qualifiers, negative distinctions, model boundaries, and evidence interpretation. Do not rewrite `not necessary for generating the core rhythm` as `not necessary for locomotion`, or `supports a mechanism` as `proves the mechanism`, unless the source warrants the stronger claim.

If the user asks for a percentage reduction that would delete protected source skeleton or citation-supported detail, reject that target and use the largest safe reduction. The final answer should not mention internal compression targets or word-count budgeting.

## Detail-Level Discipline

Named detail is valuable only when it improves the answer's function. Do not include a list of channels, receptors, nuclei, genes, cell classes, molecules, methods, firms, case names, equations, or pathways unless the lecture/source logic or exact question requires that level.

When a list is illustrative, compress it to a higher-level mechanism. When a list is examiner-relevant, keep only the items that distinguish mechanisms, evidence, limitations, or consequences.

Extra Reading and named mechanism detail should normally replace vague wording inside an existing lecture-derived sentence. They should not be added as separate expansion sentences unless the question requires that detail and the paragraph still gains mechanism or evidence density per word.

For every named detail, ask:

- Does this detail map to a PPT/source mechanism slot?
- Does it distinguish this mechanism from another?
- Does it explain an experiment, method readout, clinical consequence, sector consequence, or limitation?
- Would deleting it make the answer less accurate, or only less encyclopedic?

## Analytic-Over-Descriptive Standard

A paragraph fails if it contains more than two consecutive descriptive sentences without an analytic sentence. A complete essay also fails when the sentence-level balance is strongly descriptive-dominant. The target is approximately 40-60% analytic sentences, with enough descriptive material to keep the answer factual and enough analytic material to make the answer argumentative.

A valid analytic sentence must do at least one of the following:

- explain why the mechanism solves a control, causal, methodological, clinical, or sector-level problem;
- state what an experiment, example, dataset, or figure proves or fails to prove;
- compare two models, pathways, cases, mechanisms, or methods;
- define the scope or boundary of a claim;
- link a named detail to system-level function or the essay question.

## Example Use

Examples, case studies, firms, organisms, diseases, methods, figures, calculations, or datasets should be treated as evidence slots.

Allowed:

```text
The example demonstrates the mechanism because...
```

Forbidden:

```text
Example A happened. Example B happened. Example C happened.
```

## Citation Discipline

Use the smallest citation set that supports the claim. Do not cite:

- obvious lecture framing;
- generic background;
- every sentence in a paragraph;
- unsupported material copied from another essay.

Use citations for:

- original papers cited by lecture slides and actually read;
- verified classic experiments or landmark primary studies found because relevant lecture slides contain no usable citations;
- Citation / Extra Reading Papers with verified metadata and relevant claim support;
- Extra Reading Books matched to a chapter or section;
- online academic sources verified by DOI, PubMed, publisher page, textbook, or equivalent academic source.

Academic paper details require parenthetical author-year citation and green highlight in Example Essay DOCX output. Uploaded Extra Reading Book details require chapter/section anchoring and yellow highlight. Public source-basis preambles, prediction disclaimers, and decorative question labels are not essay prose and must be removed from final Word output.

## Completion Standard

Language quality is acceptable only when:

- no high-severity language linter failures remain;
- no medium-severity gap remains without an explicit reason;
- the source audit supports factual claims;
- Example Essay DOCX formatting and source-highlight rules pass;
- no benchmark or course identity is used as a production trigger.
