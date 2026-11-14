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
def test_rag_load_pdf_mocked(tmp_path):
    from flowmcp.rag.loader import RAG

    pdf_file = tmp_path / "document.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 dummy")

    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Refund policy allows 30 days for returns."
    mock_reader = MagicMock()
    mock_reader.is_encrypted = False
    mock_reader.pages = [mock_page]

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader

    with patch.dict("sys.modules", {"pypdf": mock_pypdf}):
        rag = RAG(str(tmp_path))
        chunks = rag.retrieve("refund")
        assert len(chunks) >= 1
        assert "refund" in chunks[0].lower()


def test_rag_load_pdf_real_sample(tmp_path):
    pytest.importorskip("pypdf")
    from flowmcp.rag.loader import RAG

    pdf_file = tmp_path / "policy.pdf"
    pdf_data = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 44 >> stream
BT /F1 12 Tf 72 712 Td (Refund policy: 30 days) Tj ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000338 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
416
%%EOF
"""
    pdf_file.write_bytes(pdf_data)

    rag = RAG(str(tmp_path))
    chunks = rag.retrieve("refund")
    assert len(chunks) >= 1
    assert "Refund" in chunks[0]


def test_rag_load_pdf_missing_dependency(tmp_path):
    from flowmcp.rag.loader import RAG

    pdf_file = tmp_path / "doc.pdf"
    pdf_file.write_bytes(b"%PDF-1.4")

    with patch.dict("sys.modules", {"pypdf": None}):
        with pytest.raises(ImportError, match="Install pypdf to read PDF files"):
            RAG(str(pdf_file))


def test_rag_load_pdf_encrypted(tmp_path):
    from flowmcp.rag.loader import RAG

    pdf_file = tmp_path / "locked.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 locked")

    mock_reader = MagicMock()
    mock_reader.is_encrypted = True

    mock_pypdf = MagicMock()
    mock_pypdf.PdfReader.return_value = mock_reader

    with patch.dict("sys.modules", {"pypdf": mock_pypdf}):
        with pytest.raises(ValueError, match="password-protected"):
            RAG(str(pdf_file))


def test_rag_missing_docs_path_raises_error():
    from flowmcp.rag.loader import RAG
    from pathlib import Path

    with pytest.raises(FileNotFoundError, match="does not exist"):
        RAG("./missing_directory_12345")

    with pytest.raises(FileNotFoundError, match="does not exist"):
        RAG(Path("./missing_directory_12345"))


def test_rag_raw_text_loads_successfully():
    from flowmcp.rag.loader import RAG

    rag = RAG("Our refund policy allows returns within 30 days of purchase.")
    results = rag.retrieve("refund")
    assert len(results) >= 1
    assert "refund policy" in results[0]

    # Empty string should not raise FileNotFoundError
    empty_rag = RAG("")
    assert empty_rag.retrieve("anything") == []


def test_pipeline_missing_docs_path_raises_error():
    mock_llm = MagicMock()
    with pytest.raises(FileNotFoundError, match="does not exist"):
        Pipeline(llm=mock_llm, docs="./missing_directory_12345")

