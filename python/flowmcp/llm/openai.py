from .base import LLMBase


class OpenAIClient(LLMBase):
    def __init__(self, model: str):
        self.model = model
        try:
            from openai import OpenAI

            self.client = OpenAI()
        except ImportError:
            raise ImportError("Install openai: pip install openai")

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": prompt}]
        )
        if response.usage:
            self.last_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return response.choices[0].message.content

    async def acomplete(self, prompt: str) -> str:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")
        client = AsyncOpenAI()
        try:
            response = await client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        finally:
            await client.close()
