# Input and source handling

This Skill uses source hints to make file handling easier. Hints help the assistant understand the file pack and decide which workflow steps are useful.

## Source hints

- `knowledge_material`: lecture slides, lecture notes, official notes, practical handouts, module notes, reading notes.
- `practice_material`: past papers, practice questions, MCQ banks, short-answer questions, long-answer questions, problem sheets, data/practical questions, essay prompts.
- `marking_material`: mark schemes, answer keys, solution sets, examiner feedback.
- `style_reference`: example answers, model answers, preferred essay style material.
- `extra_reading_book`: textbooks, book chapters, publisher extracts, recommended reading chapters.
- `extra_reading_paper`: academic papers, journal articles, primary research, recent research, DOI/PMID papers.
- `other_material`: files that do not clearly fit the hints above.

## Intake

For each file, record the file name, source hint, readable character count, extraction notes, text fragments, and extracted media when available.

Mixed files remain useful. The assistant can inspect the fragments directly and use them for course explanation, exam habit analysis, answer walkthroughs, extra reading enrichment, or essay preparation.

## Extra Reading intake

Books and Academic Papers can be uploaded directly by the user. Lecture material can also mention extra reading inside sections labelled Source, Sources, References, Recommended reading, Further reading, Textbook, Book, Chapter, DOI, PMID, or journal references.

Extra Reading material is used to add molecular detail, mechanism explanation, experimental evidence, research context, and stronger essay support.

## Practical extraction

Text files, Markdown, JSON, YAML, CSV, DOCX, PPTX, and PDF are read when the local runtime can read them. Embedded images from DOCX/PPTX can be exported to an asset folder. Files without automatic text extraction remain listed with an extraction note.
