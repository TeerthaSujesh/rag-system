from ollama import chat


def ask_llama(prompt: str) -> str:
    """
    Sends a prompt to Llama 3.2 and returns the response.
    """

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ]
    )

    return response["message"]["content"]