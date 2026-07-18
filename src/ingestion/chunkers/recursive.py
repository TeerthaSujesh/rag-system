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
    
    def _carry_overlap(self, pieces: list[str], separator: str) -> list[str]:
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

        return carried
    def _merge_pieces(self, pieces: list[str], separator: str = " ") -> list[str]:
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
    
    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        pieces = self._split_text(text, self.SEPARATORS)
        merged_texts = self._merge_pieces(pieces)

        chunks = []
        for i, chunk_text in enumerate(merged_texts):
            metadata = dict(base_metadata)
            metadata["chunk_index"] = i
            chunks.append(Chunk(text=chunk_text, metadata=metadata))

        return chunks