"""
Metadata schema attached to every chunk (task 4).

Defines one consistent shape across all chunking strategies and document
types, so retrieval never has to check "does this chunk have a chapter
field or not" - missing values are always None, not absent keys.
"""


def build_base_metadata(source: str, page: int) -> dict:
    """
    The metadata every chunk starts with, straight from pdf_loader.py's
    per-page output. Chunkers add to this (chunk_index always; chapter/
    section only HierarchicalChunker adds; problem is set manually per
    document type if relevant, e.g. a textbook with numbered problems).
    """
    return {
        "source": source,
        "page": page,
        "chapter": None,
        "section": None,
        "problem": None,
    }