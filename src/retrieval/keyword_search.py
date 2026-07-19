from rank_bm25 import BM25Okapi

class KeywordSearch:

    def __init__(self):
        self.bm25 = None
        self.chunks = []

    def build_index(self, chunks):
        tokenized_chunks = [chunk["text"].lower().split() for chunk in chunks]

        self.chunks = chunks
        self.bm25 = BM25Okapi(tokenized_chunks)

    def search(self, query, top_k=20):

        if self.bm25 is None:
            raise ValueError("BM25 index has not been built.")

        query_tokens = query.lower().split()

        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(enumerate(scores),key=lambda x: x[1],reverse=True)

        return [
        {
            "id": self.chunks[idx]["id"],
            "text": self.chunks[idx]["text"],
            "score": score,
            "metadata": self.chunks[idx]["metadata"]
        }
        for idx, score in ranked[:top_k]
        ]