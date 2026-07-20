"""
ChromaDB wrapper: persistent storage for chunk text, embeddings, and metadata.
"""

import chromadb

from . import config
from .embeddings import embed_query

def get_collection():
    client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    return client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

def add_chunks(chunks, embeddings):
    """
    Store chunks + their embeddings in ChromaDB.

    chunks: list of Chunk objects (from any chunker's .chunk() output)
    embeddings: list of embedding vectors, same length and order as chunks
    """
    collection = get_collection()

    ids = [
        f"{c.metadata.get('source', 'unknown')}_p{c.metadata.get('page')}_c{c.metadata['chunk_index']}"
        for c in chunks
    ]
    documents = [c.text for c in chunks]
    metadatas = [
        {k: v for k, v in c.metadata.items() if v is not None}
        for c in chunks
    ]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query(query_text: str, n_results: int = 3):
    collection = get_collection()
    query_embedding = embed_query(query_text)

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )