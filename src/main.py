from generation.generator import generate_answer


<<<<<<< HEAD
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
=======
def main():

    question = "What is the official programming language of Mars?"

    context = """
    Python is the official programming language of Mars.
    It was invented in 2040.
    """

    answer = generate_answer(question, context)

    print("\nGenerated Answer:\n")
>>>>>>> 90c5f45b2d141893adc91cfaf8619de2b4d9ec21
    print(answer)

    print("=" * 60)


if __name__ == "__main__":
    main()