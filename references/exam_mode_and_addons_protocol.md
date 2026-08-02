# Practice Protocol

## Purpose

Practice turns course evidence and question material into the exact learning or assessment artifact requested by the student.

## Question-Based Preparation

For MCQ and short-answer recurrence, use actual past or mock papers as recurrence evidence. Treat each short-answer subquestion as its own record. Present concise exam-needed knowledge in lecture order.

For long-answer, practical, and data questions, explain the command, relevant knowledge, method, reasoning chain, answer structure, and a source-grounded example response.

For calculations and worked solutions, show:

1. interpretation of the question;
2. givens and target;
3. method selection;
4. derivation or calculation steps;
5. units, dimensions, and assumptions;
6. final result and its meaning.

## Integrated Capabilities

Question solving connects one target question to the relevant knowledge unit, explains the reasoning, and adds closely matched transfer questions.

Question organisation extracts supplied questions and places them in lecture or knowledge-unit order with minimal provenance.

An assessment blueprint maps knowledge units evidenced by source fragments. Source occurrence may describe coverage; assessment weights come from explicit assessment evidence.

Answer evaluation compares a supplied student answer with a rubric, mark scheme, or explicit expected concepts. Evaluate concept aliases and their relationships at token and clause level, including local negation; do not treat a substring as conceptual evidence. Return one criterion status from `correct`, `partial`, `incorrect`, `contradicted`, or `missing`, together with supporting or conflicting evidence and actionable revision guidance.

Keep awarded marks distinct from estimates. Return no mark estimate when the criteria have no explicit mark allocation. When every criterion carries marks, an estimate may use rubric-supplied status credit; otherwise label the documented partial-credit heuristic and retain `mark_awarded: null`.

Timed practice uses an explicit total duration and an assessment blueprint. Each slot records its time allocation and source basis.

## Output

Use the format requested by the user. For DOCX artifacts, apply the shared academic document design. Preserve provenance in outputs where it assists checking, and keep analysis/debug fields in internal records.
