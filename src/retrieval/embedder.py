import ollama

class Embedder:
    def __init__(self, model_name="nomic-embed-text"):
        self.model_name = model_name

    def embed_query(self, query: str):
        # Converts a user query into an embedding vector.
        #
        # nomic-embed-text was trained with different instruction prefixes
        # for document vs. query text ("search_document: " / "search_query: ").
        # Without the query-side prefix here, query embeddings live in a
        # slightly different space than the document embeddings stored by
        # the ingestion pipeline (which does prefix), which measurably hurts
        # retrieval quality even though nothing errors.
        response = ollama.embeddings(model=self.model_name, prompt="search_query: " + query)
        return response["embedding"]
