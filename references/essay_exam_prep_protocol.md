# Essay Protocol

## Public Scope

Essay handles only:

- exam essay planning;
- annotated model essays;
- paragraph exemplars;
- review and model answers for closed past assessments;
- adaptation of an exam answer to a different question, command word, emphasis, or time limit.

It does not produce a complete submission for an active assessed essay, report, poster, presentation, website, or other coursework. If lifecycle state is `active`, block complete drafting as `active_assessed_complete_draft_out_of_scope` even when a legacy permission field is `allowed`. If state is `unknown`, allow only permission-neutral question analysis, concept explanation, planning, and feedback until the state is known. If state is `closed`, post-assessment reconstruction and a model answer are permitted under the source rules below.

`build_essay_views` is the enforcement boundary for dual-view model essays. Before normalising a canonical body or constructing either view, it must inspect any explicitly supplied lifecycle state. For `active`, return `restricted`; for explicit `unknown`, return `needs_clarification`. Both responses must set `views_generated: false` and omit `views`. A `closed` state, or no lifecycle field for ordinary revision, may continue under the normal evidence rules.

## Question and Argument Model

Identify the command word, topic boundaries, evidenced scope, and judgement the answer must defend. Build a thesis-led sequence in which each body paragraph has a declared function and develops claim, evidence, analysis, limitation where relevant, synthesis, and a link to the question.

Use the user's requested exam-preparation artifact: outline, paragraph plan, evidence map, paragraph exemplar, dual-view model essay, closed past-assessment review, or adaptation notes. Do not turn an exam-preparation request into a currently assessed coursework deliverable.

## One Body, Two Views

Store essay prose once as an ordered `canonical_body`. Each paragraph block has a stable `block_id`, `paragraph_function`, `adaptation_notes`, and ordered text segments. Each segment has a stable `segment_id`, its text, zero or more teaching annotations, and any source references.

Project both views from that structure:

1. `clean`: concatenate the segments in order and omit teaching metadata;
2. `annotated`: retain the identical segment text and expose the teaching metadata.

The annotated teaching view supports and audits all of:

- `thesis`;
- `claim`;
- `evidence`;
- `analysis`;
- `limitation`;
- `synthesis`;
- `paragraph_function`;
- `adaptation_notes`.

Compute the clean, annotated, and canonical hashes from ordered prose only. All three hashes must match. Annotation text, paragraph-function labels, and adaptation notes are teaching metadata and must not alter the clean essay body. Missing annotation types produce `needs_review`; never create unsupported scientific content merely to fill an annotation category.

## Source Roles

Course sources are the primary basis for course facts and course scope. Attach their source IDs and locators to evidence segments where available.

Formal past papers, official mocks, and specimens determine only the question scope and emphasis. Their allowed source-reference usages are `scope`, `emphasis`, `question_scope`, and `question_emphasis`. A past paper must not serve as factual evidence for a course claim, mechanism, experiment, or result.

External academic evidence may be used only when the user supplied it or it was actually retrieved and verified within the current task. Verification is fragment-bound, not corpus-wide: resolve each essay segment's source ID or name and locator, then check its citation identity, DOI, reported experiment, quantitative value, and empirical result claim only against the resolved non-past-paper fragment text referenced by that same segment. Evidence found only in an unreferenced fragment, whether from the same source or another source, does not verify the claim. An unknown source or unresolved locator is an explicit source-audit issue. Do not create placeholder references, plausible-looking DOI strings, inferred author-year citations, or unobserved results, and do not complete a source gap from memory.

## Writing and QA

Use the user's requested language and default to precise academic English. Keep causal statements proportional to the evidence. Distinguish observation, interpretation, and evaluation. Verify:

- the introduction answers the question and states the thesis;
- paragraph order develops rather than repeats the thesis;
- claim, evidence, analysis, limitation, and synthesis labels match their actual functions;
- evidence segments resolve to non-past-paper sources;
- each source locator resolves to the fragment actually referenced by that segment;
- past-paper references are scope or emphasis only;
- no citation, DOI, experiment, quantitative value, or result claim is accepted from an unreferenced fragment;
- clean and annotated body hashes match;
- the conclusion resolves the argument;
- adaptation notes explain how to alter the answer without becoming part of the clean prose.
