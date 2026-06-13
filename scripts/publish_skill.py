#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_SKILL_DIR = Path.home() / ".codex" / "skills" / "everything-exam-preparation"
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def run(cmd: list[str], dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"cmd": cmd, "status": "planned"}
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "cmd": cmd,
        "status": "ok" if proc.returncode == 0 else "error",
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def ignore(_: str, names: list[str]) -> set[str]:
    ignored = set()
    for name in names:
        path = Path(name)
        if name in SKIP_DIRS or path.suffix in SKIP_SUFFIXES or name == ".DS_Store":
            ignored.add(name)
    return ignored


def sync_local_skill(destination: Path, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"destination": str(destination), "status": "planned"}
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, destination, ignore=ignore)
    return {"destination": str(destination), "status": "ok"}


def basic_status() -> dict[str, Any]:
    manifest_path = ROOT / "skill_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    return {
        "repo": manifest.get("repo", "OctavianYimingZhang/Everything-Exam-Preparation"),
        "entrypoint_exists": (ROOT / "SKILL.md").exists(),
        "manifest_exists": manifest_path.exists(),
        "default_output": manifest.get("default_output"),
        "output_name_policy": manifest.get("output_name_policy"),
    }


def publish(push: bool, sync_local: bool, destination: Path, dry_run: bool) -> dict[str, Any]:
    result: dict[str, Any] = {"status": basic_status(), "steps": []}
    if push:
        result["steps"].append(run(["git", "push"], dry_run))
    if sync_local:
        result["steps"].append(sync_local_skill(destination, dry_run))
    if not push and not sync_local:
        result["steps"].append({"status": "nothing_requested", "hint": "Use --push and/or --sync-local-skill."})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal publish/update helper for Everything Exam Preparation.")
    parser.add_argument("--push", action="store_true", help="Run git push from the repository root.")
    parser.add_argument("--sync-local-skill", action="store_true", help="Copy this repository into the local Codex skill directory.")
    parser.add_argument("--local-skill-dir", default=str(DEFAULT_LOCAL_SKILL_DIR))
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without changing anything.")
    args = parser.parse_args()
    print(json.dumps(publish(args.push, args.sync_local_skill, Path(args.local_skill_dir), args.dry_run), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
