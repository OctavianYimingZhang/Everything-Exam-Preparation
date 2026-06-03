from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROUTES = {
    "exam_prep_notes": ["source_inventory", "fragment_index", "run_control_plane", "exam_prep_notes_plan", "exam_prep_notes_generation", "notes_quality_gate", "deliverable_surface_gate"],
    "exam_mode_diagnosis": ["source_inventory", "run_control_plane", "exam_mode_diagnosis"],
    "mcq_addon": ["exam_prep_notes", "exam_mode_diagnosis", "run_control_plane", "mcq_addon"],
    "short_answer_addon": ["exam_prep_notes", "exam_mode_diagnosis", "run_control_plane", "short_answer_addon"],
    "long_answer_practical_addon": ["exam_prep_notes", "exam_mode_diagnosis", "run_control_plane", "long_answer_practical_addon"],
    "essay_addon": ["exam_prep_notes", "exam_mode_diagnosis", "run_control_plane", "essay_addon"],
    "source_inventory_only": ["source_inventory", "run_control_plane"],
    "audit_lint_only": ["run_control_plane", "release_lint"],
    "github_ready_qa": ["run_control_plane", "github_ready_check"],
}
PRIMARY_NOTES_OUTPUT = "Exam_Preparation_Notes.docx"
ROUTE_OUTPUTS = {
    "exam_prep_notes": [PRIMARY_NOTES_OUTPUT],
    "mcq_addon": [PRIMARY_NOTES_OUTPUT],
    "short_answer_addon": [PRIMARY_NOTES_OUTPUT],
    "long_answer_practical_addon": [PRIMARY_NOTES_OUTPUT],
    "essay_addon": [PRIMARY_NOTES_OUTPUT, "Example_Essay.docx"],
}


def infer_route(prompt: str) -> tuple[str, str]:
    p = prompt.lower()
    if re.search(r"github|release|lint|audit", p):
        return "github_ready_qa", "exam_emphasis_first"
    if re.search(r"format only|exam mode|question type", p):
        return "exam_mode_diagnosis", "exam_emphasis_first"
    if "source-order" in p or "source order" in p or "lecture-order" in p or "lecture order" in p:
        return "exam_prep_notes", "source_order"
    if re.search(r"\bmcq\b|single[- ]best|sba", p):
        return "mcq_addon", "exam_emphasis_first"
    if "short answer" in p:
        return "short_answer_addon", "exam_emphasis_first"
    if re.search(r"practical|data|problem|calculation|long answer|scenario", p):
        return "long_answer_practical_addon", "exam_emphasis_first"
    if re.search(r"essay|model answer|example essay", p):
        return "essay_addon", "exam_emphasis_first"
    if re.search(r"inventory|sources only", p):
        return "source_inventory_only", "exam_emphasis_first"
    return "exam_prep_notes", "exam_emphasis_first"


def plan(prompt: str, source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    route, ordering = infer_route(prompt)
    actions = [{"id": action, "purpose": action.replace("_", " ")} for action in ROUTES[route]]
    outputs = ROUTE_OUTPUTS.get(route, ["chat_report"])
    return {"route": route, "ordering": ordering, "output": outputs[0], "outputs": outputs, "actions": actions, "source_roles": (source_scan or {}).get("source_roles", [])}


def self_test() -> int:
    assert plan("make notes")["route"] == "exam_prep_notes"
    assert "run_control_plane" in [a["id"] for a in plan("make notes")["actions"]]
    assert plan("make lecture-order notes")["ordering"] == "source_order"
    assert plan("MCQ prep")["route"] == "mcq_addon"
    assert plan("essay exam preparation")["route"] == "essay_addon"
    assert plan("essay exam preparation")["outputs"] == ["Exam_Preparation_Notes.docx", "Example_Essay.docx"]
    encoded = json.dumps(plan("make notes"))
    assert "Exam_Preparation_Notes.docx" in encoded
    print("plan_workflow self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="make notes")
    parser.add_argument("--source-scan")
    parser.add_argument("--out")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    scan = json.loads(Path(args.source_scan).read_text(encoding="utf-8")) if args.source_scan else None
    out = plan(args.prompt, scan)
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
