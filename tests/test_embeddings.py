"""
Tests for src/ingestion/embeddings.py.

These require Ollama running locally with nomic-embed-text pulled -
they're skipped automatically if Ollama isn't reachable, since this
is an external-service dependency, not pure logic like the chunkers.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from ingestion.embeddings import embed_text, embed_many
from ingestion.embeddings import embed_text, embed_many, cosine_similarity

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
def test_embed_text_returns_768_dim_vector():
    vec = embed_text("Force equals mass times acceleration.")
    assert len(vec) == 768
    assert all(isinstance(x, float) for x in vec)


@requires_ollama
def test_embed_many_returns_one_vector_per_text():
    texts = ["First sentence.", "Second sentence.", "Third sentence."]
    vectors = embed_many(texts)
    assert len(vectors) == 3
    assert all(len(v) == 768 for v in vectors)


@requires_ollama
def test_similar_texts_have_higher_similarity_than_unrelated_ones():
    """
    Sanity check that embeddings actually capture meaning, not just
    produce random vectors - this is the property semantic chunking
    depends on entirely.
    """
    import math

