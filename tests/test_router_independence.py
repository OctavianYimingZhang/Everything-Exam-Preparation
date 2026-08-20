from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("route_request", ROOT / "scripts" / "route_request.py")
assert SPEC and SPEC.loader
ROUTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ROUTER)


class RouterIndependenceTests(unittest.TestCase):
    def test_required_routing_fixtures(self) -> None:
        fixtures = {
            "把整门课整理成 Mind Map ZIP": ("exam-prep-atlas", "course_atlas", True),
            "分析历年卷做 Units Analysis": ("exam-prep-analysis", "exam_intelligence", True),
            "制作 12 份答案 PDF": ("exam-prep-practice", "solution_book", True),
            "生成 Example Essay": ("exam-prep-essay", "example_essay", True),
            "生成完整课程 Notes": ("exam-prep-notes", "knowledge_notes", True),
            "评估我的 MCQ 答案": ("exam-prep-practice", "answer_evaluation", True),
            "完成正在评分的 lab report": (None, "out_of_scope_assessed_coursework", False),
        }
        for request, expected in fixtures.items():
            with self.subTest(request=request):
                result = ROUTER.route_request(request)
                self.assertEqual((result["skill_id"], result["task_mode"], result["handled"]), expected)
                self.assertEqual(result["plugin_calls"], [])

    def test_out_of_scope_request_names_no_external_destination(self) -> None:
        result = ROUTER.route_request("完成正在评分的 lab report")
        self.assertFalse(result["handled"])
        self.assertIsNone(result["skill_id"])
        self.assertNotIn("destination", result)
        self.assertEqual(result["plugin_calls"], [])

    def test_explicit_model_essay_wins_over_generic_long_answer_language(self) -> None:
        result = ROUTER.route_request("Generate a long-answer annotated model essay")
        self.assertEqual(result["skill_id"], "exam-prep-essay")
        self.assertEqual(result["task_mode"], "example_essay")

    def test_currently_assessed_model_essay_is_refused_before_routing(self) -> None:
        result = ROUTER.route_request("Create a model essay for my currently assessed exam")
        self.assertFalse(result["handled"])
        self.assertIsNone(result["skill_id"])
        self.assertEqual(result["task_mode"], "out_of_scope_assessed_coursework")
        self.assertEqual(result["plugin_calls"], [])

    def test_explicit_combination_returns_each_local_owner(self) -> None:
        result = ROUTER.route_request("Create complete course Notes and practice questions")
        self.assertTrue(result["handled"])
        self.assertEqual(result["skill_id"], "everything-exam-preparation")
        self.assertEqual(result["task_mode"], "combined_artifacts")
        self.assertEqual(
            result["routes"],
            [
                {"skill_id": "exam-prep-notes", "task_mode": "knowledge_notes"},
                {"skill_id": "exam-prep-practice", "task_mode": "question_practice"},
            ],
        )
        self.assertEqual(result["plugin_calls"], [])

        compact = ROUTER.route_request("完整课程 Notes + MCQ 练习题")
        self.assertEqual(
            [item["skill_id"] for item in compact["routes"]],
            ["exam-prep-notes", "exam-prep-practice"],
        )


if __name__ == "__main__":
    unittest.main()
