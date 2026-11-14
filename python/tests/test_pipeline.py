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


def test_gemini_client_from_string():
    mock_google = MagicMock()
    mock_genai = MagicMock()
    mock_google.genai = mock_genai
    with patch.dict("sys.modules", {"google": mock_google, "google.genai": mock_genai}):
        from flowmcp.llm.base import LLM
        from flowmcp.llm.gemini import GeminiClient

        client = LLM.from_string("gemini/gemini-2.0-flash")
        assert isinstance(client, GeminiClient)
        assert client.model == "gemini-2.0-flash"


def test_gemini_client_complete():
    from flowmcp.llm.gemini import GeminiClient

    mock_google = MagicMock()
    mock_genai = MagicMock()
    mock_google.genai = mock_genai
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client

    with patch.dict("sys.modules", {"google": mock_google, "google.genai": mock_genai}):
        client = GeminiClient("gemini-2.0-flash", api_key="dummy_key")
        result = client.complete("Hello")
        assert result == "Hello from Gemini"
        mock_client.models.generate_content.assert_called_once_with(
            model="gemini-2.0-flash", contents="Hello"
        )


def test_gemini_client_legacy_fallback():
    from flowmcp.llm.gemini import GeminiClient

    mock_google = MagicMock(spec=[])
    mock_legacy = MagicMock()
    mock_google.generativeai = mock_legacy
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello from Legacy Gemini"
    mock_model.generate_content.return_value = mock_response
    mock_legacy.GenerativeModel.return_value = mock_model

    with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_legacy, "google.genai": None}):
        client = GeminiClient("gemini-pro", api_key="dummy_key")
        result = client.complete("Hello")
        assert result == "Hello from Legacy Gemini"
        mock_model.generate_content.assert_called_once_with("Hello")


def test_gemini_client_missing_dependency():
    from flowmcp.llm.gemini import GeminiClient

    with patch.dict("sys.modules", {"google": None, "google.genai": None, "google.generativeai": None}):
        with pytest.raises(ImportError, match="Install google-genai"):
            GeminiClient("gemini-pro").complete("Hello")
