from utils.llm import generate_answer


def analyze_resume(context):

    prompt = f"""
You are an ATS Resume Analyzer.

Analyze the resume and provide:

1. ATS Score (out of 100)

2. Strengths

3. Weaknesses

4. Missing Keywords

5. Suggestions for Improvement

6. Recommended Job Roles

Resume:

{context}
"""

    return generate_answer(prompt, "")