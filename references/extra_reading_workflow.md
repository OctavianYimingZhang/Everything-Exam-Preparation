# Extra Reading Workflow

Extra Reading supports Essay Question and Example Essay enrichment only. It adds academically useful external depth where essay-style outputs can earn credit for external evidence, mechanism depth, counterargument, or evaluation.

## Extra Reading Source Signals

Use extra reading signals as provenance labels for essay-enrichment sources. They help locate useful external material for essay-style outputs and do not decide general Notes depth.

Common signals include textbook-like background, book chapters, recommended reading, academic papers, primary research, recent research, journal articles, DOI/PMID references, abstract/methods/results format, figure sources, author-year citations, and reference-list text.

## Uploaded Extra Reading

Use uploaded Extra Reading when the user provides it and the material adds essay-relevant academic value.

When uploaded material is not enough, scan source fragments and knowledge-unit evidence for extra reading mentions near phrases such as:

```text
Extra reading recommendation
Recommended reading
Further reading
Source
Sources
References
Textbook
Book
Chapter
```

Create mention records when a source is identifiable:

```json
{
  "kind": "extra_reading_source",
  "title": "...",
  "authors_or_editors": "...",
  "source_detail": "...",
  "mentioned_in": "...",
  "linked_lecture_topics": ["..."]
}
```

Use extra reading material to deepen essay-style outputs with background, molecular explanation, mechanism explanation, pathway context, conceptual background, method detail, external evidence, counterargument, and evaluation.

## Academic Search

Generate online academic search queries from course topics, mechanisms, diseases, pathways, molecules, assays, experimental methods, source-backed claims, cited sources, and knowledge-unit gaps.

Search query patterns:

```text
[lecture topic] [mechanism] primary research
[molecule/pathway] [experimental evidence]
[lecture claim] recent research
[disease/topic] [mechanism] academic paper
```

Create source records with the fields that can be verified:

```json
{
  "kind": "extra_reading_source",
  "title": "...",
  "authors": "...",
  "year": "...",
  "source": "...",
  "identifier_or_url": "...",
  "evidence_type": "...",
  "linked_lecture_topics": ["..."],
  "use_in_notes": "..."
}
```

Use academic search results to add molecular mechanisms, primary findings, experimental evidence, figures, methods, limitations, and support for conclusions when they directly strengthen an essay argument or Example Essay paragraph.

## Knowledge-unit matching

Build topics from knowledge signals and source fragments, then match extra reading records to those topics.

Topic enrichment records use this shape:

```json
{
  "lecture_topic": "...",
  "core_lecture_explanation": "...",
  "background_enrichment": ["..."],
  "evidence_enrichment": ["..."],
  "molecular_or_mechanism_detail": ["..."],
  "experimental_evidence_support": ["..."],
  "knowledge_use": "..."
}
```

## Essay-style enrichment

Add Extra Reading inside relevant essay-style paragraphs with this pattern:

```text
Core course point or essay claim: [...]
Extra reading depth: [...]
Molecular/mechanism evidence: [...]
Experimental support: [...]
Knowledge use: [...]
```

Use Extra Reading in essay-style output when it improves conceptual explanation, molecular or mechanism detail, method interpretation, limitation handling, external evidence, counterargument, or evaluation.

Use Extra Reading in Exam Type Related output only when the confirmed Exam type includes Essay.

## Example Essay enrichment

Generate Example Essays with an extra-reading blend field and paragraph slots:

```json
{
  "extra_reading_blend": "15-30%",
  "extra_reading_paragraph_slots": []
}
```

Essay paragraph pattern:

```text
Claim from course topic.
Explanation of the course mechanism.
Extra reading evidence from book or paper.
Analysis of why the evidence strengthens the argument.
Link back to the essay question.
```
