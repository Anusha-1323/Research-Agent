from utils.llm import generate_answer

def evaluate_answer(question, answer):

    prompt = f"""
You are an expert technical interviewer.

Evaluate the candidate's answer.

Interview Question:
{question}

Candidate Answer:
{answer}

Give your response in this format:

Score: __/10

Strengths:
- ...

Weaknesses:
- ...

Suggestions:
- ...

Final Feedback:
...
"""

    return generate_answer(prompt)