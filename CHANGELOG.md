# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PDF document support in RAG loader (pypdf)
- Gemini provider for Python and Java
- OpenAI client for Java
- Anthropic client for Java
- Fix OllamaClient JSON parsing with Jackson

### Fixed
- RAG query punctuation matching
- RAG docs path validation

## [0.1.0] - 2026-11-13

### Added
- Python SDK: `Pipeline`, `RAG`, `LLM`, `MCP` modules
- Java SDK: `Pipeline` builder pattern, `OllamaClient`
- LLM provider support: OpenAI, Anthropic, Ollama (Python); Ollama (Java)
- Keyword-based TF-IDF retriever for RAG
- Text, file, and directory document loaders
- GitHub Actions CI/CD: Python Tests + Java Build
- Automated PR review bot using GitHub Models API
- Community health files: CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, CLA
- Dependabot for automated dependency updates
- Pre-commit hooks: black, isort, flake8
