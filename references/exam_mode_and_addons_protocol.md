# Exam Type Related Specific Research Reports

## Mode signals

- MCQ: option letters, single best answer, multiple choice, true/false style statements.
- Short Answer: define, state, list, outline, short mark values, separate mark points.
- Long Answer: explain, compare, evaluate, discuss, practical/data/problem questions, higher mark values.
- Practical/Data/Problem: method interpretation, controls, readouts, calculations, graph/table interpretation, problem statements.
- Essay: essay prompts, critically discuss, to what extent, argument-led questions, in-campus essay language.
- Online Essay Exam: online essay exam wording; take-home, open-book, 48h, or timed wording may be detection signals but not separate public Types.
- Mixed: more than one mode appears strongly; confirmed Mixed output covers each relevant component in the mix.

## Human review gate

Exam type and route detection are preliminary and must pass human review. Before producing Notes, Specific Research Reports, or Worked Solutions, display the **Auto-diagnosis review plan** and call `request_user_input` to confirm three decisions:

- Exam type/route: Notes, MCQ, Short Answer, Long Answer, Practical/Data/Problem, Worked Solutions, Essay, Online Essay Exam, Question Solving, Question Organization, or Mixed.
- Material type/source roles: knowledge material, practice material, marking material, style reference, Extra Reading, or Mixed.
- Notes generation choice: generate Notes first, skip Notes, or provide concise Notes in chat before the report.

For Online Essay Exam, the human review gate must also confirm whether Online Materials are required, optional, forbidden, or unclear; whether Lecture Materials may be used as primary evidence, background only, forbidden, or unclear; which supporting source types are allowed; whether citations or references are expected; and whether the output is chat draft, DOCX draft, or both. These source-permission answers are plan-changing items and must be recorded before any evidence map, plan, Notes, report, or draft.

Use the automatic diagnosis as evidence for the review decision. When Mixed signals appear, show the prompt signals, source-role counts, and question signals, then plan output that covers each relevant component after the user confirms the route, Material type, and Notes choice.

After the user confirms or corrects the review questions, update the route, confirmed source roles, and Notes choice before drafting. Public output is generated from the user-confirmed route and Notes decision.

## Reports

Exam Type Related Specific Research Reports are separate outputs from explanation-only Notes. They use the same knowledge map and source evidence, but shape the content around the requested exam mode. Extra Reading is used only when the confirmed Exam type includes Essay.

Slide triage is a Notes material-analysis step, not a report-priority system. `slide_decision`, `notes_role`, `detailed_explanation_allowed`, and `slide_triage_audit` must not narrow Past Paper-driven MCQ or Short Answer recurrence, Long Answer analysis, Worked Solutions, Essay reports, Question Solving, or Question Organization.

| Mode | Preparation content |
|---|---|
| MCQ | result-only Past Paper-driven recurrence report in lecture order, written as concise exam-needed knowledge points rather than a field-by-field template, answer walkthrough, or Notes-style teaching document |
| Short Answer | result-only Past Paper-driven recurrence report in lecture order, with each SAQ subquestion treated as an independent question record and the public report written as concise exam-needed knowledge points |
| Long Answer | source question, question demand, knowledge selection, reasoning order, example answer, and academic analysis/prediction result |
| Practical/Data/Problem | source task, method aim, readout, control, calculation or interpretation path, limitation, conclusion, and academic analysis/prediction result |
| Math/Physics/Practical Worked Solutions | every extracted calculation, derivation, estimate, proof, data, or problem question developed as worked-solution teaching notes with concise evidence status |
| Essay | claims, course detail, evidence integration, analysis, broad module-covering questions, example essay plans and essays |
| Online Essay Exam | locked brief, source-permission record for Online Materials and Lecture Materials, allowed-source evidence map, paragraph-level plan, CriticalAnalysisPlan, Planning Approval, draft generation, and QA rather than a Specific Research Report |
| Question Solving | target question analysis, matching knowledge display and explanation, solution reasoning, strict same-knowledge-point Past Paper or Practice Material questions, and transfer-practice prompt |
| Question Organization | Past Paper and Practice Material questions arranged by Lecture Slides or lecture knowledge-unit order in `organized_questions_docx` |

## Output relationship

Every exam route first offers explanation-only Notes. If the user accepts Notes, generate Notes before the exam-specific report. If the user declines Notes, skip Notes and generate the confirmed Specific Research Report. MCQ, short-answer, long-answer, practical/data/problem, worked-solution, essay, and Mixed routes produce separate Exam Type Related Specific Research Reports. Practice material can still inform Notes coverage by revealing repeated concepts, methods, calculations, source difficulty, and knowledge density. Question/practice material calibrates report emphasis while the full lecture/course knowledge-unit map continues to drive Notes coverage, including when no practice material is supplied or when essay/scenario questions cover only part of the course.

