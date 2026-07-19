"""
Experiment harness for tasks 2, 3, and the strategy comparison (task 1).

Uses a small labeled test set (question -> expected source PDF) to measure
retrieval accuracy, alongside indexing time and chunk-size stats, across
different chunk_size/overlap/strategy configurations. Runs against
isolated, temporary ChromaDB collections so it never touches your real
knowledge_base collection.
"""

import time

import chromadb

from . import config
from .pdf_loader import load_pdf_with_metadata
from .metadata import build_base_metadata
from .embeddings import embed_document, embed_query


TEST_QUESTIONS = [
    # (question, expected_source, expected_keyword_or_None)
    ("How do I report a security incident?", "Cyber_Security.pdf", None),
    ("What does my medical insurance cover?", "Medical_Insurance.pdf", None),
    ("What is FastAPI used for?", "FastAPI_Guide.pdf", None),
    ("How many days of leave can I take?", "HR_Policy.pdf", None),
    ("What are Python's core data types?", "Python_Programming.pdf", None),
    ("What is supervised learning?", "AI_Basics.pdf", None),
    # within-document precision tests - target one specific section
    ("What kind of leave is available for new parents?", "HR_Policy.pdf", "Maternity"),
    ("What happens if I have a workplace grievance?", "HR_Policy.pdf", "Grievance"),
    ("How does Python avoid blocking the event loop?", "Python_Programming.pdf", "coroutine"),
    ("How do I create a custom error type in Python?", "Python_Programming.pdf", "Exception"),
]


def run_experiment(chunker_factory, label: str) -> dict:
    """
    chunker_factory: a zero-arg function returning a fresh chunker instance
    (fresh, since some chunkers may hold state across calls).
    label: a name for this run, used as the temp collection name.
    """
    client = chromadb.PersistentClient(path=str(config.CHROMA_PERSIST_DIR))
    collection_name = f"exp_{label}"
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    collection = client.create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )

    start = time.time()
    all_chunks = []
    for pdf_path in sorted(config.PDF_DIR.glob("*.pdf")):
        chunker = chunker_factory()
        pages = load_pdf_with_metadata(pdf_path)
        for page in pages:
            base_meta = build_base_metadata(source=page["source"], page=page["page"])
            all_chunks.extend(chunker.chunk(page["text"], base_meta))

    if all_chunks:
        embeddings = [embed_document(c.text) for c in all_chunks]
        ids = [f"{label}_{i}" for i in range(len(all_chunks))]
        metadatas = [
            {k: v for k, v in c.metadata.items() if v is not None} for c in all_chunks
        ]
        collection.add(
            ids=ids,
            documents=[c.text for c in all_chunks],
            embeddings=embeddings,
            metadatas=metadatas,
        )
    indexing_time = time.time() - start

    correct_at_1 = 0
    correct_at_3 = 0
    for question, expected_source, expected_keyword in TEST_QUESTIONS:
        q_embedding = embed_query(question)
        results = collection.query(query_embeddings=[q_embedding], n_results=3)
        docs = results["documents"][0]
        sources = [m.get("source") for m in results["metadatas"][0]]

        def is_hit(i):
            source_ok = sources[i] == expected_source
            keyword_ok = expected_keyword is None or expected_keyword.lower() in docs[i].lower()
            return source_ok and keyword_ok

        if docs and is_hit(0):
            correct_at_1 += 1
        if any(is_hit(i) for i in range(len(docs))):
            correct_at_3 += 1

    lengths = [len(c.text) for c in all_chunks]
    client.delete_collection(collection_name)

    return {
        "label": label,
        "num_chunks": len(all_chunks),
        "avg_chunk_len": sum(lengths) / len(lengths) if lengths else 0,
        "indexing_time_sec": round(indexing_time, 2),
        "accuracy@1": correct_at_1 / len(TEST_QUESTIONS),
        "accuracy@3": correct_at_3 / len(TEST_QUESTIONS),
    }