#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "everything-exam-preparation/mastery-history"
VERSION = "1.0"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def default_store_path() -> Path:
    configured = os.environ.get("EVERYTHING_EXAM_PREP_HISTORY")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex" / "state" / "everything-exam-preparation" / "mastery_history.json"


def empty_store() -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "default_enabled": True,
        "courses": {},
    }


def load_store(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_store()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("contract") != CONTRACT or not isinstance(data.get("courses"), dict):
        raise ValueError("mastery history store has an unsupported contract")
    return data


def save_store(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
        temporary = Path(handle.name)
    temporary.replace(path)


def course_state(store: dict[str, Any], course_id: str, label: str | None = None, create: bool = False) -> dict[str, Any] | None:
    courses = store.setdefault("courses", {})
    state = courses.get(course_id)
    if state is None and create:
        state = {
            "course": {"stable_id": course_id, "label": label or course_id},
            "enabled": bool(store.get("default_enabled", True)),
            "mastery": {},
            "weakness_history": [],
            "attempts": [],
            "updated_at": None,
        }
        courses[course_id] = state
    return state


def status(store: dict[str, Any], course_id: str) -> dict[str, Any]:
    state = course_state(store, course_id)
    return {
        "course_id": course_id,
        "enabled": bool(state.get("enabled")) if state else bool(store.get("default_enabled", True)),
        "exists": state is not None,
        "attempt_count": len(state.get("attempts", [])) if state else 0,
        "weakness_event_count": len(state.get("weakness_history", [])) if state else 0,
    }


def set_enabled(store: dict[str, Any], course_id: str, enabled: bool, label: str | None = None) -> dict[str, Any]:
    state = course_state(store, course_id, label=label, create=True)
    assert state is not None
    state["enabled"] = enabled
    state["updated_at"] = now_iso()
    return status(store, course_id)


def record_attempt(store: dict[str, Any], course_id: str, event: dict[str, Any], label: str | None = None) -> dict[str, Any]:
    state = course_state(store, course_id, label=label, create=True)
    assert state is not None
    if not state.get("enabled", True):
        return {"recorded": False, "reason": "mastery_history_disabled", **status(store, course_id)}
    timestamp = str(event.get("recorded_at") or now_iso())
    attempt = {
        "recorded_at": timestamp,
        "route_id": event.get("route_id"),
        "artifact_id": event.get("artifact_id"),
        "mastery_units": list(event.get("mastery_units") or []),
        "weakness_units": list(event.get("weakness_units") or []),
        "provenance": list(event.get("provenance") or []),
    }
    state["attempts"].append(attempt)
    for unit in attempt["mastery_units"]:
        key = str(unit)
        record = state["mastery"].setdefault(key, {"successful_attempts": 0, "last_seen_at": None})
        record["successful_attempts"] += 1
        record["last_seen_at"] = timestamp
    for unit in attempt["weakness_units"]:
        state["weakness_history"].append({
            "knowledge_unit": str(unit),
            "recorded_at": timestamp,
            "route_id": attempt["route_id"],
            "provenance": attempt["provenance"],
        })
    state["updated_at"] = timestamp
    return {"recorded": True, **status(store, course_id)}


def export_course(store: dict[str, Any], course_id: str) -> dict[str, Any]:
    state = course_state(store, course_id)
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "exported_at": now_iso(),
        "course": deepcopy(state),
    }


def delete_course(store: dict[str, Any], course_id: str) -> dict[str, Any]:
    existed = store.setdefault("courses", {}).pop(course_id, None) is not None
    return {"course_id": course_id, "deleted": existed}


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "history.json"
        store = load_store(path)
        assert status(store, "BIO101")["enabled"] is True
        result = record_attempt(store, "BIO101", {
            "route_id": "answer_evaluation",
            "mastery_units": ["membranes"],
            "weakness_units": ["transport"],
            "provenance": [{"page_number": 4}],
        }, label="Biology")
        assert result["recorded"] is True
        save_store(path, store)
        reloaded = load_store(path)
        assert reloaded["courses"]["BIO101"]["mastery"]["membranes"]["successful_attempts"] == 1
        assert export_course(reloaded, "BIO101")["course"]["weakness_history"][0]["knowledge_unit"] == "transport"
        assert set_enabled(reloaded, "BIO101", False)["enabled"] is False
        ignored = record_attempt(reloaded, "BIO101", {"weakness_units": ["diffusion"]})
        assert ignored["recorded"] is False
        assert delete_course(reloaded, "BIO101")["deleted"] is True


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage default-enabled per-course mastery and weakness history.")
    parser.add_argument("--store", default=str(default_store_path()))
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="command")
    for command in ["status", "enable", "disable", "export", "delete"]:
        child = subparsers.add_parser(command)
        child.add_argument("--course-id", required=True)
        if command in {"enable", "disable"}:
            child.add_argument("--course-label")
        if command == "export":
            child.add_argument("--out")
    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--course-id", required=True)
    record_parser.add_argument("--course-label")
    record_parser.add_argument("--event", required=True)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.command:
        parser.error("choose status, enable, disable, record, export, or delete")
    path = Path(args.store).expanduser()
    store = load_store(path)
    if args.command == "status":
        result = status(store, args.course_id)
    elif args.command == "enable":
        result = set_enabled(store, args.course_id, True, args.course_label)
        save_store(path, store)
    elif args.command == "disable":
        result = set_enabled(store, args.course_id, False, args.course_label)
        save_store(path, store)
    elif args.command == "record":
        event = json.loads(Path(args.event).read_text(encoding="utf-8"))
        result = record_attempt(store, args.course_id, event, args.course_label)
        save_store(path, store)
    elif args.command == "export":
        result = export_course(store, args.course_id)
        if args.out:
            Path(args.out).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        result = delete_course(store, args.course_id)
        save_store(path, store)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