Online Essay Exam is the exception to the report relationship: Notes are optional support, and the main public output is a draft built from the locked brief, allowed-source evidence map, approved plan, and QA. It should not be narrowed into ordinary Essay Specific Research Report behavior.

When Past Paper material contains extractable questions, produce a separate question-based Specific Research Report alongside Notes when Notes are accepted. Practical Materials trigger that report when they contain explicit question, task, data, calculation, interpretation, or problem signals.

When Past Paper or Practical Materials contain calculation, derivation, estimate, proof, physics/math problem, data-interpretation, or problem-walkthrough signals, produce `practical_worked_solutions_docx` or an equivalent worked-solution teaching document. Use available solution or mark-scheme fragments to verify formula choice, algebra path, assumptions, units, final expression or numeric result, and interpretation. If no solution evidence is found, keep the worked explanation source-grounded and mark the evidence status concisely.

Math, physics, calculation, derivation, estimate, proof, and data/problem walkthrough outputs should be complete worked-solution notes. Write them as coherent teaching explanations that cover question interpretation, relevant givens, target, method choice, derivation or calculation path, answer explanation, assumptions, unit or dimension reasoning, result meaning, and evidence status where available.

Long Answer and Practical/Data/Problem reports should develop exam-answering ability through source-grounded question demand, relevant knowledge selection, answer order, and concise example-answer structure.

Question-based Specific Research Reports should be academic exam-preparation output. MCQ and Short Answer reports use a Past Paper-driven recurrence algorithm for high-frequency knowledge points. They should not copy star-ranking workflows from examples or use boundary formulas from screenshots. They should use only Past Papers, Mock Papers, and official exam papers for recurrence; ordinary Practice Material can provide context but must not count toward high-frequency recurrence.

For MCQ and Short Answer recurrence, each question record should preserve a matched lecture knowledge unit, direct exam demand, tested knowledge terms, answer-operation type, MCQ question pattern or SAQ answer pattern, source year, paper key, and locator in the internal workflow record. Cluster questions into the same recurring knowledge point only when the same or clearly explicit lecture knowledge unit, direct exam demand, shared specific terms, and compatible question or answer-operation pattern all match. Broad topic similarity is not enough.

Public MCQ and Short Answer reports are result-only. They should follow the user's reference-document style by using lecture headings, numbered knowledge-point titles, concise exam-needed knowledge-point content, and a short exam scope line when useful. Do not render template labels such as distractor logic, option selection, elimination steps, definition core, expected mark points, answer wording, or missing-mark traps. Do not render evidence tables, source locators, recurrence scores, frequency calculations, matching methods, debug fields, verification fields, or Codex workflow steps.

MCQ and Short Answer reports are concise exam-priority reinforcement, not lecture walkthrough Notes. Their recurrence results must not narrow the broad lecture reconstruction required for `docx_notes`. When Notes are generated alongside a report, Notes keep `coverage_policy: lecture_unit_complete`; the report separately highlights high-frequency or question-format-driven knowledge points.

Default public output language is English. Use Chinese, bilingual, or multiple-language output only when the user explicitly asks for it. User-provided bilingual examples are format references and do not change the default language.

## Question solving and transfer practice

When the user asks how to solve a supplied question, build `question_solution_report` from the user's material. Use this fixed order:

1. Target question analysis.
2. Matching knowledge display and explanation.
3. Solution or answer reasoning.
4. Strict same-knowledge-point Past Paper or Practice Material questions.
5. Transfer-practice prompt.

Strict same-knowledge-point retrieval must be source-grounded. A returned question should match the same lecture knowledge unit, share specific knowledge terms with the target question, and have visible source provenance such as file name, page, slide, chunk, or question order. Similar topic area or broad lecture overlap is not sufficient evidence. If the supplied material does not contain a strict same-point question, state that and do not substitute loose recommendations.

## Past Paper and Practice Material organization

When the user asks to organize Past Paper or Practice Material, generate `organized_questions_docx` by default. Extract questions from confirmed question sources, match each question to lecture knowledge units, and sort sections by Lecture Slides or lecture knowledge-unit order. If a question matches several lecture units, assign it to the latest matching lecture unit.

The organized DOCX should show question text and minimal provenance: source file, locator, and original question order when available. Keep answers, solution steps, detailed explanations, knowledge summaries, and predictions for the relevant teaching or report route rather than this organizer output.
