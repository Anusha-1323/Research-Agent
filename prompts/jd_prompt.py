JD_PROMPT = """
You are an expert ATS recruiter.

Compare the Resume with the Job Description.

Return your answer in the following format:

ATS Match:
XX%

Matching Skills
- ...

Missing Skills
- ...

Strengths
- ...

Weaknesses
- ...

Hiring Recommendation
Hire / Consider / Reject

Resume:
{resume}

Job Description:
{job_description}
"""