import os
from typing import Optional
from .base import LLMBase


class GeminiClient(LLMBase):
    """
    Google Gemini LLM client supporting both the modern `google-genai` SDK
    and fallback to legacy `google-generativeai`.
    """

    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def complete(self, prompt: str) -> str:
        try:
            import google.genai as genai
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            client = genai.Client(**kwargs)
            response = client.models.generate_content(model=self.model, contents=prompt)
            return response.text
        except ImportError:
            pass

        try:
            import google.generativeai as genai_legacy
            if self.api_key:
                genai_legacy.configure(api_key=self.api_key)
            model = genai_legacy.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        except ImportError:
            raise ImportError("Install google-genai: pip install google-genai")
