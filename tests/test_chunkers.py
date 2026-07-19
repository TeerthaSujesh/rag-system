"""
Tests for src/ingestion/chunkers/*.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
from ingestion.chunkers.semantic import SemanticChunker
from ingestion.embeddings import embed_text

from ingestion.chunkers.fixed_size import FixedSizeChunker
from ingestion.chunkers.recursive import RecursiveChunker
from ingestion.chunkers.sentence import SentenceChunker

def test_fixed_size_chunk_lengths():
    text = "A" * 600
    chunker = FixedSizeChunker(chunk_size=256, overlap=50)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    assert len(chunks) == 3
    assert len(chunks[0].text) == 256
    assert len(chunks[1].text) == 256
    assert len(chunks[2].text) == 188


def test_fixed_size_overlap_content_matches():
    text = "".join(str(i % 10) for i in range(600))
    chunker = FixedSizeChunker(chunk_size=256, overlap=50)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    assert chunks[0].text[-50:] == chunks[1].text[:50]


def test_fixed_size_metadata_is_independent_per_chunk():
    text = "A" * 600
    chunker = FixedSizeChunker(chunk_size=256, overlap=50)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    chunks[0].metadata["chunk_index"] = 999
    assert chunks[1].metadata["chunk_index"] != 999

def test_recursive_respects_paragraph_boundaries():
    text = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."
    chunker = RecursiveChunker(chunk_size=30, overlap=0)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    # chunk_size=30 is small enough that all 3 paragraphs can't merge into one
    assert len(chunks) > 1

    # every paragraph should appear whole, intact, in some chunk -
    # never truncated mid-word, which is the actual thing we care about
    for paragraph in ["First paragraph here.", "Second paragraph here.", "Third paragraph here."]:
        assert any(paragraph in c.text for c in chunks)

def test_recursive_overlap_zero_means_zero():
    text = "Paragraph one is here.\n\nParagraph two is here.\n\nParagraph three is here."
    chunker = RecursiveChunker(chunk_size=40, overlap=0)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    for i in range(len(chunks) - 1):
        assert chunks[i].text.strip() not in chunks[i + 1].text


def test_recursive_overlap_guarantees_at_least_one_piece():
    text = "Paragraph one is here.\n\nParagraph two is here.\n\nParagraph three is here."
    chunker = RecursiveChunker(chunk_size=40, overlap=10)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    overlap_found = any(
        chunks[i].text.split(".")[-2].strip() in chunks[i + 1].text
        for i in range(len(chunks) - 1)
        if len(chunks[i].text.split(".")) > 1
    )
    assert overlap_found


def test_recursive_metadata_is_independent_per_chunk():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunker = RecursiveChunker(chunk_size=30, overlap=5)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    chunks[0].metadata["chunk_index"] = 999
    assert chunks[1].metadata["chunk_index"] != 999

def test_sentence_does_not_split_on_abbreviations():
    text = "Dr. Smith calculated the force as 3.5N. The result matches the textbook value."
    chunker = SentenceChunker(chunk_size=200, overlap=0)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    # "Dr. Smith" and "3.5N." should never be torn apart by a naive
    # period-based split - this is the whole reason we chose nltk
    full_text = " ".join(c.text for c in chunks)
    assert "Dr. Smith" in full_text
    assert "3.5N." in full_text


def test_sentence_overlap_repeats_a_full_sentence():
    text = (
        "First sentence here. Second sentence here. "
        "Third sentence here. Fourth sentence here."
    )
    chunker = SentenceChunker(chunk_size=40, overlap=15)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    assert len(chunks) > 1
    # at least one full sentence should repeat between consecutive chunks
    overlap_found = any(
        chunks[i].text.strip() != chunks[i + 1].text.strip()
        and any(
            sentence.strip() in chunks[i + 1].text
            for sentence in chunks[i].text.split(". ")
            if sentence.strip()
        )
        for i in range(len(chunks) - 1)
    )
    assert overlap_found


def test_sentence_metadata_is_independent_per_chunk():
    text = "First sentence. Second sentence. Third sentence."
    chunker = SentenceChunker(chunk_size=20, overlap=5)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    chunks[0].metadata["chunk_index"] = 999
    assert chunks[1].metadata["chunk_index"] != 999

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
def test_semantic_splits_on_topic_shift():
    text = (
        "Force equals mass times acceleration, written as F=ma. "
        "This relationship was first described by Newton in his second law. "
        "A heavier object requires more force to achieve the same acceleration. "
        "Meanwhile, in an unrelated topic, photosynthesis converts sunlight into chemical energy. "
        "Plants use chlorophyll to absorb light for this process. "
        "The byproduct of photosynthesis is oxygen, released into the atmosphere."
    )
    chunker = SemanticChunker(chunk_size=500, overlap=0, breakpoint_percentile=80)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    assert len(chunks) == 2
    assert "F=ma" in chunks[0].text
    assert "photosynthesis" in chunks[1].text
    assert "photosynthesis" not in chunks[0].text
    assert "F=ma" not in chunks[1].text


@requires_ollama
def test_semantic_metadata_is_independent_per_chunk():
    text = (
        "Topic one sentence A. Topic one sentence B. Topic one sentence C. "
        "Completely different topic sentence A. Completely different topic sentence B."
    )
    chunker = SemanticChunker(chunk_size=200, overlap=0, breakpoint_percentile=70)
    chunks = chunker.chunk(text, base_metadata={"source": "test.pdf"})

    if len(chunks) > 1:
        chunks[0].metadata["chunk_index"] = 999
        assert chunks[1].metadata["chunk_index"] != 999