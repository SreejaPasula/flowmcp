from .base import LLMBase


class AnthropicClient(LLMBase):
    def __init__(self, model: str):
        self.model = model
        try:
            import anthropic

            self.client = anthropic.Anthropic()
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")

    def complete(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        if message.usage:
            self.last_usage = {
                "prompt_tokens": message.usage.input_tokens,
                "completion_tokens": message.usage.output_tokens,
                "total_tokens": message.usage.input_tokens
                + message.usage.output_tokens,
            }
        return message.content[0].text

    async def acomplete(self, prompt: str) -> str:
        try:
            import anthropic
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic")
        client = anthropic.AsyncAnthropic()
        try:
            message = await client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text
        finally:
            await client.close()
