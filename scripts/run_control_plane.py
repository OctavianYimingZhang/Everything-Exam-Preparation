from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

ALLOWED_LINKS = {
    ("source_document", "source_fragment", "contains"),
    ("source_document", "source_visual", "contains"),
    ("source_document", "source_gap", "has_gap"),
    ("source_fragment", "coverage_unit", "supports"),
    ("source_fragment", "evidence_claim", "supports"),
    ("source_visual", "evidence_claim", "supports"),
    ("evidence_claim", "prep_artifact", "supports"),
    ("workflow_action", "workflow_action", "precedes"),
    ("workflow_action", "prep_artifact", "produces"),
    ("workflow_action", "gate_result", "checks"),
}


def stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(data: Any, length: int = 16) -> str:
    return hashlib.sha256(stable_json(data).encode("utf-8")).hexdigest()[:length]


def file_fingerprint(path_text: str) -> dict[str, Any]:
    path = Path(path_text)
    if not path.exists() or not path.is_file():
        return {"path": path_text, "exists": False, "hash": digest({"path": path_text})}
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    stat = path.stat()
    return {
        "path": path_text,
        "exists": True,
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "hash": h.hexdigest(),
    }


def add_object(objects: list[dict[str, Any]], obj: dict[str, Any]) -> None:
    objects.append({k: v for k, v in obj.items() if v not in (None, [], {})})


