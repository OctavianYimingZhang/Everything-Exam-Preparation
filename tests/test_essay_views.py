from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import essay_exam_tools as tools  # noqa: E402


def source_scan() -> dict:
    return {
        "documents": [
            {"id": "L1", "name": "Lecture 1.pdf", "category": "knowledge_material"},
            {"id": "L2", "name": "Lecture 2.pptx", "category": "knowledge_material"},
            {"id": "P1", "name": "assessment-source.pdf", "exam_source_role": "formal_past_paper"},
            {"id": "R1", "name": "Supplied Review.pdf", "source_hint": "extra_reading_source"},
        ],
        "fragments": [
            {"source_id": "L1", "locator": "page 2", "text": "Selective permeability and ion gradients determine membrane potential."},
            {"source_id": "L2", "locator": "slide 5", "text": "Dynamic conductance changes limit a static equilibrium explanation."},
            {"source_id": "P1", "locator": "page 1", "text": "Discuss how selective permeability shapes membrane potential."},
            {"source_id": "R1", "locator": "page 3", "text": "Verified Author, 2024. DOI 10.1000/verified. Reported conductance changed by 20 percent."},
        ],
    }


def essay_payload() -> dict:
    return {
        "title": "Selective Permeability",
        "question": "Discuss how selective permeability shapes membrane potential.",
        "canonical_body": {"blocks": [{
            "block_id": "intro",
            "paragraph_function": "answer the question and establish the thesis",
            "adaptation_notes": ["For a compare question, state the comparator in the thesis."],
            "segments": [
                {
                    "segment_id": "intro-thesis",
                    "text": "Selective permeability is the central organising mechanism for membrane potential.",
                    "annotations": ["thesis"],
                    "source_refs": [{"source_id": "P1", "usage": "scope", "locator": "page 1"}],
                },
                {
                    "segment_id": "intro-claim",
                    "text": "The membrane is more permeable to some ions than to others.",
                    "annotations": ["claim"],
                    "source_refs": [{"source_id": "L1", "usage": "course_fact", "locator": "page 2"}],
                },
            ],
        }, {
            "block_id": "body-1",
            "paragraph_function": "explain the mechanism, evaluate its limit, and return to the judgement",
            "adaptation_notes": ["Shorten the limitation under a restrictive time limit."],
            "segments": [
                {
                    "segment_id": "body-evidence",
                    "text": "Course material links ion gradients and selective permeability to membrane potential.",
                    "annotations": ["evidence"],
                    "source_refs": [{"source_id": "L1", "usage": "course_fact", "locator": "page 2"}],
                },
                {
                    "segment_id": "body-analysis",
                    "text": "This shows that chemical diffusion and electrical opposition must be analysed together.",
                    "annotations": ["analysis"],
                },
                {
                    "segment_id": "body-limitation",
                    "text": "A static equilibrium account is limited when conductance changes over time.",
                    "annotations": ["limitation"],
                    "source_refs": [{"source_id": "L2", "usage": "course_fact", "locator": "slide 5"}],
                },
                {
                    "segment_id": "body-synthesis",
                    "text": "Therefore the strongest judgement combines ion gradients with relative and changing permeability.",
                    "annotations": ["synthesis"],
                    "source_refs": [{"source_id": "L2", "usage": "course_fact", "locator": "slide 5"}],
                },
            ],
        }]},
    }


def clean_text(package: dict) -> str:
    return "\n\n".join(item["text"] for item in package["views"]["clean"]["paragraphs"])


def annotated_body_text(package: dict) -> str:
    return "\n\n".join(
        " ".join(segment["text"] for segment in paragraph["segments"])
        for paragraph in package["views"]["annotated"]["paragraphs"]
    )


def test_clean_and_annotated_views_share_one_body() -> None:
    package = tools.build_essay_views(essay_payload(), source_scan())
    assert package["status"] == "ready"
    assert clean_text(package) == annotated_body_text(package)
    integrity = package["view_integrity"]
    assert integrity["shared_body"] is True
    assert integrity["annotation_coverage_complete"] is True
    assert set(integrity["annotation_types_present"]) == tools.ESSAY_REQUIRED_ANNOTATIONS
    assert package["views"]["clean"]["body_sha256"] == package["views"]["annotated"]["body_sha256"]
    assert "[thesis]" not in package["views"]["clean"]["rendered_text"]
    assert "[thesis]" in package["views"]["annotated"]["rendered_text"]
    assert "[Paragraph function:" in package["views"]["annotated"]["rendered_text"]
    assert "[Adaptation notes:" in package["views"]["annotated"]["rendered_text"]


def test_view_validator_detects_content_drift() -> None:
    package = tools.build_essay_views(essay_payload(), source_scan())
    drifted = copy.deepcopy(package)
    drifted["views"]["annotated"]["paragraphs"][0]["segments"][0]["text"] += " Drift."
    assert tools.validate_essay_views(drifted)["shared_body"] is False


def test_view_validator_uses_annotated_metadata_after_json_round_trip() -> None:
    package = json.loads(json.dumps(tools.build_essay_views(essay_payload(), source_scan())))
    for paragraph in package["views"]["annotated"]["paragraphs"]:
        paragraph.pop("paragraph_function")
        paragraph.pop("adaptation_notes")
        for segment in paragraph["segments"]:
            segment.pop("annotations")

    integrity = tools.validate_essay_views(package)
    assert integrity["valid"] is False
    assert integrity["shared_body"] is True
    assert integrity["annotated_metadata_matches_canonical"] is False
    assert integrity["annotated_rendered_text_matches_metadata"] is False
    assert integrity["annotation_coverage_complete"] is False
    assert set(integrity["missing_annotation_types"]) == tools.ESSAY_REQUIRED_ANNOTATIONS


