from generation.model import ask_llama


def main():
    prompt = "Explain Python in one sentence."

    answer = ask_llama(prompt)

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()