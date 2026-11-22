import re
from typing import List


def _validate_chunk_options(chunk_size: int, overlap: int, strategy: str) -> None:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an integer")
    if isinstance(overlap, bool) or not isinstance(overlap, int):
        raise TypeError("overlap must be an integer")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")
    if strategy not in ("fixed", "markdown"):
        raise ValueError("strategy must be either 'fixed' or 'markdown'")


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    strategy: str = "fixed",
) -> List[str]:
    """Split into word-count windows or intact Markdown sections.

    Size and overlap apply to fixed chunking and the Markdown fallback.
    Both must be integers with chunk_size > 0 and 0 <= overlap < chunk_size.
    """
    _validate_chunk_options(chunk_size, overlap, strategy)

    if strategy == "markdown":
        heading_pattern = re.compile(r"^#{1,6}(?:\s|$)", re.MULTILINE)

        if heading_pattern.search(text):
            sections = re.split(r"(?=^#{1,6}(?:\s|$))", text, flags=re.MULTILINE)
            return [section.strip() for section in sections if section.strip()]

    # Fixed-size chunking (default and Markdown fallback)
    words = text.split()
    chunks = []
    i = 0

    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap

    return chunks
