from abc import ABC, abstractmethod
import asyncio
import contextvars
import functools
import inspect
import time
import urllib.error

DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0

_RETRYABLE_STATUS_CODES = frozenset({429, 503, 504})
# Provider SDKs (openai, anthropic) raise these without an HTTP status code.
_RETRYABLE_ERROR_NAMES = frozenset({"APIConnectionError", "APITimeoutError"})
# Set while a retry wrapper is running so nested wrapped calls (for example an
# async fallback that delegates to ``complete``) do not multiply the retries.
_RETRY_ACTIVE: contextvars.ContextVar = contextvars.ContextVar(
    "flowmcp_retry_active", default=False
)


def _status_code(exc: BaseException):
    """Best-effort HTTP status code from an exception raised by any provider SDK."""
    for holder in (exc, getattr(exc, "response", None)):
        for attr in ("status_code", "status", "code"):
            value = getattr(holder, attr, None)
            if isinstance(value, int) and not isinstance(value, bool):
                return value
    return None


def is_retryable(exc: BaseException) -> bool:
    """True for transient failures: HTTP 429/503/504, connection errors, timeouts.

    Anything else (auth errors, bad requests, programming errors) is not retried.
    """
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    if isinstance(exc, urllib.error.URLError) and not isinstance(
        exc, urllib.error.HTTPError
    ):
        return True  # DNS failure, refused connection, socket timeout
    if any(cls.__name__ in _RETRYABLE_ERROR_NAMES for cls in type(exc).__mro__):
        return True
    return _status_code(exc) in _RETRYABLE_STATUS_CODES


def _retry_settings(llm):
    return (
        max(0, int(getattr(llm, "max_retries", DEFAULT_MAX_RETRIES))),
        float(getattr(llm, "retry_delay", DEFAULT_RETRY_DELAY)),
    )


def _with_retry(func):
    """Retry ``func`` on transient errors with exponential backoff.

    Makes up to ``max_retries`` extra attempts, sleeping
    ``retry_delay * 2 ** attempt`` seconds before each one.
    """
    if getattr(func, "_flowmcp_retry", False):
        return func

    if inspect.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            if _RETRY_ACTIVE.get():
                return await func(self, *args, **kwargs)
            max_retries, delay = _retry_settings(self)
            token = _RETRY_ACTIVE.set(True)
            try:
                for attempt in range(max_retries + 1):
                    try:
                        return await func(self, *args, **kwargs)
                    except Exception as exc:
                        if attempt >= max_retries or not is_retryable(exc):
                            raise
                        await asyncio.sleep(delay * 2**attempt)
            finally:
                _RETRY_ACTIVE.reset(token)

    else:

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if _RETRY_ACTIVE.get():
                return func(self, *args, **kwargs)
            max_retries, delay = _retry_settings(self)
            token = _RETRY_ACTIVE.set(True)
            try:
                for attempt in range(max_retries + 1):
                    try:
                        return func(self, *args, **kwargs)
                    except Exception as exc:
                        if attempt >= max_retries or not is_retryable(exc):
                            raise
                        time.sleep(delay * 2**attempt)
            finally:
                _RETRY_ACTIVE.reset(token)

    wrapper._flowmcp_retry = True
    return wrapper


class LLMBase(ABC):
    """Base class for LLM clients.

    ``complete`` and ``acomplete`` of every subclass are wrapped automatically
    so transient errors are retried with exponential backoff. Configure with
    the ``max_retries`` and ``retry_delay`` attributes (also accepted by
    ``LLM.from_string``).
    """

    last_usage: dict = {}
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_delay: float = DEFAULT_RETRY_DELAY

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for name in ("complete", "acomplete"):
            if name in cls.__dict__:
                setattr(cls, name, _with_retry(cls.__dict__[name]))

    @abstractmethod
    def complete(self, prompt: str) -> str:
        pass

    async def acomplete(self, prompt: str) -> str:
        return await asyncio.to_thread(self.complete, prompt)


class LLM:
    """
    Factory for creating LLM clients from a simple string.

    Supported formats:
        "openai/gpt-4"
        "openai-compat:local-model"
        "anthropic/claude-3-5-sonnet"
        "ollama/llama3"
        "gemini/gemini-pro"

    Transient errors (HTTP 429/503/504, connection errors, timeouts) are retried
    with exponential backoff; pass ``max_retries=`` and ``retry_delay=`` to tune.
    """

    @staticmethod
    def from_string(
        model_string: str,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        **kwargs,
    ) -> LLMBase:
        """Create a client. ``max_retries`` / ``retry_delay`` tune the backoff."""
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
        if (
            isinstance(retry_delay, bool)
            or not isinstance(retry_delay, (int, float))
            or retry_delay < 0
        ):
            raise ValueError("retry_delay must be a non-negative number")

        client = LLM._create(model_string, **kwargs)
        client.max_retries = max_retries
        client.retry_delay = float(retry_delay)
        return client

    @staticmethod
    def _create(model_string: str, **kwargs) -> LLMBase:
        if model_string.startswith("openai-compat:"):
            provider = "openai-compat"
            model = model_string.split(":", 1)[1].strip()
        elif "/" in model_string:
            provider, model = model_string.split("/", 1)
            model = model.strip()
        else:
            raise ValueError(
                f"Invalid model format '{model_string}'. "
                "Use 'provider/model' e.g. 'openai/gpt-4' or 'openai-compat:<model>'"
            )

        if not model:
            raise ValueError(f"Missing model name in '{model_string}'.")

        if provider == "openai-compat":
            unexpected = set(kwargs) - {"base_url", "api_key"}
            if unexpected:
                bad = ", ".join(sorted(unexpected))
                raise ValueError(
                    f"Unexpected keyword argument(s) for 'openai-compat': {bad}"
                )
            from .openai_compat import OpenAICompatClient

            return OpenAICompatClient(
                model,
                base_url=kwargs.get("base_url"),
                api_key=kwargs.get("api_key"),
            )

        if kwargs:
            bad = ", ".join(sorted(kwargs))
            raise ValueError(
                f"Unexpected keyword argument(s) for provider '{provider}': {bad}"
            )

        if provider == "openai":
            from .openai import OpenAIClient

            return OpenAIClient(model)
        elif provider == "anthropic":
            from .anthropic import AnthropicClient

            return AnthropicClient(model)
        elif provider == "ollama":
            from .ollama import OllamaClient

            return OllamaClient(model)
        elif provider == "gemini":
            from .gemini import GeminiClient

            return GeminiClient(model)
        elif provider == "mistral":
            from .mistral import MistralClient

            return MistralClient(model)
        elif provider == "groq":
            from .groq import GroqClient

            return GroqClient(model)
        elif provider == "huggingface":
            from .huggingface import HuggingFaceClient

            return HuggingFaceClient(model)
        else:
            raise ValueError(
                f"Unsupported provider '{provider}'. Supported: "
                "openai, openai-compat, anthropic, ollama, gemini, "
                "mistral, groq, huggingface"
            )
