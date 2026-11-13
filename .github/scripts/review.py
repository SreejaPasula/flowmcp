import urllib.request
import json
import os
import sys

def read_file(path, fallback=""):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except FileNotFoundError:
        return fallback

diff = read_file("pr_diff.txt")
changed_files = read_file("changed_files.txt")
contributing = read_file("CONTRIBUTING.md")

if not diff.strip():
    with open("review.txt", "w") as f:
        f.write("No code changes detected in this PR.")
    sys.exit(0)

if len(diff) > 15000:
    diff = diff[:15000] + "\n\n[diff truncated — showing first 15000 chars]"

prompt = """You are a strict but fair OSS maintainer reviewing a pull request for **flowmcp** — a simple RAG + MCP + LLM pipeline framework (Python + Java).

Your job is to thoroughly review this PR and give the maintainer a clear report so they can decide whether to merge or request changes. The maintainer always merges manually — you never merge.

## Changed files
{changed_files}

## Code Diff
{diff}

## CONTRIBUTING.md (project guidelines)
{contributing}

---

Review across ALL of these dimensions. Be specific — reference file names and line numbers.

### 1. CORRECTNESS
- Does the code do what the PR claims?
- Any bugs, logic errors, or wrong behaviour?

### 2. EDGE CASES
- Empty inputs, None values, special characters, large inputs
- Will this break for any realistic input?

### 3. TESTS
- Are tests included?
- Do they cover real cases or just the happy path?

### 4. CONTRIBUTING.md COMPLIANCE
- Does the PR follow the project contribution guidelines?

### 5. LICENSE
- Any new dependencies with incompatible licenses?
- Any missing license headers?

### 6. SECURITY
- Hardcoded secrets or API keys?
- Any input going directly to shell, file path, or eval?
- Any suspicious new dependency?

### 7. CODE QUALITY
- Consistent with existing codebase style?
- Any dead code, unused imports, debug statements left in?

### 8. BREAKING CHANGES
- Does this break any existing public API or behaviour?

---

Respond in exactly this format:

## flowmcp PR Review

**Verdict:** SAFE TO MERGE / NEEDS CHANGES / DO NOT MERGE

**What this PR does:**
(one clear sentence)

---

### Correctness
(findings or "No issues found")

### Edge Cases
(findings or "All major edge cases handled")

### Tests
(findings or "Tests are adequate")

### Contributing Guidelines
(findings or "Follows guidelines")

### License
(findings or "No license issues")

### Security
(findings or "No security concerns")

### Code Quality
(findings or "Clean and consistent")

### Breaking Changes
(findings or "No breaking changes")

---

### Action Required
(If NEEDS CHANGES or DO NOT MERGE: exact bullet list of what the contributor must fix.
If SAFE TO MERGE: "No action needed — maintainer can merge when ready.")

---
*Automated review — final merge decision is always made by the maintainer.*""".format(
    changed_files=changed_files,
    diff=diff,
    contributing=contributing
)

payload = json.dumps({
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 2048,
    "temperature": 0.2
}).encode()

req = urllib.request.Request(
    "https://models.inference.ai.azure.com/chat/completions",
    data=payload,
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ["GITHUB_TOKEN"]
    }
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read())
    review = result["choices"][0]["message"]["content"]

with open("review.txt", "w") as f:
    f.write(review)

print(review)
