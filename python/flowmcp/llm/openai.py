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
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
