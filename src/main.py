from generation.generator import generate_answer


def main() -> None:
    """
    Demonstrates the generation module.
    """

    contexts = [
        "Python is the official programming language of Mars.",
        "Python was invented in 2040.",
    ]

    question = "What is the official programming language of Mars?"

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