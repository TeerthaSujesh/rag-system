"""
Tests for src/ingestion/pdf_loader.py.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ingestion.pdf_loader import load_pdf_pages, load_pdf_with_metadata
from ingestion import config


def test_load_pdf_pages_returns_text_per_page():
    pdf_path = config.PDF_DIR / "HR_Policy.pdf"
    pages = load_pdf_pages(pdf_path)

    assert len(pages) >= 1
    assert isinstance(pages[0], str)
    assert len(pages[0]) > 0


def test_load_pdf_with_metadata_pages_are_1_indexed():
    pdf_path = config.PDF_DIR / "HR_Policy.pdf"
    pages = load_pdf_with_metadata(pdf_path)

    assert pages[0]["page"] == 1
    assert pages[1]["page"] == 2


def test_load_pdf_with_metadata_source_is_filename():
    pdf_path = config.PDF_DIR / "HR_Policy.pdf"
    pages = load_pdf_with_metadata(pdf_path)

    assert all(p["source"] == "HR_Policy.pdf" for p in pages)

def test_control_characters_are_stripped():
    text_with_control_char = "Casual Leave: \x7f short-notice leave"
    from ingestion.pdf_loader import _clean_text
    cleaned = _clean_text(text_with_control_char)
    assert "\x7f" not in cleaned
    assert "Casual Leave" in cleaned