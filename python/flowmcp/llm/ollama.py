from .base import LLMBase


class OllamaClient(LLMBase):
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def complete(self, prompt: str) -> str:
        import urllib.request
        import json

        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())["response"]
