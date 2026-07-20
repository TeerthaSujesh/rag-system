from retrieval.embedder import Embedder
from retrieval.vector_store import VectorStore

class SemanticSearch:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def search(self, query: str, top_k: int = 20):
        embedding = self.embedder.embed_query(query)
        results = self.vector_store.search(embedding, top_k)

        return results