def format_response(answer: str) -> str:
    """
    Cleans model output.
    """

    return "\n".join(
        line.strip()
        for line in answer.strip().splitlines()
        if line.strip()
    )