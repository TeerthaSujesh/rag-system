from nltk.tokenize import sent_tokenize

from .base import BaseChunker, Chunk
from ..embeddings import embed_many, cosine_similarity


class SemanticChunker(BaseChunker):
    def __init__(self, chunk_size: int, overlap: int = 0, breakpoint_percentile: int = 95):
        super().__init__(chunk_size, overlap)
        self.breakpoint_percentile = breakpoint_percentile

    @staticmethod
    def _percentile(sorted_data: list[float], percentile: float) -> float:
        """Linear-interpolation percentile that never extrapolates past the
        actual min/max of the data. This matters for small samples (a couple
        of pages' worth of sentences): statistics.quantiles(..., n=100) can
        return a threshold approximately equal to the max value on small n,
        which combined with a strict '>' comparison meant the max distance
        (i.e. the real topic-shift breakpoint) was silently never selected.
        """
        n = len(sorted_data)
        if n == 1:
            return sorted_data[0]
        idx = (percentile / 100) * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])

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

        if len(distances) < 2:
            return []

        sorted_distances = sorted(distances)
        threshold = self._percentile(sorted_distances, self.breakpoint_percentile)

        # >= (not >) so the strongest topic shift qualifies even when the
        # interpolated threshold lands close to (or effectively at) the max.
        return [i for i, d in enumerate(distances) if d >= threshold]

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

        return self._build_chunks(merged_texts, base_metadata)