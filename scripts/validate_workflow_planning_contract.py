#!/usr/bin/env python3
"""Validate workflow-planning files for the exam-prep skill."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    'scripts/plan_workflow.py',
    'schemas/skill_config.schema.json',
    'schemas/workflow_plan.schema.json',
    'schemas/workflow_action.schema.json',
    'schemas/source_document.schema.json',
    'schemas/source_fragment.schema.json',
    'schemas/evidence_claim.schema.json',
    'schemas/gate_result.schema.json',
]


def fail(message: str) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)


def load_json(rel: str) -> dict:
    try:
        return json.loads((ROOT / rel).read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        fail(f'invalid JSON in {rel}: {exc}')


def main() -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            fail(f'missing required file: {rel}')
    schema = load_json('schemas/skill_config.schema.json')
    properties = schema.get('properties', {})
    for key in ['task_type', 'sources', 'output_format', 'qa_checks']:
        if key not in properties:
            fail(f'skill_config schema missing property: {key}')
    print('OK: workflow planning contract passed')


if __name__ == '__main__':
    main()
