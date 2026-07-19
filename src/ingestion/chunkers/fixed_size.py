"""
Fixed-size chunking strategy.

Splits text into chunks of a fixed character length, advancing by
(chunk_size - overlap) each step, as shown in the sliding-window diagram.
"""
"""
Fixed-size chunking strategy.

Splits text into chunks of a fixed character length, advancing by
(chunk_size - overlap) each step, as shown in the sliding-window diagram.

Note: "sliding window chunking" is the same algorithm as fixed-size
chunking with overlap > 0 - there's no separate technique, so we don't
have a dedicated SlidingWindowChunker file. Set overlap=0 here to get
naive fixed-size behavior, or overlap>0 for the sliding-window variant.
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
    
    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        step = self.chunk_size - self.overlap
        texts = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            texts.append(text[start:end])
            start += step

        return self._build_chunks(texts, base_metadata)