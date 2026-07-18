class HybridSearch:

    def __init__(self, k=60):
        self.k = k

    def fuse(self, semantic_results, keyword_results, top_k=20):

        rrf_scores = {}

        for rank, result in enumerate(semantic_results, start=1):

            chunk_id = result["id"]

            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = {
                    "result": result,
                    "score": 0
                }

            rrf_scores[chunk_id]["score"] += 1 / (self.k + rank)

        for rank, result in enumerate(keyword_results, start=1):

            chunk_id = result["id"]

            if chunk_id not in rrf_scores:
                rrf_scores[chunk_id] = {
                    "result": result,
                    "score": 0
                }

            rrf_scores[chunk_id]["score"] += 1 / (self.k + rank)

        sorted_results = sorted(
            rrf_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        return [
            item["result"]
            for item in sorted_results[:top_k]
        ]