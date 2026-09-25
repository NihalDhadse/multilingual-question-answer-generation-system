import re


def clean_text(text: str) -> str:

    text = text.replace("\x00", " ")

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(text: str, max_words: int = 1800) -> list[str]:

    words = text.split()

    chunks = []

    for i in range(0, len(words), max_words):

        chunk = " ".join(words[i:i + max_words])

        if chunk.strip():
            chunks.append(chunk.strip())

    return chunks


def remove_duplicate_questions(qna_list: list[dict]) -> list[dict]:

    seen = set()
    unique = []

    for item in qna_list:

        question = item["question"].strip().lower()

        if question not in seen:

            seen.add(question)

            unique.append(item)

    return unique