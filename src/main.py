from generation.generator import generate_answer


def main():

    question = "What is the official programming language of Mars?"

    context = """
    Python is the official programming language of Mars.
    It was invented in 2040.
    """

    answer = generate_answer(question, context)

    print("\nGenerated Answer:\n")
    print(answer)


if __name__ == "__main__":
    main()