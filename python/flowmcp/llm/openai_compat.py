import os
from typing import Optional
from urllib.parse import urlparse

from .base import LLMBase


class OpenAICompatClient(LLMBase):
    """LLM client for OpenAI-compatible servers (LM Studio, vLLM, llama.cpp)."""

    def __init__(
        self,
        model: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        resolved_url = (base_url or os.environ.get("OPENAI_BASE_URL") or "").strip()
        parsed = urlparse(resolved_url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError(
                "Invalid or missing base_url. Pass base_url or set OPENAI_BASE_URL "
                "starting with http:// or https://."
            )

        self.model = model
        self.base_url = resolved_url.rstrip("/")
        self.api_key = api_key or "none"
        self.last_usage = {}

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def _record_usage(self, response) -> None:
        usage = getattr(response, "usage", None)
        if usage:
            self.last_usage = {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            }

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        self._record_usage(response)
        return response.choices[0].message.content

    async def acomplete(self, prompt: str) -> str:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")

        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            self._record_usage(response)
            return response.choices[0].message.content
        finally:
            await client.close()
