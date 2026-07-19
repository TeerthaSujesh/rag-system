"""
Tests for src/ingestion/vector_store.py.
Require Ollama running (embeddings) - skipped otherwise.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from ingestion.embeddings import embed_text, embed_document, embed_query
from ingestion.vector_store import get_collection


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
def test_collection_uses_cosine_space():
    collection = get_collection()
    assert collection.metadata.get("hnsw:space") == "cosine"


@requires_ollama
def test_embed_document_and_embed_query_use_different_prefixes():
    doc_vec = embed_document("leave policy details")
    query_vec = embed_query("leave policy details")
    assert doc_vec != query_vec
