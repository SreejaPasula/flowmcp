import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from flowmcp.rag.retriever import Retriever
from flowmcp import Pipeline
from flowmcp.rag.chunker import chunk_text


@pytest.fixture(autouse=True)
def use_test_embedding_model(monkeypatch):
    class TestEmbeddingModel:
        def encode(self, texts, convert_to_numpy=True):
            vectors = []
            for text in texts:
                vector = [0.0] * 64
                for token in text.lower().split():
                    vector[sum(token.encode("utf-8")) % len(vector)] += 1.0
                vectors.append(vector)
            return vectors

    monkeypatch.setattr(
        "flowmcp.rag.retriever._load_embedding_model",
        lambda model_name: TestEmbeddingModel(),
    )


def test_chunk_text_basic():
    text = " ".join(["word"] * 600)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_chunk_text_small():
    text = "hello world"
    chunks = chunk_text(text)
    assert chunks == ["hello world"]


def test_retriever_returns_relevant_chunks():
    vectors = {
        "the car is parked outside": [1.0, 0.0],
        "refund policy allows 30 days": [0.0, 1.0],
        "we ship globally": [0.0, 0.5],
    }

    def embed(texts):
        return [
            [1.0, 0.0] if text == "automobile" else vectors[text]
            for text in texts
        ]

    retriever = Retriever(embedder=embed)
    retriever.add(list(vectors))
    results = retriever.search("automobile")
    assert len(results) >= 1
    assert results[0] == "the car is parked outside"


def test_retriever_empty():
    retriever = Retriever()
    results = retriever.search("anything")
    assert results == []


def test_retriever_returns_no_results_for_blank_query():
    retriever = Retriever(embedder=lambda texts: [[1.0, 0.0] for _ in texts])
    retriever.add(["document text"])
    assert retriever.search("   ") == []


def test_retriever_rejects_mismatched_embedding_dimensions():
    vectors = iter([[1.0, 0.0], [1.0, 0.0, 0.0]])
    retriever = Retriever(embedder=lambda texts: [next(vectors) for _ in texts])
    retriever.add(["first document"])

    with pytest.raises(ValueError, match="inconsistent dimensions"):
        retriever.add(["second document"])


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


# --- Async tests ---

@pytest.mark.asyncio
async def test_pipeline_aask_without_rag():
    mock_llm = MagicMock()
    mock_llm.acomplete = AsyncMock(return_value="42")

    pipeline = Pipeline(llm=mock_llm)
    answer = await pipeline.aask("What is the answer?")

    assert answer == "42"
    mock_llm.acomplete.assert_awaited_once()


@pytest.mark.asyncio
async def test_pipeline_aask_with_rag(tmp_path):
    doc = tmp_path / "policy.txt"
    doc.write_text("Our refund policy allows returns within 30 days of purchase.")

    mock_llm = MagicMock()
    mock_llm.acomplete = AsyncMock(return_value="You can return within 30 days.")

    pipeline = Pipeline(llm=mock_llm, docs=str(tmp_path))
    answer = await pipeline.aask("What is the refund policy?")

    assert answer == "You can return within 30 days."
    mock_llm.acomplete.assert_awaited_once()
    prompt_arg = mock_llm.acomplete.call_args[0][0]
    assert "refund" in prompt_arg.lower()


@pytest.mark.asyncio
async def test_openai_acomplete():
    from flowmcp.llm.openai import OpenAIClient

    mock_openai = MagicMock()
    mock_async_openai = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello from AsyncOpenAI"
    mock_async_openai.return_value.close = AsyncMock()
    mock_async_openai.return_value.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch.dict("sys.modules", {"openai": mock_openai}):
        mock_openai.OpenAI.return_value = MagicMock()
        mock_openai.AsyncOpenAI = mock_async_openai
        client = OpenAIClient("gpt-4")
        result = await client.acomplete("Hello")

    assert result == "Hello from AsyncOpenAI"


@pytest.mark.asyncio
async def test_anthropic_acomplete():
    from flowmcp.llm.anthropic import AnthropicClient

    mock_anthropic = MagicMock()
    mock_async_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello from AsyncAnthropic"
    mock_async_client.return_value.close = AsyncMock()
    mock_async_client.return_value.messages.create = AsyncMock(return_value=mock_response)

    with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
        mock_anthropic.Anthropic.return_value = MagicMock()
        mock_anthropic.AsyncAnthropic = mock_async_client
        client = AnthropicClient("claude-3-5-sonnet-20241022")
        result = await client.acomplete("Hello")

    assert result == "Hello from AsyncAnthropic"


