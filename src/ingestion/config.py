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
EMBEDDING_MODEL = "nomic-embed-text"
# --- ChromaDB ------------------------------------------------------------
CHROMA_COLLECTION_NAME = "knowledge_base"
# --- Chunking experiment grid (tasks 2 & 3) -------------------------------
CHUNK_SIZES = [256, 512, 768, 1024]
CHUNK_OVERLAPS = [0, 50, 100, 150]

# Sensible defaults for a single non-experimental run (task 1/5/6 pipeline).
# Update these once the sweep in tasks 2 & 3 tells you what wins.
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50