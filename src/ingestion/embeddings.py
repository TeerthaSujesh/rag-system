"""
Embedding generation via Ollama.

Wraps `ollama.embeddings()` so the rest of the pipeline (semantic chunking,
the final ChromaDB storage step) never has to know which embedding model
or API is behind it.

All functions take an optional `model` argument — a key into
config.EMBEDDING_MODELS. When omitted, it defaults to config.EMBEDDING_MODEL,
which preserves the exact existing nomic-embed-text behavior for every
current call site (pipeline.py, vector_store.py, chunkers/semantic.py).
This lets experiments.py compare embedding models (task 7) without
touching anything else in the pipeline.
"""

import ollama
import math
from . import config


def _resolve_model(model: str | None) -> dict:
    key = model or config.EMBEDDING_MODEL
    if key not in config.EMBEDDING_MODELS:
        raise ValueError(
            f"Unknown embedding model key: {key!r}. "
            f"Known keys: {list(config.EMBEDDING_MODELS)}"
        )
    return config.EMBEDDING_MODELS[key]


def embed_text(text: str, model: str | None = None) -> list[float]:
    """
    Turn a single string into its embedding vector.

    model: key into config.EMBEDDING_MODELS (e.g. "nomic-embed-text",
    "all-minilm", "bge-small"). Defaults to config.EMBEDDING_MODEL.
    """
    spec = _resolve_model(model)
    response = ollama.embeddings(model=spec["ollama_tag"], prompt=text)
    return response["embedding"]

def embed_many(texts: list[str], model: str | None = None) -> list[list[float]]:
    """
    Embed multiple strings. Simple loop for now - Ollama's Python client
    doesn't currently batch multiple prompts in a single request, so
    this is one call per text under the hood.
    """
    return [embed_text(text, model=model) for text in texts]

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Measures how similar two embedding vectors are, from -1 (opposite)
    to 1 (identical direction). This is the standard way to compare
    embeddings - semantic chunking uses it to detect topic shifts.
    """
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)

def embed_document(text: str, model: str | None = None) -> list[float]:
    """Embed text for STORAGE - use when adding chunks to ChromaDB."""
    spec = _resolve_model(model)
    return embed_text(spec["document_prefix"] + text, model=model)


def embed_query(text: str, model: str | None = None) -> list[float]:
    """Embed text for QUERYING - use when embedding a user's question."""
    spec = _resolve_model(model)
    return embed_text(spec["query_prefix"] + text, model=model)
