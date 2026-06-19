# Exam Type Related Add-ons

## Mode signals

- MCQ: option letters, single best answer, multiple choice, true/false style statements.
- Short Answer: define, state, list, outline, short mark values, separate mark points.
- Long Answer: explain, compare, evaluate, discuss, practical/data/problem questions, higher mark values.
- Practical/Data/Problem: method interpretation, controls, readouts, calculations, graph/table interpretation, problem statements.
- Essay: essay prompts, critically discuss, to what extent, argument-led questions, in-campus essay language.
- Mixed: more than one mode appears strongly; confirmed Mixed output covers each relevant component in the mix.

## Human review gate

Exam type and route detection are preliminary and must pass human review. Before producing Notes, Exam Type Related add-ons, or Worked Solutions, display the **Auto-diagnosis review plan** and call `request_user_input` to confirm three decisions:

- Exam type/route: Notes, MCQ, Short Answer, Long Answer, Practical/Data/Problem, Worked Solutions, Essay, or Mixed.
- Material type/source roles: knowledge material, practice material, marking material, style reference, Extra Reading, or Mixed.
- output set confirmation: Notes focus, Notes plus Exam Type Related add-on, Notes plus Worked Solutions, add-on focus, or a user-specified file set.

Use the automatic diagnosis as evidence for the review decision. When Mixed signals appear, show the prompt signals, source-role counts, and question signals, then plan output that covers each relevant component after the user confirms the route, Material type, and output set.

After the user confirms or corrects the review questions, update the route, confirmed source roles, and final output set before drafting. Public output is generated from the user-confirmed final output set.

## Add-ons

Exam Type Related add-ons are separate outputs from explanation-only Notes. They use the same knowledge map, source evidence, and confirmed essay-style Extra Reading enrichment when relevant, but shape the content around the requested exam mode.

| Mode | Preparation content |
|---|---|
| MCQ | lecture-order source questions, tested distinctions, single-best-answer reasoning, plausible wrong statements, and question-derived high-frequency knowledge points for the add-on |
| Short Answer | lecture-order source questions, definitions, mark-point structures, concise answer forms, explain-style examples, and question-derived high-frequency knowledge points for the add-on |
| Long Answer | source question, question demand, knowledge selection, reasoning order, example answer, and academic analysis/prediction result |
| Practical/Data/Problem | source task, method aim, readout, control, calculation or interpretation path, limitation, conclusion, and academic analysis/prediction result |
| Math/Physics/Practical Worked Solutions | every extracted calculation, derivation, estimate, proof, data, or problem question developed as worked-solution teaching notes with concise evidence status |
| Essay | claims, course detail, evidence integration, analysis, broad module-covering questions, example essay plans and essays |

## Output relationship

`exam_prep_notes` produces explanation-only Notes. MCQ, short-answer, long-answer, practical/data/problem, and essay routes produce separate Exam Type Related add-ons. Practice material can still inform Notes coverage by revealing repeated concepts, methods, calculations, source difficulty, and knowledge density. Question/practice material calibrates add-on emphasis while the full lecture/course knowledge-unit map continues to drive Notes coverage, including when no practice material is supplied or when essay/scenario questions cover only part of the course.

When Past Paper material contains extractable questions, produce a separate question-based Exam Type Related DOCX alongside Notes. Practical Materials trigger that add-on when they contain explicit question, task, data, calculation, interpretation, or problem signals.

When Past Paper or Practical Materials contain calculation, derivation, estimate, proof, physics/math problem, data-interpretation, or problem-walkthrough signals, produce `practical_worked_solutions_docx` or an equivalent worked-solution teaching document. Use available solution or mark-scheme fragments to verify formula choice, algebra path, assumptions, units, final expression or numeric result, and interpretation. If no solution evidence is found, keep the worked explanation source-grounded and mark the evidence status concisely.

Math, physics, calculation, derivation, estimate, proof, and data/problem walkthrough outputs should be complete worked-solution notes. Write them as coherent teaching explanations that cover question interpretation, relevant givens, target, method choice, derivation or calculation path, answer explanation, assumptions, unit or dimension reasoning, result meaning, and evidence status where available.

Question-based add-ons should be academic exam-preparation output. Analysis/Prediction should develop exam-answering ability by presenting likely topic, question demand, repeated knowledge target, expected answer focus, and the academic reasoning that connects those points to the confirmed question material.
