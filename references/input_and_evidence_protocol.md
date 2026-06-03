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
- `previous_generated_output`
- `generated_output`
- `source_visual`
- `unknown`

## Authority rules

Course sources support factual course knowledge. Practical and data/problem sources support methods, calculations, readout interpretation, controls, and limitations. Past papers support exam mode, emphasis, and answer operations, but they do not create unsupported course claims. Mark schemes and answer keys support expected marking operations and answer shape.

Example answers, user drafts, and style references are style or layout evidence only unless they are official answer keys. Extra reading supports essay depth only when it is supplied, read, and linked to the prompt.

## Route-specific source decision

Every source must receive a role and a route-specific `evidence_scope` before it can affect a plan.

For `exam_prep_notes`, factual course claims may only come from sources assigned `factual_course_content` for that route. Past papers normally provide `exam_emphasis`: they shape likely emphasis, answer operations, and practice priority, but they do not override course material. Mark schemes and answer keys normally support `exam_emphasis` or answer operations, not new course facts. Style references, example answers, user drafts, and previous generated outputs may only affect style or layout when explicitly useful; they must not supply factual claims.

Allowed `exam_prep_notes` scopes:

- `factual_course_content`
- `exam_emphasis`
- `style_only`
- `visual_candidate_only`
- `ignored`
- `needs_confirmation`

For `practice_marking`, allowed scopes are `student_answer`, `question_source`, `marking_authority`, `factual_course_content`, `ignored`, and `needs_confirmation`. That route may reuse source inventory, but it must not change the notes plan or notes renderer contract.

This is a role-purpose-evidence-scope decision. It is not a filename blacklist. Ambiguous sources are assigned `needs_confirmation` or kept out of factual notes until their role is clear.

## Evidence boundaries

Do not merge source roles into one undifferentiated source pool. A claim is usable only when its source role can support that claim type. Unsupported points become gaps, not inferred facts.

If a source is unreadable or partial, record the affected source class and block only conclusions that depend on the missing material.

## Runtime identity

Each readable source document and extracted fragment should keep a stable ID and fingerprint. Downstream claims, preparation artifacts, and QA gates should link back to those IDs internally. The student-facing output must receive only the resulting explanation, not the internal IDs or link records.

## Visual source handling

Source visuals may be used when they explain a mechanism, method, graph, workflow, structure, or comparison faster than text. Decorative images are not evidence. A visual never overrides text evidence. If a resized image would be unreadable, replace it with a concise redraw, table, or description.

Extracted PPT media should retain enough locator metadata for rendering: `source_id`, `source_path`, `media_name`, role, and optional caption. Generated schematic images are allowed only as explanatory redraws from already-supported claims; they are not independent factual evidence.
