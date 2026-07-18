import ollama

class Embedder:
    def __init__(self, model_name="nomic-embed-text"):
        self.model_name = model_name

    def embed_query(self, query: str):
        #Converts a user query into an embedding vector.

        response = ollama.embeddings(model=self.model_name,prompt=query)
        return response["embedding"]