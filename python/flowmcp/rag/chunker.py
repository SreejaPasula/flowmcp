from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Splits text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap
    return chunks
