#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEGACY_SKILL_ID = "everything-exam-preparation"
DEFAULT_LOCAL_SKILL_ROOT = Path.home() / ".codex" / "skills"
DEFAULT_LOCAL_SKILL_DIR = DEFAULT_LOCAL_SKILL_ROOT / LEGACY_SKILL_ID
MULTI_SKILL_SOURCE_DIR = ROOT / "skills"
SHARED_RESOURCE_DIRS = ("references", "scripts", "schemas")
SHARED_RESOURCE_FILES = ("requirements.txt", "LICENSE", "skill_manifest.json")
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
PLUGIN_ROUTER_SKILLS = {"everything-exam-preparation"}


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
        focused = [
            {"name": item["name"], "destination": str(destination.parent / item["name"])}
            for item in discover_focused_skills()
        ]
        removed = cleanup_removed_focused_skills(destination.parent, dry_run=True)
        return {"legacy_destination": str(destination), "focused_skills": focused, "removed_focused_skills": removed, "status": "planned"}
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, destination, ignore=ignore)
    focused = [sync_focused_skill(item, destination.parent, dry_run=False) for item in discover_focused_skills()]
    removed = cleanup_removed_focused_skills(destination.parent, dry_run=False)
    return {"legacy_destination": str(destination), "focused_skills": focused, "removed_focused_skills": removed, "status": "ok"}


def read_skill_name(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, flags=re.MULTILINE)
    if match:
        return match.group(1)
    return skill_md.parent.name


def discover_focused_skills() -> list[dict[str, Any]]:
    if not MULTI_SKILL_SOURCE_DIR.exists():
        return []
    focused = []
    for skill_dir in sorted(path for path in MULTI_SKILL_SOURCE_DIR.iterdir() if path.is_dir()):
        if skill_dir.name in PLUGIN_ROUTER_SKILLS:
            continue
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            focused.append({"name": read_skill_name(skill_md), "source": skill_dir})
    return focused


def removed_focused_skill_ids() -> list[str]:
    manifest_path = ROOT / "skill_manifest.json"
    if not manifest_path.exists():
        return []
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    removed = manifest.get("removed_focused_skills", [])
    return [str(item) for item in removed if item]


def cleanup_removed_focused_skills(local_skill_root: Path, dry_run: bool) -> list[dict[str, Any]]:
    results = []
    for skill_id in removed_focused_skill_ids():
        destination = local_skill_root / skill_id
        if dry_run:
            results.append({"name": skill_id, "destination": str(destination), "status": "planned"})
        elif destination.exists():
            shutil.rmtree(destination)
            results.append({"name": skill_id, "destination": str(destination), "status": "removed"})
        else:
            results.append({"name": skill_id, "destination": str(destination), "status": "absent"})
    return results


def sync_focused_skill(skill: dict[str, Any], local_skill_root: Path, dry_run: bool) -> dict[str, Any]:
    destination = local_skill_root / skill["name"]
    if dry_run:
        return {"name": skill["name"], "destination": str(destination), "status": "planned"}
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(skill["source"] / "SKILL.md", destination / "SKILL.md")
    for dirname in SHARED_RESOURCE_DIRS:
        source = ROOT / dirname
        if source.exists():
            shutil.copytree(source, destination / dirname, ignore=ignore)
    for filename in SHARED_RESOURCE_FILES:
        source = ROOT / filename
        if source.exists():
            shutil.copy2(source, destination / filename)
    return {"name": skill["name"], "destination": str(destination), "status": "ok"}


def basic_status() -> dict[str, Any]:
    manifest_path = ROOT / "skill_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    return {
        "repo": manifest.get("repo", "OctavianYimingZhang/Everything-Exam-Preparation"),
        "entrypoint_exists": (ROOT / "SKILL.md").exists(),
        "focused_skill_count": len(discover_focused_skills()),
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
