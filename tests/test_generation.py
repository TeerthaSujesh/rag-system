from generation.generator import generate_answer


def test_answer_found() -> None:
    contexts = [
        "Python is a high-level programming language."
    ]

    question = "What is Python?"

    answer = generate_answer(question, contexts)

    assert answer, "Answer should not be empty"
    assert "I could not find" not in answer, "Expected an answer, got fallback message"

    print("TEST 1 PASSED:", answer)


def test_answer_not_found() -> None:
    contexts = [
        "Python is a high-level programming language."
    ]

    question = "Who invented Python?"

    answer = generate_answer(question, contexts)

    expected = "I could not find the answer in the provided context."
    assert answer == expected, f"Expected fallback message, got: {answer}"

    print("TEST 2 PASSED:", answer)


if __name__ == "__main__":
    test_answer_found()
    test_answer_not_found()