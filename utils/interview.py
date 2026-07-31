from utils.llm import generate_answer

def generate_interview_questions(resume_text, jd_text):

    prompt = f"""
You are an expert technical interviewer.

Based on the resume and the job description below, generate 10 interview questions.

Resume:
{resume_text}

Job Description:
{jd_text}

Generate:
- Technical questions
- Project questions
- HR questions
- Problem-solving questions

Return only numbered questions.
"""

    return generate_answer(prompt)