from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REFERENCES = {
    "input_and_evidence_protocol.md",
    "exam_prep_notes_protocol.md",
    "exam_mode_and_addons_protocol.md",
    "essay_exam_prep_protocol.md",
    "language_quality_contract.md",
    "runtime_quality_protocol.md",
}
EXPECTED_SCHEMAS = {
    "skill_config.schema.json",
    "workflow_plan.schema.json",
    "source_document.schema.json",
    "source_fragment.schema.json",
    "source_evidence_bundle.schema.json",
    "evidence_claim.schema.json",
    "exam_prep_notes_plan.schema.json",
    "exam_mode_addon.schema.json",
    "example_essay_plan.schema.json",
    "visual_aid_spec.schema.json",
    "student_output_contract.schema.json",
    "gate_result.schema.json",
    "run_control_plane.schema.json",
}
EXPECTED_SCRIPTS = {
    "extract_sources.py",
    "build_fragment_index.py",
    "input_readiness_check.py",
    "plan_workflow.py",
    "exam_mode_tools.py",
    "generate_exam_prep_notes_docx.py",
    "exam_prep_notes_quality_linter.py",
    "output_sufficiency_linter.py",
    "essay_exam_tools.py",
    "deliverable_surface_linter.py",
    "run_control_plane.py",
    "validate_skill_contracts.py",
    "github_ready_check.py",
}

def stale_term(*parts: str) -> str:
    return "".join(parts)


REQUIRED_RELEASE_GUARD_TERMS = {
    stale_term("Lecture", "_Knowledge", "_Walkthrough"),
    stale_term("Lecture ", "Knowledge ", "Walkthrough"),
    stale_term("knowledge", "_walkthrough"),
    stale_term("knowledge", "_walkthrough", "_docx"),
    stale_term("public", "_lecture", "_notes"),
    stale_term("public ", "lecture ", "notes"),
    stale_term("Public", "Lecture", "Notes", "Plan"),
    stale_term("Excel", "-first"),
    stale_term("S", "BS"),
    stale_term("onto", "logy"),
    stale_term("Snow", "flake"),
    stale_term("Data", "bricks"),
    stale_term("Pal", "antir"),
    stale_term("lake", "house"),
    stale_term("medal", "lion"),
    stale_term("bro", "nze"),
    stale_term("sil", "ver"),
    stale_term("go", "ld"),
}


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid json {path}: {exc}")


def check_sets() -> None:
    refs = {p.name for p in (ROOT / "references").glob("*.md")}
    schemas = {p.name for p in (ROOT / "schemas").glob("*.json")}
    scripts = {p.name for p in (ROOT / "scripts").glob("*.py")}
    if refs != EXPECTED_REFERENCES:
        fail(f"reference set mismatch: {sorted(refs ^ EXPECTED_REFERENCES)}")
    if schemas != EXPECTED_SCHEMAS:
        fail(f"schema set mismatch: {sorted(schemas ^ EXPECTED_SCHEMAS)}")
    if scripts != EXPECTED_SCRIPTS:
        fail(f"script set mismatch: {sorted(scripts ^ EXPECTED_SCRIPTS)}")


def check_schema(schema_path: Path, input_path: Path | None = None) -> None:
    schema = load_json(schema_path)
    if schema.get("type") != "object":
        fail(f"schema must define object type: {schema_path}")
    if input_path:
        data = load_json(input_path)
        for key in schema.get("required", []):
            if key not in data:
                fail(f"missing required key {key} in {input_path}")


def check_interaction() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if "Exam_Preparation_Notes.docx" not in skill:
        fail("default artifact missing from SKILL.md")
    if "exam_prep_notes" not in skill:
        fail("canonical route missing")


def check_student_output() -> None:
    schema = load_json(ROOT / "schemas/student_output_contract.schema.json")
    allowed = schema.get("properties", {}).get("allowed_outputs", {})
    if "Exam_Preparation_Notes.docx" not in json.dumps(allowed):
        fail("student output contract does not allow default notes artifact")


def check_workflow() -> None:
    schema = load_json(ROOT / "schemas/workflow_plan.schema.json")
    routes = json.dumps(schema)
    for route in ["exam_prep_notes", "mcq_addon", "short_answer_addon", "long_answer_practical_addon", "essay_addon"]:
        if route not in routes:
            fail(f"route missing from workflow schema: {route}")
    for key in ["output", "outputs"]:
        if key not in schema.get("required", []):
            fail(f"workflow schema missing required key: {key}")
    from plan_workflow import plan
    essay_outputs = plan("essay exam preparation").get("outputs", [])
    if essay_outputs != ["Exam_Preparation_Notes.docx", "Example_Essay.docx"]:
        fail(f"essay route outputs mismatch: {essay_outputs}")
    if "run_control_plane" not in (ROOT / "scripts/plan_workflow.py").read_text(encoding="utf-8"):
        fail("workflow planner does not schedule run_control_plane")


