# Exam Preparation Notes Protocol

Output artifact names should follow user requests when supplied. If no filename is requested, generate a clear, distinct DOCX filename for each output from the source, course, prompt, or note title.

This is the canonical contract for Notes coverage, explanation depth, default language, formula visibility, visual rendering, student-facing prose, and Word formatting.

## Unified Output Controls

Default student-facing output language is English unless the user explicitly requests another language.

Render DOCX Notes with Arial, 2.5 cm margins, 1.5 line spacing, centered main title, left-aligned headings, justified body text, compact tables, centered display formulas, compact academic captions, academically useful source visuals, and clear knowledge sections.

Readable DOCX styling should remain academic. Use moderate font sizes, black academic text, restrained heading style, compact captions, centered display formulas, and black-and-white academic paper tables when they improve scanability. Tables should use compact editable cells, concise titles above, restrained horizontal rules, portrait-friendly width, and notes below for symbols, abbreviations, units, statistical notation, or source details.

Notes are explanation-only teaching documents and remain knowledge-only teaching notes. They are broad lecture reconstruction documents for students who may not have learned the lecture well yet. Notes should let the student work through the lecture and exam-relevant knowledge and master most substantive lecture material before using MCQ, SAQ, or other Specific Research Reports for exam-priority reinforcement. Formulas, visuals, and worked examples are part of knowledge explanation when they help teach a knowledge unit. Exam Type Related preparation is handled as a separate Specific Research Report by `references/exam_mode_and_addons_protocol.md`.

## Core Notes Content

Student-facing Notes may contain:

- topic headings that name knowledge units;
- concept explanations;
- mechanism or causal-chain explanations;
- method, control, readout, limitation, or data-interpretation explanations;
- comparison tables when relationships are easier to scan;
- visible formula blocks with symbol explanations, assumptions, and conceptual use;
- source visuals when they clarify a concept, mechanism, method, formula, graph, table, pathway, scheme, or data interpretation;
- worked interpretation or calculation examples with step-by-step academic solutions when they teach reusable reasoning;
- essay-style external enrichment when the confirmed output calls for it and the source strengthens a course point or essay claim.

Student-facing Notes should present course knowledge explanation, exam-relevant understanding, academic source visuals, and worked examples. They should not collapse into a Past Paper priority list, MCQ trap list, SAQ template, prediction report, or answer-walkthrough report. Workflow artifacts, route planning, source intake narration, coverage calibration narration, QA state, and subagent narration belong to the internal workflow record.

Notes coverage comes from the full set of lecture and course knowledge units. Question and practice material calibrate Specific Research Report emphasis and can reveal repeated concepts, methods, calculations, source difficulty, and knowledge density, but they do not narrow the Notes coverage. When no question or practice material is supplied, build Notes from the lecture/course knowledge units. Essay questions and scenario questions should guide report emphasis while preserving full course knowledge coverage in Notes.

Online Essay Exam is a separate drafting branch. Notes may support it when the user wants lecture review, but Online Materials and Lecture Materials permissions must be confirmed before the Online Essay Exam evidence map or draft is planned.

## Notes and Reports Separation

Notes and Reports are intentionally separate outputs:

- Notes are lecture-unit complete teaching notes. They reconstruct and explain the lecture in course order so a weakly prepared student can learn most substantive material.
- MCQ and Short Answer reports are concise exam-priority reinforcement. They use Past Papers or question formats to highlight recurring exam-needed knowledge points.
- Reports may point back to the broad Notes knowledge map, but Reports must not replace, narrow, or determine Notes coverage.
- Notes may mention exam relevance when it clarifies why a concept matters, but they should not become a recurrence report, answer key, prediction list, or high-frequency-only summary.

## Lecture-Unit Complete Coverage

Use `coverage_policy: lecture_unit_complete` for Exam Prep Notes plans. This means near slide-by-slide coverage at the level of substantive lecture units, not literal commentary on every slide or image. The public Notes should cover most substantive lecture-slide content through coherent units, while compressing or excluding non-teaching material.

For each lecture or course file, build a coverage map before writing:

1. Preserve lecture/source order for Notes. Do not sort the public Notes primarily by exam frequency or signal score.
2. Identify intended learning outcomes, topic boundaries, definitions, mechanisms, pathways, methods, comparisons, data or diagram meanings, important examples, and conceptual applications.
3. Group slide or fragment signals into lecture units that a student can learn from in sequence.
4. Expand dense or novel units enough that a weakly prepared student can reconstruct the reasoning.
5. Maintain a `coverage_audit` in the internal plan showing which lecture sources are represented and which fragments were compressed or excluded.

Content triage for Notes:

- `core_lecture_content`: must be covered in the Notes through explanation.
- `supporting_example`: include when it teaches reusable reasoning; compress when examples repeat the same point.
- `reading_reference`: exclude unless the reading itself is directly needed to explain examinable course knowledge.
- `admin_or_boilerplate`: exclude unless it changes assessed content.
- `low_exam_relevance_context`: compress or exclude unless it directly explains a course mechanism, method, concept, or application.

