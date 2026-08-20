from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import fitz


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import exam_mode_tools as tools  # noqa: E402


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def solution_payload(title: str = "Membrane Solution Book") -> dict:
    return {
        "title": title,
        "question_groups": [{
            "group_id": "membranes",
            "group_title": "Membrane potential variants",
            "questions": [{
                "question_id": "Q1",
                "question": "Explain how selective potassium permeability establishes a resting potential.",
                "subparts": [
                    {
                        "label": "(a)",
                        "prompt": "Identify the chemical driving force.",
                        "answer": "Potassium initially moves down its concentration gradient.",
                    },
                    {"label": "(b)", "prompt": "Explain the electrical consequence."},
                ],
                "reasoning_chain": [
                    {"locator": "(b)", "text": "Charge separation creates an opposing electrical gradient."},
                    {"text": "The two forces balance at the potassium equilibrium potential."},
                ],
                "formulas": ["EK = RT/zF ln([K+]out/[K+]in)"],
                "tables": [{
                    "title": "Direction of forces",
                    "headers": ["Force", "Direction"],
                    "rows": [["Chemical", "Outward"], ["Electrical", "Inward"]],
                }],
                "final_answer": "Q1-specific answer: the resting potential approaches EK.",
            }, {
                "question_id": "Q2",
                "question": "Predict the effect of increasing sodium permeability.",
                "reasoning_chain": [
                    "Increasing sodium permeability increases the influence of the sodium gradient.",
                    "The potential therefore moves toward the sodium equilibrium potential.",
                ],
                "final_answer": "Q2-specific answer: the membrane depolarises.",
            }],
            "general_approach": [
                "Identify the dominant permeability and its ion gradient.",
                "Reason toward that ion's equilibrium potential before considering mixed permeabilities.",
            ],
        }],
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def document_xml(path: Path) -> tuple[str, ET.Element]:
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml", "word/styles.xml"}
        assert required <= set(archive.namelist())
        raw = archive.read("word/document.xml")
    return raw.decode("utf-8"), ET.fromstring(raw)


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(f"{W}t"))


def test_model_uses_major_questions_as_public_units() -> None:
    model = tools.build_solution_book(solution_payload())
    assert model["task_mode"] == "solution_book"
    assert model["public_answer_unit"] == "major_question"
    assert model["public_answer_units"] == ["Q1", "Q2"]
    assert model["subpart_policy"] == "locator_only"
    q1 = model["question_groups"][0]["questions"][0]
    assert q1["subparts"] == [
        {"label": "(a)", "prompt": "Identify the chemical driving force."},
        {"label": "(b)", "prompt": "Explain the electrical consequence."},
    ]
    assert all("answer" not in subpart for subpart in q1["subparts"])
    assert any(step["locator"] == "(a)" and "concentration gradient" in step["text"] for step in q1["reasoning_chain"])
    assert model["question_groups"][0]["general_approach"] == solution_payload()["question_groups"][0]["general_approach"]


def test_docx_pdf_and_sidecar_are_real_and_ordered(tmp_path: Path) -> None:
    result = tools.generate_solution_book_artifacts(solution_payload(), tmp_path, "membranes")
    docx_path = Path(result["docx_path"])
    pdf_path = Path(result["pdf_path"])
    manifest_path = Path(result["manifest_path"])

    xml, root = document_xml(docx_path)
    full_text = " ".join(node.text or "" for node in root.iter(f"{W}t"))
    assert full_text.count("General Approach") == 1
    assert full_text.index("Q1-specific answer") < full_text.index("Q2-specific answer") < full_text.index("General Approach")
    assert "Question Q1" in full_text and "Question Q2" in full_text
    assert xml.count("<w:keepNext") >= 4
    assert "<w:cantSplit" in xml
    assert "<w:trHeight" not in xml
    assert "<w:shd" in xml and "<w:tblBorders" in xml

    for paragraph in root.iter(f"{W}p"):
        text = paragraph_text(paragraph)
        if text.startswith("(a)") or text.startswith("(b)"):
            style = paragraph.find(f"{W}pPr/{W}pStyle")
            assert style is None or not str(style.attrib.get(f"{W}val", "")).startswith("Heading")

    assert pdf_path.read_bytes().startswith(b"%PDF-")
    with fitz.open(pdf_path) as pdf:
        assert pdf.page_count >= 1
        pdf_text = "\n".join(page.get_text() for page in pdf)
        assert pdf_text.count("General Approach") == 1
        assert pdf_text.index("Q1-specific answer") < pdf_text.index("Q2-specific answer") < pdf_text.index("General Approach")
        for page in pdf:
            for x0, y0, x1, y1, *_ in page.get_text("blocks"):
                assert x0 >= page.rect.x0 - 1
                assert y0 >= page.rect.y0 - 1
                assert x1 <= page.rect.x1 + 1
                assert y1 <= page.rect.y1 + 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["task_mode"] == "solution_book"
    assert manifest["major_question_ids"] == ["Q1", "Q2"]
    assert manifest["general_approach_count"] == 1
    assert manifest["invariants"]["general_approach_after_group"] is True
    artifacts = {item["format"]: item for item in manifest["artifacts"]}
    assert artifacts["docx"]["sha256"] == sha256(docx_path)
    assert artifacts["pdf"]["sha256"] == sha256(pdf_path)
    assert artifacts["docx"]["media_type"].endswith("wordprocessingml.document")
    assert artifacts["pdf"]["media_type"] == "application/pdf"
    assert manifest["validation"]["pdf"]["clipped_blocks"] == 0
    assert manifest["validation"]["pdf"]["orphan_titles"] == 0
    assert manifest["validation"]["pdf"]["general_approach_callouts"] == 1
    assert manifest["validation"]["pdf"]["general_approach_box_fragments"] == 1
    assert manifest["invariants"]["source_references_verified"] is True


