"""
Fixed-size chunking strategy.

Splits text into chunks of a fixed character length, advancing by
(chunk_size - overlap) each step, as shown in the sliding-window diagram.
"""

from .base import BaseChunker, Chunk


class FixedSizeChunker(BaseChunker):
    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        chunks: list[Chunk] = []
        step = self.chunk_size - self.overlap
        start = 0
        chunk_index = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            metadata = dict(base_metadata)
            metadata["chunk_index"] = chunk_index

            chunks.append(Chunk(text=chunk_text, metadata=metadata))

            chunk_index += 1
            start += step

        return chunks