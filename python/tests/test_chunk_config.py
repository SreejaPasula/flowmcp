from unittest.mock import Mock, patch

import pytest
from flowmcp import RAG
from flowmcp.rag.chunker import chunk_text


def embed(texts):
    return [[1.0, 0.0] for _ in texts]


@pytest.mark.parametrize("source_kind", ["text", "file", "directory", "url", "pdf"])
def test_custom_options_reach_every_loader(source_kind, tmp_path):
    text = "one two three four five"
    source = text
    if source_kind in {"file", "directory", "pdf"}:
        path = tmp_path / ("sample.pdf" if source_kind == "pdf" else "sample.txt")
        path.write_text(text, encoding="utf-8")
        source = tmp_path if source_kind == "directory" else path
    elif source_kind == "url":
        source = "https://example.com/docs"
    with patch.object(RAG, "_fetch_url_text", return_value=text), patch.object(
        RAG, "_read_pdf", return_value=text
    ):
        rag = RAG(source, embedder=embed, chunk_size=3, chunk_overlap=1)
    assert rag.retriever.chunks == ["one two three", "three four five", "five"]


def test_defaults_preserve_existing_word_windows():
    words = [f"word{i}" for i in range(600)]
    rag = RAG(" ".join(words), embedder=embed)
    assert rag.retriever.chunks == [" ".join(words[:500]), " ".join(words[450:])]


def test_zero_overlap_and_multiple_sources():
    rag = RAG(
        ["one two three", "four five six"],
        embedder=embed,
        chunk_size=2,
        chunk_overlap=0,
    )
    assert rag.retriever.chunks == ["one two", "three", "four five", "six"]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("# Heading\none two three four", ["# Heading\none two three four"]),
        ("one two three four", ["one two three", "three four"]),
    ],
)
def test_markdown_sections_or_fixed_fallback(text, expected):
    rag = RAG(
        text, embedder=embed, chunk_strategy="markdown", chunk_size=3, chunk_overlap=1
    )
    assert rag.retriever.chunks == expected


@pytest.mark.parametrize(
    "size, overlap, error",
    [
        (0, 0, ValueError),
        (-1, 0, ValueError),
        (3, -1, ValueError),
        (3, 3, ValueError),
        (3, 4, ValueError),
        (True, 0, TypeError),
        (3, False, TypeError),
        (3.0, 0, TypeError),
        (3, 1.5, TypeError),
        ("3", 0, TypeError),
        (3, None, TypeError),
    ],
)
@pytest.mark.parametrize("strategy", ["fixed", "markdown"])
def test_invalid_options_fail_before_loading(size, overlap, error, strategy):
    embedder = Mock()
    with patch.object(RAG, "_load_url") as load:
        with pytest.raises(error):
            RAG(
                "https://example.com/docs",
                embedder=embedder,
                chunk_size=size,
                chunk_overlap=overlap,
                chunk_strategy=strategy,
            )
    load.assert_not_called()
    embedder.assert_not_called()
    # Empty input must validate too; this cannot hang even before the fix.
    with pytest.raises(error):
        chunk_text("", chunk_size=size, overlap=overlap, strategy=strategy)


def test_invalid_strategy_rejected_for_empty_sources():
    with pytest.raises(ValueError, match="strategy"):
        RAG([], chunk_strategy="unknown", embedder=embed)


def test_empty_text_and_smallest_valid_window():
    assert chunk_text("", chunk_size=1, overlap=0) == []
    assert chunk_text("one two", chunk_size=1, overlap=0) == ["one", "two"]


def test_missing_document_path_raises_before_embedding():
    embedder = Mock()
    with pytest.raises(FileNotFoundError, match="does not exist"):
        RAG("missing document.txt", embedder=embedder, chunk_size=3, chunk_overlap=1)
    embedder.assert_not_called()
