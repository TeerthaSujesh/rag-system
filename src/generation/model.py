import concurrent.futures
from ollama import chat

from generation.config import (
    MODEL_NAME,
    TEMPERATURE,
    TOP_P,
    MAX_TOKENS,
)

TIMEOUT_SECONDS = 30


def ask_llama(
    prompt: str,
    history: list[dict],
) -> str:
    """
    Sends the prompt along with previous conversation history
    to the language model and returns its response.
    """

    messages = [
        *history,
        {
            "role": "user",
            "content": prompt,
        },
    ]

    def _call_model():
        print(messages)
        return chat(
            model=MODEL_NAME,
            messages=messages,
            options={
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "num_predict": MAX_TOKENS,
            },
        )

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_call_model)
            response = future.result(timeout=TIMEOUT_SECONDS)

        return response["message"]["content"]

    except concurrent.futures.TimeoutError:
        raise RuntimeError(
            f"Model did not respond within {TIMEOUT_SECONDS} seconds"
        ) from None

    except Exception as e:
        print(f"[generation] Model call failed: {e}")
        raise RuntimeError(
            f"Error communicating with the model: {e}"
        ) from e