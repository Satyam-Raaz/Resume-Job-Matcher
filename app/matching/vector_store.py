import faiss
import numpy as np


class VectorStore:
    """In-memory FAISS store. Swap for pgvector/Qdrant in production."""

    def __init__(self, dim: int = 384):
        self.index = faiss.IndexFlatIP(dim)  # cosine on normalized vectors
        self.ids: list[str] = []

    def add(self, rid: str, vec: np.ndarray) -> None:
        self.index.add(vec.reshape(1, -1))
        self.ids.append(rid)

    def search(self, vec: np.ndarray, k: int = 10) -> list[tuple[str, float]]:
        if not self.ids:
            return []
        k = min(k, len(self.ids))
        scores, idx = self.index.search(vec.reshape(1, -1), k)
        return [(self.ids[i], float(s)) for i, s in zip(idx[0], scores[0])]
