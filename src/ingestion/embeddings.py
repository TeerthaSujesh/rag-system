"""
Embedding generation via Ollama's Nomic Embed model.

Wraps `ollama.embeddings()` so the rest of the pipeline (semantic chunking,
the final ChromaDB storage step) never has to know which embedding model
or API is behind it.
"""

import ollama
import math
from . import config


def embed_text(text: str) -> list[float]:
    """
    Turn a single string into its embedding vector.
    """
    response = ollama.embeddings(model=config.EMBEDDING_MODEL, prompt=text)
    return response["embedding"]

def embed_many(texts: list[str]) -> list[list[float]]:
    """
    Embed multiple strings. Simple loop for now - Ollama's Python client
    doesn't currently batch multiple prompts in a single request, so
    this is one call per text under the hood.
    """
    return [embed_text(text) for text in texts]

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