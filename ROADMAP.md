# Roadmap

This document tracks what's planned for flowmcp. Priorities can shift based on contributor interest and community feedback. Open an issue or discussion to influence what gets built next.

---

## v0.1.x — Stability (current)

Bug fixes and small improvements to the existing API. No breaking changes.

- [x] Python SDK: Pipeline, RAG, LLM, MCP modules
- [x] Java SDK: Pipeline builder, OllamaClient
- [x] LLM providers: OpenAI, Anthropic, Ollama (Python)
- [x] RAG: TF-IDF keyword retriever, file/directory/text loader
- [x] GitHub Actions CI/CD
- [x] Automated PR review bot (GitHub Models)
- [ ] Gemini provider for Python — [#1](https://github.com/SreejaPasula/flowmcp/issues/1)
- [ ] OpenAI client for Java — [#2](https://github.com/SreejaPasula/flowmcp/issues/2)
- [ ] Anthropic client for Java — [#3](https://github.com/SreejaPasula/flowmcp/issues/3)
- [ ] PDF support in RAG loader — [#4](https://github.com/SreejaPasula/flowmcp/issues/4)
- [ ] Streaming support for Python Pipeline — [#5](https://github.com/SreejaPasula/flowmcp/issues/5)

---

## v0.2.0 — Smarter Retrieval

Upgrade RAG from keyword matching to real embedding-based retrieval.

- [ ] Embedding-based retrieval (sentence-transformers or OpenAI embeddings) — [#6](https://github.com/SreejaPasula/flowmcp/issues/6)
- [ ] Pluggable retriever interface so users can swap in Chroma, FAISS, Pinecone
- [ ] Metadata filtering on retrieved chunks (date range, source file, etc.)
- [ ] Hybrid retrieval: keyword + semantic combined
- [ ] Java RAG: embedding-based retriever

---

## v0.3.0 — Real MCP Integration

Replace the MCP stub with a working Model Context Protocol client.

- [ ] Connect to MCP filesystem server
- [ ] Connect to MCP GitHub server
- [ ] MCP tool discovery and schema validation
- [ ] Async MCP execution
- [ ] Java MCP client

---

## v0.4.0 — Production Ready

Features needed to run flowmcp in production services.

- [ ] Async/await support throughout Python SDK
- [ ] Token counting and cost estimation before each call
- [ ] Retry logic with exponential backoff for LLM API errors
- [ ] Structured output (JSON schema enforcement)
- [ ] Tracing and observability hooks (OpenTelemetry)
- [ ] Rate limiting support

---

## v1.0.0 — Stable API

- [ ] Finalise public API and deprecate any inconsistencies
- [ ] Full documentation site (MkDocs)
- [ ] Publish to PyPI and Maven Central
- [ ] 90%+ test coverage on both SDKs

---

## Not planned

These are out of scope for flowmcp — we want to stay small and composable:

- Built-in vector database — use a dedicated library (Chroma, Qdrant, Pinecone)
- Agent frameworks or multi-agent orchestration — this is for pipelines, not agents
- GUI or web UI
- Cloud hosting or managed service

---

## How to influence the roadmap

- **Vote on issues** — react with 👍 to issues you care about
- **Open a discussion** — propose a new direction at [GitHub Discussions](https://github.com/SreejaPasula/flowmcp/discussions)
- **Contribute** — pick any unchecked item and open a PR
