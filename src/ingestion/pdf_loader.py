"""
PDF -> raw text extraction, page by page.

Returns per-page text so downstream chunkers and metadata.py can attach
accurate page numbers to every chunk.
"""

from pathlib import Path

from pypdf import PdfReader
import re


_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def load_pdf_pages(pdf_path: Path) -> list[str]:
    """
    Extract text from a PDF, one string per page.
    Page N's text is at index N-1 (pages are 1-indexed in PDFs, this
    list is 0-indexed like normal Python).
    """
    reader = PdfReader(pdf_path)
    return [_clean_text(page.extract_text()) for page in reader.pages]
def load_pdf_with_metadata(pdf_path: Path) -> list[dict]:
    """
    Extract text page by page, paired with metadata each chunker call
    will need: source filename and page number.

    Returns a list of {"text": str, "source": str, "page": int} dicts,
    one per page. "page" is 1-indexed (matches what a human would call
    "page 3", not Python's 0-indexed list position).
    """
    pages = load_pdf_pages(pdf_path)
    source = pdf_path.name

    return [
        {"text": text, "source": source, "page": i + 1}
        for i, text in enumerate(pages)
    ]

def _clean_text(text: str) -> str:
    """
    Strip non-printable control characters that sometimes leak through
    PDF text extraction (e.g. \\x7f from bullet-point encoding quirks),
    while preserving normal whitespace (\\n, \\t) that chunkers rely on.
    """
    return _CONTROL_CHAR_PATTERN.sub("", text)
