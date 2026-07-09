---
name: exam-prep-long-answer
description: Produce long-answer, practical, data, scenario, or problem Exam Type Related preparation from past papers, practice material, mark schemes, lab tasks, datasets, or application questions.
---

# Long Answer And Practical Preparation

Create a long-answer, practical, data, scenario, or problem-focused Specific Research Report after `exam-prep-index` has confirmed this route. Use this Skill when the user needs answer structure, relevant knowledge selection, method interpretation, analysis, or prediction rather than calculation-heavy step-by-step worked solutions.

Default public output is English. Change the language only when the user explicitly overrides it for the current task; examples in another language do not change the default.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/exam_prep_notes_protocol.md` only when the index confirmed Notes or existing Notes need to be referenced

Use `scripts/exam_mode_tools.py`, `scripts/plan_workflow.py`, and `scripts/build_review_questions.py` for extraction, route planning, and human review.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Long Answer or Practical/Data/Problem output. Confirm the route, Material type/source roles, Notes generation choice, and detailed-analysis choice before writing.

## Workflow

1. Extract source questions, practical tasks, scenarios, data prompts, and marking or solution evidence.
2. Separate answer-structure tasks from calculation, derivation, estimate, proof, data, or problem tasks that should route to `exam-prep-worked-solutions`.
3. Map each item to relevant knowledge, method aim, readout, control, interpretation, limitation, conclusion, and analysis/prediction result as applicable.
4. Use the confirmed review state before public document generation if this Skill was invoked directly without `exam-prep-index`.

## Output Contract

For long-answer items, include source question, question demand, relevant knowledge, answer structure, example answer, and academic analysis/prediction result.

For practical/data/problem items, include source task, method aim, readout, control, calculation or interpretation, limitation, conclusion, and academic analysis/prediction result.

Use a separate Specific Research Report unless the user asks for chat output.
