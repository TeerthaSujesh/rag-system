"""
Tests for src/ingestion/chunkers/*.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ingestion.chunkers.fixed_size import FixedSizeChunker


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