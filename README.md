# flowmcp

**The simple way to build RAG + MCP + LLM pipelines. A clean alternative to LangChain.**

[![CI](https://github.com/SreejaPasula/flowmcp/actions/workflows/ci.yml/badge.svg)](https://github.com/SreejaPasula/flowmcp/actions)
[![codecov](https://codecov.io/gh/SreejaPasula/flowmcp/branch/main/graph/badge.svg)](https://codecov.io/gh/SreejaPasula/flowmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/16997/badge)](https://www.bestpractices.dev/projects/16997)

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
pip install flowmcp[openai]    # for OpenAI
pip install flowmcp[anthropic] # for Anthropic
pip install flowmcp[gemini]    # for Gemini
pip install flowmcp[pdf]       # for PDF document loading
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

### Multiple questions

```python
answers = pipeline.batch(
    ["What is the refund policy?", "How do I cancel?"], top_k=3
)
```

`batch()` processes queries sequentially and returns answers in the same order.
Each query performs its own document retrieval, tool calls, and LLM request.
`top_k` controls the number of retrieved chunks per query. An empty list returns
`[]` without making calls. The first error is raised immediately; later queries
are not processed. This convenience method does not use a provider-side batch
API or offer batch pricing. Existing `ask(question)` calls remain supported;
`ask(question, top_k=5)` can also customize retrieval for one question.

### Reusable prompt templates

```python
pipeline.set_template(
    "Answer using this evidence: {context}\n\nQuestion: {query}"
)
answer = pipeline.ask("What is the refund policy?")
# The same template also applies to await pipeline.aask(...).
```

`{query}` contains the current question and `{context}` contains retrieved chunks
joined by blank lines (or an empty string when no documents are available).
Templates may use either placeholder; a query-only template is supported.
Use `{{` and `}}` for literal braces, such as JSON examples. Unknown fields,
attribute/index lookups, format specifications, and conversions are rejected
when setting the template. An invalid replacement leaves the previous template
intact. If MCP tools return results, these are appended after the rendered
prompt. Without a template, existing prompt construction is unchanged.

### Automatic retries

LLM calls that fail with a transient error (HTTP 429, 503, 504, a connection
error, or a timeout) are retried with exponential backoff. Auth errors and
other 4xx responses are raised immediately.

```python
from flowmcp import LLM

llm = LLM.from_string("openai/gpt-4o-mini")  # 3 retries, 1s base delay
llm = LLM.from_string("openai/gpt-4o-mini", max_retries=5, retry_delay=0.5)
```

The wait before retry `n` (starting at 0) is `retry_delay * 2**n` seconds.
Set `max_retries=0` to turn retries off.

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
| OpenAI | ✅ | ✅ |
| Anthropic | ✅ | 🚧 |
| Ollama (local) | ✅ | ✅ |
| Gemini | ✅ | 🚧 |

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
