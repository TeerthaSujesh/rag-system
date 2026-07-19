# Hybrid Retrieval-Augmented Generation (RAG) System

A modular Retrieval-Augmented Generation (RAG) system built to retrieve relevant context using multiple retrieval strategies before generating grounded responses.

## Features

- Semantic Search using ChromaDB
- Keyword Search using BM25
- Hybrid Retrieval using Reciprocal Rank Fusion (RRF)
- Cross-Encoder Re-ranking
- Modular architecture
- Local embeddings using Ollama (`nomic-embed-text`)

## Project Structure

```text
rag-system/
│
├── data/
│   ├── sample_contexts.json
│   └── sample_questions.json
│
├── docs/
│   └── retrieval_design.md
│
├── src/
│   ├── retrieval/
│   │   ├── embedder.py
│   │   ├── vector_store.py
│   │   ├── semantic_search.py
│   │   ├── keyword_search.py
│   │   ├── hybrid_search.py
│   │   ├── reranker.py
│   │   └── retriever.py
│   │
│   ├── generation/
│   └── main.py
│
├── tests/
│   ├── test_retrieval.py
│   └── test_generation.py
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Retrieval Pipeline
User Query
│
▼
Embedding (Ollama)
│
▼
Semantic Search (ChromaDB)
│
▼
Keyword Search (BM25)
│
▼
Hybrid Search (RRF)
│
▼
Cross Encoder Re-ranking
│
▼
Top-k Relevant Chunks
---

## Installation

Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install the project

```bash
pip install -e .
```

---

## Download Embedding Model

```bash
ollama pull nomic-embed-text
```

Start Ollama

```bash
ollama serve
```

---

## Ingest Sample Data

```bash
python src/ingest_sample.py
```

---

## Run Retrieval Tests

```bash
python -m tests.test_retrieval
```

---

## Technologies Used

- Python
- ChromaDB
- Ollama
- BM25 (rank-bm25)
- Sentence Transformers
- Cross Encoder
- HuggingFace

---

## Generation Module

### Responsibilities

- Prompt Engineering
- Llama 3.2 Integration
- Response Generation
- Response Formatting

### Input

Question

Retrieved Context Chunks

### Output

Generated Answer

### Model

Llama 3.2 3B via Ollama

### Prompt Strategies

- Strict Prompt
- Quote Prompt
- Helpful Prompt