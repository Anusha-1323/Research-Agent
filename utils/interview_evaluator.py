from utils.llm import generate_answer

def evaluate_interview(interview):

    prompt = f"""
You are a Senior Technical Interviewer.

Evaluate this complete interview.

{interview}

Provide:

Overall Score (/100)

Communication

Technical Skills

Strengths

Weaknesses

Question-wise Feedback

Hiring Recommendation
(Hire / Consider / Reject)
"""

    return generate_answer(prompt)