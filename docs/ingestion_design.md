# Ingestion Pipeline Design: Chunking Strategy

This doc summarizes the experiments behind our chunking configuration for the
PDF → ChromaDB ingestion pipeline, and the reasoning for the defaults in
`config.py`.

Test corpus: 6 short 2-page auto-generated PDFs in `data/pdfs/`
(`AI_Basics`, `Cyber_Security`, `FastAPI_Guide`, `HR_Policy`,
`Medical_Insurance`, `Python_Programming`). Evaluation harness:
`run_experiment()` in `experiments.py`, using 10 test questions (6
"which document" + 4 within-document precision questions keyed on real
terms like "Maternity", "Grievance", "coroutine", "Exception").

## 1. Chunk Size

Swept with `RecursiveChunker`, overlap fixed at 50:

| size | chunks | avg_len | time(s) | acc@1 | acc@3 |
|------|--------|---------|---------|-------|-------|
| 256  | 104    | 248     | 2.94    | 0.80  | 1.00  |
| 512  | 56     | 467     | 1.63    | 1.00  | 1.00  |
| 768  | 36     | 631     | 1.20    | 1.00  | 1.00  |
| 1024 | 25     | 821     | 0.95    | 1.00  | 1.00  |

**Decision: `chunk_size = 512`.** Accuracy plateaus at 512 and beyond —
going to 768 or 1024 buys nothing in retrieval quality, just fewer,
coarser chunks. 256 is the standout: acc@1 drops to 0.80, meaning
individual facts are getting cut across chunk boundaries often enough to
hurt precision. 512 is the smallest size that doesn't pay that cost.

## 2. Chunk Overlap

Swept with `RecursiveChunker`, chunk_size fixed at 512:

| overlap | chunks | avg_len | time(s) | acc@1 | acc@3 |
|---------|--------|---------|---------|-------|-------|
| 0       | 46     | 387     | 1.26    | 0.90  | 1.00  |
| 50      | 56     | 467     | 1.58    | 1.00  | 1.00  |
| 100     | 58     | 463     | 1.63    | 1.00  | 1.00  |
| 150     | 59     | 468     | 1.66    | 1.00  | 1.00  |

**Decision: `overlap = 50`.** Zero overlap costs 0.10 in acc@1 — a fact
is landing right at a chunk boundary and getting split, so the answer
just isn't fully present in the top-ranked chunk. 50 fully closes that
gap. 100 and 150 add more chunks and indexing time with zero further
accuracy improvement — pure redundant duplication of content across
chunks with no retrieval benefit, so we don't pay for it.

## 3. Strategy Comparison

All five chunkers at the winning `chunk_size=512, overlap=50`:

| strategy     | chunks | avg_len | time(s) | acc@1 | acc@3 |
|--------------|--------|---------|---------|-------|-------|
| fixed_size   | 44     | 443     | 1.40    | 1.00  | 1.00  |
| recursive    | 56     | 467     | 1.57    | 1.00  | 1.00  |
| sentence     | 61     | 421     | 1.65    | 0.90  | 1.00  |
| semantic     | 63     | 390     | 4.76    | 1.00  | 1.00  |
| hierarchical | 54     | 325     | 1.40    | 1.00  | 1.00  |

**Observations:**

- **`hierarchical`** is the strongest overall: matches top accuracy
  (1.00/1.00) with the fewest chunks and smallest average chunk size of
  any 1.00-accuracy strategy, at the fastest indexing time tied with
  fixed_size. It finds efficient boundaries without sacrificing
  retrieval quality.
- **`recursive`** (current default) ties on accuracy with solid,
  unremarkable timing — a safe, simple baseline.
- **`fixed_size`** reaches 1.00/1.00 but with no boundary awareness at
  all; timing is comparable to the others here, so there's no real
  argument for it over recursive or hierarchical.
- **`semantic`** also reaches 1.00/1.00 and produces the smallest
  average chunk size after hierarchical, but at ~3x the indexing time
  of every other strategy — it embeds every sentence individually to
  detect topic breakpoints, on top of normal chunk embeddings. That's a
  real, inherent cost, not a bug (see below for a bug that *was* fixed
  along the way). Worth it if you have longer, more topically varied
  documents; on our short 2-page test docs, the cost isn't buying much
  extra accuracy over cheaper strategies.
- **`sentence`** is the one strategy that didn't fully solve the
  boundary problem — 0.90 acc@1, the same shape of accuracy dip we saw
  with overlap=0. A fact is likely landing at a sentence-chunk boundary
  and getting split. Not investigated further this round; worth a
  look if sentence chunking becomes a real candidate.

**Recommendation:** `RecursiveChunker` remains a reasonable default —
simple, fast, no bugs found. If squeezing out marginally smaller/more
efficient chunks matters, `HierarchicalChunker` is a strong alternative
with the same accuracy and best-in-class timing.

## 4. Bug found: SemanticChunker breakpoints silently never firing

While preparing to run the strategy comparison, `semantic` and
`sentence` initially produced **identical** results (same chunk count,
same avg length, same accuracy) — differing only in that `semantic` was
~3x slower. That's a strong signal something was wrong, since the two
strategies use entirely different boundary logic.

**Root cause:** `_find_breakpoints` computed a threshold via
`statistics.quantiles(distances, n=100)[percentile - 1]` and selected
distances strictly greater than that threshold. On the short sentence
lists typical of our 2-page test docs (roughly 5-15 sentences per page,
i.e. very few distance values), this quantile method — using strict
`>` — produced a threshold approximately equal to the maximum distance
in the sample. Since the comparison was strict, the max value (i.e. the
single strongest topic-shift signal) was excluded, so `breakpoints` came
back empty. With no breakpoints, every sentence in the page fell into
one group, which then went through the exact same merge logic as
`SentenceChunker` — hence the identical output, minus the wasted
per-sentence embedding cost.

**Fix:** replaced the quantile calculation with a percentile function
that interpolates strictly within the bounds of the actual data (never
extrapolating past the max), and changed the comparison to `>=`. This
lets the strongest breakpoint qualify even when the threshold lands
at or near the top of the sample. Verified with:

- A new/existing unit test, `test_semantic_splits_on_topic_shift`,
  asserting a 6-sentence, 2-topic synthetic example splits into exactly
  2 chunks.
- Re-running the full strategy comparison: `semantic` now diverges
  meaningfully from `sentence` (63 vs 61 chunks, avg_len 390 vs 421)
  while holding 1.00/1.00 accuracy.

**Takeaway for future chunker work:** any threshold derived from
sample statistics (quantiles, percentiles, z-scores) needs to be
sanity-checked against small-N behavior specifically, since our test
corpus and likely a lot of real per-page chunking will have relatively
few sentences to work with per call.

## Summary

| Parameter   | Value       | Why |
|-------------|-------------|-----|
| chunk_size  | 512         | Smallest size with no accuracy penalty |
| overlap     | 50          | Smallest overlap that fully fixes the boundary-split accuracy gap |
| strategy    | recursive (default), hierarchical (recommended alternative) | Both hit 1.00/1.00; hierarchical is more efficient |

These match the current defaults in `config.py`
(`DEFAULT_CHUNK_SIZE = 512`, `DEFAULT_CHUNK_OVERLAP = 50`) — this doc
is the empirical justification for those numbers rather than a change
to them.
