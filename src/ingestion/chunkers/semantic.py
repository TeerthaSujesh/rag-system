"""
Semantic chunking strategy.

Embeds each sentence (using nomic-embed-text's "clustering: " prefix, which
it requires for accurate similarity comparisons), measures similarity
between consecutive sentences, and cuts wherever similarity drops sharply
(a topic shift) - see the breakpoint diagram. Each detected topic group is
then merged internally up to chunk_size (same overlap logic as other
strategies), but chunks never merge ACROSS a topic boundary.
"""

import statistics

from nltk.tokenize import sent_tokenize

from .base import BaseChunker, Chunk
from ..embeddings import embed_many, cosine_similarity


class SemanticChunker(BaseChunker):
    def __init__(self, chunk_size: int, overlap: int = 0, breakpoint_percentile: int = 95):
        super().__init__(chunk_size, overlap)
        self.breakpoint_percentile = breakpoint_percentile

    def _find_breakpoints(self, sentences: list[str]) -> list[int]:
        if len(sentences) < 3:
            return []

        prefixed = ["clustering: " + s for s in sentences]
        embeddings = embed_many(prefixed)
        similarities = [
            cosine_similarity(embeddings[i], embeddings[i + 1])
            for i in range(len(embeddings) - 1)
        ]
        distances = [1 - s for s in similarities]

        threshold = statistics.quantiles(distances, n=100)[self.breakpoint_percentile - 1]
        return [i for i, d in enumerate(distances) if d > threshold]

    def _group_sentences_by_breakpoints(
        self, sentences: list[str], breakpoints: list[int]
    ) -> list[list[str]]:
        groups = []
        start = 0
        for bp in breakpoints:
            groups.append(sentences[start : bp + 1])
            start = bp + 1
        groups.append(sentences[start:])
        return groups

    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        sentences = sent_tokenize(text)

        if len(sentences) <= 1:
            topic_groups = [sentences] if sentences else []
        else:
            breakpoints = self._find_breakpoints(sentences)
            topic_groups = self._group_sentences_by_breakpoints(sentences, breakpoints)

        merged_texts = []
        for group in topic_groups:
            merged_texts.extend(self._merge_pieces(group))

        chunks = []
        for i, chunk_text in enumerate(merged_texts):
            metadata = dict(base_metadata)
            metadata["chunk_index"] = i
            chunks.append(Chunk(text=chunk_text, metadata=metadata))

        return chunks
    

    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        sentences = sent_tokenize(text)

        if len(sentences) <= 1:
            topic_groups = [sentences] if sentences else []
        else:
            breakpoints = self._find_breakpoints(sentences)
            topic_groups = self._group_sentences_by_breakpoints(sentences, breakpoints)

        merged_texts = []
        for group in topic_groups:
            merged_texts.extend(self._merge_pieces(group))

        return self._build_chunks(merged_texts, base_metadata)