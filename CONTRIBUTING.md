# Contributing to flowmcp

Thank you for your interest! flowmcp is actively looking for contributors.

## Setup (under 5 minutes)

### Python
```bash
git clone https://github.com/SreejaPasula/flowmcp
cd flowmcp/python
pip install -e ".[all]"
pip install pytest
pytest tests/
```

### Java
```bash
cd flowmcp/java
mvn verify
```

## Good first issues

These are small, self-contained tasks perfect for a first contribution:

- Add Gemini provider for Python (`python/flowmcp/llm/gemini.py`)
- Add Gemini provider for Java (`java/.../llm/GeminiClient.java`)
- Implement OpenAI client for Java (`java/.../llm/OpenAIClient.java`)
- Implement Anthropic client for Java (`java/.../llm/AnthropicClient.java`)
- Add PDF support to RAG loader (`python/flowmcp/rag/loader.py`)
- Add embedding-based retrieval to replace TF-IDF (`python/flowmcp/rag/retriever.py`)
- Implement MCP filesystem tool connection
- Add streaming support to Python Pipeline
- Write more tests for edge cases

All issues are labeled [`good first issue`](https://github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22) on GitHub.

## How to contribute

1. Pick an issue or propose something new
2. Fork the repo and create a branch: `git checkout -b my-feature`
3. Make your change and add tests
4. Open a PR — describe what you changed and why

## Code style

- Python: follow PEP 8, no external formatters required
- Java: standard Java conventions, Java 17+

## Questions?

Open an issue or start a discussion on GitHub.
