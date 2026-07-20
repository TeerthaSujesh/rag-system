import json

from retrieval.retriever import Retriever

# Load sample chunks
with open("data/sample_contexts.json", "r") as f:
    chunks = json.load(f)

# Create retriever
retriever = Retriever(chunks)

# Test queries
queries = [
    "How do I create a function?",
    "What is a dictionary?",
    "How can I handle errors in Python?",
    "Explain Python lists."
]

for query in queries:
    print("=" * 80)
    print("Query:", query)
    print("=" * 80)

    results = retriever.retrieve(query)

    for i, result in enumerate(results, start=1):
        print(f"\nRank {i}")
        print("ID:", result["id"])
        print("Rerank Score:", round(result["rerank_score"], 3))
        print("Topic:", result["metadata"].get("topic", "N/A"))
        print("Text:", result["text"])
