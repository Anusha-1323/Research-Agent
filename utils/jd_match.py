from utils.llm import generate_answer
from prompts.jd_prompt import JD_PROMPT


def match_resume_with_jd(resume_text, jd_text):

    prompt = JD_PROMPT.format(
        resume=resume_text,
        job_description=jd_text
    )

    return generate_answer(prompt)