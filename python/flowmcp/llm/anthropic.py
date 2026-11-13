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
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
