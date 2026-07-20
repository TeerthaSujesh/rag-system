"""
Central configuration for the PDF -> ChromaDB pipeline.

Keeping every tunable value here (instead of scattered across files) means
the experiments in tasks 2 & 3 (chunk size / overlap sweeps) are just a
matter of looping over these lists — no need to touch chunker or embedding
code at all.
"""

from pathlib import Path
# --- Paths -------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = PROJECT_ROOT / "data" / "pdfs"
CHROMA_PERSIST_DIR = PROJECT_ROOT / "data" / "chroma_db"

# --- Embedding model -----------------------------------------------------
# Served locally via Ollama, matching the generation branch's stack.
# Run once before using: `ollama pull nomic-embed-text`
#
# EMBEDDING_MODEL is the *key* into EMBEDDING_MODELS below, used as the
# default everywhere embed_document()/embed_query() are called without an
# explicit model= argument. This keeps the existing task 1/5/6 pipeline
# behavior completely unchanged.
EMBEDDING_MODEL = "nomic-embed-text"

# Registry of embedding models available for comparison (task 7).
# Each model has its own instruction-prefix convention learned during
# training — reusing nomic's "search_document:"/"search_query:" prefixes
# on a different model would hurt its accuracy rather than help it, so
# prefixes are looked up per-model rather than hardcoded in embeddings.py.
#
# Run once before using a given model:
#   ollama pull nomic-embed-text
#   ollama pull all-minilm
#   ollama pull qllama/bge-small-en-v1.5
EMBEDDING_MODELS = {
    "nomic-embed-text": {
        "ollama_tag": "nomic-embed-text",
        "document_prefix": "search_document: ",
        "query_prefix": "search_query: ",
        "dimensions": 768,
    },
    "all-minilm": {
        "ollama_tag": "all-minilm",
        "document_prefix": "",
        "query_prefix": "",
        "dimensions": 384,
    },
    "bge-small": {
        "ollama_tag": "qllama/bge-small-en-v1.5",
        # BGE models are conventionally trained with no prefix on the
        # document/passage side, and an instruction prefix only on the
        # query side.
        "document_prefix": "",
        "query_prefix": "Represent this sentence for searching relevant passages: ",
        "dimensions": 384,
    },
}

# --- ChromaDB ------------------------------------------------------------
CHROMA_COLLECTION_NAME = "knowledge_base"
# --- Chunking experiment grid (tasks 2 & 3) -------------------------------
CHUNK_SIZES = [256, 512, 768, 1024]
CHUNK_OVERLAPS = [0, 50, 100, 150]

# Sensible defaults for a single non-experimental run (task 1/5/6 pipeline).
# Update these once the sweep in tasks 2 & 3 tells you what wins.
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50
