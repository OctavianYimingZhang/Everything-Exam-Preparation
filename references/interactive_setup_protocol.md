# Interactive Setup Protocol

Use setup mode when the request is broad, multi-file, or underspecified.

## Required fields

| Field | Purpose |
| --- | --- |
| `task_type` | Notes, essay, model answer, question drill, prediction, walkthrough, or workbook. |
| `exam_target` | Course, exam board, module, paper, or assessment. |
| `source_roles` | Which files are lectures, readings, past papers, examples, marking guides, or drafts. |
| `allowed_sources` | Whether external research is allowed. |
| `output_format` | Chat, Markdown, DOCX, workbook, table, or JSON. |
| `quality_checks` | Source coverage, citation discipline, language, formatting, and gap checks. |

## Setup behavior

- Ask only for missing fields that change the output.
- Infer harmless formatting preferences from the user's request.
- Treat unsupported content as a gap.
- Confirm file output before creating files.