def source_objects(source_scan: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    objects: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    inputs: list[dict[str, Any]] = []

    for doc in source_scan.get("documents", []):
        doc_id = str(doc.get("id") or f"source:{digest(doc)}")
        fp = file_fingerprint(str(doc.get("path", doc_id)))
        inputs.append({"source_id": doc_id, "path": doc.get("path"), "role": doc.get("role"), "fingerprint": fp})
        add_object(objects, {
            "object_id": doc_id,
            "object_type": "source_document",
            "role": doc.get("role"),
            "readable": doc.get("readable"),
            "fingerprint": fp["hash"],
        })

    for frag in source_scan.get("fragments", []):
        frag_id = str(frag.get("id") or f"fragment:{digest(frag)}")
        source_id = str(frag.get("source_id", ""))
        add_object(objects, {
            "object_id": frag_id,
            "object_type": "source_fragment",
            "role": frag.get("role"),
            "source_ids": [source_id] if source_id else [],
            "fingerprint": digest({"text": frag.get("text", ""), "source_id": source_id}),
        })
        if source_id:
            links.append({"from_id": source_id, "to_id": frag_id, "link_type": "contains"})

    for idx, visual in enumerate(source_scan.get("visual_source_references", []), start=1):
        visual_id = str(visual.get("id") or f"visual:{idx}:{digest(visual, 10)}")
        source_id = str(visual.get("source_id") or visual.get("source_path") or "")
        add_object(objects, {
            "object_id": visual_id,
            "object_type": "source_visual",
            "source_ids": [source_id] if source_id else [],
            "fingerprint": digest(visual),
        })
        if source_id:
            links.append({"from_id": source_id, "to_id": visual_id, "link_type": "contains"})

    for idx, gap in enumerate(source_scan.get("unsupported_gaps", []), start=1):
        gap_id = str(gap.get("id") or f"gap:{idx}:{digest(gap, 10)}")
        source_id = str(gap.get("source_id", ""))
        add_object(objects, {
            "object_id": gap_id,
            "object_type": "source_gap",
            "source_ids": [source_id] if source_id else [],
            "gap": gap.get("gap"),
            "fingerprint": digest(gap),
        })
        if source_id:
            links.append({"from_id": source_id, "to_id": gap_id, "link_type": "has_gap"})

    return objects, links, inputs


def index_objects(fragment_index: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    objects: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    for idx, unit in enumerate(fragment_index.get("coverage_units", []), start=1):
        fragment_id = str(unit.get("fragment_id", ""))
        unit_id = str(unit.get("id") or f"coverage:{idx}:{fragment_id}")
        add_object(objects, {
            "object_id": unit_id,
            "object_type": "coverage_unit",
            "source_ids": [fragment_id] if fragment_id else [],
            "role": unit.get("role"),
            "fingerprint": digest(unit),
        })
        if fragment_id:
            links.append({"from_id": fragment_id, "to_id": unit_id, "link_type": "supports"})
    return objects, links


def workflow_objects(workflow_plan: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    objects: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    previous_id = ""
    for raw in workflow_plan.get("actions", []):
        action_key = str(raw.get("id") or raw.get("purpose") or f"action:{len(actions) + 1}")
        action_id = f"action:{action_key}"
        action = {
            "action_id": action_id,
            "kind": action_key,
            "purpose": raw.get("purpose"),
            "status": raw.get("status", "planned"),
        }
        actions.append(action)
        add_object(objects, {
            "object_id": action_id,
            "object_type": "workflow_action",
            "fingerprint": digest(action),
        })
        if previous_id:
            links.append({"from_id": previous_id, "to_id": action_id, "link_type": "precedes"})
        previous_id = action_id

    outputs = workflow_plan.get("outputs") or ([workflow_plan["output"]] if workflow_plan.get("output") else [])
    for output in outputs:
        artifact_id = f"artifact:{output}"
        add_object(objects, {
            "object_id": artifact_id,
            "object_type": "prep_artifact",
            "route": workflow_plan.get("route"),
            "fingerprint": digest({"route": workflow_plan.get("route"), "output": output}),
        })
        if previous_id:
            links.append({"from_id": previous_id, "to_id": artifact_id, "link_type": "produces"})

    return objects, links, actions


def validate_graph(objects: list[dict[str, Any]], links: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    for obj in objects:
        object_id = str(obj.get("object_id", ""))
        object_type = str(obj.get("object_type", ""))
        if not object_id:
            errors.append("object missing object_id")
            continue
        if object_id in seen:
            errors.append(f"duplicate object_id: {object_id}")
        seen[object_id] = object_type

    for link in links:
        from_id = str(link.get("from_id", ""))
        to_id = str(link.get("to_id", ""))
        link_type = str(link.get("link_type", ""))
        if from_id not in seen:
            errors.append(f"link has unknown from_id: {from_id}")
            continue
        if to_id not in seen:
            errors.append(f"link has unknown to_id: {to_id}")
            continue
        shape = (seen[from_id], seen[to_id], link_type)
        if shape not in ALLOWED_LINKS:
            errors.append(f"link has invalid shape: {shape[0]} -> {shape[1]} ({link_type})")
    return errors


def reuse_decisions(objects: list[dict[str, Any]], previous_manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    previous = {
        obj.get("object_id"): obj.get("fingerprint")
        for obj in (previous_manifest or {}).get("objects", [])
        if obj.get("object_id") and obj.get("fingerprint")
    }
    decisions: list[dict[str, Any]] = []
    for obj in objects:
        object_id = obj.get("object_id")
        current = obj.get("fingerprint")
        if not object_id or not current:
            continue
        old = previous.get(object_id)
        decision = "reuse" if old == current else "rebuild"
        reason = "fingerprint_unchanged" if decision == "reuse" else "new_or_changed_fingerprint"
        decisions.append({"object_id": object_id, "decision": decision, "reason": reason})
    return decisions


def build_manifest(
    source_scan: dict[str, Any],
    fragment_index: dict[str, Any] | None = None,
    workflow_plan: dict[str, Any] | None = None,
    previous_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    objects, links, inputs = source_objects(source_scan)
    index_objs, index_links = index_objects(fragment_index or {})
    workflow_objs, workflow_links, actions = workflow_objects(workflow_plan or {})
    objects.extend(index_objs)
    objects.extend(workflow_objs)
    links.extend(index_links)
    links.extend(workflow_links)
    errors = validate_graph(objects, links)
    events = [
        {
            "event_id": f"lineage:{i + 1}",
            "from_id": link["from_id"],
            "to_id": link["to_id"],
            "link_type": link["link_type"],
        }
        for i, link in enumerate(links)
    ]
    manifest_body = {
        "inputs": inputs,
        "objects": objects,
        "links": links,
        "actions": actions,
        "lineage_events": events,
    }
    return {
        "run_id": f"run:{digest(manifest_body, 12)}",
        "status": "fail" if errors else "pass",
        **manifest_body,
        "reuse_decisions": reuse_decisions(objects, previous_manifest),
        "validation_errors": errors,
    }


def read_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def self_test() -> int:
    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "lecture_notes.txt"
        source_path.write_text("ATP hydrolysis supports active transport.", encoding="utf-8")
        scan = {
            "documents": [{"id": "S1", "path": str(source_path), "role": "lecture_notes", "readable": True}],
            "fragments": [{"id": "F1", "source_id": "S1", "role": "lecture_notes", "text": "ATP hydrolysis supports active transport."}],
            "unsupported_gaps": [],
            "visual_source_references": [],
        }
        index = {"coverage_units": [{"fragment_id": "F1", "role": "lecture_notes"}]}
        plan = {
            "route": "exam_prep_notes",
            "output": "Exam_Preparation_Notes.docx",
            "outputs": ["Exam_Preparation_Notes.docx"],
            "actions": [{"id": "source_inventory", "purpose": "source inventory"}, {"id": "notes_quality_gate", "purpose": "notes quality gate"}],
        }
        first = build_manifest(scan, index, plan)
        second = build_manifest(scan, index, plan, first)
        assert first["status"] == "pass"
        assert first["lineage_events"]
        assert any(d["decision"] == "reuse" for d in second["reuse_decisions"])
    print("run_control_plane self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-scan")
    parser.add_argument("--fragment-index")
    parser.add_argument("--workflow-plan")
    parser.add_argument("--previous-run")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.source_scan:
        parser.error("--source-scan is required")
    manifest = build_manifest(
        read_json(args.source_scan),
        read_json(args.fragment_index),
        read_json(args.workflow_plan),
        read_json(args.previous_run),
    )
    text = json.dumps(manifest, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