## Slide Triage Before Notes

For slide decks and slide-like PDFs, run internal `exam-prep-slide-triage` material analysis before writing Notes. Slide triage is not a detail-level grading system and is not used to save time by dropping legitimate course knowledge. Its function is to exclude useless slides from detailed public explanation and to keep structural slides available for topic order, lecture flow, and coverage audit.

Each slide-like fragment should carry:

- `slide_decision`: `use`, `merge_with_previous`, or `exclude`;
- `notes_role`: `knowledge_source`, `structure_marker`, `visual_or_data_support`, `example_or_summary_support`, or `non_teaching_material`;
- `detailed_explanation_allowed`: boolean;
- `triage_reason`: concise internal reason;
- provenance fields such as source name, lecture order, slide or page number, and likely slide title.

Use `use` with `detailed_explanation_allowed: true` for substantive knowledge slides: definitions, concepts, mechanisms, pathways, methods, assays, comparisons, formulas, calculations, direct graph interpretation, direct data interpretation, and conceptual applications.

Use `use` with `detailed_explanation_allowed: false` for ILOs, agendas, topic boundaries, section dividers, summaries, conclusions, and recaps. These slides should help topic splitting and lecture order, but they should not become long public explanations unless they contain substantive knowledge signals.

Use `merge_with_previous` for repeated examples, continuation slides, supporting cases, non-core visuals, non-essential data, and recap material that should support a nearby knowledge unit without becoming its own Notes section.

Use `exclude` for administrative, contact, deadline, copyright/license, source-credit, reading-list-only, textbook-reference-only, decorative, empty, pure transition, duplicate-with-no-new-knowledge, and generic awareness/social-framing slides that do not teach course knowledge.

Maintain `slide_triage_audit` internally with retained, merged, and excluded slide counts plus exclusion reasons. Excluded slides should not become public Notes sections, detailed paragraphs, visual explanations, or exam-priority claims. Specific Research Reports must not use slide triage to narrow or replace their Past Paper-driven or route-specific analysis.

## Coverage Calibration

Coverage calibration is internal. Build the notes from connected knowledge signals:

1. Identify terms, definitions, mechanisms, methods, comparisons, equations, data interpretation, evidence, applications, and explanatory examples.
2. Group connected signals into knowledge units.
3. For each unit, determine what a student must understand:
   - what the unit is;
   - why it matters;
   - how the mechanism, derivation, method, calculation, graph, or comparison works;
   - which assumptions, boundary conditions, approximations, or limits affect interpretation;
   - how the result or concept is used within the discipline.
4. Match explanation depth to knowledge density, mechanism complexity, calculation burden, method-interpretation needs, evidence density, and source difficulty. Dense or difficult units should receive enough explanation for a student to reconstruct the reasoning.

Source hints act as provenance labels. They help locate knowledge signals and essay-enrichment sources, while the public Notes structure is set by the knowledge units.

## Teaching Depth

A knowledge unit is sufficiently explained when the notes answer the relevant questions below:

- Identity: What is the concept, quantity, method, or relationship?
- Role: Why does it matter in the course or discipline?
- Mechanism or derivation: How does it work, follow, or get used?
- Conditions: What assumptions, boundary conditions, approximations, or limits apply?
- Interpretation: What does the result mean physically, mathematically, experimentally, clinically, analytically, or computationally?
- Conceptual application: How does the student use the knowledge to reason about a new case, calculation, diagram, method, or dataset?

Use examples when they teach reusable reasoning. A worked example should show the method path: identify givens, state the target, choose the relationship, solve step by step, check units or assumptions where relevant, interpret the result, and state the conceptual conclusion.

## Formula Visibility

Formula-heavy material must be visible and readable in the final DOCX.

Use display formula blocks for important equations, derivation results, reaction schemes, algorithms written as mathematical relationships, or calculation templates. A formula block should include:

- a readable mathematical or technical expression;
- definitions of non-obvious symbols;
- assumptions or domain of validity when relevant;
- a short explanation of how the formula or expression is interpreted.

Prefer Word equation/OMML rendering for display formulas. When equation conversion is unavailable, use a readable Unicode mathematical fallback.

Formula normalization should be domain-neutral. The renderer should classify technical expressions before conversion and then preserve or normalize them according to intent:

- mathematical expressions: derivatives, gradients, sums, products, integrals, limits, powers, roots, vectors, matrices, tensors, inequalities, and Greek symbols;
- physics expressions: vector notation, dot and cross products, constants, units, dimensions, fields, conservation equations, and rate equations;
- chemistry expressions: molecular formulae, charges, isotopes, stoichiometric coefficients, reaction arrows, reversible reactions, equilibrium notation, and state labels;
- biological-science expressions: pH/pK notation, enzyme constants, metabolite formulae, concentrations, rates, and pathway reaction equations;
- coding-adjacent expressions: preserve code-like syntax when programming meaning is likely, while rendering mathematical relationships in readable notation.

Ambiguous expressions should remain stable and readable rather than being over-converted.

