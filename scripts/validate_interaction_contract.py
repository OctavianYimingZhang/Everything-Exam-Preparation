#!/usr/bin/env python3
"""Validate public interaction metadata for the exam-prep skill."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    'SKILL.md',
    'agents/openai.yaml',
    'agents/presets.yaml',
    'agents/prompt_cards.yaml',
    'agents/setup_wizard.yaml',
    'references/user_interaction_protocol.md',
    'references/interactive_setup_protocol.md',
]

REQUIRED_SKILL_TEXT = [
    'Use only the sources supplied by the user',
    'Preserve source boundaries',
    'unsupported points as gaps',
]


def fail(message: str) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            fail(f'missing required file: {rel}')
    text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    for phrase in REQUIRED_SKILL_TEXT:
        if phrase not in text:
            fail(f'SKILL.md missing required interaction phrase: {phrase}')
    print('OK: interaction contract passed')


if __name__ == '__main__':
    main()
