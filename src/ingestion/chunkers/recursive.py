"""
Recursive character chunking strategy.

Tries to split on the largest natural boundary first (paragraphs), only
falling back to smaller boundaries (sentences, words, characters) if a
piece is still larger than chunk_size. See the separator-fallback diagram.
"""

from .base import BaseChunker, Chunk


class RecursiveChunker(BaseChunker):
    # Ordered largest -> smallest boundary. "" means "give up, cut anywhere".
    SEPARATORS = ["\n\n", ". ", " ", ""]
    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            pieces = list(text)
        else:
            pieces = text.split(separator)

        good_pieces = []
        for piece in pieces:
            if len(piece) <= self.chunk_size:
                good_pieces.append(piece)
            else:
                good_pieces.extend(self._split_text(piece, remaining_separators))

        return good_pieces
    
    """
Recursive character chunking strategy.

Tries to split on the largest natural boundary first (paragraphs), only
falling back to smaller boundaries (sentences, words, characters) if a
piece is still larger than chunk_size. See the separator-fallback diagram.

Merge/overlap logic lives in BaseChunker, shared with SentenceChunker.
"""

from .base import BaseChunker, Chunk


class RecursiveChunker(BaseChunker):
    # Ordered largest -> smallest boundary. "" means "give up, cut anywhere".
    SEPARATORS = ["\n\n", ". ", " ", ""]

    def _split_text(self, text: str, separators: list[str]) -> list[str]:
        if not separators:
            return [text]

        separator = separators[0]
        remaining_separators = separators[1:]

        if separator == "":
            pieces = list(text)
        else:
            pieces = text.split(separator)

        good_pieces = []
        for piece in pieces:
            if len(piece) <= self.chunk_size:
                good_pieces.append(piece)
            else:
                good_pieces.extend(self._split_text(piece, remaining_separators))

        return good_pieces

    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        pieces = self._split_text(text, self.SEPARATORS)
        merged_texts = self._merge_pieces(pieces)

        chunks = []
        for i, chunk_text in enumerate(merged_texts):
            metadata = dict(base_metadata)
            metadata["chunk_index"] = i
            chunks.append(Chunk(text=chunk_text, metadata=metadata))

        return chunks
    
    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        pieces = self._split_text(text, self.SEPARATORS)
        merged_texts = self._merge_pieces(pieces)

        chunks = []
        for i, chunk_text in enumerate(merged_texts):
            metadata = dict(base_metadata)
            metadata["chunk_index"] = i
            chunks.append(Chunk(text=chunk_text, metadata=metadata))

        return chunks
    