@pytest.mark.asyncio
async def test_llm_base_acomplete_default_fallback():
    from flowmcp.llm.base import LLMBase

    class SyncOnlyClient(LLMBase):
        def complete(self, prompt: str) -> str:
            return f"sync:{prompt}"

    client = SyncOnlyClient()
    result = await client.acomplete("hello")
    assert result == "sync:hello"



@pytest.fixture(autouse=True)
def use_test_embedding_model(monkeypatch):
    class TestEmbeddingModel:
        def encode(self, texts, convert_to_numpy=True):
            vectors = []
            for text in texts:
                vector = [0.0] * 64
                for token in text.lower().split():
                    vector[sum(token.encode("utf-8")) % len(vector)] += 1.0
                vectors.append(vector)
            return vectors

    monkeypatch.setattr(
        "flowmcp.rag.retriever._load_embedding_model",
        lambda model_name: TestEmbeddingModel(),
    )


def test_chunk_text_basic():
    text = " ".join(["word"] * 600)
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_chunk_text_small():
    text = "hello world"
    chunks = chunk_text(text)
    assert chunks == ["hello world"]


def test_retriever_returns_relevant_chunks():
    vectors = {
        "the car is parked outside": [1.0, 0.0],
        "refund policy allows 30 days": [0.0, 1.0],
        "we ship globally": [0.0, 0.5],
    }

    def embed(texts):
        return [
            [1.0, 0.0] if text == "automobile" else vectors[text]
            for text in texts
        ]

    retriever = Retriever(embedder=embed)
    retriever.add(list(vectors))
    results = retriever.search("automobile")
    assert len(results) >= 1
    assert results[0] == "the car is parked outside"


def test_retriever_empty():
    retriever = Retriever()
    results = retriever.search("anything")
    assert results == []


def test_retriever_returns_no_results_for_blank_query():
    retriever = Retriever(embedder=lambda texts: [[1.0, 0.0] for _ in texts])
    retriever.add(["document text"])
    assert retriever.search("   ") == []


def test_retriever_rejects_mismatched_embedding_dimensions():
    vectors = iter([[1.0, 0.0], [1.0, 0.0, 0.0]])
    retriever = Retriever(embedder=lambda texts: [next(vectors) for _ in texts])
    retriever.add(["first document"])

    with pytest.raises(ValueError, match="inconsistent dimensions"):
        retriever.add(["second document"])


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


def test_mistral_client_complete():
    from flowmcp.llm.mistral import MistralClient

    mock_mistralai = MagicMock()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello from Mistral"
    mock_client.chat.complete.return_value = mock_response
    mock_mistralai.Mistral.return_value = mock_client

    with patch.dict("sys.modules", {"mistralai": mock_mistralai}):
        client = MistralClient("mistral-small-latest", api_key="dummy_key")
        result = client.complete("Hello")
        assert result == "Hello from Mistral"
        mock_client.chat.complete.assert_called_once_with(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": "Hello"}]
        )


def test_mistral_client_from_string():
    from flowmcp.llm.base import LLM
    from flowmcp.llm.mistral import MistralClient

    mock_mistralai = MagicMock()
    mock_client = MagicMock()
    mock_mistralai.Mistral.return_value = mock_client

    with patch.dict("sys.modules", {"mistralai": mock_mistralai}):
        client = LLM.from_string("mistral/mistral-small-latest")
        assert isinstance(client, MistralClient)
        assert client.model == "mistral-small-latest"


def test_mistral_client_missing_dependency():
    from flowmcp.llm.mistral import MistralClient

    with patch.dict("sys.modules", {"mistralai": None}):
        with pytest.raises(ImportError, match="Install mistralai"):
            MistralClient("mistral-small-latest").complete("Hello")


def test_groq_client_complete():
    from flowmcp.llm.groq import GroqClient

    mock_groq = MagicMock()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello from Groq"
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq.Groq.return_value = mock_client

    with patch.dict("sys.modules", {"groq": mock_groq}):
        client = GroqClient("llama3-8b-8192", api_key="dummy_key")
        result = client.complete("Hello")
        assert result == "Hello from Groq"
        mock_client.chat.completions.create.assert_called_once_with(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Hello"}]
        )


def test_groq_client_from_string():
    from flowmcp.llm.base import LLM
    from flowmcp.llm.groq import GroqClient

    mock_groq = MagicMock()
    mock_groq.Groq.return_value = MagicMock()

    with patch.dict("sys.modules", {"groq": mock_groq}):
        client = LLM.from_string("groq/llama3-8b-8192")
        assert isinstance(client, GroqClient)
        assert client.model == "llama3-8b-8192"


