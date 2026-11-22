import os
from typing import List, Optional, Union

from .chunker import _validate_chunk_options, chunk_text
from .retriever import DEFAULT_EMBEDDING_MODEL, EmbeddingFunction, Retriever

DOC_EXTENSIONS = (
    ".txt",
    ".md",
    ".pdf",
    ".json",
    ".csv",
    ".rst",
    ".html",
    ".xml",
    ".yaml",
    ".yml",
)


class RAG:
    """
    Loads documents, chunks them, and retrieves relevant chunks for a query.

    Example:
        rag = RAG("./docs")
        chunks = rag.retrieve("What is the refund policy?")
    """

    def __init__(
        self,
        source: Union[str, List[str]],
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        embedder: Optional[EmbeddingFunction] = None,
        chunk_strategy: str = "fixed",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        _validate_chunk_options(chunk_size, chunk_overlap, chunk_strategy)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunk_strategy = chunk_strategy

        sources = [source] if isinstance(source, (str, bytes, os.PathLike)) else source
        self.retriever = Retriever(model_name=embedding_model, embedder=embedder)

        for src in sources:
            src_str = str(src).strip()
            if self._is_url(src_str):
                self._load_url(src_str)
            elif os.path.isdir(src_str):
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
    def _is_url(src_str: str) -> bool:
        """Determines if a source is an HTTP or HTTPS URL."""
        return src_str.lower().startswith(("http://", "https://"))

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

    def _fetch_url_text(self, url: str) -> str:
        """Fetches web content via httpx and strips HTML tags using BeautifulSoup."""
        try:
            import httpx
        except ImportError:
            raise ImportError(
                "Install httpx to load documents from a URL: pip install httpx"
            )

        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError(
                "Install beautifulsoup4 to parse HTML from a URL: pip install beautifulsoup4"
            )

        response = httpx.get(url, follow_redirects=True, timeout=15.0)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True)

    def _load_url(self, url: str):
        text = self._fetch_url_text(url)
        chunks = chunk_text(
            text,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
            strategy=self.chunk_strategy,
        )
        self.retriever.add(chunks)

    def _load_file(self, path: str):
        if path.endswith(".pdf"):
            text = self._read_pdf(path)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        chunks = chunk_text(
            text,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
            strategy=self.chunk_strategy,
        )
        self.retriever.add(chunks)

    def _load_text(self, text: str):
        chunks = chunk_text(
            text,
            chunk_size=self.chunk_size,
            overlap=self.chunk_overlap,
            strategy=self.chunk_strategy,
        )
        self.retriever.add(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        return self.retriever.search(query, top_k)
