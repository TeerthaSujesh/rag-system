"""
Orchestrates the full PDF -> ChromaDB flow:

    pdf_loader.load() -> chunker.chunk() -> embeddings.embed_document() -> vector_store.add_chunks()

The chunker is passed in, not hardcoded, so this same pipeline can be
re-run with any strategy/chunk_size/overlap combination - exactly what
tasks 2 & 3's experiments need.
"""

from pathlib import Path

from . import config
from .pdf_loader import load_pdf_with_metadata
from .metadata import build_base_metadata
from .embeddings import embed_document
from .vector_store import add_chunks
from .chunkers.base import BaseChunker


def ingest_pdf(pdf_path: Path, chunker: BaseChunker) -> int:
    """
    Process one PDF through the full pipeline. Returns the number of
    chunks added.
    """
    pages = load_pdf_with_metadata(pdf_path)

    all_chunks = []
    for page in pages:
        base_meta = build_base_metadata(source=page["source"], page=page["page"])
        all_chunks.extend(chunker.chunk(page["text"], base_meta))

    if not all_chunks:
        return 0

    embeddings = [embed_document(c.text) for c in all_chunks]
    add_chunks(all_chunks, embeddings)

    return len(all_chunks)

def ingest_all_pdfs(chunker: BaseChunker, pdf_dir: Path = None) -> dict:
    """
    Process every PDF in pdf_dir (defaults to config.PDF_DIR) through
    the pipeline. Returns {filename: chunk_count} for a quick summary.
    """
    pdf_dir = pdf_dir or config.PDF_DIR
    results = {}

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        count = ingest_pdf(pdf_path, chunker)
        results[pdf_path.name] = count

    return results