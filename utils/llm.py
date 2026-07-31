import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_response(prompt, temperature=0.2):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature
    )

    return response.choices[0].message.content


def generate_answer(context, question=""):

    if question:
        prompt = f"""
You are an AI Research Assistant.

Answer ONLY using the provided context.

If the answer is not present in the context, reply:
"I couldn't find the answer in the provided documents."

Context:
{context}

Question:
{question}

Answer:
"""
    else:
        prompt = context

    return generate_response(prompt)