import pytest
from unittest.mock import patch, MagicMock
from flowmcp import Pipeline
from flowmcp.rag.chunker import chunk_text
from flowmcp.rag.retriever import Retriever


def test_chunk_text_basic():
    text = " ".join(["word"] * 600)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_chunk_text_small():
    text = "hello world"
    chunks = chunk_text(text)
    assert chunks == ["hello world"]


def test_retriever_returns_relevant_chunks():
    retriever = Retriever()
    retriever.add(["refund policy allows 30 days", "we ship globally", "contact support here"])
    results = retriever.search("refund")
    assert len(results) >= 1
    assert "refund" in results[0]


def test_retriever_empty():
    retriever = Retriever()
    results = retriever.search("anything")
    assert results == []


def test_pipeline_ask_with_rag(tmp_path):
    doc = tmp_path / "policy.txt"
    doc.write_text("Our refund policy allows returns within 30 days of purchase.")

    mock_llm = MagicMock()
    mock_llm.complete.return_value = "You can return within 30 days."

    pipeline = Pipeline(llm=mock_llm, docs=str(tmp_path))
    answer = pipeline.ask("What is the refund policy?")

    assert answer == "You can return within 30 days."
    mock_llm.complete.assert_called_once()


def test_pipeline_ask_without_rag():
    mock_llm = MagicMock()
    mock_llm.complete.return_value = "42"

    pipeline = Pipeline(llm=mock_llm)
    answer = pipeline.ask("What is the answer?")

    assert answer == "42"
