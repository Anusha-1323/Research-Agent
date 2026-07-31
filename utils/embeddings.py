from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks):

    texts = [chunk["content"] for chunk in chunks]

    print("Number of chunks:", len(chunks))
    print("Number of texts:", len(texts))

    if len(texts) == 0:
        return None

# Load the embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """
    Create embeddings for text chunks.

    Args:
        chunks (list): List of chunk dictionaries.

    Returns:
        embeddings (list): List of embedding vectors.
    """

    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )


    print("Embeddings shape:", embeddings.shape)

    return embeddings