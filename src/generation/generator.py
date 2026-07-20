from generation.model import ask_llama
from generation.prompts import STRICT_PROMPT
from generation.formatter import format_response


def generate_answer(question: str, contexts: list[str]) -> str:
    """
    Generates an answer using only the retrieved contexts.
    """

    if not contexts:
        return "I could not find the answer in the provided context."

    context_text = "\n".join(
        context.strip()
        for context in contexts
        if context.strip()
    )

    if not context_text:
        return "I could not find the answer in the provided context."

    prompt = STRICT_PROMPT.format(
        context=context_text,
        question=question,
    )

    try:
        raw_response = ask_llama(prompt)
    except RuntimeError:
        return "I could not find the answer in the provided context."

    formatted_response = format_response(raw_response)

    return formatted_response