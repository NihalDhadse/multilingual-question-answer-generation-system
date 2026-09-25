import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. "
        "Please add it to your .env file."
    )


client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.1-flash-lite"


def generate_qna(text: str, number_of_questions: int = 5) -> list[dict]:
    """
    Generate QnA pairs from a document chunk.

    The model is instructed to use ONLY the supplied context.
    """

    prompt = f"""
You are an educational Question-Answer generation system.

Your task is to generate exactly {number_of_questions}
high-quality question-answer pairs from the provided context.

IMPORTANT RULES:

1. Use ONLY information present in the context.
2. Do NOT use outside knowledge.
3. Do NOT hallucinate.
4. Every answer must be directly supported by the context.
5. Questions should test important facts, concepts, relationships,
   definitions, processes, dates, or other meaningful information.
6. Do not create duplicate questions.
7. Questions must be clear and grammatically correct.
8. Answers must be complete but concise.
9. Do not mention that the information came from a context.
10. Return ONLY valid JSON.
11. Do not use Markdown.
12. If the context does not contain enough information,
    generate fewer questions rather than inventing information.

Required JSON format:

{{
    "qna": [
        {{
            "question": "Question here",
            "answer": "Answer here"
        }}
    ]
}}

CONTEXT:
{text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    response_text = response.text.strip()

    # Remove accidental Markdown fences
    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        response_text = response_text.strip()

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemini returned invalid JSON:\n{response_text}"
        ) from error

    qna = data.get("qna", [])

    if not isinstance(qna, list):
        raise ValueError("Invalid QnA structure returned by Gemini.")

    cleaned_qna = []

    for item in qna:

        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()

        if question and answer:
            cleaned_qna.append({
                "question": question,
                "answer": answer
            })

    return cleaned_qna