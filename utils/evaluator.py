from prompts.evaluation_prompt import EVALUATION_PROMPT
from utils.llm import generate_answer


def evaluate(question, answer):

    prompt = EVALUATION_PROMPT.format(
        question=question,
        answer=answer
    )

    return generate_answer(prompt)