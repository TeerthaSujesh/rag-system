"""
Shared contract for all chunking strategies.

Every strategy (fixed-size, recursive, sentence, sliding-window, semantic,
hierarchical) will subclass BaseChunker and implement `chunk()`. This means:
  - main.py / pipeline.py never needs to know which strategy is active
  - the comparison harness (task 1 deliverable) can loop over a list of
    chunker instances and treat them identically
  - swapping strategies later is a one-line change
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
@dataclass
class Chunk:
    """A single unit that will be embedded and stored in ChromaDB."""

    text: str
    metadata: dict = field(default_factory=dict)

class BaseChunker(ABC):
    """
    Common interface for all chunking strategies.

    chunk_size and overlap are measured in characters by default; strategies
    that operate on tokens/sentences instead should document that deviation
    clearly in their own docstring, since it affects how task 2/3 results
    are compared across strategies.
    """

    def __init__(self, chunk_size: int, overlap: int = 0):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    @abstractmethod
    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        """
        Split `text` into a list of Chunk objects.

        base_metadata carries document-level info (source PDF, page,
        chapter, etc. - see metadata.py) that every chunk produced from
        this text should inherit, plus a chunk_index this method should add.
        """
        raise NotImplementedError