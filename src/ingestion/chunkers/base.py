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
    
    def _carry_overlap(self, pieces: list[str], separator: str) -> list[str]:
        """
        Decide which trailing pieces from a just-closed chunk should carry
        over into the next chunk as overlap. Shared by any strategy that
        builds chunks by merging small pieces (sentences, paragraphs, etc.)
        up to chunk_size - e.g. RecursiveChunker, SentenceChunker.
        """
        if self.overlap == 0 or not pieces:
            return []

        carried = [pieces[-1]]
        carried_length = len(pieces[-1])

        for piece in reversed(pieces[:-1]):
            extra = len(piece) + len(separator)
            if carried_length + extra > self.overlap:
                break
            carried.insert(0, piece)
            carried_length += extra

        return carried

    def _merge_pieces(self, pieces: list[str], separator: str = " ") -> list[str]:
        """
        Merge small pieces into chunks up to chunk_size, carrying overlap
        between consecutive chunks via _carry_overlap.
        """
        chunks: list[str] = []
        current: list[str] = []

        for piece in pieces:
            candidate_text = separator.join(current + [piece])

            if len(candidate_text) > self.chunk_size and current:
                chunks.append(separator.join(current))
                current = self._carry_overlap(current, separator)

            current.append(piece)

        if current:
            chunks.append(separator.join(current))

        return chunks
    
    def _build_chunks(self, texts: list[str], base_metadata: dict) -> list[Chunk]:
        """
        Wrap a list of chunk texts into Chunk objects, each with its own
        independent metadata copy and a chunk_index. Shared by every
        strategy's chunk() method as the final step.
        """
        chunks = []
        for i, text in enumerate(texts):
            metadata = dict(base_metadata)
            metadata["chunk_index"] = i
            chunks.append(Chunk(text=text, metadata=metadata))
        return chunks