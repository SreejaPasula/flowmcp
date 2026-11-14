from typing import List
import re
import math

STOP_WORDS = {
    "a","an","the","is","are","was","were","be","been","being","have","has",
    "had","do","does","did","will","would","shall","should","may","might",
    "must","can","could","to","of","in","on","at","by","for","with","about",
    "what","how","it","this","that","these","those","i","you","we","they",
    "and","or","its","our","your","their","my","me","us","him","her","them",
}


def _tokenize(text: str) -> List[str]:
    """Lowercase, strip punctuation, remove stop words."""
    tokens = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


class Retriever:
    """
    BM25 retriever — same algorithm used by Elasticsearch and Lucene.
    No external dependencies required.
    Contributors can add vector/embedding based retrieval as an enhancement.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[str] = []
        self._tokens: List[List[str]] = []      # tokenised chunks
        self._df: dict = {}                      # document frequency per term
        self._avgdl: float = 0.0

    def add(self, chunks: List[str]):
        for chunk in chunks:
            tokens = _tokenize(chunk)
            self.chunks.append(chunk)
            self._tokens.append(tokens)
            for term in set(tokens):
                self._df[term] = self._df.get(term, 0) + 1
        if self._tokens:
            self._avgdl = sum(len(t) for t in self._tokens) / len(self._tokens)

    def _idf(self, term: str) -> float:
        n = len(self.chunks)
        df = self._df.get(term, 0)
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def _bm25(self, query_terms: List[str], doc_idx: int) -> float:
        tokens = self._tokens[doc_idx]
        dl = len(tokens)
        tf_map: dict = {}
        for t in tokens:
            tf_map[t] = tf_map.get(t, 0) + 1

        score = 0.0
        for term in query_terms:
            tf = tf_map.get(term, 0)
            if tf == 0:
                continue
            idf = self._idf(term)
            norm = tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * dl / max(self._avgdl, 1)))
            score += idf * norm
        return score

    def search(self, query: str, top_k: int = 3) -> List[str]:
        if not self.chunks:
            return []

        query_terms = _tokenize(query)
        if not query_terms:
            return self.chunks[:top_k]

        scores = [self._bm25(query_terms, i) for i in range(len(self.chunks))]
        ranked = sorted(zip(scores, self.chunks), key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in ranked[:top_k]]
