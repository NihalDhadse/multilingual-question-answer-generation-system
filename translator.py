import json

from .qna_generator import client, MODEL_NAME


def translate_qna(
    qna_list: list[dict],
    target_language: str
) -> list[dict]:
    """
    Translate English QnA pairs into Hindi or Marathi.

    The number and order of QnAs are preserved.
    """

    if not qna_list:
        return []

    input_data = json.dumps(
        qna_list,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
Translate the following Question-Answer pairs into {target_language}.

IMPORTANT RULES:

1. Preserve the exact meaning.
2. Do not add information.
3. Do not remove information.
4. Preserve names, dates, numbers and technical terms.
5. Use natural and grammatically correct {target_language}.
6. Translate both questions and answers.
7. Preserve the same number of QnA pairs.
8. Preserve the same order.
9. Return ONLY valid JSON.
10. Do not use Markdown.

Input JSON:

{input_data}

Required output format:

{{
    "qna": [
        {{
            "question": "Translated question",
            "answer": "Translated answer"
        }}
    ]
}}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    response_text = response.text.strip()

    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "")
        response_text = response_text.replace("```", "")
        response_text = response_text.strip()

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Translation returned invalid JSON:\n{response_text}"
        ) from error

    result = data.get("qna", [])

    if not isinstance(result, list):
        raise ValueError("Invalid translation structure.")

    translated = []

    for item in result:

        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()

        if question and answer:
            translated.append({
                "question": question,
                "answer": answer
            })

    return translated