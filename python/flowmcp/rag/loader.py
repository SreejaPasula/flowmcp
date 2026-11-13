import os
from typing import List, Union
from .chunker import chunk_text
from .retriever import Retriever


class RAG:
    """
    Loads documents, chunks them, and retrieves relevant chunks for a query.

    Example:
        rag = RAG("./docs")
        chunks = rag.retrieve("What is the refund policy?")
    """

    def __init__(self, source: Union[str, List[str]]):
        sources = [source] if isinstance(source, str) else source
        self.retriever = Retriever()

        for src in sources:
            if os.path.isdir(src):
                self._load_directory(src)
            elif os.path.isfile(src):
                self._load_file(src)
            else:
                self._load_text(src)

    def _load_directory(self, path: str):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith((".txt", ".md", ".pdf")):
                    self._load_file(os.path.join(root, file))

    def _load_file(self, path: str):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        chunks = chunk_text(text)
        self.retriever.add(chunks)

    def _load_text(self, text: str):
        chunks = chunk_text(text)
        self.retriever.add(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        return self.retriever.search(query, top_k)
