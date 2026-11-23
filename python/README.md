# flowmcp

The simple way to build RAG + MCP + LLM pipelines. A clean alternative to LangChain.

```bash
pip install flowmcp
pip install flowmcp[openai]    # or [anthropic], [gemini], [pdf], ...
```

```python
from flowmcp import Pipeline

pipeline = Pipeline(llm="openai/gpt-4", docs="./my-docs")
print(pipeline.ask("What is our refund policy?"))
```

Full documentation: https://github.com/SreejaPasula/flowmcp
