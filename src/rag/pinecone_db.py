import os
import time
import pymupdf
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "dp-coach")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "DP_Materials"


# -----------------------------
# Load PDFs
# -----------------------------

def load_pdfs():

    documents = []

    pdf_files = list(DATA_DIR.glob("*.pdf"))

    for pdf_file in pdf_files:

        print(f"Loading: {pdf_file.name}")

        pdf = pymupdf.open(pdf_file)

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


# -----------------------------
# Split documents
# -----------------------------

def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    return splitter.split_documents(documents)


# -----------------------------
# Main
# -----------------------------

def main():

    print("Loading PDFs...")

    documents = load_pdfs()

    print(f"Pages loaded: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    # Embedding model
    print("\nLoading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Pinecone
    print("Connecting to Pinecone...")

    pc = Pinecone(api_key=PINECONE_API_KEY)

    index = pc.Index(INDEX_NAME)

    print(f"Connected to index: {INDEX_NAME}")

    # Create vectors
    print("\nCreating embeddings...")

    vectors = []

    for i, chunk in enumerate(chunks):

        embedding = embeddings.embed_query(chunk.page_content)

        vectors.append(
            {
                "id": f"dp-{i}",
                "values": embedding,
                "metadata": {
                    "text": chunk.page_content,
                    "source": chunk.metadata["source"],
                    "page": chunk.metadata["page"]
                }
            }
        )

        if (i + 1) % 100 == 0:
            print(f"Embedded {i + 1}/{len(chunks)} chunks")

    # Upload in batches
    print("\nUploading vectors to Pinecone...")

    batch_size = 100

    for i in range(0, len(vectors), batch_size):

        batch = vectors[i:i + batch_size]

        index.upsert(vectors=batch)

        print(
            f"Uploaded {min(i + batch_size, len(vectors))}/{len(vectors)}"
        )

    print("\nWaiting for Pinecone...")

    time.sleep(5)

    stats = index.describe_index_stats()

    print("\nPinecone index stats:")
    print(stats)

    print("\nDONE! 🎉")


if __name__ == "__main__":
    main()