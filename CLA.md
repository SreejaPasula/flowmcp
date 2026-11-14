# Contributor License Agreement

By submitting a pull request to flowmcp, you agree that:

1. **You own the code** — the contribution is your original work and you have the right to submit it.
2. **You grant a license** — you grant the flowmcp project maintainers a perpetual, worldwide, non-exclusive, royalty-free license to use, copy, modify, and distribute your contribution as part of this project under the MIT License.
3. **No warranty** — your contribution is provided "as is", without warranty of any kind.
4. **You understand** — contributing to an open source project does not give you any ownership of the project itself.

This agreement follows the standard [Individual Contributor License Agreement](https://www.apache.org/licenses/icla.pdf) used across major open source projects.

---

## How flowmcp enforces the CLA

flowmcp uses a **comment-based CLA** enforced automatically by the CLA Assistant GitHub Action on every pull request.

To sign, post this exact comment on your PR:

```
I have read the CLA Document and I hereby sign the CLA
```

You only need to sign once. All your future PRs are covered. See [CONTRIBUTING.md](CONTRIBUTING.md#signing-the-cla) for full instructions.

---

## Types of CLA Signing in Open Source

Different open source projects use different CLA mechanisms. Here is a clear explanation of each type so contributors understand what they are signing and why.

---

### 1. Individual CLA (ICLA)

**What it is:** Signed by a single developer contributing in a personal capacity.

**How it works:** The contributor agrees that their code is their own original work and grants the project a license to use it. This is the most common CLA in OSS.

**Who uses it:** Apache Software Foundation, Google (Android, Chromium), Oracle, MongoDB

**When to use:** When you are contributing on your own time, not as part of your job.

---

### 2. Corporate CLA (CCLA) / Entity CLA

**What it is:** Signed by a company or organisation on behalf of its employees.

**How it works:** A manager or legal representative signs once on behalf of the company. All employees named under that agreement can then contribute without signing individually.

**Who uses it:** Apache Software Foundation, Google, Microsoft Azure OSS projects

**When to use:** When you are contributing as part of your job and your employer owns the intellectual property of your work. If unsure, check with your employer's legal team.

> **flowmcp note:** If you are contributing on behalf of a company, email sreejap974@gmail.com before opening a PR so we can set up a corporate agreement.

---

### 3. Developer Certificate of Origin (DCO)

**What it is:** A lightweight alternative to a CLA. The contributor adds a `Signed-off-by` line to every commit message certifying the code is theirs to submit.

**How it works:**
```bash
git commit -s -m "feat: add Gemini provider"
# Adds: Signed-off-by: Your Name <you@example.com>
```

**Who uses it:** Linux Kernel, Kubernetes, CNCF projects, GitLab, Node.js

**Why some projects prefer it:** No external service, no bot, no blocking — just a line in the commit. It is simpler but gives the project less legal protection than a CLA.

**flowmcp does not use DCO** — we use an ICLA via the CLA bot because it provides stronger IP clarity for a framework that LLM providers and enterprises may integrate with.

---

### 4. Click-through CLA (Web Form)

**What it is:** A web form where a contributor clicks "I agree" to sign the CLA. Often tied to a login via GitHub OAuth.

**How it works:** The contributor visits a URL (e.g. cla-assistant.io), reads the agreement, and clicks a button. Their GitHub username is recorded.

**Who uses it:** SAP, Microsoft (older repos), JetBrains

**Advantage:** Clear audit trail with timestamps and legal name. Good for enterprise projects.

---

### 5. Comment-based CLA (what flowmcp uses)

**What it is:** A contributor signs by posting a specific comment on their pull request. The bot records their GitHub username in the repository.

**How it works:**
1. Contributor opens a PR
2. The CLA bot comments asking them to sign
3. Contributor posts: `I have read the CLA Document and I hereby sign the CLA`
4. The bot marks the check as passed and stores the username in `signatures/cla.json`

**Who uses it:** Many GitHub-native projects using [contributor-assistant/github-action](https://github.com/contributor-assistant/github-action)

**Why flowmcp uses this:** It is the most accessible approach — no external website, no OAuth, no context switching. The contributor never leaves GitHub.

---

### 5. No CLA (permissive projects)

**What it is:** Some projects, particularly those under very permissive licences like MIT or BSD, skip the CLA entirely and rely on the licence itself to govern contributions.

**Who uses it:** FastAPI, pydantic, requests, many small OSS libraries

**Risk:** Without a CLA, the project has less legal clarity about whether contributors can later revoke their contribution or dispute licensing. For small libraries with no commercial backing this is usually acceptable.

---

## Comparison

| Type | Effort for contributor | Legal strength | Used by |
|------|----------------------|----------------|---------|
| Individual CLA (ICLA) | Low — sign once | High | Apache, Google |
| Corporate CLA (CCLA) | Low for employees, legal sign-off needed once | High | Apache, Microsoft |
| DCO | Very low — one flag per commit | Medium | Linux, Kubernetes |
| Click-through CLA | Low — one click on a website | High | SAP, JetBrains |
| Comment-based CLA | Very low — one comment on PR | Medium-High | flowmcp, GitHub-native projects |
| No CLA | None | Low | FastAPI, requests |

---

*This CLA is enforced automatically via the CLA Assistant GitHub Action on every pull request.*
