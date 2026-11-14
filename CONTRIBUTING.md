# Contributing to flowmcp

Thank you for your interest in contributing! This document covers everything you need to know — from opening your first issue to getting a PR merged.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Issue Templates](#issue-templates)
5. [Pull Request Template](#pull-request-template)
6. [Policies](#policies)
7. [Code Style](#code-style)
8. [Good First Issues](#good-first-issues)
9. [Questions](#questions)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold it. Report unacceptable behaviour to sreejap974@gmail.com.

---

## Getting Started

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

---

## How to Contribute

1. **Find or create an issue** — pick one labeled [`good first issue`](https://github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22) or open a new one
2. **Comment on the issue** to let maintainers know you are working on it
3. **Fork the repo** and create a branch: `git checkout -b feature/my-feature`
4. **Make your change** — add tests, update docs if needed
5. **Open a PR** — fill in the PR template fully
6. **Respond to review feedback** — the automated bot and maintainers may leave comments
7. **Sign the CLA** — the CLA bot will prompt you on your first PR (see [CLA.md](CLA.md))

---

## Issue Templates

When opening a new issue, choose the template that best fits:

### Bug Report

Use this when something is not working as expected.

**Fields to fill in:**

| Field | What to write |
|-------|--------------|
| **What happened?** | Describe the actual behaviour |
| **What did you expect?** | Describe the expected behaviour |
| **Steps to reproduce** | Numbered list of exact steps |
| **Environment** | flowmcp version, Python/Java version, LLM provider |

Title format: `[Bug] short description`
Label: `bug`

---

### Feature Request

Use this to propose a new feature or improvement.

**Fields to fill in:**

| Field | What to write |
|-------|--------------|
| **What problem does this solve?** | Describe the gap or pain point |
| **Describe the solution** | What should be built |
| **Example API** | Show how you would use it in code |

Title format: `[Feature] short description`
Label: `enhancement`

---

## Pull Request Template

Every PR must fill in the following template. GitHub auto-populates it when you open a PR.

```
## What does this PR do?
(Briefly describe the change and which issue it resolves)

Fixes #

---

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Other (describe):

---

## Checklist
- [ ] I have read CONTRIBUTING.md
- [ ] My code follows the existing style of the project
- [ ] I have added tests that cover my changes
- [ ] All existing tests pass (pytest tests/ or mvn verify)
- [ ] I have not introduced any breaking changes to the existing API
- [ ] I have not hardcoded any secrets, API keys, or credentials
- [ ] My changes do not introduce any new dependencies with incompatible licenses

---

## How has this been tested?
(Describe how you tested your change)
```

**Rules:**
- Every item in the checklist must be ticked before a PR can be merged
- The `Fixes #` line must reference an open issue — PRs without a linked issue will be asked to create one first
- PRs that fail CI (Python Tests or Java Build) will not be reviewed until they are fixed

---

## Policies

### Branching

| Branch | Purpose |
|--------|---------|
| `main` | Stable, always passing CI — direct pushes are blocked |
| `feature/*` | New features |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation only |
| `chore/*` | Tooling, dependencies, config |

### Review Policy

- Every PR requires **at least 1 approving review** from a maintainer
- The automated PR review bot will comment on every PR — read its output and address any flagged issues
- Stale reviews are dismissed when new commits are pushed
- Maintainers may request changes; address all comments before requesting a re-review

### Merge Policy

- **Only maintainers merge PRs** — contributors do not merge their own work
- PRs are merged once: CI passes + 1 approval + all checklist items ticked + CLA signed
- We use **squash and merge** to keep a clean commit history on `main`

### Breaking Changes

- Breaking changes to the public API require a `breaking change` label and a note in CHANGELOG.md
- They will not be merged without a migration path or a major version bump

### Security

- Do not open public issues for security vulnerabilities
- Report them privately to sreejap974@gmail.com following [SECURITY.md](SECURITY.md)

### Licensing

- All contributions are licensed under MIT (see [LICENSE](LICENSE))
- By submitting a PR you confirm the code is your own original work and you agree to the [CLA](CLA.md)
- Do not copy code from projects with incompatible licenses (GPL, AGPL, etc.)

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add Gemini provider for Python
fix: correct TF-IDF scoring for short queries
docs: update RAG usage example in README
chore: bump openai dependency to 1.35
test: add edge case for empty document list
```

---

## Code Style

### Python

- Formatter: [black](https://black.readthedocs.io/) (line length 100)
- Import order: [isort](https://pycqa.github.io/isort/) with black profile
- Linter: [flake8](https://flake8.pycqa.org/) (`--max-line-length=100`)
- Run all checks: `pre-commit run --all-files`

### Java

- Standard Java conventions, Java 17+
- 4-space indentation
- Run: `mvn verify`

---

## Good First Issues

These tasks are small, self-contained, and well-defined — ideal for a first contribution:

| Issue | Description | Skill |
|-------|-------------|-------|
| [#1](https://github.com/SreejaPasula/flowmcp/issues/1) | Add Gemini provider for Python | Python |
| [#2](https://github.com/SreejaPasula/flowmcp/issues/2) | Implement OpenAI client for Java | Java |
| [#3](https://github.com/SreejaPasula/flowmcp/issues/3) | Implement Anthropic client for Java | Java |
| [#4](https://github.com/SreejaPasula/flowmcp/issues/4) | Add PDF support to RAG loader | Python |
| [#5](https://github.com/SreejaPasula/flowmcp/issues/5) | Add streaming support to Python Pipeline | Python |
| [#6](https://github.com/SreejaPasula/flowmcp/issues/6) | Add embedding-based retrieval | Python |

Browse all: [github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22](https://github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22)

---

## Questions?

- Open a [GitHub Discussion](https://github.com/SreejaPasula/flowmcp/discussions) for general questions
- Open an issue if you found a bug or want to propose a feature
- Email sreejap974@gmail.com for anything private
