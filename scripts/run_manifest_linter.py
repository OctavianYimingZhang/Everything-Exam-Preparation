#!/usr/bin/env python3
"""Lint run manifests for exam-prep workflows."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_KEYS = {'run_id', 'task_type', 'sources', 'outputs'}


def fail(message: str) -> None:
    print(f'ERROR: {message}', file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding='utf-8'))
    missing = sorted(REQUIRED_KEYS - set(data))
    if missing:
        fail('missing required keys: ' + ', '.join(missing))
    for source in data.get('sources', []):
        if not source.get('id') or not source.get('role'):
            fail('each source must include id and role')
    print('OK: run manifest passed')


if __name__ == '__main__':
    main()
