"""
Hierarchical chunking strategy.

Detects chapter and section headings via regex, builds a two-level
structure (chapter -> section -> content), then delegates actual
size-bound chunking of each section's text to a RecursiveChunker.
Every resulting chunk carries chapter/section metadata.

Falls back gracefully when no headings are found: documents without
detectable chapter/section structure are treated as one flat section,
chunked normally - same output as RecursiveChunker alone.
"""

import re

from .base import BaseChunker, Chunk
from .recursive import RecursiveChunker


class HierarchicalChunker(BaseChunker):
    CHAPTER_PATTERN = re.compile(r"^chapter\s+\d+[:.]?\s*.*$", re.MULTILINE | re.IGNORECASE)
    SECTION_PATTERN = re.compile(r"^\d+\.\d+\s+.+$", re.MULTILINE)

    def __init__(self, chunk_size: int, overlap: int = 0):
        super().__init__(chunk_size, overlap)
        self._inner_chunker = RecursiveChunker(chunk_size, overlap)

    def _split_by_pattern(self, text: str, pattern: re.Pattern) -> list[tuple[str | None, str]]:
        """
        Split text at every heading matching `pattern`. Returns a list of
        (heading_text_or_None, content_after_heading) pairs. If no heading
        is found at all, returns [(None, text)] - the fallback case.
        """
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
        chapters = self._split_by_pattern(text, self.CHAPTER_PATTERN)

        all_chunks: list[Chunk] = []
        for chapter_heading, chapter_text in chapters:
            sections = self._split_by_pattern(chapter_text, self.SECTION_PATTERN)

            for section_heading, section_text in sections:
                if not section_text.strip():
                    continue

                section_metadata = dict(base_metadata)
                if chapter_heading:
                    section_metadata["chapter"] = chapter_heading
                if section_heading:
                    section_metadata["section"] = section_heading

                sub_chunks = self._inner_chunker.chunk(section_text, section_metadata)
                all_chunks.extend(sub_chunks)

        # each call to the inner chunker restarts chunk_index at 0 for its
        # own section, so reindex once, globally, across the whole document
        for i, c in enumerate(all_chunks):
            c.metadata["chunk_index"] = i

        return all_chunks