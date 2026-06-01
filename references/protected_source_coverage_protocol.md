# Protected Source Coverage Protocol

This protocol prevents two opposite failures: public notes that omit examinable source content, and public notes that expose internal audit scaffolds. It is used before `KnowledgeSurfaceContract` rendering.

```text
SourceFragment -> SlideAtomicLedger -> ProtectedSourceUnit -> PublicOutputPoint -> SourceToOutputBinding -> ZeroMentionLint
```

## Core Principle

Official course material must be decomposed before it is compressed. Past papers may change density, ordering and priority, but they must not define the factual boundary of ordinary notes.

## SlideAtomicLedger

Use `SlideAtomicLedger` for lecture slides, practical notes, mocks, postlab documents, answer keys and diagram-heavy sources.

```yaml
SlideAtomicLedger:
  ledger_id:
  source_id:
  source_role:
  slide_or_page_units:
    - unit_id:
      locator:
      raw_heading:
      unit_type:
      protected_status:
      expected_public_mentions:
      bound_public_point_ids:
      qa_flags:
```

Protected units include:

- learning outcomes;
- lecture, slide, page or practical-problem headings;
- official definitions;
- contrast pairs;
- criteria, stages, classes and component lists;
- named examples and named experiments;
- diagram labels, table rows and graph axes that teach content;
- equations, calculations, units and workflows;
- “Why X?” explanatory blocks;
- summary or take-home points;
- formal-past-paper terms and operations.

## ProtectedSourceUnit

```yaml
ProtectedSourceUnit:
  unit_id:
  source_id:
  locator:
  unit_kind:
    - definition
    - term
    - contrast_pair
    - criteria_item
    - mechanism_step
    - method_step
    - equation
    - calculation_rule
    - graph_data_rule
    - diagram_label
    - table_entry
    - named_example
    - experimental_result
    - practical_operation
    - past_paper_term
    - summary_point
  required_visibility:
    - public_knowledge
    - internal_audit_only
    - excluded_admin
    - duplicate_bound_elsewhere
  expected_public_mentions:
  coverage_status:
```

Protected units must either appear in public knowledge output or be explicitly classified as duplicate, administrative, unreadable, unsupported, or internal-audit-only. Silence is not a valid outcome.

## PastPaperTermMustAppear

When a formal past paper, mock, practical problem or answer key uses a term, calculation, graph operation, reagent, method or diagnostic distinction that is also supported by course material, it becomes a protected public mention.

Rules:

- Past-paper terms increase protection and density; they do not invent new course facts.
- A past-paper term may be grouped under a broader module, but it must remain name-visible if the term itself is testable.
- Old-regime past-paper terms can support coverage only when the term is course-backed and not obsolete.
- If the public output contains the broader topic but omits the tested term, fail `zero_mention_lint`.

## SourceToOutputBinding

Every protected public unit must bind to a visible output point.

```yaml
SourceToOutputBinding:
  binding_id:
  protected_unit_id:
  public_point_id:
  public_block_id:
  mention_text:
  binding_quality:
    - exact_named
    - grouped_but_named
    - paraphrased_with_equivalent_term
    - missing
```

Acceptable binding:

- `exact_named`: the official term or equation appears.
- `grouped_but_named`: the term is inside a list or compact paragraph, but still visible.
- `paraphrased_with_equivalent_term`: allowed only for prose explanations where the source term is not the examinable term.

Unacceptable binding:

- only implied by a broad topic title;
- only present in a hidden audit map;
- only mentioned in `Common Error`, `Exam Use`, `Must Master`, or source notes that are suppressed from public output;
- merged into generic wording so the tested term disappears.

## ZeroMentionLint

Run `zero_mention_lint` after public rendering.

Fail when:

- a protected official term has zero visible mentions;
- a past-paper-backed term is omitted from public notes;
- a diagram/table/equation is referenced only as “the graph/figure” without its knowledge content;
- a calculation appears without units or conversion logic;
- a method workflow appears without principle, readout or interpretation;
- a named example is deleted because a broad module title seemed to cover it.

## Density Rules

Protected source coverage is not a licence to make unreadable notes. Use compact grouping only when all protected names and operations remain visible.

Allowed compression:

```text
PCR-RFLP turns a SNP into a fragment-pattern difference: amplify the target, digest with an enzyme whose site changes between alleles, then separate fragments by agarose gel electrophoresis.
```

Forbidden compression:

```text
PCR diagnostics are important.
```

## Public Surface Interaction

This protocol controls coverage. `knowledge_surface_protocol.md` controls what is allowed to be visible. A protected unit that contains audit or source-route text must be rewritten as knowledge rather than copied.

Example:

- Source text: `The second slide shows the opposite side of the body.`
- Protected knowledge: crossed extensor reflex.
- Public rewrite: `The crossed extensor reflex activates contralateral extensors and inhibits contralateral flexors so the unstimulated limb supports body weight.`

## Route Integration

- `exam_prep_notes_docx`: required for every ordinary notes run.
- `knowledge_walkthrough_docx`: required when lecture-first walkthrough is generated.
- `practical_data_problem_protocol.md`: required for calculations, graph interpretation, protocols and postlab materials.
- `essay_exam_prep`: use protected source skeleton before adding extra reading or compression.

## Publish Gate

Before public output is approved:

1. Build or conceptually maintain `SlideAtomicLedger`.
2. Mark protected units.
3. Bind each protected unit to public output.
4. Run zero-mention lint.
5. Run knowledge-surface lint so the coverage does not expose audit/provenance text.
