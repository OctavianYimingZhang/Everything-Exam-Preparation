#!/usr/bin/env python3
"""Lint PublicLectureNotesPlan modules for teaching depth."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")

FUNCTION_RULES: dict[str, tuple[str, re.Pattern[str]]] = {
    "definition_boundary": (
        "definition_or_boundary_signal_missing",
        re.compile(r"\b(?:is|are|means|refers?\s+to|defined\s+as|describes?|distinguishes|separates|boundary|scope)\b", re.I),
    ),
    "mechanism_process": (
        "mechanism_or_process_signal_missing",
        re.compile(r"\b(?:because|by|through|via|therefore|leads?\s+to|drives?|converts?|activates?|inhibits?|depends\s+on|step|sequence|process|pathway)\b", re.I),
    ),
    "method_readout": (
        "method_readout_signal_missing",
        re.compile(r"\b(?:method|assay|experiment(?:al|ally)?|measure(?:s|d|ment)?|readout|control|detect(?:s|ed|ion)?|sample|protocol|interpret(?:s|ed|ation)?|conductance|saturable|gating|binding)\b", re.I),
    ),
    "graph_data_interpretation": (
        "graph_data_interpretation_signal_missing",
        re.compile(r"\b(?:graph|plot|curve|axis|axes|slope|trend|data|read(?:s|ing)?|pattern|gradient|inference|interpret(?:s|ed|ation)?)\b", re.I),
    ),
    "calculation_unit_worked_example": (
        "calculation_unit_signal_missing",
        re.compile(r"\b(?:calculate|calculation|equation|formula|unit|units|convert|conversion|substitut(?:e|ion)|equals?|compare|free-energy|voltage|=|µM|mM|mol|rate)\b", re.I),
    ),
    "named_example": (
        "named_example_signal_missing",
        re.compile(r"\b(?:example|case|including|such\s+as|illustrate|illustrates|demonstrates|shows|supports)\b", re.I),
    ),
    "limitation_trap": (
        "limitation_or_trap_signal_missing",
        re.compile(r"\b(?:limitation|limit|boundary|trap|error|mistake|false|cannot|does\s+not|only|unless|fails?|invalid|overinterpret)\b", re.I),
    ),
}

BROAD_TITLES = re.compile(r"^\s*(?:overview|introduction|background|key\s+concepts|main\s+ideas|important\s+points|summary|revision\s+notes)\s*$", re.I)
ANALYTIC_MARKERS = re.compile(
    r"\b(?:because|by|through|therefore|so|whereas|although|while|thereby|as\s+a\s+result|consequently|"
    r"means\s+that|explains|limits|enables|prevents|distinguishes|rules?\s+out|supports|implies|requires|changes?|combined)\b",
    re.I,
)
DIRECT_CLAIM_MARKERS = re.compile(r"\b(?:is|are|has|have|means|refers?\s+to|defines?|describes?|differs?|forms?|moves?|allows?|measures?|calculates?|converts?|links)\b", re.I)


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def block_text(block: Any) -> str:
    if not isinstance(block, dict):
        return str(block or "")
    label = str(block.get("label") or "").strip()
    content = block.get("content")
    if isinstance(content, list):
        rendered = "; ".join(str(item).strip() for item in content if str(item).strip())
    else:
        rendered = str(content or "").strip()
    return f"{label}: {rendered}" if label and rendered else (label or rendered)


def module_text(module: dict[str, Any]) -> str:
    chunks = [
        str(module.get("module_title") or ""),
        str(module.get("explanation") or ""),
    ]
    chunks.extend(block_text(block) for block in module.get("blocks", []) or [])
    return "\n".join(chunk for chunk in chunks if chunk.strip())


def iter_modules(plan: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    modules: list[tuple[str, dict[str, Any]]] = []
    for lecture_index, lecture in enumerate(plan.get("public_lecture_sections", []) or [], start=1):
        if not isinstance(lecture, dict):
            continue
        for module_index, module in enumerate(lecture.get("modules", []) or [], start=1):
            if isinstance(module, dict):
                modules.append((f"public_lecture_sections[{lecture_index}].modules[{module_index}]", module))
    return modules


def lint_module(module: dict[str, Any], where: str) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    title = str(module.get("module_title") or "").strip()
    explanation = str(module.get("explanation") or "").strip()
    text = module_text(module)
    functions = module.get("knowledge_functions") if isinstance(module.get("knowledge_functions"), list) else []
    normalized_functions = [str(function).strip() for function in functions if str(function).strip()]
    blocks = module.get("blocks") if isinstance(module.get("blocks"), list) else []
    block_types = {str(block.get("block_type") or "").strip() for block in blocks if isinstance(block, dict)}

    if BROAD_TITLES.match(title):
        failures.append({"type": "module_title_not_micro_topic", "where": where, "module_title": title})
    if len(words(title)) > 16:
        failures.append({"type": "module_title_too_broad_or_long", "where": where, "module_title": title, "words": len(words(title))})
    if len(normalized_functions) < 2:
        failures.append({"type": "module_has_fewer_than_two_knowledge_functions", "where": where, "module_title": title})
    if len(words(explanation)) < 35:
        failures.append({"type": "module_explanation_too_short_for_teaching", "where": where, "module_title": title, "words": len(words(explanation))})
    if not DIRECT_CLAIM_MARKERS.search(explanation):
        failures.append({"type": "module_lacks_direct_definition_or_identity_claim", "where": where, "module_title": title})
    if not ANALYTIC_MARKERS.search(text):
        failures.append({"type": "module_lacks_decision_consequence_or_boundary", "where": where, "module_title": title})

    for function in normalized_functions:
        rule = FUNCTION_RULES.get(function)
        if rule is None:
            continue
        failure_type, pattern = rule
        if not pattern.search(text):
            failures.append({"type": failure_type, "where": where, "module_title": title, "knowledge_function": function})

    if "calculation_unit_worked_example" in normalized_functions and "calculation" not in block_types:
        failures.append({"type": "calculation_function_without_calculation_block", "where": where, "module_title": title})
    if "graph_data_interpretation" in normalized_functions and "graph_data" not in block_types:
        failures.append({"type": "graph_data_function_without_graph_data_block", "where": where, "module_title": title})
    if "method_readout" in normalized_functions and not ({"method", "graph_data", "table", "comparison"} & block_types):
        failures.append({"type": "method_readout_function_without_method_or_readout_block", "where": where, "module_title": title})
    if "limitation_trap" in normalized_functions and "limitation" not in block_types:
        failures.append({"type": "limitation_function_without_limitation_block", "where": where, "module_title": title})
    if "named_example" in normalized_functions and "example" not in block_types and not re.search(r"\b(?:demonstrates|illustrates|shows|supports)\b", text, re.I):
        failures.append({"type": "named_example_without_interpretation_or_example_block", "where": where, "module_title": title})
    return failures


def lint_plan(plan: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for where, module in iter_modules(plan):
        failures.extend(lint_module(module, where))
    return {"pass": not failures, "failures": failures}


def positive_plan() -> dict[str, Any]:
    return {
        "public_lecture_sections": [
            {
                "lecture_title": "Lecture 1",
                "modules": [
                    {
                        "module_title": "Initial slope gives initial reaction rate",
                        "knowledge_functions": ["method_readout", "graph_data_interpretation", "limitation_trap"],
                        "explanation": "The initial rate is the early linear change in signal per unit time. It is used because later curve sections can reflect substrate depletion or product effects, so the first straight portion gives the least distorted estimate of velocity.",
                        "blocks": [
                            {"block_type": "method", "content": "Measure the early signal against time under defined assay conditions."},
                            {"block_type": "graph_data", "content": "Read the gradient from the first linear section of the graph."},
                            {"block_type": "limitation", "content": "A later curved section is invalid for initial velocity because the reaction conditions have changed."},
                        ],
                    },
                    {
                        "module_title": "Beer-Lambert conversion links absorbance to concentration",
                        "knowledge_functions": ["definition_boundary", "calculation_unit_worked_example", "limitation_trap"],
                        "explanation": "Beer-Lambert conversion is the quantitative relationship between absorbance, path length, extinction coefficient and concentration. It works because absorbance scales with the amount of absorbing material in the light path, so dimension-aware substitution can convert an optical reading into concentration.",
                        "blocks": [
                            {"block_type": "calculation", "label": "Worked example", "content": "Use A = epsilon c l and rearrange for c while keeping path length and concentration units explicit."},
                            {"block_type": "limitation", "content": "The conversion is valid only within the linear absorbance range."},
                        ],
                    },
                ],
            }
        ]
    }


def self_test() -> dict[str, Any]:
    good = lint_plan(positive_plan())
    bad = positive_plan()
    bad["public_lecture_sections"][0]["modules"][0] = {
        "module_title": "Overview",
        "knowledge_functions": ["definition_boundary"],
        "explanation": "This topic includes rate, slope, graphs and enzyme activity.",
        "blocks": [{"block_type": "explanation", "content": "Short list."}],
    }
    bad_result = lint_plan(bad)
    failures: list[dict[str, Any]] = []
    if not good["pass"]:
        failures.append({"type": "positive_plan_rejected", "result": good})
    if bad_result["pass"]:
        failures.append({"type": "shallow_module_not_rejected", "result": bad_result})
    return {"pass": not failures, "positive": good, "negative": bad_result, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
    elif args.plan:
        result = lint_plan(load_json(args.plan))
    else:
        result = {"pass": False, "failures": [{"type": "missing_plan_or_self_test"}]}
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
