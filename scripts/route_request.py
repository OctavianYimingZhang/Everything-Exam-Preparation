#!/usr/bin/env python3
"""Route an exam-preparation request without invoking another plugin."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any


ROUTER_ID = "everything-exam-preparation"


def _contains(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def _result(
    skill_id: str | None,
    task_mode: str,
    reason: str,
    handled: bool = True,
    routes: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "router_id": ROUTER_ID,
        "handled": handled,
        "skill_id": skill_id,
        "task_mode": task_mode,
        "reason": reason,
        "plugin_calls": [],
    }
    if routes is not None:
        result["routes"] = routes
    return result


def _combined_route_candidates(text: str) -> list[dict[str, str]]:
    """Return independently runnable owners in public architecture order."""
    routes: list[dict[str, str]] = []
    if _contains(text, (
        "mind map", "mindmap", "course atlas", "course knowledge tree", "concept graph",
        "website-import", "website import", "知识树", "概念图", "思维导图",
    )):
        routes.append({"skill_id": "exam-prep-atlas", "task_mode": "course_atlas"})
    if _contains(text, (
        "units analysis", "past-paper analysis", "past paper analysis", "exam intelligence",
        "question-family", "question family", "recurrence", "cross-year stability",
        "分析历年卷", "历年卷分析", "题型聚类", "频率分析",
    )):
        routes.append({"skill_id": "exam-prep-analysis", "task_mode": "exam_intelligence"})
    if _contains(text, (
        "notes", "lecture revision", "course-complete", "knowledge-only",
        "完整课程", "课程笔记", "复习笔记", "知识笔记",
    )):
        routes.append({"skill_id": "exam-prep-notes", "task_mode": "knowledge_notes"})

    practice_mode: str | None = None
    if _contains(text, ("answer pdf", "solution book", "答案 pdf", "答案pdf", "答案册")) or re.search(
        r"(?:create|make|制作|生成)\s*\d+\s*(?:份|files?)?\s*(?:answer|solution|答案).*pdf", text
    ):
        practice_mode = "solution_book"
    elif _contains(text, ("evaluate my", "mark my", "assess my answer", "评估我的", "批改我的")) and _contains(
        text, ("answer", "mcq", "saq", "答案", "作答")
    ):
        practice_mode = "answer_evaluation"
    elif _contains(text, ("timed practice", "mock exam", "限时练习", "模拟考试")):
        practice_mode = "timed_practice"
    elif _contains(text, (
        "worked solution", "solve this", "calculation practice", "question bank",
        "mcq", "saq", "long-answer", "long answer", "practice questions",
        "详解", "解题", "计算题", "练习题", "题库",
    )):
        practice_mode = "question_practice"
    if practice_mode:
        routes.append({"skill_id": "exam-prep-practice", "task_mode": practice_mode})

    if _contains(text, (
        "example essay", "model essay", "annotated essay", "essay plan",
        "paragraph exemplar", "closed past assessment", "exam-answer adaptation",
        "范文", "示例 essay", "论文计划", "段落实例", "已结束的考试",
    )):
        routes.append({"skill_id": "exam-prep-essay", "task_mode": "example_essay"})
    return routes


def _explicitly_combined(text: str) -> bool:
    return bool(re.search(
        r"\b(?:and|plus|alongside)\b|as well as|[+&]|同时|分别|以及|并且|和|与|、",
        text,
        re.I,
    ))


def route_request(request: str) -> dict[str, Any]:
    """Return one or more public owners for *request*, or a local out-of-scope result."""
    text = re.sub(r"\s+", " ", request or "").strip().casefold()
    if not text:
        return _result(None, "missing_request", "A request is required before routing.", handled=False)

    assessed_work = (
        "正在评分", "正在考核", "summative coursework", "assessed coursework",
        "graded coursework", "active assessment", "complete my lab report",
        "write my lab report", "完成我的实验报告", "完成 lab report",
    )
    assessed_artifact = (
        "lab report", "assessed report", "poster", "presentation", "website",
        "essay", "model answer", "complete answer", "full answer",
    )
    if _contains(text, assessed_work) or (
        _contains(text, ("assessed", "graded", "正在评分", "正在考核"))
        and _contains(text, assessed_artifact)
    ):
        return _result(
            None,
            "out_of_scope_assessed_coursework",
            "A complete deliverable for currently assessed coursework is outside this plugin.",
            handled=False,
        )

    if _contains(text, (
        "university timetable", "course timetable", "announcement", "student record",
        "module deadline", "exam deadline", "assessment deadline", "coursework deadline",
        "课程表", "大学通知", "学生记录", "管理 deadline", "截止日期",
    )):
        return _result(
            None,
            "out_of_scope_university_administration",
            "University administration and student-record management are outside this plugin.",
            handled=False,
        )

    combined_routes = _combined_route_candidates(text)
    if len(combined_routes) > 1 and _explicitly_combined(text):
        return _result(
            ROUTER_ID,
            "combined_artifacts",
            "The request explicitly combines independently owned exam-preparation artifacts.",
            routes=combined_routes,
        )

    if _contains(text, (
        "mind map", "mindmap", "course atlas", "course knowledge tree", "concept graph",
        "website-import", "website import", "知识树", "概念图", "思维导图",
        "mind map zip", "mindmap zip",
    )):
        return _result("exam-prep-atlas", "course_atlas", "The request asks for a course knowledge map or Atlas package.")

    if _contains(text, (
        "units analysis", "past-paper analysis", "past paper analysis", "exam intelligence",
        "question-family", "question family", "recurrence", "cross-year stability",
        "分析历年卷", "历年卷分析", "题型聚类", "频率分析",
    )):
        return _result("exam-prep-analysis", "exam_intelligence", "The request asks for past-paper or unit-level exam analysis.")

    if _contains(text, (
        "answer pdf", "solution book", "答案 pdf", "答案pdf", "答案册",
    )) or re.search(r"(?:create|make|制作|生成)\s*\d+\s*(?:份|files?)?\s*(?:answer|solution|答案).*pdf", text):
        return _result("exam-prep-practice", "solution_book", "The request asks for answer PDFs or a solution book.")

    if _contains(text, (
        "evaluate my", "mark my", "assess my answer", "评估我的", "批改我的",
    )) and _contains(text, ("answer", "mcq", "saq", "答案", "作答")):
        return _result("exam-prep-practice", "answer_evaluation", "The request asks to evaluate a student answer.")

    if _contains(text, ("timed practice", "mock exam", "限时练习", "模拟考试")):
        return _result("exam-prep-practice", "timed_practice", "The request asks for timed practice.")

    if _contains(text, (
        "example essay", "model essay", "annotated essay", "essay plan",
        "paragraph exemplar", "closed past assessment", "exam-answer adaptation",
        "范文", "示例 essay", "论文计划", "段落实例", "已结束的考试",
    )):
        return _result("exam-prep-essay", "example_essay", "The request asks for an exam essay learning artifact.")

    if _contains(text, (
        "worked solution", "solve this", "calculation practice", "question bank",
        "mcq", "saq", "long-answer", "long answer", "practice questions",
        "详解", "解题", "计算题", "练习题", "题库",
    )):
        return _result("exam-prep-practice", "question_practice", "The request asks for question-based practice or worked reasoning.")

    if _contains(text, (
        "notes", "lecture revision", "course-complete", "knowledge-only",
        "完整课程", "课程笔记", "复习笔记", "知识笔记",
    )):
        return _result("exam-prep-notes", "knowledge_notes", "The request asks for course-complete knowledge-only Notes.")

    return _result(
        None,
        "needs_artifact_choice",
        "The requested exam-preparation artifact is not explicit enough to select a single owner.",
        handled=False,
    )


def self_test() -> None:
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
        result = route_request(request)
        actual = (result["skill_id"], result["task_mode"], result["handled"])
        assert actual == expected, (request, actual, expected)
        assert result["plugin_calls"] == []
    combined = route_request("Create complete course Notes and practice questions")
    assert combined["task_mode"] == "combined_artifacts"
    assert combined["skill_id"] == ROUTER_ID
    assert [item["skill_id"] for item in combined["routes"]] == ["exam-prep-notes", "exam-prep-practice"]
    assessed_essay = route_request("Create a model essay for my currently assessed exam")
    assert assessed_essay["task_mode"] == "out_of_scope_assessed_coursework"
    assert assessed_essay["handled"] is False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("OK: route_request self-test passed")
        return 0
    print(json.dumps(route_request(args.request or ""), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
