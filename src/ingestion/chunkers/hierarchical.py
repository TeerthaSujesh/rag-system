"""
Hierarchical chunking strategy.

Detects section headings via a title-case heuristic (short lines, most
words capitalized, no ending punctuation - matches how these documents
are actually formatted, since they don't use numbered chapters/sections).
Delegates actual size-bound chunking of each section's content to a
RecursiveChunker. Every resulting chunk carries section metadata.

Falls back gracefully when no headings are found: documents without
detectable structure are treated as one flat section, chunked normally -
same output as RecursiveChunker alone.
"""

import re

from .base import BaseChunker, Chunk
from .recursive import RecursiveChunker


class HierarchicalChunker(BaseChunker):
    _CONNECTORS = r"and|of|the|in|for|to|a|an|or|with"
    _WORD = rf"(?:[A-Z][A-Za-z0-9&/'-]*|(?:{_CONNECTORS}))"
    SECTION_PATTERN = re.compile(
        rf"^[A-Z][A-Za-z0-9&/'-]*(?:[ \t]{_WORD}){{0,5}}$",
        re.MULTILINE,
    )

    def __init__(self, chunk_size: int, overlap: int = 0):
        super().__init__(chunk_size, overlap)
        self._inner_chunker = RecursiveChunker(chunk_size, overlap)

    def _split_by_pattern(self, text: str, pattern: re.Pattern) -> list[tuple[str | None, str]]:
        matches = list(pattern.finditer(text))
        if not matches:
            return [(None, text)]

        blocks = []
        if matches[0].start() > 0:
            preamble = text[: matches[0].start()].strip()
            if preamble:
                blocks.append((None, preamble))

        for i, match in enumerate(matches):
            heading = match.group().strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            blocks.append((heading, text[start:end].strip()))

        return blocks

    def chunk(self, text: str, base_metadata: dict) -> list[Chunk]:
        sections = self._split_by_pattern(text, self.SECTION_PATTERN)

        all_chunks: list[Chunk] = []
        for section_heading, section_text in sections:
            if not section_text.strip():
                continue

            section_metadata = dict(base_metadata)
            if section_heading:
                section_metadata["section"] = section_heading

            sub_chunks = self._inner_chunker.chunk(section_text, section_metadata)
            all_chunks.extend(sub_chunks)

        for i, c in enumerate(all_chunks):
            c.metadata["chunk_index"] = i

        return all_chunks