def test_groq_client_missing_dependency():
    from flowmcp.llm.groq import GroqClient

    with patch.dict("sys.modules", {"groq": None}):
        with pytest.raises(ImportError, match="Install groq"):
            GroqClient("llama3-8b-8192").complete("Hello")


def test_huggingface_client_complete():
    from flowmcp.llm.huggingface import HuggingFaceClient

    mock_hf = MagicMock()
    mock_client = MagicMock()
    mock_client.text_generation.return_value = "Hello from HuggingFace"
    mock_hf.InferenceClient.return_value = mock_client

    with patch.dict("sys.modules", {"huggingface_hub": mock_hf}):
        client = HuggingFaceClient("mistralai/Mistral-7B-Instruct-v0.3", api_key="dummy_key")
        result = client.complete("Hello")
        assert result == "Hello from HuggingFace"
        mock_client.text_generation.assert_called_once_with("Hello", max_new_tokens=512)


def test_huggingface_client_from_string():
    from flowmcp.llm.base import LLM
    from flowmcp.llm.huggingface import HuggingFaceClient

    mock_hf = MagicMock()
    mock_hf.InferenceClient.return_value = MagicMock()

    with patch.dict("sys.modules", {"huggingface_hub": mock_hf}):
        client = LLM.from_string("huggingface/mistralai/Mistral-7B-Instruct-v0.3")
        assert isinstance(client, HuggingFaceClient)
        assert client.model == "mistralai/Mistral-7B-Instruct-v0.3"


def test_huggingface_client_missing_dependency():
    from flowmcp.llm.huggingface import HuggingFaceClient

    with patch.dict("sys.modules", {"huggingface_hub": None}):
        with pytest.raises(ImportError, match="Install huggingface_hub"):
            HuggingFaceClient("mistralai/Mistral-7B-Instruct-v0.3").complete("Hello")


# --- Token usage tracking tests ---

def test_openai_client_last_usage():
    from flowmcp.llm.openai import OpenAIClient

    mock_openai = MagicMock()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello"
    mock_response.usage.prompt_tokens = 5
    mock_response.usage.completion_tokens = 10
    mock_response.usage.total_tokens = 15
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.OpenAI.return_value = mock_client

    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = OpenAIClient("gpt-4")
        client.complete("Hello")
        assert client.last_usage == {
            "prompt_tokens": 5,
            "completion_tokens": 10,
            "total_tokens": 15,
        }


def test_anthropic_client_last_usage():
    from flowmcp.llm.anthropic import AnthropicClient

    mock_anthropic = MagicMock()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello"
    mock_response.usage.input_tokens = 8
    mock_response.usage.output_tokens = 12
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.Anthropic.return_value = mock_client

    with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
        client = AnthropicClient("claude-3-5-sonnet-20241022")
        client.complete("Hello")
        assert client.last_usage == {
            "prompt_tokens": 8,
            "completion_tokens": 12,
            "total_tokens": 20,
        }


def test_gemini_client_last_usage():
    from flowmcp.llm.gemini import GeminiClient

    mock_google = MagicMock()
    mock_genai = MagicMock()
    mock_google.genai = mock_genai
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello from Gemini"
    mock_response.usage_metadata.prompt_token_count = 6
    mock_response.usage_metadata.candidates_token_count = 11
    mock_response.usage_metadata.total_token_count = 17
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client

    with patch.dict("sys.modules", {"google": mock_google, "google.genai": mock_genai}):
        client = GeminiClient("gemini-2.0-flash", api_key="dummy_key")
        client.complete("Hello")
        assert client.last_usage == {
            "prompt_tokens": 6,
            "completion_tokens": 11,
            "total_tokens": 17,
        }


def test_ollama_client_last_usage():
    from flowmcp.llm.ollama import OllamaClient
    import json

    mock_data = {
        "response": "Hello from Ollama",
        "prompt_eval_count": 7,
        "eval_count": 14,
    }

    class FakeResponse:
        def read(self):
            return json.dumps(mock_data).encode()
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    with patch("urllib.request.urlopen", return_value=FakeResponse()):
        client = OllamaClient("llama3")
        result = client.complete("Hello")
        assert result == "Hello from Ollama"
        assert client.last_usage == {
            "prompt_tokens": 7,
            "completion_tokens": 14,
            "total_tokens": 21,
        }


def test_llm_base_last_usage_default():
    from flowmcp.llm.base import LLMBase

    class MinimalClient(LLMBase):
        def complete(self, prompt: str) -> str:
            return "ok"

    client = MinimalClient()
    assert client.last_usage == {}
