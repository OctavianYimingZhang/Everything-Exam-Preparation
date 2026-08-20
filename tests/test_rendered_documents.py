from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import fitz
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import exam_mode_tools as practice  # noqa: E402


def _payload() -> dict:
    return {
        "title": "Rendered Solution Book QA",
        "question_groups": [{
            "group_id": "group-1",
            "group_title": "Signal transduction",
            "questions": [{
                "question_id": "Q1",
                "question": "Explain receptor activation.",
                "reasoning_chain": [
                    "Ligand binding changes receptor conformation.",
                    "The conformational change activates downstream signalling.",
                ],
                "final_answer": "Q1 final answer sentinel.",
            }, {
                "question_id": "Q2",
                "question": "Explain signal termination.",
                "reasoning_chain": [
                    "Ligand removal and phosphatase activity reverse activation.",
                    "The pathway therefore returns toward baseline.",
                ],
                "final_answer": "Q2 final answer sentinel.",
            }],
            "general_approach": ["Track activation, propagation, and termination in causal order."],
        }],
    }


def test_solution_book_docx_renders_to_readable_pdf(tmp_path: Path) -> None:
    soffice = shutil.which("soffice")
    if not soffice:
        pytest.skip("LibreOffice is unavailable in this runtime")
    book = practice.build_solution_book(_payload())
    docx = tmp_path / "render_check.docx"
    practice.write_solution_book_docx(docx, book)
    profile = tmp_path / "lo-profile"
    command = [
        soffice,
        "--headless",
        f"-env:UserInstallation={profile.resolve().as_uri()}",
        "--convert-to",
        "pdf",
        "--outdir",
        str(tmp_path),
        str(docx),
    ]
    completed = subprocess.run(command, text=True, capture_output=True, timeout=60)
    assert completed.returncode == 0, completed.stderr or completed.stdout
    rendered = tmp_path / "render_check.pdf"
    assert rendered.is_file() and rendered.read_bytes().startswith(b"%PDF-")
    with fitz.open(rendered) as pdf:
        assert pdf.page_count >= 1
        text = "\n".join(page.get_text() for page in pdf)
        assert text.count("General Approach") == 1
        assert text.index("Q1 final answer sentinel") < text.index("Q2 final answer sentinel") < text.index("General Approach")
        for page in pdf:
            for x0, y0, x1, y1, *_ in page.get_text("blocks"):
                assert x0 >= page.rect.x0 - 1 and y0 >= page.rect.y0 - 1
                assert x1 <= page.rect.x1 + 1 and y1 <= page.rect.y1 + 1
