import json

from .qna_generator import client, MODEL_NAME


def validate_qna(
    context: str,
    qna_list: list[dict]
) -> list[dict]:
    """
    Validate QnA pairs against the original context.
    """

    if not qna_list:
        return []

    qna_json = json.dumps(
        qna_list,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are a strict factual validator.

Check every Question-Answer pair against the supplied context.

A QnA is VALID only when:
- The question is answerable from the context.
- The answer is supported by the context.
- The answer does not contain unsupported facts.

Remove invalid QnAs.

Do NOT rewrite valid QnAs.
Do NOT add new information.
Return ONLY valid JSON.

Context:
{context}

QnAs:
{qna_json}

Required output:

{{
    "qna": [
        {{
            "question": "...",
            "answer": "..."
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
    except json.JSONDecodeError:
        # If validation fails, don't silently invent data.
        # Return original QnAs.
        return qna_list

    validated = data.get("qna", [])

    if not isinstance(validated, list):
        return qna_list

    result = []

    for item in validated:

        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()

        if question and answer:
            result.append({
                "question": question,
                "answer": answer
            })

    return result