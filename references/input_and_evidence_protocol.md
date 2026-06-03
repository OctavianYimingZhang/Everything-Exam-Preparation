# Input and evidence protocol

## Source roles

Use these roles exactly:

- `lecture_slides`
- `lecture_notes`
- `official_course_notes`
- `practical_material`
- `data_problem_material`
- `past_paper`
- `mark_scheme`
- `answer_key`
- `example_answer`
- `user_draft`
- `style_reference`
- `extra_reading`
- `source_visual`

## Authority rules

Course sources support factual course knowledge. Practical and data/problem sources support methods, calculations, readout interpretation, controls, and limitations. Past papers support exam mode, emphasis, and answer operations, but they do not create unsupported course claims. Mark schemes and answer keys support expected marking operations and answer shape.

Example answers, user drafts, and style references are style or layout evidence only unless they are official answer keys. Extra reading supports essay depth only when it is supplied, read, and linked to the prompt.

## Evidence boundaries

Do not merge source roles into one undifferentiated source pool. A claim is usable only when its source role can support that claim type. Unsupported points become gaps, not inferred facts.

If a source is unreadable or partial, record the affected source class and block only conclusions that depend on the missing material.

## Runtime identity

Each readable source document and extracted fragment should keep a stable ID and fingerprint. Downstream claims, preparation artifacts, and QA gates should link back to those IDs internally. The student-facing output must receive only the resulting explanation, not the internal IDs or link records.

## Visual source handling

Source visuals may be used when they explain a mechanism, method, graph, workflow, structure, or comparison faster than text. Decorative images are not evidence. A visual never overrides text evidence. If a resized image would be unreadable, replace it with a concise redraw, table, or description.

Extracted PPT media should retain enough locator metadata for rendering: `source_id`, `source_path`, `media_name`, role, and optional caption. Generated schematic images are allowed only as explanatory redraws from already-supported claims; they are not independent factual evidence.
