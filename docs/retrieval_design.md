# Retrieval Module Design

## Objective

The retrieval module is responsible for identifying the most relevant context for a user query before passing it to the generation module.

Instead of relying on a single retrieval strategy, the system combines semantic retrieval, keyword matching, hybrid fusion, and neural re-ranking.

---

# Architecture

```text
                 User Query
                     │
                     ▼
            Query Embedding
                     │
                     ▼
          Semantic Search
              (ChromaDB)
                     │
                     │
                     ▼
           Keyword Search
                (BM25)
                     │
                     ▼
      Reciprocal Rank Fusion
               (Hybrid)
                     │
                     ▼
      Cross Encoder Re-ranking
                     │
                     ▼
          Top-k Context Chunks
```

---

# Components

## 1. Embedder

Responsible for generating dense vector embeddings using:

- Ollama
- nomic-embed-text

Output:

- Query embeddings
- Document embeddings

---

## 2. Vector Store

Stores embeddings inside ChromaDB.

Responsibilities

- Store embeddings
- Perform similarity search
- Return top semantic matches

---

## 3. Semantic Search

Uses vector similarity search to retrieve semantically related documents.

Advantages

- Understands meaning
- Handles paraphrases
- Robust to wording changes

Limitations

- Can miss exact keyword matches

---

## 4. Keyword Search

Implemented using BM25.

Advantages

- Excellent exact keyword matching
- Handles rare terms
- Fast retrieval

Limitations

- Does not understand semantics

---

## 5. Hybrid Search

Combines semantic and keyword retrieval using Reciprocal Rank Fusion (RRF).

RRF Score

```
Score = Σ 1 / (k + rank)
```

where

- k = 60

Benefits

- Improves recall
- Combines strengths of both retrieval methods

---

## 6. Cross Encoder Re-ranking

Model

```
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The Cross Encoder scores each (query, document) pair jointly and produces a relevance score.

The retrieved documents are sorted according to these scores.

Benefits

- Better ranking quality
- Strong semantic understanding

---

# Retrieval Flow

1. Generate query embedding
2. Perform semantic search
3. Perform BM25 search
4. Fuse both rankings using RRF
5. Re-rank using Cross Encoder
6. Return top-k chunks

---

# Advantages

- High recall
- Better precision
- Reduced hallucinations
- Modular architecture
- Easy to extend

---

# Future Improvements

- Metadata filtering
- Query expansion
- Multi-query retrieval
- Dense retrievers (BGE, E5)
- Parent-child retrieval
- Context compression
- Hybrid weighting
- Caching
