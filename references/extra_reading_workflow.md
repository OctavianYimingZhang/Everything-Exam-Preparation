# Extra Reading Workflow

Extra Reading adds book and academic paper material to exam preparation notes and example essays.

## Source hints

Use two extra reading hints:

- `extra_reading_book`: textbooks, book chapters, publisher book extracts, recommended reading chapters.
- `extra_reading_paper`: academic papers, primary research, recent research, journal articles, papers with DOI/PMID, abstract/methods/results format.

## Book workflow

Use uploaded Books when the user provides them.

When no obvious uploaded Book is present, scan lecture material for book mentions near phrases such as:

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

Create book mention records:

```json
{
  "kind": "book",
  "title": "...",
  "author_or_editor": "...",
  "chapter_or_section": "...",
  "mentioned_in": "...",
  "linked_lecture_topics": ["..."]
}
```

Use book material to deepen lecture notes with textbook background, molecular explanation, mechanism explanation, pathway context, and conceptual background.

## Academic Paper workflow

Use uploaded Academic Papers when the user provides them.

Then scan lecture material for paper mentions, including DOI, PMID, author-year citation, journal reference, reference list entry, figure source caption, and Source/Sources/References sections.

Then generate online academic search queries from lecture topics, mechanisms, diseases, pathways, molecules, assays, experimental methods, and lecture claims.

Search query patterns:

```text
[lecture topic] [mechanism] primary research
[molecule/pathway] [experimental evidence]
[lecture claim] recent research
[disease/topic] [mechanism] academic paper
```

Create paper mention records:

```json
{
  "kind": "academic_paper",
  "title": "...",
  "authors": "...",
  "year": "...",
  "journal": "...",
  "doi_or_url": "...",
  "evidence_type": "...",
  "linked_lecture_topics": ["..."],
  "use_in_notes": "..."
}
```

Use paper material to add molecular mechanisms, primary findings, experimental evidence, figures, methods, and support for conclusions.

## Lecture-topic matching

Build lecture topics from lecture fragments and match extra reading records to those topics.

Topic enrichment records use this shape:

```json
{
  "lecture_topic": "...",
  "core_lecture_explanation": "...",
  "book_enrichment": ["..."],
  "paper_enrichment": ["..."],
  "molecular_or_mechanism_detail": ["..."],
  "experimental_evidence_support": ["..."],
  "exam_use": "..."
}
```

## Notes enrichment

Add Extra Reading inside relevant topic notes with this pattern:

```text
Core lecture point: [...]
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
Claim from lecture topic.
Explanation of the lecture mechanism.
Extra reading evidence from book or paper.
Analysis of why the evidence strengthens the argument.
Link back to the essay question.
```
