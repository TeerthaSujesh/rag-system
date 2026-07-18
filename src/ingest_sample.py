import json

from retrieval.embedder import Embedder
from retrieval.vector_store import VectorStore

with open("data/sample_contexts.json", "r") as f:
    chunks = json.load(f)

embedder = Embedder()
vector_store = VectorStore()

for chunk in chunks:
    embedding = embedder.embed_query(chunk["text"])

    vector_store.collection.add(
        ids=[chunk["id"]],
        documents=[chunk["text"]],
        metadatas=[chunk["metadata"]],
        embeddings=[embedding]
    )

print("Done!")