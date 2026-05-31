#!/usr/bin/env python3
"""Build an executable WorkflowPlan from a SkillConfig."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SOURCE_INPUT_KEYS = (
    "lecture_slides",
    "official_notes",
    "course_notes",
    "student_notes",
    "ai_generated_notes",
    "formal_past_papers",
    "practical_materials",
    "mocks_quizzes_answer_keys",
    "exemplars_or_feedback",
    "extra_reading_books_or_papers",
)

PRESET_ALIASES = {
    "full_workflow": "exam_prep_notes_docx",
    "source_inventory": "source_inventory_only",
    "exam_prep_notes": "exam_prep_notes_docx",
    "exam_ready_notes": "exam_prep_notes_docx",
    "notes_generation": "exam_prep_notes_docx",
    "lecture_walkthrough_docx": "knowledge_walkthrough_docx",
    "knowledge_walkthrough": "knowledge_walkthrough_docx",
    "prediction_workbook": "exam_format_diagnosis",
    "past_paper_prediction": "exam_format_diagnosis",
    "mcq_prep": "mcq_exam_prep",
    "short_answer_prep": "short_answer_exam_prep",
    "practical_data_prep": "long_answer_project_scenario_prep",
    "practical_data_problem_prep": "long_answer_project_scenario_prep",
    "long_answer_plan": "long_answer_project_scenario_prep",
    "project_scenario_long_answer": "long_answer_project_scenario_prep",
    "essay_theme_plan": "essay_exam_prep",
    "example_essay": "essay_exam_prep",
    "example_essay_docx": "essay_exam_prep",
    "evidence_gap_audit": "audit_lint_only",
    "incremental_refresh": "exam_prep_notes_docx",
}

PRESET_REQUIRED_CLASSES = {
    "source_inventory_only": ["any_source"],
    "exam_format_diagnosis": ["formal_past_papers"],
    "exam_prep_notes_docx": ["readable_course_notes"],
    "knowledge_walkthrough_docx": ["lecture_or_official_notes"],
    "mcq_exam_prep": ["lecture_or_official_notes"],
    "short_answer_exam_prep": ["lecture_or_official_notes"],
    "long_answer_project_scenario_prep": ["lecture_or_official_notes"],
    "essay_exam_prep": ["lecture_or_official_notes"],
    "audit_lint_only": [],
    "github_ready_qa": [],
}

PRESET_MODULES = {
    "source_inventory_only": ["source_inventory"],
    "exam_format_diagnosis": ["source_inventory", "exam_regime", "question_type"],
    "exam_prep_notes_docx": [
        "source_inventory",
        "fragment_index",
        "course_section_reconstruction",
        "lecture_session_mapping",
        "lecture_concept_module_extraction",
        "knowledge_points",
        "atomic_knowledge_ledger",
        "source_baseline_notes_plan",
        "baseline_coverage_floor_qa",
        "exam_emphasis_profile",
        "exam_overlay_pass",
        "overlay_did_not_damage_coverage_qa",
        "knowledge_only_student_view_filter",
        "output_language_profile",
        "route_docx_style_profile",
        "public_output_point_build",
        "point_coverage_binding",
        "knowledge_only_rendering_gate",
        "exam_prep_notes_plan",
        "public_output_point_linter",
        "output_language_request_linter",
        "question_type_addon_generation",
        "visual_aid_planning",
        "visual_aid_generation_optional",
        "exam_prep_notes_docx_generation",
        "exam_prep_docx_style_linter",
        "exam_prep_notes_linter",
        "deliverable_qa",
    ],
    "knowledge_walkthrough_docx": [
        "source_inventory",
        "fragment_index",
        "lecture_module_extraction",
        "route_docx_style_profile",
        "knowledge_walkthrough_plan",
        "knowledge_only_rendering_gate",
        "knowledge_walkthrough_docx_generation",
        "knowledge_walkthrough_docx_style_linter",
        "deliverable_qa",
    ],
    "mcq_exam_prep": [
        "source_inventory",
        "fragment_index",
        "course_section_reconstruction",
        "lecture_session_mapping",
        "lecture_concept_module_extraction",
        "knowledge_points",
        "atomic_knowledge_ledger",
        "source_baseline_notes_plan",
        "baseline_coverage_floor_qa",
        "exam_emphasis_profile",
        "exam_overlay_pass",
        "overlay_did_not_damage_coverage_qa",
        "knowledge_only_student_view_filter",
        "output_language_profile",
        "route_docx_style_profile",
        "public_output_point_build",
        "point_coverage_binding",
        "knowledge_only_rendering_gate",
        "exam_prep_notes_plan",
        "public_output_point_linter",
        "output_language_request_linter",
        "question_type_addon_generation",
        "visual_aid_planning",
        "visual_aid_generation_optional",
        "exam_prep_notes_docx_generation",
        "exam_prep_docx_style_linter",
        "exam_prep_notes_linter",
        "mcq_policy",
        "mcq_exam_report_docx",
        "deliverable_qa",
    ],
    "short_answer_exam_prep": [
        "source_inventory",
        "fragment_index",
        "course_section_reconstruction",
        "lecture_session_mapping",
        "lecture_concept_module_extraction",
        "knowledge_points",
        "atomic_knowledge_ledger",
        "source_baseline_notes_plan",
        "baseline_coverage_floor_qa",
        "exam_emphasis_profile",
        "exam_overlay_pass",
        "overlay_did_not_damage_coverage_qa",
        "knowledge_only_student_view_filter",
        "output_language_profile",
        "route_docx_style_profile",
        "public_output_point_build",
        "point_coverage_binding",
        "knowledge_only_rendering_gate",
        "exam_prep_notes_plan",
        "public_output_point_linter",
        "output_language_request_linter",
        "question_type_addon_generation",
        "visual_aid_planning",
        "visual_aid_generation_optional",
        "exam_prep_notes_docx_generation",
        "exam_prep_docx_style_linter",
        "exam_prep_notes_linter",
        "short_answer_variants",
        "short_answer_exam_report_docx",
        "deliverable_qa",
    ],
    "long_answer_project_scenario_prep": [
        "source_inventory",
        "fragment_index",
        "course_section_reconstruction",
        "lecture_session_mapping",
        "lecture_concept_module_extraction",
        "knowledge_points",
        "atomic_knowledge_ledger",
        "source_baseline_notes_plan",
        "baseline_coverage_floor_qa",
        "exam_emphasis_profile",
        "exam_overlay_pass",
        "overlay_did_not_damage_coverage_qa",
        "knowledge_only_student_view_filter",
        "output_language_profile",
        "route_docx_style_profile",
        "public_output_point_build",
        "point_coverage_binding",
        "knowledge_only_rendering_gate",
        "exam_prep_notes_plan",
        "public_output_point_linter",
        "output_language_request_linter",
        "question_type_addon_generation",
        "visual_aid_planning",
        "visual_aid_generation_optional",
        "exam_prep_notes_docx_generation",
        "exam_prep_docx_style_linter",
        "exam_prep_notes_linter",
        "method_blocks",
        "long_answer_project_report_docx",
        "deliverable_qa",
    ],
    "essay_exam_prep": [
        "source_inventory",
        "fragment_index",
        "course_section_reconstruction",
        "lecture_session_mapping",
        "lecture_concept_module_extraction",
        "knowledge_points",
        "atomic_knowledge_ledger",
        "source_baseline_notes_plan",
        "baseline_coverage_floor_qa",
        "exam_emphasis_profile",
        "exam_overlay_pass",
        "overlay_did_not_damage_coverage_qa",
        "knowledge_only_student_view_filter",
        "output_language_profile",
        "route_docx_style_profile",
        "public_output_point_build",
        "point_coverage_binding",
        "knowledge_only_rendering_gate",
        "exam_prep_notes_plan",
        "public_output_point_linter",
        "output_language_request_linter",
        "question_type_addon_generation",
        "visual_aid_planning",
        "visual_aid_generation_optional",
        "exam_prep_notes_docx_generation",
        "exam_prep_docx_style_linter",
        "exam_prep_notes_linter",
        "essay_coverage_plan",
        "citation_resolution",
        "citation_rendering_gate",
        "essay_module_example_essays_docx",
        "deliverable_qa",
    ],
    "audit_lint_only": ["audit"],
    "github_ready_qa": ["repository_qa"],
}

PAST_PAPER_AWARE_PRESETS = {
    "exam_prep_notes_docx",
    "mcq_exam_prep",
    "short_answer_exam_prep",
    "long_answer_project_scenario_prep",
    "essay_exam_prep",
}

STYLE_AWARE_PRESETS = {
    "exam_prep_notes_docx",
    "knowledge_walkthrough_docx",
    "mcq_exam_prep",
    "short_answer_exam_prep",
    "long_answer_project_scenario_prep",
    "essay_exam_prep",
}

PAST_PAPER_EVIDENCE_MODULES = ["exam_regime", "past_paper_questions", "question_archetypes", "examiner_operations"]
EXAMPLE_LEARNING_MODULES = [
    "example_learning",
    "transferable_rule_synthesis",
    "rule_promotion_gate",
    "example_transfer_linter",
]

MODULE_DEFS = {
    "source_inventory": {
        "action_type": "CreateSourceInventory",
        "minimum_inputs": ["any_source"],
        "expected_outputs": ["SourceDocument", "SourceCoverageMap"],
        "qa_checks": ["source roles", "extraction status", "evidence-use limits"],
    },
    "fragment_index": {
        "action_type": "BuildFragmentIndex",
        "minimum_inputs": ["source_inventory"],
        "expected_outputs": ["FragmentPartition"],
        "qa_checks": ["partition metadata", "source hash"],
    },
    "example_learning": {
        "action_type": "AnalyzeExamplesIntoTransferableRules",
        "minimum_inputs": ["style_or_example_evidence"],
        "expected_outputs": ["ExampleReviewLedger", "TransferableRuleSet", "NonTransferableContentBlocklist", "ExampleTransferQA"],
        "qa_checks": [
            "one review record per example",
            "what worked and what failed recorded",
            "no course topic or example-name hardcoding",
            "non-transferable content blocked",
            "no factual or prediction support",
        ],
    },
    "transferable_rule_synthesis": {
        "action_type": "SynthesizeTransferableRules",
        "minimum_inputs": ["ExampleReviewLedger", "NonTransferableContentBlocklist"],
        "expected_outputs": ["TransferableRuleSet", "QAFlag"],
        "qa_checks": [
            "source-specific content stripped",
            "rules expressed as generic conditions",
            "rule destination declared",
            "anti-overfit rule retained",
        ],
    },
    "rule_promotion_gate": {
        "action_type": "RunRulePromotionGate",
        "minimum_inputs": ["ExampleReviewLedger", "TransferableRuleSet", "NonTransferableContentBlocklist"],
        "expected_outputs": ["ExampleTransferQA", "QAFlag"],
        "qa_checks": [
            "each promoted rule has validation check",
            "positive and negative regression coverage declared",
            "non-transferable content absent from promoted rules",
            "promotion status explicit",
        ],
    },
    "example_transfer_linter": {
        "action_type": "LintExampleTransfer",
        "minimum_inputs": ["ExampleReviewLedger", "TransferableRuleSet", "ExampleTransferQA"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": [
            "good and bad analysis present",
            "anti-overfit rule present",
            "no direct example-to-skill copying",
            "accepted rules have validation checks",
        ],
    },
    "lecture_module_extraction": {
        "action_type": "BuildLectureModules",
        "minimum_inputs": ["lecture_or_official_notes"],
        "expected_outputs": ["LectureModule"],
        "qa_checks": ["lecture order", "conceptual module boundaries", "student-facing filter"],
    },
    "course_section_reconstruction": {
        "action_type": "ReconstructCourseSections",
        "minimum_inputs": ["readable_course_notes"],
        "expected_outputs": ["CourseSection"],
        "qa_checks": ["source authority", "course-section boundaries", "no note-order leakage"],
    },
    "lecture_session_mapping": {
        "action_type": "MapLectureSessions",
        "minimum_inputs": ["CourseSection"],
        "expected_outputs": ["LectureSession"],
        "qa_checks": ["source order used for prerequisites", "section mapping"],
    },
    "lecture_concept_module_extraction": {
        "action_type": "BuildLectureConceptModules",
        "minimum_inputs": ["LectureSession"],
        "expected_outputs": ["LectureConceptModule"],
        "qa_checks": ["conceptual boundaries", "source-backed module function", "student-facing filter"],
    },
    "knowledge_walkthrough_plan": {
        "action_type": "BuildKnowledgeWalkthroughPlan",
        "minimum_inputs": ["LectureModule", "RouteDocxStyleProfile"],
        "expected_outputs": ["KnowledgeWalkthroughPlan"],
        "qa_checks": ["module map", "lecture recap", "route style profile", "forbidden student fields"],
    },
    "knowledge_walkthrough_docx_generation": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["KnowledgeWalkthroughPlan", "RouteDocxStyleProfile"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["compact walkthrough DOCX format", "2.0 cm margins", "left-aligned compact body text", "knowledge walkthrough linter", "public output boundary"],
    },
    "knowledge_walkthrough_docx_style_linter": {
        "action_type": "LintKnowledgeWalkthroughDocxStyle",
        "minimum_inputs": ["PrepArtifact", "RouteDocxStyleProfile"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": ["black text", "Arial", "2.0 cm margins", "compact line spacing", "left body alignment", "lecture page breaks", "essay-style spacing absent"],
    },
    "exam_regime": {
        "action_type": "SplitExamRegime",
        "minimum_inputs": ["formal_past_papers"],
        "expected_outputs": ["AssessmentRegime", "ExamBlueprint"],
        "qa_checks": ["current regime separation", "answer rules"],
    },
    "question_type": {
        "action_type": "ClassifyQuestionType",
        "minimum_inputs": ["formal_past_papers"],
        "expected_outputs": ["question-type route"],
        "qa_checks": ["mode-specific route"],
    },
    "past_paper_questions": {
        "action_type": "ExtractPastPaperQuestions",
        "minimum_inputs": ["formal_past_papers"],
        "expected_outputs": ["PastPaperQuestion"],
        "qa_checks": ["question numbers", "marks", "command verbs"],
    },
    "question_archetypes": {
        "action_type": "InferQuestionArchetype",
        "minimum_inputs": ["PastPaperQuestion"],
        "expected_outputs": ["QuestionArchetype", "ExaminerOperation", "SlotGrammar"],
        "qa_checks": ["slot grammar", "confidence band"],
    },
    "knowledge_points": {
        "action_type": "SegmentKnowledgePoints",
        "minimum_inputs": ["readable_course_notes"],
        "expected_outputs": ["KnowledgePoint", "EvidenceClaim"],
        "qa_checks": ["source anchors", "claim strength"],
    },
    "atomic_knowledge_ledger": {
        "action_type": "BuildAtomicKnowledgeLedger",
        "minimum_inputs": ["SourceFragment", "KnowledgePoint"],
        "expected_outputs": ["AtomicKnowledgeLedger"],
        "qa_checks": [
            "every source block decomposed",
            "administrative units excluded from student view",
            "knowledge units bound to modules",
            "visual and unreadable units flagged",
        ],
    },
    "source_baseline_notes_plan": {
        "action_type": "BuildSourceBaselineNotesPlan",
        "minimum_inputs": ["CourseSection", "LectureSession", "LectureConceptModule", "KnowledgePoint", "AtomicKnowledgeLedger"],
        "expected_outputs": ["SourceBaselineNotesPlan"],
        "qa_checks": ["source-first module coverage", "protected knowledge points", "atomic knowledge coverage", "no exam pruning"],
    },
    "baseline_coverage_floor_qa": {
        "action_type": "RunBaselineCoverageFloorQA",
        "minimum_inputs": ["SourceBaselineNotesPlan"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": ["definitions preserved", "criteria lists preserved", "named examples preserved", "visual items preserved"],
    },
    "exam_emphasis_profile": {
        "action_type": "BuildExamEmphasisProfile",
        "minimum_inputs": ["KnowledgePoint"],
        "expected_outputs": ["ExamEmphasisProfile"],
        "qa_checks": ["formal papers used when available", "no invented frequency", "public priority filter"],
    },
    "exam_overlay_pass": {
        "action_type": "ApplyExamOverlayPass",
        "minimum_inputs": ["SourceBaselineNotesPlan", "ExamEmphasisProfile"],
        "expected_outputs": ["ExamOverlayPass", "QAFlag"],
        "qa_checks": ["exam overlay only adds or densifies", "source baseline protected", "no exact prediction"],
    },
    "overlay_did_not_damage_coverage_qa": {
        "action_type": "RunOverlayCoverageQA",
        "minimum_inputs": ["SourceBaselineNotesPlan", "ExamOverlayPass"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": ["protected items still visible", "no over-compression", "old template fields absent"],
    },
    "exam_prep_notes_plan": {
        "action_type": "BuildExamPrepNotesPlan",
        "minimum_inputs": [
            "KnowledgeOnlyStudentView",
            "PublicOutputPoint",
            "PointCoverageBinding",
            "OutputLanguageProfile",
            "RouteDocxStyleProfile",
            "SourceBaselineNotesPlan",
            "ExamOverlayPass",
            "CourseSection",
            "LectureSession",
            "LectureConceptModule",
            "KnowledgePoint",
            "ExamEmphasisProfile",
        ],
        "expected_outputs": ["ExamPrepNotesPlan"],
        "qa_checks": [
            "public output points present",
            "internal card fields hidden from ordinary notes",
            "protected atomic coverage bound to public points",
            "route style and output language profiles attached",
        ],
    },
    "knowledge_only_student_view_filter": {
        "action_type": "BuildKnowledgeOnlyStudentView",
        "minimum_inputs": ["AtomicKnowledgeLedger", "SourceBaselineNotesPlan", "ExamOverlayPass"],
        "expected_outputs": ["KnowledgeOnlyStudentView", "QAFlag"],
        "qa_checks": [
            "assessment and audit text filtered",
            "course knowledge map only",
            "exam use restricted to module-level application",
            "protected knowledge units still visible",
        ],
    },
    "output_language_profile": {
        "action_type": "SelectOutputLanguageProfile",
        "minimum_inputs": ["UserExamPrepRequest", "SourceDocument"],
        "expected_outputs": ["OutputLanguageProfile"],
        "qa_checks": [
            "explicit requested language followed when supplied",
            "default English labels retained when request is silent",
            "mixed-language output used only when requested",
            "source-language mixture does not force multilingual output",
        ],
    },
    "route_docx_style_profile": {
        "action_type": "SelectRouteDocxStyleProfile",
        "minimum_inputs": ["WorkflowPlan"],
        "expected_outputs": ["RouteDocxStyleProfile"],
        "qa_checks": [
            "exam prep notes use compact revision style",
            "knowledge walkthrough uses compact lecture-note style",
            "example essays keep essay submission style",
            "lecture page break policy explicit",
        ],
    },
    "public_output_point_build": {
        "action_type": "BuildPublicOutputPoints",
        "minimum_inputs": ["KnowledgeOnlyStudentView", "SourceBaselineNotesPlan", "ExamOverlayPass", "OutputLanguageProfile"],
        "expected_outputs": ["PublicOutputPoint", "PublicPointBlock", "RenderDecision"],
        "qa_checks": [
            "internal scaffold fields not exposed",
            "only knowledge-bearing blocks rendered",
            "ordinary notes omit Exam Use, Common Error / Trap, and Must Master headings",
        ],
    },
    "point_coverage_binding": {
        "action_type": "BindAtomicItemsToPublicPoints",
        "minimum_inputs": ["AtomicKnowledgeLedger", "PublicOutputPoint", "PublicPointBlock"],
        "expected_outputs": ["PointCoverageBinding", "QAFlag"],
        "qa_checks": [
            "protected definitions, criteria, mechanisms, examples, equations, graphs, tables, and workflows bound",
            "administrative items excluded",
            "missing protected bindings flagged",
        ],
    },
    "knowledge_only_rendering_gate": {
        "action_type": "RunKnowledgeOnlyRenderingGate",
        "minimum_inputs": ["KnowledgeOnlyStudentView", "PublicOutputPoint", "PublicPointBlock", "KnowledgeWalkthroughPlan"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": [
            "only source-backed knowledge points rendered",
            "generic answer advice suppressed",
            "integrated reasoning and recommended approach sections absent",
            "question-type reliability commentary absent from ordinary notes",
            "real distinctions rewritten as comparison, limitation, method workflow, graph logic, or calculation logic",
        ],
    },
    "public_output_point_linter": {
        "action_type": "LintPublicOutputPoints",
        "minimum_inputs": ["PublicOutputPoint", "PointCoverageBinding", "RenderDecision"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": [
            "forbidden internal headings absent",
            "protected source-backed items visible",
            "background points compact",
        ],
    },
    "output_language_request_linter": {
        "action_type": "LintOutputLanguageRequestPolicy",
        "minimum_inputs": ["OutputLanguageProfile", "PublicOutputPoint", "PrepArtifact"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": [
            "non-English or mixed-language output requires explicit user request",
            "internal schema keys do not leak as headings",
            "default English labels remain stable when no language override is requested",
        ],
    },
    "question_type_addon_generation": {
        "action_type": "BuildQuestionTypeAddOns",
        "minimum_inputs": ["ExamPrepNotesPlan"],
        "expected_outputs": ["QuestionTypeAddOn"],
        "qa_checks": ["add-ons after base notes", "question-type separation", "forbidden field filter"],
    },
    "visual_aid_planning": {
        "action_type": "PlanVisualAid",
        "minimum_inputs": ["ExamPrepNotesPlan"],
        "expected_outputs": ["VisualAidSpec"],
        "qa_checks": ["optional final layer", "source-backed labels", "copyright boundary"],
    },
    "visual_aid_generation_optional": {
        "action_type": "GenerateVisualAid",
        "minimum_inputs": ["VisualAidSpec"],
        "expected_outputs": ["GeneratedVisualAid"],
        "qa_checks": ["not evidence", "caption boundary", "skip if unavailable"],
    },
    "exam_prep_notes_docx_generation": {
        "action_type": "GenerateExamPrepNotesDocx",
        "minimum_inputs": ["ExamPrepNotesPlan", "PublicOutputPoint", "RouteDocxStyleProfile", "OutputLanguageProfile"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": [
            "compact exam prep DOCX format",
            "2.0 cm margins",
            "left-aligned compact body text",
            "lecture page breaks",
            "public output boundary",
        ],
    },
    "exam_prep_docx_style_linter": {
        "action_type": "LintExamPrepDocxStyle",
        "minimum_inputs": ["PrepArtifact"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": ["black text", "Arial", "2.0 cm margins", "compact line spacing", "left body alignment", "lecture page breaks", "no internal card headings"],
    },
    "exam_prep_notes_linter": {
        "action_type": "LintExamPrepNotes",
        "minimum_inputs": ["PrepArtifact"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": ["star priority labels", "protected modules present", "old template fields absent"],
    },
    "examiner_operations": {
        "action_type": "InferQuestionArchetype",
        "minimum_inputs": ["KnowledgePoint", "question-type route"],
        "expected_outputs": ["ExaminerOperation"],
        "qa_checks": ["answer shape", "marking logic"],
    },
    "mcq_policy": {
        "action_type": "BuildMCQScoringPolicy",
        "minimum_inputs": ["KnowledgePoint"],
        "expected_outputs": ["MCQScoringPolicy"],
        "qa_checks": ["student-facing point cards", "answer-key boundary", "negative marking visibility"],
    },
    "short_answer_variants": {
        "action_type": "GenerateShortAnswerVariants",
        "minimum_inputs": ["KnowledgePoint"],
        "expected_outputs": ["ShortAnswerVariant"],
        "qa_checks": ["module logic", "highlighted keywords", "example answers"],
    },
    "practical_operations": {
        "action_type": "BuildPracticalOperations",
        "minimum_inputs": ["practical_materials"],
        "expected_outputs": ["PracticalOperation"],
        "qa_checks": ["input operation inference limitation follow-up"],
    },
    "method_blocks": {
        "action_type": "BuildMethodBlocks",
        "minimum_inputs": ["KnowledgePoint"],
        "expected_outputs": ["MethodBlock"],
        "qa_checks": ["readout", "control", "caveat"],
    },
    "essay_coverage_plan": {
        "action_type": "BuildEssayCoveragePlan",
        "minimum_inputs": ["KnowledgePoint"],
        "expected_outputs": ["EssayCoveragePlan"],
        "qa_checks": ["coverage role", "argument skeleton"],
    },
    "citation_resolution": {
        "action_type": "VerifyReadingSource",
        "minimum_inputs": ["lecture_or_official_notes"],
        "expected_outputs": ["ReadingSource", "EvidenceClaim"],
        "qa_checks": ["citation verified", "classic-study fallback if needed"],
    },
    "citation_rendering_gate": {
        "action_type": "RunCitationRenderingGate",
        "minimum_inputs": ["EvidenceClaim", "EssayCoveragePlan"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": [
            "academic paper attribution parenthetical only",
            "author-led citation prose absent unless literature history explicitly requested",
            "citation source claims remain content-first",
        ],
    },
    "docx_generation": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["EssayCoveragePlan", "EvidenceClaim"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["DOCX language", "format", "source audit"],
    },
    "mcq_exam_report_docx": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["KnowledgePoint", "MCQScoringPolicy"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["MCQ Point Cards", "forbidden field filter", "DOCX format"],
    },
    "short_answer_exam_report_docx": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["KnowledgePoint", "ShortAnswerVariant"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["module logic", "highlighted keywords", "Example Answer", "forbidden field filter"],
    },
    "long_answer_project_report_docx": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["MethodBlock"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["question analysis", "reusable answer blocks", "Example Answer", "forbidden field filter"],
    },
    "essay_module_example_essays_docx": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["EssayCoveragePlan", "EvidenceClaim"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["module-level Example Essays", "adaptation map", "source audit", "DOCX format"],
    },
    "prep_artifact": {
        "action_type": "GeneratePrepArtifact",
        "minimum_inputs": ["KnowledgePoint"],
        "expected_outputs": ["PrepArtifact"],
        "qa_checks": ["student-facing language", "source links"],
    },
    "deliverable_qa": {
        "action_type": "RunDeliverableQA",
        "minimum_inputs": ["PrepArtifact"],
        "expected_outputs": ["QAFlag"],
        "qa_checks": ["public output boundary", "language lint", "workflow validation"],
    },
    "audit": {
        "action_type": "RunDeliverableQA",
        "minimum_inputs": [],
        "expected_outputs": ["QA report"],
        "qa_checks": ["requested checks only"],
    },
    "repository_qa": {
        "action_type": "RunDeliverableQA",
        "minimum_inputs": [],
        "expected_outputs": ["GitHub-ready QA result"],
        "qa_checks": ["repository checks"],
    },
}

ALL_MODULES = tuple(MODULE_DEFS)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_id(prefix: str, payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def normalize_preset(raw: str | None) -> str:
    value = (raw or "exam_prep_notes_docx").strip()
    value = PRESET_ALIASES.get(value, value)
    if value not in PRESET_MODULES:
        raise ValueError(f"unsupported output preset: {raw}")
    return value


def list_items(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item not in ("", None)]
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def class_for_source_key(key: str) -> str:
    if key in {"lecture_slides", "official_notes"}:
        return "lecture_or_official_notes"
    if key in {"course_notes", "student_notes", "ai_generated_notes"}:
        return "readable_course_notes"
    if key == "formal_past_papers":
        return "formal_past_papers"
    if key == "practical_materials":
        return "practical_materials"
    if key == "mocks_quizzes_answer_keys":
        return "answer_keys"
    if key == "exemplars_or_feedback":
        return "exemplars_or_feedback"
    if key == "extra_reading_books_or_papers":
        return "extra_reading"
    return key


def class_for_scan_role(role: str) -> str | None:
    role = role.lower()
    if "lecture" in role or role in {"official_note", "official_notes"}:
        return "lecture_or_official_notes"
    if ("student" in role and "note" in role) or role in {"course_note", "course_notes", "structured_revision_note", "ai_generated_note"}:
        return "readable_course_notes"
    if "past_paper" in role:
        return "formal_past_papers"
    if "practical" in role or "protocol" in role:
        return "practical_materials"
    if "answer_key" in role or "solution" in role:
        return "answer_keys"
    if "exemplar" in role or "feedback" in role or "guidance" in role:
        return "exemplars_or_feedback"
    if "reading" in role or "book" in role:
        return "extra_reading"
    return None


def scan_has_style_evidence(source_scan: dict[str, Any] | None) -> bool:
    if not source_scan:
        return False
    for item in source_scan.get("files", []):
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).lower()
        analysis_context = str(item.get("analysis_context", "")).lower()
        if item.get("allowed_style_use") or item.get("allowed_layout_use") or item.get("allowed_transferable_example_use"):
            return True
        if analysis_context in {"style_exemplar", "cross_target_example", "docx_format_reference", "layout_exemplar"}:
            return True
        if role in {"exemplar_answer", "exemplar_image", "essay_guidance", "docx_format_reference"}:
            return True
    return False


def style_evidence_available(config: dict[str, Any], source_scan: dict[str, Any] | None = None) -> bool:
    source_inputs = config.get("source_inputs", {})
    if list_items(source_inputs.get("exemplars_or_feedback")):
        return True
    return scan_has_style_evidence(source_scan)


def available_source_classes(config: dict[str, Any], source_scan: dict[str, Any] | None = None) -> set[str]:
    available: set[str] = set()
    source_inputs = config.get("source_inputs", {})
    for key in SOURCE_INPUT_KEYS:
        if list_items(source_inputs.get(key)):
            available.add(class_for_source_key(key))
    if "lecture_or_official_notes" in available:
        available.add("readable_course_notes")
    if source_scan:
        for item in source_scan.get("files", []):
            if not isinstance(item, dict):
                continue
            source_class = class_for_scan_role(str(item.get("role", "")))
            if source_class and item.get("status", "ok") != "missing":
                available.add(source_class)
    if "lecture_or_official_notes" in available:
        available.add("readable_course_notes")
    if style_evidence_available(config, source_scan):
        available.add("style_or_example_evidence")
    if available:
        available.add("any_source")
    return available


def missing_required_classes(required: list[str], available: set[str]) -> list[str]:
    return [item for item in required if item not in available]


def blocker_for_missing(index: int, missing_input: str, selected_preset: str, blocked_modules: list[str] | None = None) -> dict[str, Any]:
    labels = {
        "any_source": "at least one readable source",
        "lecture_or_official_notes": "lecture slides or official notes",
        "readable_course_notes": "at least one readable course-note source",
        "formal_past_papers": "formal past papers",
        "practical_materials": "practical or data/problem materials",
    }
    label = labels.get(missing_input, missing_input.replace("_", " "))
    return {
        "blocker_id": f"block_{index:03d}_{re.sub(r'[^a-z0-9]+', '_', missing_input.lower()).strip('_')}",
        "severity": "blocking",
        "missing_input": missing_input,
        "resolution_prompt": f"Provide {label}, or choose a narrower preset that does not require it.",
        "blocked_modules": blocked_modules or PRESET_MODULES[selected_preset],
    }


def action_for_module(index: int, module: str, modules: list[str], reuse_existing: bool, blockers: list[dict[str, Any]]) -> dict[str, Any]:
    module_def = MODULE_DEFS[module]
    blocking = bool(blockers) and module not in {"source_inventory", "audit", "repository_qa"}
    return {
        "action_id": f"act_{index:03d}_{module}",
        "action_type": module_def["action_type"],
        "module": module,
        "depends_on": [f"act_{idx + 1:03d}_{name}" for idx, name in enumerate(modules[: index - 1])],
        "minimum_inputs": module_def["minimum_inputs"],
        "expected_outputs": module_def["expected_outputs"],
        "can_reuse_existing": reuse_existing,
        "skip_reason": "blocked by missing required input" if blocking else None,
        "qa_gate": {
            "gate_name": f"{module}_gate",
            "required": module not in {"audit", "repository_qa"},
            "checks": module_def["qa_checks"],
        },
    }


def insert_after_once(modules: list[str], anchor: str, additions: list[str]) -> None:
    index = modules.index(anchor) + 1 if anchor in modules else len(modules)
    for addition in additions:
        if addition not in modules:
            modules.insert(index, addition)
            index += 1


def modules_for_preset(
    selected_preset: str,
    available: set[str],
    config: dict[str, Any],
    source_scan: dict[str, Any] | None = None,
) -> list[str]:
    modules = list(PRESET_MODULES[selected_preset])
    if selected_preset in PAST_PAPER_AWARE_PRESETS and "formal_past_papers" in available:
        insert_after_once(modules, "baseline_coverage_floor_qa", PAST_PAPER_EVIDENCE_MODULES)
    if selected_preset in STYLE_AWARE_PRESETS and style_evidence_available(config, source_scan):
        insert_after_once(modules, "fragment_index", EXAMPLE_LEARNING_MODULES)
    return modules


def build_plan(config: dict[str, Any], source_scan: dict[str, Any] | None = None) -> dict[str, Any]:
    output_mode = config.get("output_mode", {})
    raw_mode = output_mode.get("preset") or output_mode.get("mode") or "exam_prep_notes_docx"
    selected_preset = normalize_preset(str(raw_mode))
    required = PRESET_REQUIRED_CLASSES[selected_preset]
    available = available_source_classes(config, source_scan)
    missing = missing_required_classes(required, available)
    modules = modules_for_preset(selected_preset, available, config, source_scan)
    blockers = [blocker_for_missing(index, item, selected_preset, modules) for index, item in enumerate(missing, start=1)]
    advanced = config.get("advanced", {})
    reuse_existing = bool(advanced.get("reuse_existing_intermediates", True))

    actions = [action_for_module(index, module, modules, reuse_existing, blockers) for index, module in enumerate(modules, start=1)]

    skipped_modules = [
        {
            "module": module,
            "reason": f"not required for selected preset {selected_preset}",
        }
        for module in ALL_MODULES
        if module not in modules
    ]

    project = config.get("project", {})
    qa = config.get("qa", {})
    request_scope = {
        "raw_mode": str(raw_mode),
        "normalized_preset": selected_preset,
        "student_visible_only": bool(output_mode.get("student_visible_only", True)),
        "include_audit_package": bool(output_mode.get("include_audit_package", False)),
        "requested_artifacts": list(output_mode.get("requested_artifacts", [])) if isinstance(output_mode.get("requested_artifacts", []), list) else [],
        "available_source_classes": sorted(available),
        "required_source_classes": required,
        "optional_modules_enabled": [
            module
            for module in modules
            if module in {
                "exam_regime",
                "past_paper_questions",
                "question_archetypes",
                "examiner_operations",
                *EXAMPLE_LEARNING_MODULES,
            }
        ],
    }
    target_group_key = str(project.get("target_group_key") or "unspecified_target")
    plan_seed = {
        "target_group_key": target_group_key,
        "selected_preset": selected_preset,
        "request_scope": request_scope,
    }
    return {
        "object_type": "WorkflowPlan",
        "plan_id": stable_id("workflow_plan", plan_seed),
        "request_scope": request_scope,
        "selected_preset": selected_preset,
        "target_group_key": target_group_key,
        "source_inventory_required": "source_inventory" in modules,
        "fragment_index_required": "fragment_index" in modules,
        "actions": actions,
        "skipped_modules": skipped_modules,
        "blockers": blockers,
        "publish_gate": {
            "object_validation": bool(qa.get("run_workflow_validator", True)),
            "lineage_required": bool(qa.get("require_lineage", True)),
            "qa_required": True,
            "strict_publish_gate": bool(qa.get("strict_publish_gate", True)),
            "fail_on_blocking_flags": bool(qa.get("fail_on_blocking_flags", True)),
        },
    }


def validate_plan_shape(plan: dict[str, Any]) -> list[str]:
    required = [
        "plan_id",
        "request_scope",
        "selected_preset",
        "target_group_key",
        "source_inventory_required",
        "fragment_index_required",
        "actions",
        "skipped_modules",
        "blockers",
        "publish_gate",
    ]
    failures = [f"missing top-level field: {field}" for field in required if field not in plan]
    for index, action in enumerate(plan.get("actions", []), start=1):
        for field in ("action_id", "action_type", "module", "depends_on", "minimum_inputs", "expected_outputs", "can_reuse_existing", "skip_reason", "qa_gate"):
            if field not in action:
                failures.append(f"action {index} missing field: {field}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True, help="SkillConfig JSON file.")
    parser.add_argument("--source-scan", type=Path, help="Optional extract_sources.py source_scan.json.")
    parser.add_argument("--output", type=Path, help="Where to write the WorkflowPlan JSON.")
    parser.add_argument("--fail-on-blockers", action="store_true")
    parser.add_argument("--require-module", action="append", default=[], help="Fail unless the generated plan includes this module.")
    parser.add_argument("--forbid-module", action="append", default=[], help="Fail if the generated plan includes this module.")
    args = parser.parse_args()

    try:
        config = load_json(args.config)
        source_scan = load_json(args.source_scan) if args.source_scan else None
        plan = build_plan(config, source_scan)
        failures = validate_plan_shape(plan)
        if failures:
            raise ValueError("; ".join(failures))
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    text = json.dumps(plan, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    modules = {action.get("module") for action in plan.get("actions", [])}
    assertion_failures = []
    for module in args.require_module:
        if module not in modules:
            assertion_failures.append(f"required module missing: {module}")
    for module in args.forbid_module:
        if module in modules:
            assertion_failures.append(f"forbidden module present: {module}")
    if assertion_failures:
        print(json.dumps({"status": "fail", "failures": assertion_failures}, indent=2), file=sys.stderr)
        return 1
    if args.fail_on_blockers and plan["blockers"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
