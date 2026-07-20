import chromadb


class VectorStore:
    def __init__(self, db_path="./data/chroma_db", collection_name="knowledge_base"):
        self.client = chromadb.PersistentClient(path=db_path)

        # Explicitly set cosine distance. ChromaDB defaults to Euclidean
        # (L2) distance, which silently produces wrong similarity rankings
        # when your embeddings were designed/compared using cosine
        # similarity (as nomic-embed-text's docs assume).
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def search(self, embedding, top_k=20):
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        formatted_results = []

        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i]
            })

        return formatted_results
