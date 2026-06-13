# Exam Preparation Notes Protocol

Output artifact names should follow user requests when supplied. If no filename is requested, generate a clear DOCX filename from the source, course, prompt, or note title. The contract below controls content quality and rendering behavior, not exact filenames.

This is the canonical contract for coverage, teaching depth, formula visibility, student-facing prose, and Word formatting.

## Core Output Rule

Exam Preparation Notes are knowledge-only teaching notes. The public document must teach the course content and exam use of that content. It must not describe the workflow that produced the notes.

Student-facing notes may contain:

- topic headings that name knowledge units;
- concept explanations;
- mechanism or causal-chain explanations;
- method, control, readout, limitation, or data-interpretation explanations;
- comparison tables when relationships are easier to scan;
- visible formula blocks with symbol explanations and use steps;
- worked interpretation or calculation examples when they teach a reusable method;
- exam-answer guidance connected to the knowledge.

Student-facing notes must not contain:

- source intake summaries, extraction notes, route notes, source-routing labels, confidence bands, evidence scores, internal manifests, QA flags, planning text, subagent narration, or workflow phase names;
- public sections whose purpose is to report process rather than teach knowledge;
- checklists that only audit the workflow rather than revise knowledge;
- decorative examples that do not explain a concept, mechanism, method, calculation, comparison, data interpretation, evidence use, or answer move.

## Coverage Calibration

Coverage calibration is internal. It must happen before writing, but it must not appear as a public section.

Build the notes from connected knowledge signals:

1. Identify terms, definitions, mechanisms, methods, comparisons, equations, data interpretation, evidence, applications, and exam-answer uses.
2. Group connected signals into knowledge units.
3. For each unit, determine what a student must understand to revise and answer questions:
   - what the unit is;
   - why it matters;
   - how the mechanism, derivation, method, calculation, graph, or comparison works;
   - which assumptions or limitations control its use;
   - how it appears in an answer.
4. Expand dense or difficult units until the explanation is teachable. Do not compress high-density material into headings or one-sentence summaries.

Source hints are provenance labels only. They do not set public section titles, output length, or explanation depth.

## Teaching Depth

A knowledge unit is sufficiently explained only when the notes answer the relevant questions below:

- Identity: What is the concept, quantity, method, or relationship?
- Role: Why does it matter in the course?
- Mechanism or derivation: How does it work, follow, or get used?
- Conditions: What assumptions, boundary conditions, approximations, or limits apply?
- Interpretation: What does the result mean physically, mathematically, experimentally, clinically, or analytically?
- Exam use: How should a student use it to earn marks?

Use examples only when they teach reusable reasoning. A worked example should show the method path: identify givens, choose the relationship, substitute or reason, interpret the result, and state the exam conclusion.

## Formula Visibility

Formula-heavy material must be visible and readable in the final DOCX.

Use display formula blocks for important equations. A formula block must include:

- a readable mathematical expression;
- definitions of non-obvious symbols;
- assumptions or domain of validity when relevant;
- a short explanation of how to use the formula.

Prefer Word equation/OMML rendering for display formulas. If that is not available, use a Unicode mathematical fallback that is directly readable in Word.

Final formulas must not be left as raw pseudo-code when a mathematical expression is required. Avoid public formula text such as:

- `partial x`, `partial/partial x`, or `d/dt` when a visible derivative can be shown;
- `sqrt(...)` when a radical can be shown;
- `sum_ij`, `sum_i`, or `int` when summation or integral symbols can be shown;
- `dot` or `cross` when the dot product or cross product symbol can be shown;
- ASCII-only powers and subscripts when readable superscripts or subscripts are practical.

Acceptable public formula examples:

- `p = mv`
- `M = r × p`
- `Eₙ = (n + 1/2)ℏω`
- `∂ρ/∂t + ∇ · J = 0`
- `δ = √(2/(μγω))`
- `∇²E = μ₀ε₀ ∂²E/∂t²`

## Student-Facing Voice

Write like a strong tutor preparing a student for an exam. Use direct academic English. Prefer concise explanation, but do not reduce explanations to labels.

Good notes:

- explain before they compress;
- connect formulas to meaning;
- use bullets for separable answer points;
- use tables for repeated comparisons or criteria;
- use paragraphs for connected reasoning;
- keep headings informative but never use headings as a substitute for explanation.

Avoid filler introductions, process narration, and generic template prose.

## Render Modes

Each knowledge block should use the form that best teaches the content:

| Render mode | Use when | Public form |
|---|---|---|
| `paragraph` | The unit needs connected explanation, interpretation, or caveat handling. | Short teaching paragraph. |
| `kp_list` | The unit contains separable answer points, steps, assumptions, uses, features, or limitations. | Bullets with label plus explanation. |
| `compact_table` | The unit is a comparison, criteria set, parameter set, phase set, method set, or definition group. | Real DOCX table. |
| `mechanism_chain` | The unit is causal, sequential, or procedural. | Numbered or arrow-linked mechanism steps. |
| `formula_block` | The unit contains an important equation, derivation result, or calculation template. | Visible formula plus symbol/use explanation. |
| `image_plus_kp_list` | A source visual explains faster than text and has block-owned key points. | Small visual plus explanatory key points. |

Bullets must contain explanation. A label-only bullet is invalid.

## Document Style

Use these document settings:

| Element | Style |
|---|---|
| Font | Arial |
| Page margins | 2.5 cm on all sides |
| Line spacing | 1.5 |
| Main title | Centered |
| Section headings | Left aligned |
| Body text | Justified |
| Tables | Compact Word tables with visible borders |
| Display formulas | Centered, readable, separated from body text |

## Public Document Shape

Use the minimum public structure needed to teach the material. A typical notes document contains:

1. Main title.
2. Knowledge-unit sections in course or exam-priority order.
3. Optional mode-specific sections when the user asks for MCQ, short-answer, long-answer, practical/data/problem, or essay preparation.

Do not create public sections for internal planning, source extraction, coverage calibration, example filtering, QA, or release checks.

## Mode-Specific Knowledge

Mode-specific preparation must still be knowledge-first:

- MCQ: tested point, correct reasoning, plausible distractor logic, and why the distractor is wrong.
- Short answer: definition, mark-bearing points, explanation sentence, and concise answer form.
- Long answer: knowledge selection, reasoning order, formula or mechanism use, and answer structure.
- Practical/data/problem: method aim, readout, control, calculation or interpretation, limitation, and conclusion.
- Essay: claim, explanation, course detail, evidence when available, analysis, and link back to the question.

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
          "use": "Use this to connect current divergence to local charge change."
        }
      ]
    }
  ]
}
```

Loose top-level planning fields are internal. They must not be rendered as public workflow sections.
