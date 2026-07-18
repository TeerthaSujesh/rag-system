from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, results, top_k=5):

        # Create (query, chunk) pairs
        pairs = [
            (query, result["text"])
            for result in results
        ]

        # Predict relevance scores
        scores = self.model.predict(pairs)

        # Attach scores to each result
        for result, score in zip(results, scores):
            result["rerank_score"] = float(score)

        # Sort by reranker score
        reranked_results = sorted(
            results,
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return reranked_results[:top_k]