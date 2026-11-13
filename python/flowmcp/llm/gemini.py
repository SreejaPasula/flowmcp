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
        self._use_new_sdk = True

        try:
            # Prefer modern Google GenAI SDK (google-genai)
            from google import genai
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            self.client = genai.Client(**kwargs)
        except ImportError:
            try:
                # Fallback to legacy google-generativeai if installed
                import google.generativeai as genai_legacy
                if self.api_key:
                    genai_legacy.configure(api_key=self.api_key)
                self.client = genai_legacy.GenerativeModel(model)
                self._use_new_sdk = False
            except ImportError:
                raise ImportError(
                    "Install google-genai: pip install google-genai"
                )

    def complete(self, prompt: str) -> str:
        if self._use_new_sdk:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text
        else:
            response = self.client.generate_content(prompt)
            return response.text
