import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from flowmcp.llm import LLM, OpenAICompatClient


def test_openai_compat_from_string_with_explicit_args():
    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = MagicMock()

    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = LLM.from_string(
            "openai-compat:local-model",
            base_url="http://localhost:1234/v1/",
            api_key="none",
        )

    assert isinstance(client, OpenAICompatClient)
    assert client.model == "local-model"
    assert client.base_url == "http://localhost:1234/v1"
    assert client.api_key == "none"
    mock_openai.OpenAI.assert_called_once_with(
        base_url="http://localhost:1234/v1",
        api_key="none",
    )


def test_openai_compat_model_with_slash_and_default_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-real-key-must-not-leak")
    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = MagicMock()

    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = LLM.from_string(
            "openai-compat:meta-llama/Llama-3-8B-Instruct",
            base_url="http://localhost:8000/v1",
        )

    assert isinstance(client, OpenAICompatClient)
    assert client.model == "meta-llama/Llama-3-8B-Instruct"
    assert client.api_key == "none"
    mock_openai.OpenAI.assert_called_once_with(
        base_url="http://localhost:8000/v1",
        api_key="none",
    )


def test_openai_compat_slash_syntax_and_env_fallback(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:8080/v1")
    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = MagicMock()

    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = LLM.from_string("openai-compat/qwen2.5:7b")

    assert isinstance(client, OpenAICompatClient)
    assert client.model == "qwen2.5:7b"
    assert client.base_url == "http://127.0.0.1:8080/v1"
    mock_openai.OpenAI.assert_called_once_with(
        base_url="http://127.0.0.1:8080/v1",
        api_key="none",
    )


def test_openai_compat_missing_or_invalid_base_url(monkeypatch):
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    with pytest.raises(ValueError, match="base_url"):
        OpenAICompatClient("local-model")

    with pytest.raises(ValueError, match="base_url"):
        OpenAICompatClient("local-model", base_url="ftp://localhost:1234/v1")

    with pytest.raises(ValueError, match="base_url"):
        OpenAICompatClient("local-model", base_url="http:///v1")


def test_openai_compat_empty_model_and_unexpected_kwargs():
    with pytest.raises(ValueError, match="Missing model name"):
        LLM.from_string("openai-compat:", base_url="http://localhost:1234/v1")

    with pytest.raises(ValueError, match="Unexpected keyword argument"):
        LLM.from_string(
            "openai-compat:local-model",
            base_url="http://localhost:1234/v1",
            timeout=10,
        )

    with pytest.raises(ValueError, match="Unexpected keyword argument"):
        LLM.from_string("ollama/llama3", base_url="http://localhost:11434")


def test_openai_compat_complete_and_usage():
    mock_openai = MagicMock()
    mock_sdk_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello from local server"
    mock_response.usage.prompt_tokens = 12
    mock_response.usage.completion_tokens = 7
    mock_response.usage.total_tokens = 19
    mock_sdk_client.chat.completions.create.return_value = mock_response
    mock_openai.OpenAI.return_value = mock_sdk_client

    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = OpenAICompatClient(
            "local-model",
            base_url="http://localhost:1234/v1",
            api_key="local-secret",
        )
        result = client.complete("Ping")

    assert result == "Hello from local server"
    mock_sdk_client.chat.completions.create.assert_called_once_with(
        model="local-model",
        messages=[{"role": "user", "content": "Ping"}],
    )
    assert client.last_usage == {
        "prompt_tokens": 12,
        "completion_tokens": 7,
        "total_tokens": 19,
    }


def test_openai_compat_acomplete_and_usage():
    mock_openai = MagicMock()
    mock_openai.OpenAI.return_value = MagicMock()
    mock_async_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Async hello"
    mock_response.usage.prompt_tokens = 4
    mock_response.usage.completion_tokens = 6
    mock_response.usage.total_tokens = 10
    mock_async_client.chat.completions.create = AsyncMock(return_value=mock_response)
    mock_async_client.close = AsyncMock()
    mock_openai.AsyncOpenAI.return_value = mock_async_client

    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = OpenAICompatClient(
            "local-model",
            base_url="http://localhost:1234/v1",
            api_key="none",
        )
        result = asyncio.run(client.acomplete("Ping"))

    assert result == "Async hello"
    mock_openai.AsyncOpenAI.assert_called_once_with(
        base_url="http://localhost:1234/v1",
        api_key="none",
    )
    assert client.last_usage == {
        "prompt_tokens": 4,
        "completion_tokens": 6,
        "total_tokens": 10,
    }


def test_openai_compat_missing_dependency():
    with patch.dict("sys.modules", {"openai": None}):
        with pytest.raises(ImportError, match="Install openai"):
            OpenAICompatClient("local-model", base_url="http://localhost:1234/v1")
