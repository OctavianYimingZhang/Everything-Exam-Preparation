#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check() -> dict[str, object]:
    files = [
        "SKILL.md",
        "README.md",
        "skill_manifest.json",
        "scripts/validate_skill_contracts.py",
        "scripts/github_ready_check.py",
        "scripts/publish_skill.py",
        ".github/workflows/ci.yml",
        ".github/workflows/skill-health.yml",
    ]
    return {
        "status": "ok" if all((ROOT / name).exists() for name in files) else "check_files",
        "files": {name: (ROOT / name).exists() for name in files},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.parse_args()
    print(json.dumps(check(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
