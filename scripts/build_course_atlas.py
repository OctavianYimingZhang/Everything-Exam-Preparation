#!/usr/bin/env python3
"""Build a deterministic, source-metadata-only Course Atlas ZIP."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import stat
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_course_atlas import (
    AtlasValidationError,
    SCHEMA_VERSION,
    load_json_file,
    render_qa_report,
    validate_build_spec,
    validate_package,
    validate_schema_documents,
)


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _lineage_key(node: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> tuple[Any, ...]:
    lineage: list[tuple[int, str, str]] = []
    current = node
    while True:
        lineage.append(
            (
                current["sequence_index"],
                current["node_type"],
                current["node_id"],
            )
        )
        if current["parent_id"] is None:
            break
        current = by_id[current["parent_id"]]
    return tuple(reversed(lineage))


def _module_filename(position: int, node_id: str) -> str:
    digest = hashlib.sha256(node_id.encode("utf-8")).hexdigest()[:12]
    return f"modules/{position:04d}-{digest}.json"


def _module_ancestor(node: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str | None:
    current = node
    while current["node_type"] not in {"lecture", "module", "course"}:
        current = by_id[current["parent_id"]]
    return current["node_id"] if current["node_type"] in {"lecture", "module"} else None


def _web_entry(node: dict[str, Any], module_file: str) -> dict[str, Any]:
    return {
        "node_id": node["node_id"],
        "node_type": node["node_type"],
        "parent_id": node["parent_id"],
        "title": node["title"],
        "sequence_index": node["sequence_index"],
        "keywords": node["keywords"],
        "aliases": node["aliases"],
        "knowledge_status": node["knowledge_status"],
        "module_file": module_file,
    }


def _checksum_file(files: dict[str, bytes]) -> bytes:
    lines = [
        f"{hashlib.sha256(files[name]).hexdigest()}  {name}"
        for name in sorted(files)
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def _write_zip(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name in sorted(files):
            archive.writestr(_zip_info(name), files[name])


def assemble_package_files(spec_value: Any) -> tuple[dict[str, bytes], dict[str, Any]]:
    """Validate a normalized spec and render all generated package members."""

    validate_schema_documents()
    spec = copy.deepcopy(spec_value)
    if not isinstance(spec, dict):
        raise AtlasValidationError("spec: must be an object")
    spec.setdefault(
        "generated_at",
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    )
    state = validate_build_spec(spec)
    nodes = sorted(
        state["nodes"],
        key=lambda node: _lineage_key(node, state["node_by_id"]),
    )
    hierarchy_nodes = [
        node for node in nodes if node["node_type"] in {"course", "theme"}
    ]
    units = [
        node for node in nodes if node["node_type"] in {"lecture", "module"}
    ]

    module_file_by_root: dict[str, str] = {}
    for position, unit in enumerate(units, 1):
        module_file_by_root[unit["node_id"]] = _module_filename(position, unit["node_id"])

    node_file: dict[str, str] = {}
    for node in hierarchy_nodes:
        node_file[node["node_id"]] = "modules/hierarchy.json"
    for node in nodes:
        if node["node_type"] in {"course", "theme"}:
            continue
        ancestor = (
            node["node_id"]
            if node["node_type"] in {"lecture", "module"}
            else _module_ancestor(node, state["node_by_id"])
        )
        if ancestor is None:
            raise AtlasValidationError(f"node {node['node_id']!r}: has no lecture/module ancestor")
        node_file[node["node_id"]] = module_file_by_root[ancestor]

    files: dict[str, bytes] = {}
    files["modules/hierarchy.json"] = _json_bytes(
        {
            "schema_version": SCHEMA_VERSION,
            "scope": "course_and_themes",
            "nodes": hierarchy_nodes,
        }
    )
    for unit in units:
        name = module_file_by_root[unit["node_id"]]
        owned_nodes = [
            node
            for node in nodes
            if node_file.get(node["node_id"]) == name
        ]
        files[name] = _json_bytes(
            {
                "schema_version": SCHEMA_VERSION,
                "module_id": unit["node_id"],
                "nodes": owned_nodes,
            }
        )

    sources = sorted(spec["sources"], key=lambda item: item["source_id"])
    relations = sorted(spec["relations"], key=lambda item: item["relation_id"])
    past_links = sorted(spec["past_paper_links"], key=lambda item: item["link_id"])
    coverage = sorted(
        spec["audit"]["coverage_ledger"],
        key=lambda item: item["source_id"],
    )
    exclusions = sorted(
        spec["audit"]["exclusions"],
        key=lambda item: item["exclusion_id"],
    )
    manual_review = sorted(
        spec["audit"]["manual_review"],
        key=lambda item: item["review_id"],
    )
    files["sources.json"] = _json_bytes(
        {"schema_version": SCHEMA_VERSION, "sources": sources}
    )
    files["relations.json"] = _json_bytes(
        {"schema_version": SCHEMA_VERSION, "relations": relations}
    )
    files["past_paper_links.json"] = _json_bytes(
        {"schema_version": SCHEMA_VERSION, "links": past_links}
    )
    files["audit/coverage_ledger.json"] = _json_bytes(
        {"schema_version": SCHEMA_VERSION, "records": coverage}
    )
    files["audit/exclusions.json"] = _json_bytes(
        {"schema_version": SCHEMA_VERSION, "records": exclusions}
    )
    files["audit/manual_review.json"] = _json_bytes(
        {"schema_version": SCHEMA_VERSION, "records": manual_review}
    )
    files["public/web_index.json"] = _json_bytes(
        {
            "schema_version": SCHEMA_VERSION,
            "package_id": spec["package_id"],
            "course_node_id": state["course_root_id"],
            "node_id_scope": "package_local",
            "relations_file": "relations.json",
            "nodes": [
                _web_entry(node, node_file[node["node_id"]])
                for node in nodes
            ],
        }
    )

    counts = {
        "sources": len(sources),
        "nodes": len(nodes),
        "relations": len(relations),
        "past_paper_links": len(past_links),
        "excluded_items": len(exclusions),
        "pending_manual_review": state["pending_count"],
    }
    qa_status = "pass_with_gaps" if state["has_gaps"] else "pass"
    module_files = sorted(name for name in files if name.startswith("modules/"))
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "course_atlas",
        "package_id": spec["package_id"],
        "generated_at": spec["generated_at"],
        "node_id_scope": "package_local",
        "course": spec["course"],
        "hierarchy": {
            "levels": [
                "course",
                "theme",
                "lecture_or_module",
                "concept",
                "detail",
            ],
            "unit_types": ["lecture", "module"],
        },
        "module_files": module_files,
        "public_files": sorted(
            [
                "sources.json",
                "relations.json",
                "past_paper_links.json",
                "public/web_index.json",
                *module_files,
            ]
        ),
        "audit_files": [
            "audit/coverage_ledger.json",
            "audit/exclusions.json",
            "audit/manual_review.json",
        ],
        "counts": counts,
        "qa_status": qa_status,
    }
    files["course_manifest.json"] = _json_bytes(manifest)
    files["qa_report.md"] = render_qa_report(spec["package_id"], qa_status, counts)
    files["checksums.sha256"] = _checksum_file(files)
    return files, {
        "package_id": spec["package_id"],
        "qa_status": qa_status,
        **counts,
    }


def build_course_atlas(
    spec_value: Any,
    output_path: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Build and validate an Atlas ZIP, replacing the target atomically."""

    output = Path(output_path)
    if output.exists() and not overwrite:
        raise AtlasValidationError(
            f"{output}: already exists; pass overwrite=True or --overwrite explicitly"
        )
    if output.exists() and not output.is_file():
        raise AtlasValidationError(f"{output}: output target is not a regular file")
    output.parent.mkdir(parents=True, exist_ok=True)
    files, _ = assemble_package_files(spec_value)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=output.parent,
            delete=False,
        ) as temporary:
            temporary_name = temporary.name
        temporary_path = Path(temporary_name)
        _write_zip(temporary_path, files)
        validate_package(temporary_path)
        os.replace(temporary_path, output)
        temporary_name = None
        return validate_package(output)
    finally:
        if temporary_name is not None:
            Path(temporary_name).unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a validated Course Atlas ZIP from a normalized JSON specification."
    )
    parser.add_argument("--input", required=True, help="Course Atlas build specification JSON")
    parser.add_argument("--output", required=True, help="Destination .zip path")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Explicitly replace an existing output file",
    )
    args = parser.parse_args(argv)
    try:
        spec = load_json_file(args.input)
        result = build_course_atlas(spec, args.output, overwrite=args.overwrite)
    except (AtlasValidationError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Course Atlas build failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
