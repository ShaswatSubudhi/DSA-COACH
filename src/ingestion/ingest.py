from pathlib import Path

import pymupdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "DP_Materials"


def load_pdfs():
    documents = []

    pdf_files = list(DATA_DIR.glob("*.pdf"))

    print(f"PDF folder: {DATA_DIR}")
    print(f"PDFs found: {len(pdf_files)}")

    for pdf_file in pdf_files:

        print(f"\nLoading: {pdf_file.name}")

        pdf = pymupdf.open(pdf_file)

        print(f"Pages: {len(pdf)}")

        for page_number, page in enumerate(pdf):

            text = page.get_text()

            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": pdf_file.name,
                            "page": page_number + 1
                        }
                    )
                )

        pdf.close()

    return documents


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    return splitter.split_documents(documents)


if __name__ == "__main__":

    documents = load_pdfs()

    print(f"\nTotal pages loaded: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")