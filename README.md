# flowmcp

**The simple way to build RAG + MCP + LLM pipelines. A clean alternative to LangChain.**

[![CI](https://github.com/SreejaPasula/flowmcp/actions/workflows/ci.yml/badge.svg)](https://github.com/SreejaPasula/flowmcp/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The problem

Building an AI feature that uses your own data and tools requires wiring three things together:
1. An LLM (OpenAI, Claude, Gemini, Ollama)
2. Your documents (RAG — so the AI knows YOUR data)
3. External tools (via MCP — so the AI can take actions)

LangChain does this but needs hundreds of lines of setup. **flowmcp does it in 5 lines.**

---

## Quickstart

### Python

```bash
pip install flowmcp
pip install flowmcp[openai]   # for OpenAI
pip install flowmcp[anthropic] # for Anthropic
```

```python
from flowmcp import Pipeline

pipeline = Pipeline(
    llm="openai/gpt-4",
    docs="./my-docs",
    tools=["filesystem", "github"]
)

answer = pipeline.ask("What is our refund policy?")
print(answer)
```

### Java

```xml
<dependency>
    <groupId>io.flowmcp</groupId>
    <artifactId>flowmcp</artifactId>
    <version>0.1.0</version>
</dependency>
```

```java
Pipeline pipeline = new Pipeline.Builder()
    .llm("ollama/llama3")
    .docs("./my-docs")
    .build();

String answer = pipeline.ask("What is our refund policy?");
```

---

## Supported LLM Providers

| Provider | Python | Java |
|---|---|---|
| OpenAI | ✅ | 🚧 |
| Anthropic | ✅ | 🚧 |
| Ollama (local) | ✅ | ✅ |
| Gemini | 🚧 | 🚧 |

✅ = done · 🚧 = contributions welcome

---

## How it works

```
Your Data (docs, files, text)
         ↓
      RAG Pipeline  → finds relevant chunks for your query
         ↓
      MCP Tools     → runs external tools (filesystem, github, etc.)
         ↓
      LLM           → generates a response with full context
         ↓
      Answer
```

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.

Good first issues are labeled [`good first issue`](https://github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22).

---

## License

MIT — see [LICENSE](LICENSE)
