#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def json_readable(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except Exception:
        return False


def check_all() -> dict[str, Any]:
    files = ["SKILL.md", "README.md", "skill_manifest.json", "scripts/publish_skill.py"]
    schemas = sorted(str(path.relative_to(ROOT)) for path in (ROOT / "schemas").glob("*.schema.json"))
    return {
        "status": "ok",
        "files": {name: (ROOT / name).exists() for name in files},
        "schemas": {name: json_readable(ROOT / name) for name in schemas},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="all")
    parser.add_argument("--schema")
    parser.add_argument("--input")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        assert check_all()["status"] == "ok"
        return
    print(json.dumps(check_all(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
