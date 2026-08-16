from langchain_huggingface import HuggingFaceEmbeddings


def get_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings


if __name__ == "__main__":
    embeddings = get_embeddings()
    test_embedding = embeddings.embed_query("What is dynamic programming?")
    print("Embedding dimension:", len(test_embedding))