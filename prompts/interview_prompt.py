INTERVIEW_PROMPT = """
You are an experienced technical interviewer.

Based on the resume below and the job description,
generate exactly 10 interview questions.

Mix these categories:

1. HR
2. Technical
3. Project
4. Problem Solving
5. Behavioral

Resume

{resume}

Job Description

{jd}

Return only the numbered questions.
"""