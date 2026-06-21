---
name: exam-prep-extra-reading
description: Find, classify, and match Extra Reading sources only for confirmed essay-style exam preparation, including academic source discovery, lecture-topic matching, mechanism evidence, molecular evidence, experimental evidence, counterargument, and evaluation support.
---

# Extra Reading Enrichment

Use this Skill only after `exam-prep-index` or `exam-prep-essay` confirms the Exam type includes essay. Do not use Extra Reading for MCQ, short-answer, long-answer, practical/data/problem, worked-solution, or general Notes routes unless the user also confirms an essay output.

## Load First

Read:

- `references/extra_reading_workflow.md`
- `references/input_and_evidence_protocol.md`
- `references/essay_exam_prep_protocol.md` when essay output is planned

Use `scripts/extra_reading_tools.py` and `scripts/essay_exam_tools.py` when structured source scans, query generation, or essay-enrichment plans are useful.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Workflow

1. Identify lecture topics, course claims, essay questions, and enrichment needs.
2. Classify supplied sources as essay-enrichment sources, course-facing sources, example-answer sources, or unclear sources.
3. Use reliable academic sources first: textbooks, review articles, primary papers, official datasets, DOI/PMID sources, or lecture-mentioned references.
4. Match each useful source to a course point or essay claim.
5. Produce search queries, source tables, paragraph slots, or enrichment notes as requested.

## Output Contract

Extra Reading supports Essay Question and Example Essay enrichment. Use it to add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation. Do not use Extra Reading to decide general Notes depth or non-essay exam preparation.
