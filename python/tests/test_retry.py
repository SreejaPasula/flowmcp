import asyncio
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from flowmcp.llm import LLM, LLMBase
from flowmcp.llm.base import is_retryable


class HTTPStatusError(Exception):
    def __init__(self, status_code):
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


class APIConnectionError(Exception):
    """Mimics the class name used by the openai / anthropic SDKs."""


class Flaky(LLMBase):
    def __init__(self, failures, error):
        self.failures = failures
        self.error = error
        self.calls = 0

    def complete(self, prompt):
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error
        return "ok"

    async def acomplete(self, prompt):
        return self.complete(prompt)


@pytest.fixture
def sleeps():
    with patch("flowmcp.llm.base.time.sleep") as sleep:
        yield sleep


def test_retries_then_succeeds_with_exponential_delays(sleeps):
    llm = Flaky(2, HTTPStatusError(429))
    llm.retry_delay = 1.0
    assert llm.complete("hi") == "ok"
    assert llm.calls == 3
    assert [c.args[0] for c in sleeps.call_args_list] == [1.0, 2.0]


def test_gives_up_after_max_retries_and_reraises(sleeps):
    llm = Flaky(99, HTTPStatusError(503))
    llm.max_retries = 3
    with pytest.raises(HTTPStatusError):
        llm.complete("hi")
    assert llm.calls == 4  # first try + 3 retries
    assert sleeps.call_count == 3


@pytest.mark.parametrize("status", [400, 401, 403, 404])
def test_client_errors_are_not_retried(sleeps, status):
    llm = Flaky(99, HTTPStatusError(status))
    with pytest.raises(HTTPStatusError):
        llm.complete("hi")
    assert llm.calls == 1
    sleeps.assert_not_called()


def test_unrelated_exceptions_are_not_retried(sleeps):
    llm = Flaky(99, ValueError("bad"))
    with pytest.raises(ValueError):
        llm.complete("hi")
    assert llm.calls == 1


@pytest.mark.parametrize(
    "error",
    [
        ConnectionError("x"),
        TimeoutError("x"),
        APIConnectionError("x"),
        HTTPStatusError(504),
    ],
)
def test_transient_errors_are_retried(sleeps, error):
    llm = Flaky(1, error)
    assert llm.complete("hi") == "ok"
    assert llm.calls == 2


def test_zero_retries_disables_retrying(sleeps):
    llm = Flaky(1, HTTPStatusError(429))
    llm.max_retries = 0
    with pytest.raises(HTTPStatusError):
        llm.complete("hi")
    assert llm.calls == 1


def test_is_retryable_reads_status_from_response_attribute():
    err = Exception("boom")
    err.response = MagicMock(status_code=429)
    assert is_retryable(err)


def test_is_retryable_urllib_errors():
    assert is_retryable(urllib.error.URLError("connection refused"))
    assert is_retryable(
        urllib.error.HTTPError("http://x", 503, "unavailable", {}, None)
    )
    assert not is_retryable(urllib.error.HTTPError("http://x", 401, "no", {}, None))


async def test_async_retries(monkeypatch):
    sleeps = []

    async def fake_sleep(seconds):
        sleeps.append(seconds)

    monkeypatch.setattr("flowmcp.llm.base.asyncio.sleep", fake_sleep)
    llm = Flaky(2, HTTPStatusError(429))
    llm.retry_delay = 0.5
    assert await llm.acomplete("hi") == "ok"
    assert sleeps == [0.5, 1.0]


async def test_async_non_retryable_raises_immediately():
    llm = Flaky(5, HTTPStatusError(401))
    with pytest.raises(HTTPStatusError):
        await llm.acomplete("hi")
    assert llm.calls == 1


def test_nested_wrapped_calls_do_not_multiply_retries(sleeps):
    # acomplete (wrapped) calls complete (wrapped): still only max_retries + 1 tries.
    llm = Flaky(99, HTTPStatusError(429))
    llm.max_retries = 2
    with pytest.raises(HTTPStatusError):
        asyncio.run(llm.acomplete("hi"))
    assert llm.calls == 3


def test_from_string_configures_retries_for_every_provider():
    mock_openai = MagicMock()
    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = LLM.from_string("openai/gpt-4", max_retries=5, retry_delay=0.25)
    assert client.max_retries == 5
    assert client.retry_delay == 0.25

    ollama = LLM.from_string("ollama/llama3", max_retries=1)
    assert ollama.max_retries == 1
    assert ollama.retry_delay == 1.0


def test_from_string_defaults():
    client = LLM.from_string("ollama/llama3")
    assert client.max_retries == 3
    assert client.retry_delay == 1.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_retries": -1},
        {"max_retries": 1.5},
        {"retry_delay": -0.1},
        {"retry_delay": "1"},
    ],
)
def test_from_string_rejects_invalid_retry_settings(kwargs):
    with pytest.raises(ValueError):
        LLM.from_string("ollama/llama3", **kwargs)


def test_unknown_kwargs_still_rejected():
    with pytest.raises(ValueError):
        LLM.from_string("ollama/llama3", bogus=1)


def test_real_client_is_retried_end_to_end(sleeps):
    mock_openai = MagicMock()
    create = mock_openai.OpenAI.return_value.chat.completions.create
    good = MagicMock()
    good.usage = None
    good.choices[0].message.content = "hello"
    create.side_effect = [HTTPStatusError(429), good]
    with patch.dict("sys.modules", {"openai": mock_openai}):
        client = LLM.from_string("openai/gpt-4")
        assert client.complete("hi") == "hello"
    assert create.call_count == 2