def test_past_papers_are_scope_only_and_citations_are_not_invented() -> None:
    good = tools.build_essay_views(essay_payload(), source_scan())
    assert good["source_audit"]["status"] == "grounded"
    assert good["source_audit"]["past_paper_source_ids"] == ["P1"]
    assert good["source_audit"]["past_paper_use"] == "question_scope_and_emphasis_only"
    assert good["source_audit"]["fabricated_citations_added"] is False

    bad = essay_payload()
    evidence = bad["canonical_body"]["blocks"][1]["segments"][0]
    evidence["source_refs"] = [{"source_id": "P1", "usage": "course_fact"}]
    evidence["text"] += " Fictional et al., 2026 reported this result (10.9999/invented)."
    audited = tools.build_essay_views(bad, source_scan())
    codes = {issue["code"] for issue in audited["source_audit"]["issues"]}
    assert audited["status"] == "needs_review"
    assert "past_paper_used_as_factual_evidence" in codes
    assert "evidence_without_course_source" in codes
    assert "unverified_citation" in codes
    assert "unverified_doi" in codes


def test_unresolved_locator_is_reported() -> None:
    payload = essay_payload()
    payload["canonical_body"]["blocks"][1]["segments"][0]["source_refs"][0]["locator"] = "page 999"
    package = tools.build_essay_views(payload, source_scan())
    codes = {issue["code"] for issue in package["source_audit"]["issues"]}
    assert package["status"] == "needs_review"
    assert "unresolved_source_locator" in codes


def test_citation_and_doi_must_be_in_the_referenced_fragment() -> None:
    payload = essay_payload()
    evidence = payload["canonical_body"]["blocks"][1]["segments"][0]
    evidence["text"] += " Verified Author, 2024 reported a conductance change (10.1000/verified)."
    package = tools.build_essay_views(payload, source_scan())
    codes = {issue["code"] for issue in package["source_audit"]["issues"]}
    assert package["status"] == "needs_review"
    assert "unverified_citation" in codes
    assert "unverified_doi" in codes


def test_unsupported_quantitative_experiment_is_reported() -> None:
    payload = essay_payload()
    evidence = payload["canonical_body"]["blocks"][1]["segments"][0]
    evidence["text"] += " A fictional experiment reported a 97 percent increase in conductance."
    package = tools.build_essay_views(payload, source_scan())
    codes = {issue["code"] for issue in package["source_audit"]["issues"]}
    assert package["status"] == "needs_review"
    assert "unsupported_quantitative_claim" in codes
    assert "unsupported_result_claim" in codes


def test_supplied_verified_citation_is_accepted_without_generation() -> None:
    payload = essay_payload()
    evidence = payload["canonical_body"]["blocks"][1]["segments"][0]
    evidence["text"] += " Verified Author, 2024 reported a conductance change (10.1000/verified)."
    evidence["source_refs"].append({"source_id": "R1", "usage": "external_evidence", "locator": "page 3"})
    package = tools.build_essay_views(payload, source_scan())
    codes = {issue["code"] for issue in package["source_audit"]["issues"]}
    assert package["status"] == "ready"
    assert "unverified_citation" not in codes
    assert "unverified_doi" not in codes
    assert "unsupported_result_claim" not in codes
    assert "unsupported_quantitative_claim" not in codes
    assert package["source_audit"]["fabricated_citations_added"] is False


def test_active_assessed_complete_draft_is_out_of_scope_even_if_allowed() -> None:
    active = tools.online_essay_permission_status(
        {"assessment_state": "active", "complete_draft": "allowed"},
        requested_actions=["complete_draft"],
    )
    assert active["status"] == "restricted"
    assert active["complete_draft"] == "denied_by_scope"
    assert active["blocked_actions"] == [{
        "action": "complete_draft",
        "reason": "active_assessed_complete_draft_out_of_scope",
    }]
    assert "complete_draft" not in active["allowed_actions"]

    closed = tools.online_essay_permission_status(
        {"assessment_state": "closed"},
        requested_actions=["complete_draft"],
    )
    assert closed["status"] == "ready"
    assert closed["action_conditions"]["complete_draft"] == "post_assessment_model_answer_not_live_submission_support"


def test_active_example_essay_draft_is_refused_without_views() -> None:
    payload = essay_payload()
    payload["assessment_state"] = "active"
    payload["permissions"] = {"complete_draft": "allowed"}
    result = tools.build_essay_views(payload, source_scan())
    assert result["status"] == "restricted"
    assert result["views_generated"] is False
    assert result["reason"] == "active_assessed_complete_draft_out_of_scope"
    assert "views" not in result


def test_explicit_unknown_example_essay_needs_clarification_without_views() -> None:
    payload = essay_payload()
    payload["assessment_state"] = "unknown"
    result = tools.build_essay_views(payload, source_scan())
    assert result["status"] == "needs_clarification"
    assert result["views_generated"] is False
    assert result["reason"] == "assessment_state_unknown"
    assert "views" not in result


def test_closed_or_omitted_lifecycle_allows_example_essay_views() -> None:
    closed_payload = essay_payload()
    closed_payload["assessment_state"] = "closed"
    closed = tools.build_essay_views(closed_payload, source_scan())
    omitted = tools.build_essay_views(essay_payload(), source_scan())
    assert closed["status"] == "ready"
    assert omitted["status"] == "ready"
    assert "views" in closed
    assert "views" in omitted


def test_cli_refuses_active_example_essay_without_views(tmp_path: Path) -> None:
    payload = essay_payload()
    payload["assessment_state"] = "active"
    input_path = tmp_path / "active-example-essay.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "essay_exam_tools.py"),
            "build-essay-views",
            "--input",
            str(input_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["status"] == "restricted"
    assert result["views_generated"] is False
    assert "views" not in result