def test_long_content_paginates_without_losing_sentinels(tmp_path: Path) -> None:
    payload = solution_payload("Long Solution Book")
    question = payload["question_groups"][0]["questions"][0]
    question["reasoning_chain"] = [
        {"text": f"Reasoning step {index:03d} preserves the causal chain through a deliberately detailed explanation."}
        for index in range(1, 181)
    ]
    question["tables"] = [{
        "title": "Large verification table",
        "headers": ["Step", "Interpretation"],
        "rows": [[str(index), f"Table sentinel {index:03d} with explanatory content."] for index in range(1, 61)],
    }]
    result = tools.generate_solution_book_artifacts(payload, tmp_path, "long-book")
    with fitz.open(result["pdf_path"]) as pdf:
        assert pdf.page_count > 2
        text = "\n".join(page.get_text() for page in pdf)
        assert "Reasoning step 001" in text
        assert "Reasoning step 180" in text
        assert "Table sentinel 001" in text
        assert "Table sentinel 060" in text
        assert text.count("General Approach") == 1
        for page in pdf:
            for x0, y0, x1, y1, *_ in page.get_text("blocks"):
                assert x0 >= page.rect.x0 - 1 and y0 >= page.rect.y0 - 1
                assert x1 <= page.rect.x1 + 1 and y1 <= page.rect.y1 + 1


def test_batch_creates_independent_artifact_sets(tmp_path: Path) -> None:
    second = solution_payload("Enzyme Solution Book")
    second["basename"] = "enzymes"
    batch = tools.generate_solution_book_batch(
        {"batch_name": "twelve-answer-books", "books": [solution_payload(), second]},
        tmp_path,
    )
    assert batch["book_count"] == 2
    batch_manifest = json.loads(Path(batch["batch_manifest_path"]).read_text(encoding="utf-8"))
    assert batch_manifest["book_count"] == 2
    assert len(batch_manifest["books"]) == 2
    for item in batch_manifest["books"]:
        manifest_path = tmp_path / item["manifest_path"]
        assert manifest_path.exists()
        assert item["manifest_sha256"] == sha256(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for artifact in manifest["artifacts"]:
            artifact_path = tmp_path / artifact["path"]
            assert artifact_path.exists()
            assert artifact["sha256"] == sha256(artifact_path)


def test_source_references_must_resolve_to_the_shared_scan(tmp_path: Path) -> None:
    ungrounded = solution_payload()
    ungrounded["question_groups"][0]["questions"][0]["source_refs"] = [{
        "source_name": "Invented Review.pdf",
        "locator": "page 999",
    }]
    book = tools.build_solution_book(ungrounded)
    assert book["qa"]["status"] == "incomplete"
    assert {item["code"] for item in book["qa"]["issues"]} >= {"unknown_source_reference"}
    result = tools.generate_solution_book_artifacts(ungrounded, tmp_path, "ungrounded")
    assert result["manifest"]["validation"]["model_status"] == "incomplete"
    assert result["manifest"]["invariants"]["source_references_verified"] is False

    grounded = solution_payload()
    grounded["source_scan"] = {
        "documents": [{"id": "L1", "name": "Lecture 1.pdf"}],
        "fragments": [{"source_id": "L1", "locator": "page 2", "text": "Potassium permeability."}],
    }
    grounded["question_groups"][0]["questions"][0]["source_refs"] = [{
        "source_id": "L1",
        "source_name": "Lecture 1.pdf",
        "locator": "page 2",
    }]
    verified = tools.build_solution_book(grounded)
    assert verified["qa"]["status"] == "ready"
    assert tools.solution_book_invariants(verified)["source_references_verified"] is True

    tampered = tools.build_solution_book(solution_payload())
    tampered["question_groups"][0]["questions"][0]["source_refs"] = [{
        "source_name": "Invented Review.pdf",
        "locator": "page 999",
    }]
    tampered_result = tools.generate_solution_book_artifacts(tampered, tmp_path, "tampered")
    assert tampered_result["manifest"]["validation"]["model_status"] == "incomplete"
    assert tampered_result["manifest"]["invariants"]["source_references_verified"] is False


def test_oversized_table_row_repeats_header_without_header_only_page(tmp_path: Path) -> None:
    payload = solution_payload("Oversized Row")
    payload["question_groups"][0]["questions"] = [payload["question_groups"][0]["questions"][0]]
    payload["question_groups"][0]["general_approach"] = ["First step", "Second step"]
    payload["question_groups"][0]["questions"][0]["tables"] = [{
        "title": "Oversized verification table",
        "headers": ["Column Header"],
        "rows": [[" ".join(f"rowword{i:04d}" for i in range(1200))]],
    }]
    result = tools.generate_solution_book_artifacts(payload, tmp_path, "oversized-row")
    xml, _ = document_xml(Path(result["docx_path"]))
    oversized_row = re.search(r"<w:tr><w:trPr></w:trPr>.*?rowword0000", xml)
    assert oversized_row is not None

    with fitz.open(result["pdf_path"]) as pdf:
        page_texts = [page.get_text() for page in pdf]
    table_pages = [text for text in page_texts if "Column Header" in text or "rowword" in text]
    assert len(table_pages) > 1
    assert all("Column Header" in text and "rowword" in text for text in table_pages)
    assert result["manifest"]["validation"]["pdf"]["general_approach_callouts"] == 1
    assert result["manifest"]["validation"]["pdf"]["general_approach_box_fragments"] == 1
