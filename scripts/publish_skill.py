#!/usr/bin/env python3
"""Synchronise, compare, or push manifest-declared Exam Preparation Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "skill_manifest.json"
DEFAULT_LOCAL_SKILL_ROOT = Path.home() / ".codex" / "skills"
SHARED_RESOURCE_DIRS = ("references", "scripts")
SHARED_RESOURCE_FILES = ("requirements.txt", "LICENSE", "skill_manifest.json")
SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "out",
    "qa",
    "tmp",
    ".skill_assets",
}
SKIP_SUFFIXES = {".pyc", ".pyo", ".docx", ".pdf", ".pptx", ".xlsx", ".zip", ".jsonl"}


def load_manifest() -> dict[str, Any]:
    value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("skill_manifest.json must be an object")
    return value


def ignored(_: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in SKIP_DIRS or name == ".DS_Store" or Path(name).suffix in SKIP_SUFFIXES
    }


def skill_name(skill_md: Path) -> str:
    match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", skill_md.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise RuntimeError(f"Cannot read Skill name: {skill_md}")
    return match.group(1)


def public_skills() -> list[dict[str, Any]]:
    manifest = load_manifest()
    raw = manifest.get("public_skills", [])
    if not isinstance(raw, list) or len(raw) < 2:
        raise RuntimeError("The manifest must declare a Router and at least one focused Skill")
    entries: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            raise RuntimeError(f"Invalid public Skill declaration: {item!r}")
        name = str(item.get("name", ""))
        source_file = ROOT / str(item.get("path", ""))
        if (
            source_file != ROOT / "skills" / name / "SKILL.md"
            or not source_file.is_file()
            or skill_name(source_file) != name
        ):
            raise RuntimeError(f"Invalid public Skill declaration: {item!r}")
        entries.append({"name": name, "source": source_file.parent})
    names = [entry["name"] for entry in entries]
    architecture = manifest.get("architecture", {})
    if len(set(names)) != len(names) or names[0] != manifest.get("skill_id"):
        raise RuntimeError("The first unique public Skill must be the manifest Router")
    if architecture.get("router") != names[0] or architecture.get("focused_skill_policy") != "manifest_driven":
        raise RuntimeError("The architecture must declare a manifest-driven Router")
    return entries


def is_package_root() -> bool:
    try:
        entries = public_skills()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError):
        return False
    return (ROOT / "SKILL.md").is_file() and bool(entries)


def copy_child_resources(source: Path, destination: Path) -> None:
    for item in source.iterdir():
        if item.name == "SKILL.md" or item.name in SKIP_DIRS or item.name == ".DS_Store":
            continue
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=ignored)
        elif item.suffix not in SKIP_SUFFIXES:
            shutil.copy2(item, target)


def install_focused(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / "SKILL.md", destination / "SKILL.md")
    copy_child_resources(source, destination)
    for dirname in SHARED_RESOURCE_DIRS:
        shared = ROOT / dirname
        if shared.exists():
            shutil.copytree(shared, destination / dirname, ignore=ignored)
    for filename in SHARED_RESOURCE_FILES:
        shared = ROOT / filename
        if shared.exists():
            shutil.copy2(shared, destination / filename)


def removed_ids() -> list[str]:
    public = {entry["name"] for entry in public_skills()}
    removed = [str(item) for item in load_manifest().get("removed_focused_skills", []) if item]
    if public & set(removed):
        raise RuntimeError("A public Skill cannot also be retired")
    return removed


def cleanup_removed(install_root: Path, dry_run: bool) -> list[dict[str, str]]:
    results = []
    for name in removed_ids():
        destination = install_root / name
        if dry_run:
            status = "planned"
        elif destination.exists():
            shutil.rmtree(destination)
            status = "removed"
        else:
            status = "absent"
        results.append({"name": name, "destination": str(destination), "status": status})
    return results


def synchronise(destination: Path, dry_run: bool = False) -> dict[str, Any]:
    if not is_package_root():
        return {"status": "error", "error": "Run this helper from the Exam Preparation package root."}
    entries = public_skills()
    install_root = destination.parent
    if dry_run:
        return {
            "status": "planned",
            "router": str(destination),
            "focused_skills": [
                {"name": entry["name"], "destination": str(install_root / entry["name"]), "status": "planned"}
                for entry in entries[1:]
            ],
            "removed_focused_skills": cleanup_removed(install_root, dry_run=True),
        }
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT, destination, ignore=ignored)
    focused = []
    for entry in entries[1:]:
        focused_destination = install_root / entry["name"]
        install_focused(entry["source"], focused_destination)
        focused.append(
            {"name": entry["name"], "destination": str(focused_destination), "status": "synchronised"}
        )
    return {
        "status": "ok",
        "router": str(destination),
        "focused_skills": focused,
        "removed_focused_skills": cleanup_removed(install_root, dry_run=False),
    }


def tree_manifest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS or part == ".DS_Store" for part in relative.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        result[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def compare(expected: Path, actual: Path, name: str) -> dict[str, Any]:
    left = tree_manifest(expected)
    right = tree_manifest(actual)
    missing = sorted(left.keys() - right.keys())
    unexpected = sorted(right.keys() - left.keys())
    changed = sorted(key for key in left.keys() & right.keys() if left[key] != right[key])
    return {
        "name": name,
        "status": "ok" if not missing and not unexpected and not changed else "drift",
        "missing": missing,
        "unexpected": unexpected,
        "changed": changed,
    }


def check_installed(destination: Path) -> dict[str, Any]:
    entries = public_skills()
    with tempfile.TemporaryDirectory() as temporary:
        expected_root = Path(temporary) / "skills"
        expected_router = expected_root / entries[0]["name"]
        result = synchronise(expected_router)
        if result.get("status") != "ok":
            return result
        checks = [
            compare(
                expected_root / entry["name"],
                destination.parent / entry["name"],
                entry["name"],
            )
            for entry in entries
        ]
    retired_present = [name for name in removed_ids() if (destination.parent / name).exists()]
    return {
        "status": "ok" if all(item["status"] == "ok" for item in checks) and not retired_present else "drift",
        "checks": checks,
        "retired_present": retired_present,
    }


def run_push(dry_run: bool) -> dict[str, Any]:
    command = ["git", "push", "origin", "HEAD:main"]
    if dry_run:
        return {"cmd": command, "status": "planned"}
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return {
        "cmd": command,
        "status": "ok" if proc.returncode == 0 else "error",
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def self_test() -> None:
    manifest = load_manifest()
    entries = public_skills()
    assert manifest.get("architecture", {}).get("focused_skill_policy") == "manifest_driven"
    assert len(entries) >= 2
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary) / "skills"
        destination = root / entries[0]["name"]
        for name in removed_ids()[:2]:
            (root / name).mkdir(parents=True)
        result = synchronise(destination)
        assert result["status"] == "ok"
        assert all((root / entry["name"] / "SKILL.md").exists() for entry in entries)
        assert not any((root / name).exists() for name in removed_ids())
        assert check_installed(destination)["status"] == "ok"
        drift_target = root / entries[-1]["name"] / "requirements.txt"
        drift_target.write_text("drift\n", encoding="utf-8")
        assert check_installed(destination)["status"] == "drift"


def has_failure(value: Any) -> bool:
    if isinstance(value, dict):
        if value.get("status") in {"error", "drift"}:
            return True
        return any(has_failure(item) for item in value.values())
    if isinstance(value, list):
        return any(has_failure(item) for item in value)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--sync-local-skill", action="store_true")
    parser.add_argument("--check-installed", action="store_true")
    parser.add_argument("--local-skill-dir")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("OK: publish_skill self-test passed")
        return 0

    router = public_skills()[0]["name"]
    destination = Path(args.local_skill_dir or DEFAULT_LOCAL_SKILL_ROOT / router).expanduser().resolve()
    result: dict[str, Any] = {"steps": []}
    if args.sync_local_skill:
        result["steps"].append({"sync": synchronise(destination, args.dry_run)})
    if args.check_installed:
        result["steps"].append({"installed_check": check_installed(destination)})
    if args.push:
        result["steps"].append({"push": run_push(args.dry_run)})
    if not result["steps"]:
        result["steps"].append({"status": "nothing_requested"})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if has_failure(result) else 0


if __name__ == "__main__":
    raise SystemExit(main())