## Visual Rendering

PDF visual-region assets, DOCX/PPTX embedded media, and source visual assets may be included in Notes when they strengthen a knowledge unit. Prefer PDF crops that isolate the specific figure, table, diagram, graph, pathway, scheme, or image that carries the academic meaning. Select visuals by positive academic value:

- concept clarity;
- mechanism or pathway density;
- diagram dependence;
- calculation or data-interpretation burden;
- method readout, control, or limitation value;
- close source relevance to the surrounding explanation.

For PDFs, use a cropped visual asset when the extractor can identify a concrete visual region. When the source evidence gives a page locator without a reliable local visual crop, use the locator to support the written explanation. Pair each included visual with an academic caption or source locator and explanatory key points. Keep visual placement inside the relevant knowledge unit.

Acceptable public formula examples:

- `p = mv`
- `M = r × p`
- `Eₙ = (n + 1/2)ℏω`
- `∂ρ/∂t + ∇ · J = 0`
- `δ = √(2/(μγω))`
- `∇²E = μ₀ε₀ ∂²E/∂t²`
- `HCO₃⁻ + H⁺ ⇌ H₂CO₃ ⇌ CO₂ + H₂O`

## Student-Facing Voice

Write like a strong tutor preparing a student for an exam. Use direct academic English by default. Prefer concise explanation, but do not reduce explanations to labels.

Good Notes:

- explain before they compress;
- connect formulas to meaning;
- use bullets for separable explanation points, steps, assumptions, uses, features, or limitations;
- use tables for repeated comparisons, criteria, parameter sets, phase sets, method sets, or definition groups;
- use paragraphs for connected reasoning;
- keep headings informative while giving the actual explanation in the body.

## Render Modes

Each knowledge block should use the form that best teaches the content:

| Render mode | Use when | Public form |
|---|---|---|
| `paragraph` | The unit needs connected explanation, interpretation, or caveat handling. | Short teaching paragraph. |
| `kp_list` | The unit contains separable explanation points, steps, assumptions, uses, features, or limitations. | Bullets with label plus explanation. |
| `compact_table` | The unit is a comparison, criteria set, parameter set, phase set, method set, or definition group. | Real DOCX table. |
| `mechanism_chain` | The unit is causal, sequential, procedural, or derivational. | Numbered or arrow-linked mechanism steps. |
| `formula_block` | The unit contains an important equation, derivation result, reaction scheme, or calculation template. | Visible formula plus symbol/use explanation. |
| `worked_example` | A calculation, derivation, estimate, proof, data, or problem example teaches the knowledge unit. | Coherent worked-solution teaching explanation that shows the question interpretation, method path, calculation or reasoning, result, checks, and meaning. |
| `image_plus_kp_list` | A source visual explains faster than text and has block-owned key points. | Academic visual, caption/source locator, and explanatory key points. |

Bullets should contain explanation. A label becomes useful when it is paired with the reason, mechanism, condition, or interpretation that makes it meaningful.

## Public Document Shape

A typical Notes document contains:

1. Main title.
2. Knowledge-unit sections in course order or knowledge-priority order.
3. Formula, method, comparison, and data-interpretation explanations inside the relevant knowledge unit.
4. Essay-style external enrichment inside the confirmed essay report paragraph or beside the course point it strengthens.

Exam Type Related sections such as MCQ traps, short-answer templates, long-answer structures, practical/data tactics, essay plans, and standalone reading lists are Specific Research Report content. Route them through the separate preparation report workflow.

## Renderer Input Shape

The renderer should prefer strict section/block input:

```json
{
  "title": "Exam Preparation Notes",
  "sections": [
    {
      "heading": "Knowledge Unit",
      "blocks": [
        {
          "render_mode": "paragraph",
          "heading": "Concept",
          "text": "Teaching explanation."
        },
        {
          "render_mode": "formula_block",
          "heading": "Key relationship",
          "formula": "∂ρ/∂t + ∇ · J = 0",
          "symbols": ["ρ is charge density", "J is current density"],
          "assumptions": ["The equation is local and continuous."],
          "use": "Use this to connect current divergence to local charge change."
        },
        {
          "render_mode": "worked_example",
          "heading": "Worked calculation example",
          "question": "Teaching question.",
          "givens": ["Given quantity or condition."],
          "target": "Quantity or expression to find.",
          "method": "Relevant course relationship or derivation path.",
          "steps": ["Step-by-step academic solution."],
          "final_answer": "Final expression or value.",
          "assumptions": ["Assumption or approximation."],
          "unit_check": "Dimensional or unit check.",
          "interpretation": "Meaning of the result."
        },
        {
          "render_mode": "image_plus_kp_list",
          "heading": "Source visual",
          "asset_path": "assets/source_visual.png",
          "caption": "Figure source locator.",
          "key_points": ["Explain what the visual shows and why it matters."]
        }
      ]
    }
  ]
}
```

Loose top-level planning fields are internal. They should be converted into strict sections and blocks before rendering public Notes.
