---
name: exam-prep-extra-reading
description: Find, classify, and match Extra Reading sources only for confirmed essay-style exam preparation or Online Essay Exam drafting when source permissions allow it, including academic source discovery, lecture-topic matching, mechanism evidence, molecular evidence, experimental evidence, counterargument, and evaluation support.
---

# Extra Reading Enrichment

Use this Skill only after `exam-prep-index`, `exam-prep-essay`, or `exam-prep-online-essay-exam` confirms the branch includes Essay Question or Online Essay Exam. For Online Essay Exam, first confirm whether Online Materials, Lecture Materials, uploaded readings, and external academic sources are allowed. Do not use Extra Reading for MCQ, short-answer, long-answer, practical/data/problem, worked-solution, or general Notes routes unless the user also confirms an essay-style output.

Default public output is English. Change the language only when the user explicitly overrides it for the current task; examples in another language do not change the default.

## Load First

Read:

- `references/extra_reading_workflow.md`
- `references/input_and_evidence_protocol.md`
- `references/essay_exam_prep_protocol.md` when essay output is planned
- `references/online_essay_exam_protocol.md` when Online Essay Exam drafting is planned

Use `scripts/extra_reading_tools.py` and `scripts/essay_exam_tools.py` when structured source scans, query generation, or essay-enrichment plans are useful.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index`, `exam-prep-essay`, or `exam-prep-online-essay-exam` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Extra Reading output. Confirm that the branch includes Essay Question or Online Essay Exam and that source permissions allow the Extra Reading use.

## Workflow

1. Identify lecture topics, course claims, essay questions, and enrichment needs.
2. Classify supplied sources as essay-enrichment sources, course-facing sources, example-answer sources, or unclear sources.
3. Use reliable academic sources first: textbooks, review articles, primary papers, official datasets, DOI/PMID sources, or lecture-mentioned references.
4. Match each useful source to a course point or essay claim.
5. Produce search queries, source tables, paragraph slots, or enrichment notes as requested.

## Output Contract

Extra Reading supports Essay Question, Example Essay, and Online Essay Exam enrichment when confirmed source permissions allow it. Use it to add mechanism depth, molecular evidence, experimental evidence, counterargument, or evaluation. Do not use Extra Reading to decide general Notes depth or non-essay exam preparation.
