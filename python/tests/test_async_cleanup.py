import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from flowmcp.llm.anthropic import AnthropicClient
from flowmcp.llm.openai import OpenAIClient
from flowmcp.llm.openai_compat import OpenAICompatClient


@pytest.mark.parametrize(
    "adapter, module, factory",
    [
        (OpenAIClient, "openai", "AsyncOpenAI"),
        (OpenAICompatClient, "openai", "AsyncOpenAI"),
        (AnthropicClient, "anthropic", "AsyncAnthropic"),
    ],
)
@pytest.mark.parametrize("outcome", ["success", "error", "cancel"])
@pytest.mark.asyncio
async def test_temporary_async_client_is_closed(adapter, module, factory, outcome):
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))],
        content=[SimpleNamespace(text="answer")],
        usage=None,
    )
    error = (
        RuntimeError("request failed")
        if outcome == "error"
        else asyncio.CancelledError()
    )
    create = AsyncMock(
        return_value=response, side_effect=None if outcome == "success" else error
    )
    transport = Mock()
    transport.chat.completions.create = create
    transport.messages.create = create
    transport.close = AsyncMock()
    sdk = Mock()
    getattr(sdk, factory).return_value = transport
    kwargs = (
        {"base_url": "http://localhost:1234/v1"}
        if adapter is OpenAICompatClient
        else {}
    )
    with patch.dict("sys.modules", {module: sdk}):
        client = adapter("test-model", **kwargs)
        if outcome == "success":
            assert await client.acomplete("hello") == "answer"
        else:
            with pytest.raises(type(error)) as raised:
                await client.acomplete("hello")
            assert raised.value is error
    create.assert_awaited_once()
    assert create.call_args.kwargs["model"] == "test-model"
    assert create.call_args.kwargs["messages"] == [{"role": "user", "content": "hello"}]
    transport.close.assert_awaited_once()
    client.client.close.assert_not_called()
