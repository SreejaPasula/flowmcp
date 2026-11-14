# Contributing to flowmcp

Thank you for your interest in contributing! This document is your single reference — it covers setup, templates for issues and PRs, and all policies.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Signing the CLA](#signing-the-cla)
5. [DCO Sign-off](#dco-sign-off)
6. [Issue Templates](#issue-templates)
   - [Bug Report](#-bug-report-template)
   - [Feature Request](#-feature-request-template)
7. [Pull Request Template](#pull-request-template)
8. [Policies](#policies)
9. [Code Style](#code-style)
10. [Good First Issues](#good-first-issues)
11. [Questions](#questions)

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

1. **Find or create an issue** — pick one labeled [`good first issue`](https://github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22) or open a new one using the templates below
2. **Comment on the issue** to let maintainers know you are working on it
3. **Fork the repo** and create a branch: `git checkout -b feature/my-feature`
4. **Make your change** — add tests, update docs if needed
5. **Open a PR** — fill in the PR template below exactly as shown
6. **Respond to review feedback** — the automated review bot and maintainers will leave comments
7. **Sign the CLA** — the CLA bot will prompt you automatically on your first PR (see [Signing the CLA](#signing-the-cla) below)
8. **DCO sign-off** — every commit must include a `Signed-off-by` line (see [DCO Sign-off](#dco-sign-off) below)

---

## Signing the CLA

All contributors must sign the **Contributor License Agreement (CLA)** before their first PR can be merged. You only need to sign once — your signature covers all future contributions.

### What is the CLA?

The CLA confirms that:
- The code is your original work and you have the right to submit it
- You grant the flowmcp project a license to use your contribution under MIT
- Read the full agreement: [CLA.md](CLA.md)

### How to sign

When you open a PR for the first time, the CLA bot will automatically post a comment like this on your PR:

> *"Thank you for your submission. Please sign our Contributor License Agreement before we can accept your contribution."*

**To sign, post a comment on your PR with exactly this text:**

```
I have read the CLA Document and I hereby sign the CLA
```

> **Important:** Copy the text exactly as shown above — the bot does an exact match.

Once you post that comment, the CLA check will turn green within seconds. You only need to do this **once** — all your future PRs will pass the CLA check automatically.

### Already have a PR open?

If you opened a PR before the CLA check was set up, a maintainer will comment `recheck` on your PR to trigger the bot. You will then see the sign instruction appear — just post the comment above and you are done.

### CLA check is failing — what to do

| Problem | Fix |
|---------|-----|
| Bot hasn't commented yet | Ask the maintainer to comment `recheck` on your PR |
| You posted the comment but check is still red | Wait 30 seconds and refresh — the bot may still be processing |
| You signed on one PR but another PR still shows unsigned | Comment `recheck` on the other PR to sync |
| You disagree with the CLA terms | Email sreejap974@gmail.com before contributing |

---

## DCO Sign-off

In addition to the CLA, every **commit** in your PR must carry a `Signed-off-by` line. This is the same mechanism used by the **Linux kernel, Kubernetes, and GitLab**.

It certifies that the code is your original work and you have the right to submit it under the project's licence. Read the full [Developer Certificate of Origin](DCO.md).

### How to sign each commit

Add the `-s` flag every time you commit. Here are real examples based on flowmcp contributions:

```bash
# Adding a new LLM provider
git commit -s -m "feat: add Gemini provider for Python LLM module"

# Fixing a bug
git commit -s -m "fix: handle empty query string in RAG retriever"

# Writing tests
git commit -s -m "test: add edge cases for OllamaClient JSON escaping"

# Updating docs
git commit -s -m "docs: add streaming usage example to README"
```

Each of these automatically appends a line like this to the commit message:

```
feat: add Gemini provider for Python LLM module

Signed-off-by: Alex Rivera <alex.rivera@example.com>
```

> Git uses your `user.name` and `user.email` to fill in the sign-off. Make sure they match how you want to appear in the project history:
>
> ```bash
> git config --global user.name "Alex Rivera"
> git config --global user.email "alex.rivera@example.com"
> ```

### Forgot to sign a commit?

**You added one commit and forgot `-s`:**

```bash
# You ran: git commit -m "fix: correct chunker overlap calculation"
# Fix it like this:
git commit --amend -s --no-edit
git push --force-with-lease
```

**You have several commits in the branch, none of them signed:**

```bash
# For example, a branch with 3 commits:
# feat: scaffold GeminiClient for Java
# feat: implement GeminiClient.complete()
# test: add GeminiClient unit tests

git rebase --signoff HEAD~3
git push --force-with-lease
```

### DCO check is failing — what to do

| Problem | Fix |
|---------|-----|
| One unsigned commit at the tip | `git commit --amend -s --no-edit && git push --force-with-lease` |
| Several unsigned commits | `git rebase --signoff HEAD~N` where N = number of commits in your PR |
| Sign-off has the wrong name or email | Update git config, then `git commit --amend -s --no-edit` |
| Check still red after fixing | Push an empty amend to re-trigger: `git commit --amend --no-edit && git push --force-with-lease` |

---

## Issue Templates

When opening a new issue on GitHub, copy and fill in the relevant template below.

---

### 🐛 Bug Report Template

> Use this when something is not working as expected.
> **Title format:** `[Bug] short description of the problem`
> **Label to add:** `bug`

```markdown
**What happened?**
(Describe what actually happened — include error messages or unexpected output)

**What did you expect?**
(Describe what you expected to happen instead)

**Steps to reproduce:**
1. 
2. 
3. 

**Minimal code example:**
​```python
# Paste the smallest code that reproduces the issue
​```

**Environment:**
- flowmcp version:
- Python / Java version:
- LLM provider (OpenAI / Anthropic / Ollama / Gemini):
- Operating system:
```

---

### ✨ Feature Request Template

> Use this to propose a new feature or improvement.
> **Title format:** `[Feature] short description of the feature`
> **Label to add:** `enhancement`

```markdown
**What problem does this solve?**
(Describe the gap, limitation, or pain point this feature addresses)

**Describe the solution you'd like:**
(Describe what should be built and how it should behave)

**Example API (if applicable):**
​```python
# Show how you would use this feature once it exists
from flowmcp import Pipeline

pipeline = Pipeline(llm="openai/gpt-4")
# ...
​```

**Alternatives you have considered:**
(List any other approaches you thought of and why they are not ideal)

**Additional context:**
(Screenshots, links, references — anything that helps explain the request)
```

---

## Pull Request Template

> Every PR must fill in this template. Copy it when opening a PR on GitHub.
> A PR that skips sections or leaves the checklist unticked will be asked to update before review begins.

```markdown
## What does this PR do?
(Briefly describe the change and what problem it solves)

Fixes #

---

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactor (no behaviour change)
- [ ] Other (describe):

---

## Checklist
- [ ] I have read CONTRIBUTING.md
- [ ] My code follows the existing style of the project
- [ ] I have added tests that cover my changes
- [ ] All existing tests pass (`pytest tests/` or `mvn verify`)
- [ ] I have updated documentation or comments where needed
- [ ] I have not introduced any breaking changes to the existing API
- [ ] I have not hardcoded any secrets, API keys, or credentials
- [ ] My changes do not introduce dependencies with incompatible licenses
- [ ] I have signed the CLA (the bot will prompt me if this is my first PR)

---

## How has this been tested?
(Describe how you verified your change works — include command output or screenshots if helpful)

---

## Breaking changes (if any)
(If this PR changes or removes a public API, describe what breaks and how users should migrate)
```

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
- The automated PR review bot comments on every PR — read its output and address flagged issues before requesting human review
- Stale reviews are dismissed when new commits are pushed
- Address all review comments before requesting a re-review

### Merge Policy

- **Only maintainers merge PRs** — contributors do not merge their own work
- PRs are merged once: CI passes + 1 approval + all checklist items ticked + CLA signed
- We use **squash and merge** to keep a clean commit history on `main`

### Breaking Changes

- Any change that removes or renames a public API requires a `breaking change` label
- Must be discussed in a GitHub issue for at least 14 days before the PR is opened
- Requires a migration guide in the PR description
- Results in a minor version bump (0.x.0)

### Security

- Do not open public issues for security vulnerabilities
- Report them privately by email following [SECURITY.md](SECURITY.md)

### Licensing

- All contributions are licensed under MIT (see [LICENSE](LICENSE))
- By submitting a PR you confirm the code is your own original work and you agree to the [CLA](CLA.md)
- Do not copy code from projects with incompatible licences (GPL, AGPL, etc.)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

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

Small, well-defined tasks ideal for a first contribution:

| Issue | Description | Skill |
|-------|-------------|-------|
| [#1](https://github.com/SreejaPasula/flowmcp/issues/1) | Add Gemini provider for Python | Python |
| [#2](https://github.com/SreejaPasula/flowmcp/issues/2) | Implement OpenAI client for Java | Java |
| [#3](https://github.com/SreejaPasula/flowmcp/issues/3) | Implement Anthropic client for Java | Java |
| [#4](https://github.com/SreejaPasula/flowmcp/issues/4) | Add PDF support to RAG loader | Python |
| [#5](https://github.com/SreejaPasula/flowmcp/issues/5) | Add streaming support to Python Pipeline | Python |
| [#6](https://github.com/SreejaPasula/flowmcp/issues/6) | Add embedding-based retrieval | Python |

Browse all: [`good first issue`](https://github.com/SreejaPasula/flowmcp/issues?q=label%3A%22good+first+issue%22)

---

## Questions?

- Open a [GitHub Discussion](https://github.com/SreejaPasula/flowmcp/discussions) for general questions
- Open an issue if you found a bug or want to propose a feature
- Email sreejap974@gmail.com for anything private
