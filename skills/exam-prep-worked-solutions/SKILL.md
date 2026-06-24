---
name: exam-prep-worked-solutions
description: Produce Math, Physics, Practical, calculation, derivation, estimate, proof, data, or problem worked-solution teaching notes from questions, practical materials, answer keys, mark schemes, or solution fragments.
---

# Worked Solutions

Create a worked-solutions Specific Research Report for calculation-heavy or reasoning-heavy questions after `exam-prep-index` has confirmed this route. Use this Skill when the material contains calculations, derivations, estimates, proofs, data analysis, physics/math problems, or practical problem-solving tasks.

## Load First

Read:

- `references/input_and_evidence_protocol.md`
- `references/exam_mode_and_addons_protocol.md`
- `references/exam_prep_notes_protocol.md` for visible formulas and DOCX styling

Use `scripts/exam_mode_tools.py`, `scripts/plan_workflow.py`, `scripts/build_review_questions.py`, and `scripts/generate_exam_prep_notes_docx.py` when producing DOCX output.

When this Skill is read from the source checkout instead of an installed local skill, shared resources live two directories up from this file.

## Direct Invocation Gate

If this Skill is invoked directly without a confirmed `exam-prep-index` review state, apply the Direct Invocation Gate in `references/input_and_evidence_protocol.md` before public Worked Solutions output. Confirm the worked-solution route, Material type/source roles, Notes generation choice, and teaching-depth choice before writing.

## Workflow

1. Extract every calculation, derivation, estimate, proof, data, or problem question.
2. Collect mark schemes, solution fragments, answer keys, units, assumptions, diagrams, and source context.
3. Use available solution evidence for formula choice, algebra path, units, assumptions, final result, and interpretation.
4. Where evidence is incomplete, state the evidence status and derive from course principles rather than inventing source-backed certainty.
5. Use the confirmed review state before writing public Worked Solutions if this Skill was invoked directly without `exam-prep-index`.

## Output Contract

Write complete worked-solution notes in coherent prose. Teach the question interpretation, givens, target, method choice, derivation or calculation path, answer explanation, assumptions, unit or dimension reasoning, result meaning, and evidence status.

Use visible formulas with Word equation/OMML where possible and readable Unicode mathematical fallback when equation conversion is unavailable.
