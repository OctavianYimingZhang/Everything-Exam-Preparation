---
name: everything-exam-preparation
description: Route standalone exam and revision requests to Course Atlas, past-paper Analysis, knowledge-only Notes, Practice, or exam Essay support while refusing out-of-scope assessed coursework and administration.
---

# Everything Exam Preparation Router

Use the package workflow in [`../../SKILL.md`](../../SKILL.md) and the shared result contract in `references/input_and_evidence_protocol.md`.

Route the requested artifact directly:

- Mind Map, Course Atlas, knowledge tree, concept graph, website-import JSON or ZIP → `exam-prep-atlas`
- Units Analysis, formal recurrence, question mapping or clustering, exam intelligence → `exam-prep-analysis`
- course-complete knowledge-only Notes → `exam-prep-notes`
- questions, worked solutions, Answer PDFs, evaluation, or timed work → `exam-prep-practice`
- exam essay plans, shared-body model essay views, paragraph exemplars, or closed past-assessment review → `exam-prep-essay`

For an explicit multi-artifact request, return every local owner and run each independently. Keep the resulting artifacts separate unless the student asks for a combined file.

Complete deliverables for currently assessed coursework and university administration are outside this Plugin. State that boundary and stop. Do not call or identify another plugin as a destination.

Each focused Skill accepts the raw user files and independently invokes the shared source processor. No prior focused-Skill run or prepared index is required.
