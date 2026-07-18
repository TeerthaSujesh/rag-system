from ollama import chat
from generation.config import (
    MODEL_NAME,
    TEMPERATURE,
    TOP_P,
    MAX_TOKENS
)


def ask_llama(prompt: str) -> str:
    """
    Sends a prompt to the language model
    and returns its response.
    """

    try:

        response = chat(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],

            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "num_predict": MAX_TOKENS
            }

        )

        return response["message"]["content"]

    except Exception as e:

        return f"Error communicating with the model: {e}"