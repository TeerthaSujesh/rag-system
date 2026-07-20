"""
FastAPI backend for the RAG system.

Endpoint shape matches what was agreed with the team (POST /ask,
question/answer/retrieved_contexts), wired to the real ingested
knowledge_base collection instead of the sample_contexts.json fixture,
and serving the static frontend from the same app (no CORS needed
since everything is same-origin).

Run with:
    uvicorn src.api:app --reload --app-dir .
or, from the repo root:
    uvicorn api:app --reload --app-dir src
"""

import sys
from pathlib import Path

# Allow "from retrieval..." / "from generation..." imports to work
# the same way they do everywhere else in src/, regardless of cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from retrieval.retriever import Retriever
from generation.generator import generate_answer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_PATH = PROJECT_ROOT / "data" / "chroma_db"
COLLECTION_NAME = "knowledge_base"
STATIC_DIR = PROJECT_ROOT / "static"


def load_chunks_from_chroma() -> list[dict]:
    """
    Pull every chunk out of the real ingested ChromaDB collection and
    reshape it into the {id, text, metadata} format Retriever/KeywordSearch
    expect. Falls back to an empty list (not a crash) if the collection
    doesn't exist yet, so the server can still start and /ask can return
    a clear error instead of failing to boot.
    """
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        return []

    result = collection.get(include=["documents", "metadatas"])
    chunks = []
    for chunk_id, text, metadata in zip(
        result["ids"], result["documents"], result["metadatas"]
    ):
        chunks.append({"id": chunk_id, "text": text, "metadata": metadata or {}})
    return chunks


app = FastAPI()

# Load data once when the server starts, from the real ingested
# collection rather than the sample_contexts.json fixture.
chunks = load_chunks_from_chroma()
retriever = Retriever(chunks) if chunks else None


class QuestionRequest(BaseModel):
    question: str


@app.get("/api/health")
def health():
    return {"status": "ok", "chunks_indexed": len(chunks)}


@app.post("/ask")
def ask(request: QuestionRequest):
    if retriever is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "No ingested data found. Run the ingestion pipeline "
                "(ingest_all_pdfs) before asking questions."
            ),
        )

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    retrieved_results = retriever.retrieve(question, top_k=5)
    contexts = [chunk["text"] for chunk in retrieved_results]
    answer = generate_answer(question, contexts)

    return {
        "question": question,
        "answer": answer,
        "retrieved_contexts": contexts,
        # kept alongside retrieved_contexts (not replacing it) so the
        # frontend can still show rank/score/source per passage without
        # changing the agreed contract's existing fields
        "retrieved_results": [
            {
                "id": r["id"],
                "text": r["text"],
                "score": r.get("rerank_score"),
                "metadata": r.get("metadata", {}),
            }
            for r in retrieved_results
        ],
    }


# Mounted last so it acts as a fallback for "/" and any non-API path,
# without shadowing /ask and /api/health defined above.
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
