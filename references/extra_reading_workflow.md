# Extra Reading Workflow

Extra Reading adds academically useful external depth to exam preparation notes and example essays.

## Extra Reading Source Signals

Use extra reading signals as provenance labels only. They help locate useful enrichment; they do not define a closed source taxonomy or decide notes depth.

Common signals include textbook-like background, book chapters, recommended reading, academic papers, primary research, recent research, journal articles, DOI/PMID references, abstract/methods/results format, figure sources, author-year citations, and reference-list text.

## Uploaded Extra Reading

Use uploaded Extra Reading when the user provides it and the material adds academic value to a knowledge unit.

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

Use extra reading material to deepen course notes with background, molecular explanation, mechanism explanation, pathway context, conceptual background, method detail, evidence, and evaluation.

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

Use academic search results to add molecular mechanisms, primary findings, experimental evidence, figures, methods, limitations, and support for conclusions when they directly strengthen a knowledge unit.

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
  "exam_use": "..."
}
```

## Notes enrichment

Add Extra Reading inside relevant topic notes with this pattern:

```text
Core course point: [...]
Extra reading depth: [...]
Molecular/mechanism evidence: [...]
Experimental support: [...]
Exam use: [...]
```

Use extra reading in practical/data explanations for method, readout, control, limitation, and interpretation.

Use extra reading in MCQ, Short Answer, and Long Answer preparation when it improves explanation, answer depth, mechanism detail, or evidence support.

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
