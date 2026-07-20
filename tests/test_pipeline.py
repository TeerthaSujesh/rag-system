"""
Tests for src/ingestion/pipeline.py.
Require Ollama running - skipped otherwise.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from ingestion.embeddings import embed_text
from ingestion.pipeline import ingest_pdf, ingest_all_pdfs
from ingestion.chunkers.fixed_size import FixedSizeChunker
from ingestion import config


def _ollama_available() -> bool:
    try:
        embed_text("test")
        return True
    except Exception:
        return False


requires_ollama = pytest.mark.skipif(
    not _ollama_available(), reason="Ollama not running or model not pulled"
)


@requires_ollama
def test_ingest_pdf_returns_chunk_count():
    chunker = FixedSizeChunker(chunk_size=300, overlap=50)
    pdf_path = config.PDF_DIR / "HR_Policy.pdf"
    count = ingest_pdf(pdf_path, chunker)
    assert count > 0


@requires_ollama
def test_ingest_all_pdfs_processes_every_file():
    chunker = FixedSizeChunker(chunk_size=300, overlap=50)
    results = ingest_all_pdfs(chunker)
    assert len(results) == 6
    assert all(count > 0 for count in results.values())
