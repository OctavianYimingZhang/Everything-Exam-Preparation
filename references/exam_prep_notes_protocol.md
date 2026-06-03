# Exam Preparation Notes protocol

Default artifact: `Exam_Preparation_Notes.docx`.

## Required structure

The notes plan must be section/block based.

Each section contains ordered blocks. Each block must include:

- `block_id`
- `heading`
- `render_mode`
- `listability_reason`
- optional `exam_prompt_signal` and `source_form_signal` when they explain the render decision
- `source_ids`
- content matching the selected render mode
- optional `visual_ids` only when a source or generated visual is attached to that block
- `visual_decisions` with candidate, selected, and text-only status for the run

Do not generate a generic introduction unless it directly improves revision.

## Ordering

Default ordering is `exam_emphasis_first`: course-source baseline first, then depth weighted by past-paper emphasis and practical/data value. If the user requests source-order or lecture-order notes, use `ordering=source_order` while keeping the same artifact name.

## Practical/data/problem integration

Practical, data, and problem material must be integrated into the main notes when present. Include method steps, readouts, graph/table interpretation, controls, limitations, and calculation templates.

## Readable-not-verbose rule

Student-facing notes must be dense, readable, and exam-useful.

Rules:

- Use the fewest words that clearly explain the concept, mechanism, method, graph, assay, limitation, or exam operation.
- Do not write generic introductions.
- Do not copy source text wholesale.
- Do not merely list terms without explaining why they matter.
- Do not explain internal workflow.
- Use bullet lists and compact tables when they improve scan speed.
- Prefer direct explanations over filler.
- Compress low-exam-frequency or weakly supported material.
- Expand frequently tested, methodologically central, or conceptually difficult material.
- When slides contain diagrams/images that improve explanation efficiency, use the image directly or recreate a simplified visual, but keep it small enough not to dominate the page.

## Render mode selection

Each knowledge block must choose exactly one render mode.

Decision algorithm:

1. Identify source form: numbered list, bullet list, table, diagram, graph, paragraph, worked example, or mixed slide.
2. Identify exam signal: list/state/name/give, describe N points, compare, calculate, interpret graph, explain mechanism, evaluate limitation, or essay-style reasoning.
3. Set `listability_reason`. Use a specific listable reason when source form or exam signal contains separable answer units. Use `not_listable` only when connected reasoning is required.
4. Choose `compact_table` for comparisons, parameter sets, definition groups, phase sets, assay sets, or rule/criteria sets with repeated columns.
5. Choose `image_plus_kp_list` only when a selected block-owned visual explains faster than text and the block also has structured key points.
6. Choose `kp_list` when the answer is separable but not table-shaped.
7. Choose `mechanism_chain` for causal or sequence content that loses meaning as isolated labels.
8. Choose `paragraph` only when `listability_reason=not_listable` and the idea needs integrated explanation or caveat handling.

| render_mode | Use when | Student-facing form |
|---|---|---|
| `kp_list` | The source or exam asks for named points, criteria, uses, causes, features, examples, advantages, limitations, steps, or `describe/list TWO/THREE/N` answers. | Compact bullets. Each bullet has a label plus one short explanatory clause. |
| `compact_table` | The content is a comparison, distinction, parameter set, assay type set, phase set, response type set, or definition group. | A real DOCX table. Keep cells short. |
| `mechanism_chain` | The content is causal or sequential and loses meaning if split into isolated facts. | Arrow chain or short ordered bullets. |
| `image_plus_kp_list` | A source slide, figure, graph, or table explains faster than text, and key points can be listed beside or below it. | Small source image plus compact bullets. |
| `paragraph` | The content needs integrated explanation, evaluation, or caveat handling. | Short paragraph, usually under 90 words. |

## Listable content rule

Use `kp_list` or `compact_table` when at least one of these is true:

1. The source itself is a numbered or bulleted list.
2. The past paper or mark scheme asks `list`, `state`, `name`, `give`, `describe TWO/THREE/N`, or gives low marks for multiple discrete points.
3. The topic is a criteria set, such as drug-likeness rules, assay quality requirements, licence types, clinical phases, bioassay types, or animal-study principles.
4. The topic is a taxonomy or contrast, such as graded versus quantal, EC50 versus ED50, or active versus hit versus lead.
5. Each point can be explained in one line without losing mechanism.

Do not use list mode when the core meaning is a causal mechanism, argument, or multi-step interpretation that needs connected reasoning.

## Bullet explanation minimum

A bullet is valid only if it is a structured point with `label` and `explanation`. The explanation must contain the answer point plus at least one of: why it matters, how it works, when it applies, what it predicts, what limitation follows, or how it earns marks. Optional `exam_use` and `limitation` may be added when they reduce prose elsewhere.

Invalid bullets:

- `EC50: 50% response.`
- `Replacement: avoid animals.`

Valid bullets:

- `EC50 - concentration giving 50% of maximal response; lower EC50 means higher potency only when Emax is comparable.`
- `Replacement - use non-animal methods when they can answer the aim; required before animal work is justified.`

## Example render choices

For a listable source slide such as `what only in vivo studies can do`, use `image_plus_kp_list` or `kp_list`:

- Whole-body effects - captures integrated physiology that isolated cells cannot reproduce.
- Long-term effects - detects chronic adaptation or toxicity.
- Pharmacokinetics - measures ADME and tissue exposure in a living system.
- Unexpected systemic effects - reveals effects not predicted from isolated assays.
- Dose range - links effect and toxicity to a usable dose.
- Safety/toxicology - tests organism-level harm before human exposure.

For a low-mark rule question, use `kp_list`:

- H-bond donors - keep the count below 5 to preserve likely oral absorption.
- H-bond acceptors - keep the count below 10 to limit excessive polarity.
- Molecular mass - keep it below 500 Da because larger molecules often cross membranes less efficiently.
- logP - keep it at or below 5 to avoid excessive lipophilicity and solubility problems.

For a comparison such as graded versus quantal response, use `compact_table` with columns for type, measure, and typical output.

## Visual policy

Use source slide images only if they explain faster than text. Do not use decorative images. Default maximum image width is 3.8 inches. Use captions only when they help locate meaning. Do not expand the document with huge screenshots.

Visuals are block-level only. A visual may appear only when `selection_state=selected`, a block explicitly references it through `visual_ids`, and the visual placement points back to that block. The renderer must not append all images to a final `Visual aids` section, insert images without block ownership, use generic captions such as `Visual aid for ...`, or silently convert a missing image into caption-only text.

The default visual policy is `auto_source_visuals`. `user_requested_text_only` is valid only when the user explicitly asks for text-only or no images. If source visual candidates exist under `auto_source_visuals`, the plan must either select block-owned visuals or record structured rejection reasons for every candidate.

A visual is required only when a block chooses `image_plus_kp_list`. Blocks using other render modes must not carry `visual_ids`. This prevents uncontrolled auxiliary images from entering the notes.

## Forbidden legacy plan behaviour

The notes renderer must consume strict `sections[].blocks[]` plans. It must not infer document structure from loose top-level fields such as `topics`, `methods_and_data`, `confusions`, `practical_operations`, `past_paper_emphasis`, `add_on_sections`, `revision_checklist`, or root-level image dumps.
