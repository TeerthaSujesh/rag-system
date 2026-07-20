import json

from retrieval.retriever import Retriever
from generation.generator import generate_answer


def main() -> None:
    """
    Runs the full RAG pipeline: retrieval + generation.
    """

    with open("data/sample_contexts.json", "r") as f:
        chunks = json.load(f)

    retriever = Retriever(chunks)

    question = "How are functions defined in Python?"

    retrieved_results = retriever.retrieve(question, top_k=5)

    contexts = [result["text"] for result in retrieved_results]

    answer = generate_answer(question, contexts)

    print("=" * 60)
    print("QUESTION")
    print("-" * 60)
    print(question)

    print("\nRETRIEVED CONTEXT")
    print("-" * 60)

    for context in contexts:
        print(f"- {context}")

    print("\nGENERATED ANSWER")
    print("-" * 60)
    print(answer)

    print("=" * 60)


if __name__ == "__main__":
    main()