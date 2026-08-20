# Exam Intelligence Protocol

## Purpose

Exam Intelligence describes the historical recurrence and course mapping of supplied exam questions. It supports Units Analysis, question extraction, lecture/unit/concept mapping, question-family clustering, and student-facing export. It does not infer official weighting or promise future questions.

## Source Roles

Assign exactly one role to each source:

- `formal_past_paper`: a paper from an actual formal examination sitting;
- `official_mock_specimen`: an official mock, sample, or specimen that was not a formal sitting;
- `practice_worksheet`: tutorial, revision, worksheet, question-bank, or other practice material;
- `lecture_material`: slides, notes, recordings, transcripts, or other taught course material;
- `mark_scheme`: an answer key, rubric, examiner guidance, or marking scheme.

An explicit user label takes precedence. If the evidence cannot distinguish a formal paper from a mock or practice source, do not promote it to `formal_past_paper`; record the ambiguity for review. A mark scheme linked to a formal paper can supply explicit marks, but its repeated question wording is not an additional occurrence.

## Question Records and Mapping

Create one record per independently examinable prompt. Preserve the source name and the narrowest reliable page, slide, paragraph, or timestamp locator. A formal record may keep `formal_year: null` when the year is unavailable; do not infer a year from file order.

Mapping has two states:

- `resolved`: at least one lecture, unit, or concept target is explicitly supported by the supplied course evidence;
- `unresolved`: no reliable target is available, targets conflict, or only a similarity guess is possible.

An unresolved mapping has no selected target and must state a reason. Similarity candidates may be kept in audit review notes, but they do not increase mapping coverage.

## Question Families

Prefer explicit family labels or confirmed course concept mappings. A deterministic similarity cluster may be used only when its method is recorded and the family is flagged for manual review. Never merge questions merely because they share a command word such as *describe* or *explain*. Preserve family membership and the exact supporting question IDs in the audit section.

## Metric Definitions

All counts operate on family-member question records. The formal-year universe is the set of distinct, explicitly dated years represented by formal past papers in the whole package.

- `formal_occurrence_count`: number of member records whose role is exactly `formal_past_paper`, including undated formal records.
- `distinct_formal_years`: number of distinct explicit years among those formal member records.
- `formal_year_coverage`: `distinct_formal_years` divided by the number of years in the formal-year universe; zero when that universe is empty.
- `auxiliary_occurrence_count`: number of member records from `official_mock_specimen` or `practice_worksheet`. Lecture material and mark schemes are excluded.
- `format_diversity`: number of distinct recorded question formats across formal and auxiliary occurrences.
- `explicit_mark_exposure`: sum of explicitly stated marks across formal and auxiliary occurrences. A linked mark-scheme value may populate the corresponding question record once; never double-count the scheme as another occurrence or infer missing marks.
- `retention`: among formal years from the family's first observed year through the newest corpus year, the fraction in which the family appears. Return zero when fewer than two such years exist because persistence has not yet been observed.
- `cross_year_stability`: for at least two corpus years, calculate annual formal occurrence counts across the full formal-year universe, then return `max(0, 1 - mean_absolute_deviation / mean_count)`. Return zero with insufficient or absent formal evidence. This describes evenness of historical counts, not future likelihood.
- `mapping_coverage`: resolved formal and auxiliary occurrences divided by all formal and auxiliary occurrences; zero when no occurrence exists.
- `unresolved_mapping_count`: number of formal and auxiliary occurrences whose mapping is unresolved.

Round ratios to six decimal places. Keep the family years, annual counts, contributing question IDs, mapped IDs, unresolved IDs, observed formats, and explicitly marked IDs in audit metric evidence so each public value can be recomputed.

Do not collapse these measures into one overall score. Do not convert occurrence counts or explicit-mark exposure into assessment weighting. Do not describe any family as guaranteed, certain, or known to appear in a future paper.

## Public and Audit Separation

The `public` section is the student-facing export. It contains:

- package status and corpus scope;
- all ten named metrics for each family;
- metric definitions;
- limitations and interpretation guardrails.

The `audit` section is the verification record. It contains:

- source-role assignments;
- complete question records and locators;
- family memberships and clustering methods;
- metric evidence;
- unresolved mappings, exclusions, and warnings.

Do not place audit-only question text, source locators, mapping candidates, or internal review notes in `public`. A package is `completed_with_gaps` when useful analysis exists but mappings or formal years remain unresolved. With no formal past-paper source, use `needs_material_input`; auxiliary material alone cannot support formal recurrence.

## Validation

Validate the JSON structure with `schemas/exam_intelligence_package.schema.json` and run the semantic validator in `scripts/exam_intelligence_tools.py`. Semantic validation must recompute family metrics from audit records, reject source-role drift, reject resolved mappings with no explicit target, and reject prediction, weighting, probability, or composite-score fields.
