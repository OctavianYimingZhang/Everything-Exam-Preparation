# Practice Protocol

## Purpose

Practice turns course evidence and question material into the exact learning or assessment artifact requested by the student.

## Question-Based Preparation

For MCQ and short-answer Practice, extract the supplied questions with provenance and treat each short-answer subquestion as its own practice record. Present concise exam-needed knowledge in lecture order. Do not publish historical recurrence, cross-year stability, or Units Analysis from this mode; those are separate Analysis artifacts.

For long-answer, practical, and data questions, explain the command, relevant knowledge, method, reasoning chain, answer structure, and a source-grounded example response.

For calculations and worked solutions, show:

1. interpretation of the question;
2. givens and target;
3. method selection;
4. derivation or calculation steps;
5. units, dimensions, and assumptions;
6. final result and its meaning.

## Integrated Capabilities

Question solving connects one target question to the relevant knowledge unit, explains the reasoning, and adds closely matched transfer questions.

Question organisation extracts supplied questions and places them in lecture or knowledge-unit order with minimal provenance.

An assessment blueprint maps knowledge units evidenced by source fragments. Source occurrence may describe coverage; assessment weights come from explicit assessment evidence.

Answer evaluation compares a supplied student answer with a rubric, mark scheme, or explicit expected concepts. Evaluate concept aliases and their relationships at token and clause level, including local negation; do not treat a substring as conceptual evidence. Return one criterion status from `correct`, `partial`, `incorrect`, `contradicted`, or `missing`, together with supporting or conflicting evidence and actionable revision guidance.

Keep awarded marks distinct from estimates. Return no mark estimate when the criteria have no explicit mark allocation. When every criterion carries marks, an estimate may use rubric-supplied status credit; otherwise label the documented partial-credit heuristic and retain `mark_awarded: null`.

Timed practice uses an explicit total duration and an assessment blueprint. Each slot records its time allocation and source basis.

## Solution Book Task Mode

Select `task_mode: solution_book` for a worked-answer book or Answer PDF. This is a Practice mode, not a separate public Skill.

The public answer unit is one complete major question. A question containing `(a)`, `(b)`, or later subparts remains one answer unit:

- show subpart labels only as light locators;
- keep interpretation, method, working, intermediate conclusions, and the final result in one ordered reasoning chain;
- do not render separate subpart mini-answers or promote subpart labels to answer headings;
- never merge or discard similar questions: retain each prompt and its specific answer.

Group genuinely similar questions in their supplied order. Render all question-specific answers first. After the final question in that group, render exactly one `General Approach` callout. Do not place it before the group, repeat it after each question, or substitute it for a specific answer. If a multi-question group has no evidence-backed general approach, mark the model incomplete rather than inventing one.

The callout must be visually distinct but restrained: use a light background, a border, normal body-sized text, and no decorative full-page treatment.

### Solution-book input model

A book contains `title` and `question_groups`. Each group contains `group_id`, `group_title`, `questions`, and optional `general_approach`. Each major question contains `question_id`, `question`, optional locator-only `subparts`, one `reasoning_chain`, optional `formulas` and `tables`, an optional question-level `final_answer`, and `source_refs`. If legacy input places reasoning or an answer inside a subpart, lift that text into the major question's single ordered reasoning chain while retaining the subpart label only as its locator.

When `source_refs` are shown, resolve both their source identity and locator against the shared source scan used for this run. A free-text, unknown-source, missing-locator, or nonexistent-locator reference makes the model incomplete; a displayed reference cannot authenticate itself.

### Required artifacts

Generate:

1. a valid OOXML `.docx`;
2. a real `.pdf` whose bytes begin with the PDF signature and whose pages can be parsed by a PDF reader;
3. a `.manifest.json` sidecar containing `task_mode`, artifact media types, filenames, byte sizes, SHA-256 hashes, major-question IDs, group counts, layout validation, and the answer-unit invariants.

For a batch, preflight unique basenames and collisions, generate every book as its own DOCX/PDF/manifest set, and write a batch manifest. Do not relabel HTML or plain text as either DOCX or PDF.

### Pagination and render QA

- Apply keep-with-next and keep-lines controls to titles and headings so a heading is not orphaned at the foot of a page.
- Use widow/orphan control for prose and preserve the continuous reasoning order across page breaks.
- Give table rows automatic height and prevent ordinary rows from splitting; repeat table headers after a PDF page break. Split only a row that is itself taller than a usable page, and continue it without clipping content.
- Put formulas and callout rows in measured, bordered containers with no fixed height. Move or split an oversized container before it crosses the printable area.
- Render `General Approach` only after its group and exactly once per group.
- Verify the DOCX ZIP parts, PDF page count/signature, text order, occurrence counts, and sidecar checksums. A filename extension alone is not format validation.

## Output

Use the format requested by the user. For DOCX artifacts, apply the shared academic document design. Preserve provenance in outputs where it assists checking, and keep analysis/debug fields in internal records. For `solution_book`, the artifact bundle and verification rules above are mandatory even when the user informally calls the result an “Answer PDF”.
