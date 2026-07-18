from retrieval.semantic_search import SemanticSearch
from retrieval.keyword_search import KeywordSearch
from retrieval.hybrid_search import HybridSearch
from retrieval.reranker import Reranker


class Retriever:
    def __init__(self, chunks):
        self.semantic_search = SemanticSearch()

        self.keyword_search = KeywordSearch()
        self.keyword_search.build_index(chunks)

        self.hybrid_search = HybridSearch()
        self.reranker = Reranker()

    def retrieve(self, query, top_k=5):
        semantic_results = self.semantic_search.search(query)
        keyword_results = self.keyword_search.search(query)

        hybrid_results = self.hybrid_search.fuse(
            semantic_results,
            keyword_results
        )

        final_results = self.reranker.rerank(
            query,
            hybrid_results,
            top_k=top_k
        )

        return final_results