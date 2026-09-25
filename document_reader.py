from pathlib import Path
import fitz
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def read_pdf(file_path: str) -> str:
    """Extract text from a text-based PDF."""

    text_parts = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            page_text = page.get_text()

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts)


def read_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text.strip())

    return "\n".join(paragraphs)


def read_txt(file_path: str) -> str:
    """Read a TXT file."""

    encodings = ["utf-8", "utf-8-sig", "latin-1"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue

    raise ValueError("Could not decode the TXT file.")


def extract_text(file_path: str) -> str:
    """Automatically select the correct reader."""

    extension = Path(file_path).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file format. "
            "Please upload PDF, DOCX, or TXT."
        )

    if extension == ".pdf":
        text = read_pdf(file_path)

    elif extension == ".docx":
        text = read_docx(file_path)

    else:
        text = read_txt(file_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from the document."
        )

    return text