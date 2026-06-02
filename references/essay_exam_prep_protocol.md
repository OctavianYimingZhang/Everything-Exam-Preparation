# Essay Exam Prep Protocol

This is the only canonical protocol for Essay Exam Prep, Example Essay generation, essay-specific planning, citation handling, paragraph banks, adaptation maps, and Essay DOCX output.

## Trigger

Use this route only when the user asks for essay preparation, Example Essays, model essays, full essay-style answers, essay plans, assessed-style drafts, or an essay add-on to exam preparation. Do not trigger it for MCQ, Short Answer, Long Answer, Practical/Data, prediction-only, or ordinary notes requests.

The default essay-prep package is core notes plus:

```text
Essay_Module_Example_Essays.docx
```

Separate essay DOCX files are allowed only when explicitly requested.

## Essay Pipeline

```text
essay-specific intake
-> source readiness
-> question analysis
-> source scope detection
-> lecture/source logic reconstruction
-> citation detection and resolution
-> optional verified extra reading
-> essay coverage plan
-> paragraph plan
-> Example Essay drafting
-> language quality pass
-> source-to-run mapping
-> DOCX generation
-> DOCX formatting/language/source audit QA
```

An Example Essay is a controlled answer to a question, not a longer lecture summary. Every paragraph must advance the answer by linking question demand, source-backed knowledge, evidence, interpretation, limitation, and synthesis.

## Evidence And Citations

Do not write complete essays from memory, from a predicted theme alone, or from past-paper stems without reading the relevant source material. Slide citations must be resolved before source-derived essay prose uses them as factual support. Extra reading must be verified through a book chapter, paper, DOI, PubMed record, publisher page, or textbook source. Unverified citation use is blocking.

Examples, exemplars, feedback, and previous outputs may teach structure, density, and style only. They never provide factual claims or direct predictions for a new target. Example Essay generation must fail or report blocking QA when body paragraphs lack lecture anchors, citation-derived claims use unread or unresolved sources, or extra reading lacks a chapter, section, DOI, PubMed, publisher, paper, or textbook anchor.

## DOCX Output

Essay DOCX files use Arial, 2.5 cm margins, 1.5 line spacing, justified body text, centered main title, left-aligned subtitle and subheadings, no empty spacer paragraphs, and default Word settings otherwise.

Final user-facing essay output includes only the requested DOCX or text artifact. Internal QA JSON, source maps, manifests, source audits, and citation-resolution logs are delivered only when the user explicitly asks for an audit package.

## Language

Use `references/language_quality_contract.md` as the only prose polish authority. Do not duplicate polish rules here. For essays, ensure argument structure, descriptive/analytic balance, citation discipline, compression without mechanism loss, direct positive claims, and conclusion-level synthesis.
