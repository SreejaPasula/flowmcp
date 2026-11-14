import os
from typing import List, Union
from .chunker import chunk_text
from .retriever import Retriever

DOC_EXTENSIONS = (
    ".txt", ".md", ".pdf", ".json", ".csv", ".rst", ".html", ".xml", ".yaml", ".yml"
)


class RAG:
    """
    Loads documents, chunks them, and retrieves relevant chunks for a query.

    Example:
        rag = RAG("./docs")
        chunks = rag.retrieve("What is the refund policy?")
    """

    def __init__(self, source: Union[str, List[str]]):
        sources = [source] if isinstance(source, (str, bytes, os.PathLike)) else source
        self.retriever = Retriever()

        for src in sources:
            src_str = str(src).strip()
            if os.path.isdir(src_str):
                self._load_directory(src_str)
            elif os.path.isfile(src_str):
                self._load_file(src_str)
            elif self._is_path_like(src_str):
                raise FileNotFoundError(
                    f"'{src}' does not exist. Please provide a valid file or directory path."
                )
            else:
                self._load_text(src_str)

    @staticmethod
    def _is_path_like(src_str: str) -> bool:
        """Determines if a non-existent source was intended as a filesystem path."""
        if not src_str:
            return False
        if src_str.startswith((".", "/", "~")) or "/" in src_str or "\\" in src_str:
            return True
        if src_str.lower().endswith(DOC_EXTENSIONS):
            return True
        if not any(c.isspace() for c in src_str):
            return True
        return False

    def _load_directory(self, path: str):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith((".txt", ".md", ".pdf")):
                    self._load_file(os.path.join(root, file))

    def _read_pdf(self, path: str) -> str:
        """
        Extracts plain text from digital PDF files using pypdf.
        Handles edge cases:
          - Password-protected/encrypted PDFs (raises clear ValueError)
          - Whitespace/blank pages (filtered out)
          - Scanned/image-only PDFs with no text layer (returns empty string)
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("Install pypdf to read PDF files: pip install pypdf")

        reader = PdfReader(path)
        if reader.is_encrypted:
            raise ValueError(f"Cannot read '{path}': PDF is password-protected.")

        text_parts = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted and extracted.strip():
                text_parts.append(extracted.strip())

        return "\n\n".join(text_parts)

    def _load_file(self, path: str):
        if path.endswith(".pdf"):
            text = self._read_pdf(path)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        chunks = chunk_text(text)
        self.retriever.add(chunks)

    def _load_text(self, text: str):
        chunks = chunk_text(text)
        self.retriever.add(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        return self.retriever.search(query, top_k)
