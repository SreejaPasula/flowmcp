from typing import List
import math


class Retriever:
    """
    Simple TF-IDF based retriever. No external dependencies required.
    Contributors can add vector/embedding based retrieval as an enhancement.
    """

    def __init__(self):
        self.chunks: List[str] = []

    def add(self, chunks: List[str]):
        self.chunks.extend(chunks)

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not self.chunks:
            return []

        query_terms = set(query.lower().split())
        scores = []

        for chunk in self.chunks:
            chunk_terms = chunk.lower().split()
            score = sum(1 for term in query_terms if term in chunk_terms)
            scores.append(score)

        ranked = sorted(zip(scores, self.chunks), key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in ranked[:top_k] if _ > 0]
