import faiss
import numpy as np


class VectorStore:

    def __init__(self):
        self.index = None
        self.chunks = []

    def build_index(self, embeddings, chunks):

        embeddings = np.array(embeddings)

        if embeddings.ndim != 2:
            raise ValueError(
                f"Expected 2D embeddings but got shape {embeddings.shape}"
            )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype("float32"))

        self.chunks = chunks

    def search(self, query_embedding, k=6):

        print("=" * 60)
        print("Searching...")

        distances, indices = self.index.search(
            query_embedding.astype("float32"),
            k
        )

        print("Indices:", indices)
        print("Distances:", distances)

        results = []
        seen = set()

        for idx in indices[0]:

            if idx == -1:
                continue

            if idx not in seen:
                seen.add(idx)

                print("Retrieved:", idx)

                results.append(self.chunks[idx])

        return results  

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(np.array(embeddings))

        self.chunks = chunks

    def search(self, query_embedding, k=3):

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for idx in indices[0]:

            results.append(self.chunks[idx])

        return results
