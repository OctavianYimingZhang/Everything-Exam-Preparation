# Exam Preparation Notes protocol

Default artifact: `Exam_Preparation_Notes.docx`.

## Required structure

1. High-yield exam map
2. Core concepts by source/topic
3. Mechanisms, methods, calculations, and data interpretation
4. Common confusions and contrasts
5. Practical/data/problem operations
6. Past-paper emphasis map
7. Exam-mode add-on section if applicable
8. Final quick revision checklist

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

| render_mode | Use when | Student-facing form |
|---|---|---|
| `kp_list` | The source or exam asks for named points, criteria, uses, causes, features, examples, advantages, limitations, steps, or `describe/list TWO/THREE/N` answers. | Compact bullets. Each bullet has a label plus one short explanatory clause. |
| `compact_table` | The content is a comparison, distinction, parameter set, assay type set, phase set, response type set, or definition group. | A short table or table-like rows. Keep cells short. |
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

A bullet is valid only if it contains the answer point plus at least one of: why it matters, how it works, when it applies, what it predicts, what limitation follows, or how it earns marks.

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

- H-bond donors below 5.
- H-bond acceptors below 10.
- Molecular mass below 500 Da.
- logP not above 5.

For a comparison such as graded versus quantal response, use `compact_table` with columns for type, measure, and typical output.

## Visual policy

Use source slide images only if they explain faster than text. Do not use decorative images. Default maximum image width is 3.8 inches. Use captions only when they help locate meaning. Do not expand the document with huge screenshots. If the renderer cannot safely embed a source image, replace it with a compact table or redraw description rather than a long paragraph.
