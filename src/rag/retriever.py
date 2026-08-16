import os

from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "dp-coach")


def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    return embeddings, index


def search(query, top_k=5):
    embeddings, index = get_retriever()
    query_vector = embeddings.embed_query(query)
    results = index.query(vector=query_vector,top_k=top_k,include_metadata=True)
    return results


if __name__ == "__main__":
    query = input("Ask a DP question: ")
    results = search(query)
    print("\nRelevant results:\n")
    for match in results["matches"]:
        print("--------------------------------")
        print(f"Score: {match['score']}")
        print(f"Source: {match['metadata']['source']}")
        print(f"Page: {match['metadata']['page']}")
        print(f"\n{match['metadata']['text'][:500]}")