def check_notes_rendering_contract() -> None:
    notes_schema_obj = load_json(ROOT / "schemas/exam_prep_notes_plan.schema.json")
    notes_schema = json.dumps(notes_schema_obj)
    if notes_schema_obj.get("additionalProperties") is not False:
        fail("notes plan schema must reject loose top-level fields")
    for key in ["title", "ordering", "visual_policy", "sections"]:
        if key not in notes_schema_obj.get("required", []):
            fail(f"notes plan schema missing required key: {key}")
    for legacy in ["topics", "methods_and_data", "confusions", "practical_operations", "past_paper_emphasis", "add_on_sections", "revision_checklist"]:
        if f'"{legacy}"' in notes_schema:
            fail(f"notes plan schema still accepts legacy key: {legacy}")
    for mode in ["kp_list", "compact_table", "mechanism_chain", "image_plus_kp_list", "paragraph"]:
        if mode not in notes_schema:
            fail(f"notes plan schema missing render mode: {mode}")
    visual_schema = json.dumps(load_json(ROOT / "schemas/visual_aid_spec.schema.json"))
    for token in ["visual_id", "placement", "after_block_id", "use_reason"]:
        if token not in visual_schema:
            fail(f"visual schema missing block-level ownership token: {token}")
    source_schema = json.dumps(load_json(ROOT / "schemas/source_evidence_bundle.schema.json"))
    for token in ["source_decisions", "evidence_scope", "factual_course_content", "needs_confirmation"]:
        if token not in source_schema:
            fail(f"source evidence schema missing route-scope token: {token}")
    renderer = (ROOT / "scripts/generate_exam_prep_notes_docx.py").read_text(encoding="utf-8")
    for token in ["validate_plan_contract", "build_docx_blocks", "visual_bytes", "word/media/", "image_plus_kp_list", "compact_table"]:
        if token not in renderer:
            fail(f"notes renderer missing visual/render support: {token}")
    if "plan.get(\"topics\"" in renderer or "plan.get('topics'" in renderer:
        fail("notes renderer still consumes legacy top-level topics")
    extractor = (ROOT / "scripts/extract_sources.py").read_text(encoding="utf-8")
    for token in ["decision_for_route", "source_decisions", "factual_course_content", "style_only"]:
        if token not in extractor:
            fail(f"source extractor missing route-specific source decision support: {token}")
    fragment_index = (ROOT / "scripts/build_fragment_index.py").read_text(encoding="utf-8")
    if "fragment_allowed_for_notes" not in fragment_index:
        fail("fragment index does not enforce notes source-scope filtering")
    linter = (ROOT / "scripts/exam_prep_notes_quality_linter.py").read_text(encoding="utf-8")
    for token in ["FORBIDDEN_SURFACE_PATTERNS", "forbidden_internal_surface_templates", "generic_colon_label_overuse", "repeated_generic_sentence_frame"]:
        if token not in linter:
            fail(f"notes quality linter missing surface-template guard: {token}")


def check_release_guards() -> None:
    guard = (ROOT / "scripts/github_ready_check.py").read_text(encoding="utf-8")
    missing = sorted(term for term in REQUIRED_RELEASE_GUARD_TERMS if term not in guard)
    if missing:
        fail(f"github_ready_check missing stale-term guards: {missing}")
    if "check_readability" not in guard:
        fail("github_ready_check missing compressed-file readability guard")
    if "check_yaml_syntax" not in guard or "yaml.safe_load" not in guard:
        fail("github_ready_check missing yaml syntax guard")


def run_all() -> None:
    check_sets()
    for schema_path in (ROOT / "schemas").glob("*.json"):
        check_schema(schema_path)
    check_interaction()
    check_student_output()
    check_workflow()
    check_notes_rendering_contract()
    check_release_guards()


def self_test() -> int:
    run_all()
    print("validate_skill_contracts self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", nargs="?", default="all")
    parser.add_argument("--schema")
    parser.add_argument("--input")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.command == "all":
        run_all()
    elif args.command == "schema":
        if not args.schema:
            parser.error("--schema is required")
        check_schema(Path(args.schema), Path(args.input) if args.input else None)
    elif args.command == "interaction":
        check_interaction()
    elif args.command == "student-output":
        check_student_output()
    elif args.command == "workflow":
        check_workflow()
    else:
        parser.error("command must be all, schema, interaction, student-output, or workflow")
    print("validation passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
