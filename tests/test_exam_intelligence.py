from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "exam_intelligence_tools.py"
SPEC = importlib.util.spec_from_file_location("exam_intelligence_tools", MODULE_PATH)
assert SPEC and SPEC.loader
exam_intelligence = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exam_intelligence)


def sample_payload() -> dict:
    resolved = {
        "status": "resolved",
        "concept_ids": ["signal-transduction"],
        "evidence": ["Lecture 2 slide 7"],
    }
    unresolved = {
        "status": "unresolved",
        "unresolved_reason": "The supplied course material does not identify a unique target.",
    }
    return {
        "course_id": "BIO101",
        "course_title": "Example Biology",
        "sources": [
            {
                "source_id": "formal-2020",
                "source_name": "Formal paper 2020",
                "source_role": "formal_past_paper",
                "formal_year": 2020,
                "source_locator": "Formal paper 2020.pdf",
            },
            {
                "source_id": "formal-2021",
                "source_name": "Formal paper 2021",
                "source_role": "formal_past_paper",
                "formal_year": 2021,
                "source_locator": "Formal paper 2021.pdf",
            },
            {
                "source_id": "formal-2022",
                "source_name": "Formal paper 2022",
                "source_role": "formal_past_paper",
                "formal_year": 2022,
                "source_locator": "Formal paper 2022.pdf",
            },
            {
                "source_id": "specimen",
                "source_name": "Official specimen",
                "source_role": "official_mock_specimen",
                "source_locator": "Specimen.pdf",
            },
            {
                "source_id": "worksheet",
                "source_name": "Practice worksheet",
                "source_role": "practice_worksheet",
                "source_locator": "Worksheet.docx",
            },
            {
                "source_id": "lecture",
                "source_name": "Lecture material",
                "source_role": "lecture_material",
                "source_locator": "Lecture 2.pptx",
            },
            {
                "source_id": "scheme",
                "source_name": "Mark scheme",
                "source_role": "mark_scheme",
                "source_locator": "Scheme.pdf",
            },
        ],
        "questions": [
            {
                "question_id": "q-formal-2020",
                "source_id": "formal-2020",
                "question_text": "State how signal transduction begins. [4 marks]",
                "question_format": "short_answer",
                "family_id": "signal-family",
                "mapping": resolved,
            },
            {
                "question_id": "q-formal-2021",
                "source_id": "formal-2021",
                "question_text": "Explain signal transduction. [6 marks]",
                "question_format": "long_answer",
                "family_id": "signal-family",
                "mapping": unresolved,
            },
            {
                "question_id": "q-specimen",
                "source_id": "specimen",
                "question_text": "Which of the following initiates signal transduction? [3 marks]",
                "question_format": "mcq",
                "family_id": "signal-family",
                "mapping": resolved,
            },
            {
                "question_id": "q-worksheet",
                "source_id": "worksheet",
                "question_text": "Calculate the signalling response.",
                "question_format": "calculation",
                "family_id": "signal-family",
                "mapping": unresolved,
            },
            {
                "question_id": "q-lecture",
                "source_id": "lecture",
                "question_text": "Lecture recap: explain signal transduction. [100 marks]",
                "question_format": "long_answer",
                "family_id": "signal-family",
                "mapping": resolved,
            },
            {
                "question_id": "q-scheme",
                "source_id": "scheme",
                "question_text": "Signal-transduction marking points. [20 marks]",
                "question_format": "other",
                "family_id": "signal-family",
                "mapping": resolved,
            },
        ],
    }


class ExamIntelligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = exam_intelligence.build_exam_intelligence_package(sample_payload())
        self.family = self.package["public"]["question_families"][0]

    def test_all_five_source_roles_are_explicit(self) -> None:
        counts = self.package["public"]["corpus_scope"]["source_role_counts"]
        self.assertEqual(set(counts), set(exam_intelligence.SOURCE_ROLES))
        self.assertEqual(counts["formal_past_paper"], 3)
        self.assertEqual(counts["official_mock_specimen"], 1)
        self.assertEqual(counts["practice_worksheet"], 1)
        self.assertEqual(counts["lecture_material"], 1)
        self.assertEqual(counts["mark_scheme"], 1)

    def test_required_metrics_have_traceable_values(self) -> None:
        self.assertEqual(set(exam_intelligence.METRIC_NAMES), set(self.package["public"]["metric_definitions"]))
        self.assertEqual(self.family["formal_occurrence_count"], 2)
        self.assertEqual(self.family["distinct_formal_years"], 2)
        self.assertAlmostEqual(self.family["formal_year_coverage"], 2 / 3, places=6)
        self.assertEqual(self.family["auxiliary_occurrence_count"], 2)
        self.assertEqual(self.family["format_diversity"], 4)
        self.assertEqual(self.family["explicit_mark_exposure"], 13)
        self.assertAlmostEqual(self.family["retention"], 2 / 3, places=6)
        self.assertAlmostEqual(self.family["cross_year_stability"], 1 / 3, places=6)
        self.assertEqual(self.family["mapping_coverage"], 0.5)
        self.assertEqual(self.family["unresolved_mapping_count"], 2)

    def test_only_formal_papers_contribute_to_formal_recurrence(self) -> None:
        evidence = self.package["audit"]["metric_evidence"][0]
        self.assertEqual(evidence["formal_question_ids"], ["q-formal-2020", "q-formal-2021"])
        self.assertEqual(evidence["auxiliary_question_ids"], ["q-specimen", "q-worksheet"])
        self.assertNotIn("q-lecture", evidence["formal_question_ids"])
        self.assertNotIn("q-scheme", evidence["formal_question_ids"])
        self.assertNotIn("q-specimen", evidence["formal_question_ids"])

    def test_public_and_audit_data_are_separate(self) -> None:
        rendered_public = json.dumps(self.package["public"], ensure_ascii=False)
        for audit_field in ("question_records", "family_memberships", "metric_evidence", "source_locator"):
            self.assertNotIn(audit_field, rendered_public)
        self.assertIn("question_records", self.package["audit"])
        self.assertIn("metric_evidence", self.package["audit"])

    def test_unmapped_questions_stay_unresolved(self) -> None:
        payload = sample_payload()
        payload["questions"] = [
            {
                "question_id": "q-ambiguous",
                "source_id": "formal-2020",
                "question_text": "Explain the response.",
                "mapping": {
                    "status": "resolved",
                    "concept_ids": ["candidate-only"],
                },
            }
        ]
        package = exam_intelligence.build_exam_intelligence_package(payload)
        question = package["audit"]["question_records"][0]
        self.assertEqual(question["mapping"]["status"], "unresolved")
        self.assertEqual(question["mapping"]["concept_ids"], [])
        self.assertEqual(package["public"]["question_families"][0]["unresolved_mapping_count"], 1)

    def test_no_formal_source_means_no_formal_recurrence(self) -> None:
        payload = sample_payload()
        payload["sources"] = [item for item in payload["sources"] if item["source_role"] != "formal_past_paper"]
        allowed_ids = {item["source_id"] for item in payload["sources"]}
        payload["questions"] = [item for item in payload["questions"] if item["source_id"] in allowed_ids]
        package = exam_intelligence.build_exam_intelligence_package(payload)
        family = package["public"]["question_families"][0]
        self.assertEqual(package["public"]["status"], "needs_material_input")
        self.assertEqual(family["formal_occurrence_count"], 0)
        self.assertEqual(family["formal_year_coverage"], 0)

    def test_shared_source_scan_is_accepted_directly(self) -> None:
        scan_payload = {
            "course_id": "BIO101",
            "scan": {
                "documents": [
                    {
                        "id": "S1",
                        "name": "Formal Paper 2020.pdf",
                        "path": "Formal Paper 2020.pdf",
                        "exam_source_role": "formal_past_paper",
                    },
                    {
                        "id": "S2",
                        "name": "Official specimen.pdf",
                        "path": "Official specimen.pdf",
                        "exam_source_role": "official_mock_specimen",
                    },
                ],
                "fragments": [
                    {
                        "id": "S1_F1",
                        "source_id": "S1",
                        "locator": "page 1",
                        "locator_status": "complete",
                        "family_id": "signalling",
                        "text": "1. Explain receptor signalling. [5 marks]",
                    },
                    {
                        "id": "S2_F1",
                        "source_id": "S2",
                        "locator": "page 2",
                        "locator_status": "complete",
                        "family_id": "signalling",
                        "text": "1. State receptor signalling. [2 marks]",
                    },
                ],
            },
        }
        package = exam_intelligence.build_exam_intelligence_package(scan_payload)
        family = package["public"]["question_families"][0]
        self.assertEqual(package["public"]["corpus_scope"]["formal_years"], [2020])
        self.assertEqual(family["formal_occurrence_count"], 1)
        self.assertEqual(family["auxiliary_occurrence_count"], 1)
        self.assertEqual(package["audit"]["question_records"][0]["source_locator"], "page 1; line 1")

    def test_question_year_is_derived_only_from_owning_formal_source(self) -> None:
        payload = sample_payload()
        payload["questions"][0]["formal_year"] = 2021
        with self.assertRaisesRegex(
            exam_intelligence.ExamIntelligenceError,
            "formal_year must match its owning source",
        ):
            exam_intelligence.build_exam_intelligence_package(payload)

        payload = sample_payload()
        del payload["sources"][0]["formal_year"]
        payload["questions"][0]["formal_year"] = 2020
        with self.assertRaisesRegex(
            exam_intelligence.ExamIntelligenceError,
            "formal_year must match its owning source",
        ):
            exam_intelligence.build_exam_intelligence_package(payload)

    def test_semantic_validation_rejects_question_source_year_drift(self) -> None:
        tampered = copy.deepcopy(self.package)
        question = next(
            item
            for item in tampered["audit"]["question_records"]
            if item["question_id"] == "q-formal-2020"
        )
        question["formal_year"] = 2030
        errors = exam_intelligence.validation_errors(tampered)
        self.assertTrue(any("formal_year differs from its owning source" in error for error in errors))
        self.assertEqual(
            exam_intelligence._formal_year_universe(tampered["audit"]["sources"]),
            [2020, 2021, 2022],
        )

    def test_validator_rejects_weighting_prediction_and_metric_tampering(self) -> None:
        tampered = copy.deepcopy(self.package)
        tampered["public"]["assessment_weight"] = 0.8
        tampered["public"]["question_families"][0]["formal_occurrence_count"] = 999
        errors = exam_intelligence.validation_errors(tampered)
        self.assertTrue(any("Forbidden" in error for error in errors))
        self.assertTrue(any("does not recompute" in error for error in errors))

        predicted = copy.deepcopy(self.package)
        predicted["public"]["limitations"][0] = "This family will be tested."
        errors = exam_intelligence.validation_errors(predicted)
        self.assertTrue(any("Certain future-question claim" in error for error in errors))

    def test_validator_rejects_natural_language_weighting_and_future_predictions(self) -> None:
        weighted = copy.deepcopy(self.package)
        weighted["public"]["question_families"][0]["title"] = "Official assessment weighting: 40%"
        errors = exam_intelligence.validation_errors(weighted)
        self.assertTrue(any("Official assessment-weighting claim" in error for error in errors))

        expected = copy.deepcopy(self.package)
        expected["public"]["question_families"][0]["description"] = (
            "This topic is expected to appear in the next examination."
        )
        errors = exam_intelligence.validation_errors(expected)
        self.assertTrue(any("Future-question prediction claim" in error for error in errors))

        predicted = copy.deepcopy(self.package)
        predicted["public"]["question_families"][0]["title"] = "Predicted next exam question"
        errors = exam_intelligence.validation_errors(predicted)
        self.assertTrue(any("Future-question prediction claim" in error for error in errors))

        expected_on_paper = copy.deepcopy(self.package)
        expected_on_paper["public"]["question_families"][0]["description"] = (
            "This topic is expected in the next exam paper."
        )
        errors = exam_intelligence.validation_errors(expected_on_paper)
        self.assertTrue(any("Future-question prediction claim" in error for error in errors))

        weighted_phrase = copy.deepcopy(self.package)
        weighted_phrase["public"]["question_families"][0]["description"] = (
            "This family accounts for 40% of the examination."
        )
        errors = exam_intelligence.validation_errors(weighted_phrase)
        self.assertTrue(any("Official assessment-weighting claim" in error for error in errors))

    def test_schemas_are_valid_json_and_package_is_semantically_valid(self) -> None:
        for name in (
            "exam_intelligence_package.schema.json",
            "question_record.schema.json",
            "question_family.schema.json",
        ):
            schema = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        result = exam_intelligence.validate_exam_intelligence_package(self.package)
        self.assertEqual(result["status"], "valid")

        try:
            import jsonschema
        except ModuleNotFoundError:
            return
        schema = json.loads(
            (ROOT / "schemas" / "exam_intelligence_package.schema.json").read_text(encoding="utf-8")
        )
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(self.package)

    def test_cli_build_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "input.json"
            output_path = Path(temp_dir) / "package.json"
            input_path.write_text(json.dumps(sample_payload()), encoding="utf-8")
            subprocess.run(
                [sys.executable, str(MODULE_PATH), "build", "--input", str(input_path), "--out", str(output_path)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            completed = subprocess.run(
                [sys.executable, str(MODULE_PATH), "validate", "--input", str(output_path)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(json.loads(completed.stdout)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
