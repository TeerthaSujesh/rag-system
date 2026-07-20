"""
Sentence-based chunking strategy.

Uses nltk's sentence tokenizer to split text into real sentences (handling
abbreviations, decimals, and units correctly), then groups sentences
together up to chunk_size using the shared merge/overlap logic in
BaseChunker.
"""

from nltk.tokenize import sent_tokenize

from .base import BaseChunker, Chunk


class SentenceChunker(BaseChunker):
    def _split_sentences(self, text: str) -> list[str]:
        return sent_tokenize(text)

    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        pieces = self._split_sentences(text)
        merged_texts = self._merge_pieces(pieces)

        chunks = []
        for i, chunk_text in enumerate(merged_texts):
            metadata = dict(base_metadata)
            metadata["chunk_index"] = i
            chunks.append(Chunk(text=chunk_text, metadata=metadata))

        return chunks
    
    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        pieces = self._split_sentences(text)
        merged_texts = self._merge_pieces(pieces)
        return self._build_chunks(merged_texts, base_metadata)