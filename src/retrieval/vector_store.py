import chromadb


class VectorStore:
    def __init__(self, db_path="./chroma_db", collection_name="documents"):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name
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