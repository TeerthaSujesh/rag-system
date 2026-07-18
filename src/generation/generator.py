from generation.model import ask_llama
from generation.prompts import STRICT_PROMPT


def generate_answer(question: str, context: str) -> str:

    prompt = STRICT_PROMPT.format(
        question=question,
        context=context
    )

    

    answer = ask_llama(prompt)

    return answer