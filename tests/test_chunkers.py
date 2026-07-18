"""
Tests for src/ingestion/chunkers/*.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ingestion.chunkers.fixed_size import FixedSizeChunker
from ingestion.chunkers.recursive import RecursiveChunker

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