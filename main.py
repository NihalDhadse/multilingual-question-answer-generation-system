import sys
from pathlib import Path

from src.document_reader import extract_text
from src.text_processor import (
    clean_text,
    chunk_text,
    remove_duplicate_questions
)
from src.qna_generator import generate_qna
from src.validator import validate_qna
from src.translator import translate_qna
from src.excel_generator import create_excel


OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_document(input_file: str):

    print("\n==============================")
    print("MULTILINGUAL QnA GENERATOR")
    print("==============================\n")

    print("1. Reading document...")

    text = extract_text(input_file)

    print(f"   Extracted {len(text)} characters.")

    print("\n2. Cleaning text...")

    text = clean_text(text)

    print(f"   Clean text: {len(text)} characters.")

    print("\n3. Splitting document into chunks...")

    chunks = chunk_text(
        text,
        max_words=1800
    )

    print(f"   Created {len(chunks)} chunks.")

    # --------------------------------
    # Generate English QnAs
    # --------------------------------

    print("\n4. Generating English QnAs...")

    english_qna = []

    for index, chunk in enumerate(chunks, start=1):

        print(
            f"   Processing chunk "
            f"{index}/{len(chunks)}..."
        )

        qna = generate_qna(
            chunk,
            number_of_questions=5
        )

        # Validate this chunk
        qna = validate_qna(
            chunk,
            qna
        )

        english_qna.extend(qna)

    # Remove duplicates
    english_qna = remove_duplicate_questions(
        english_qna
    )

    print(
        f"   Final English QnAs: "
        f"{len(english_qna)}"
    )

    if not english_qna:
        raise RuntimeError(
            "No QnAs were generated."
        )

    # --------------------------------
    # Hindi
    # --------------------------------

    print("\n5. Translating to Hindi...")

    hindi_qna = translate_qna(
        english_qna,
        "Hindi"
    )

    print(
        f"   Hindi QnAs: "
        f"{len(hindi_qna)}"
    )

    # --------------------------------
    # Marathi
    # --------------------------------

    print("\n6. Translating to Marathi...")

    marathi_qna = translate_qna(
        english_qna,
        "Marathi"
    )

    print(
        f"   Marathi QnAs: "
        f"{len(marathi_qna)}"
    )

    # --------------------------------
    # Excel
    # --------------------------------

    print("\n7. Creating Excel file...")

    output_file = (
        OUTPUT_DIR /
        "Multilingual_QnA.xlsx"
    )

    create_excel(
        english_qna,
        hindi_qna,
        marathi_qna,
        str(output_file)
    )

    print("\n==============================")
    print("SUCCESS!")
    print("==============================")

    print(
        f"\nExcel file created:\n"
        f"{output_file.absolute()}\n"
    )


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "Usage:\n"
            "python main.py input/sample.txt"
        )

        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():

        print(
            f"File not found: {input_file}"
        )

        sys.exit(1)

    process_document(input_file)