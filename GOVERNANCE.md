# Governance

This document describes who is responsible for what in flowmcp and how decisions are made.

---

## Project Roles

### Maintainer

**Current maintainer:** [SreejaPasula](https://github.com/SreejaPasula)

Responsibilities:
- Set the project direction and roadmap
- Triage issues and label them
- Review and merge pull requests
- Publish releases and update CHANGELOG.md
- Enforce the Code of Conduct
- Manage repository settings, branch protection, and access
- Respond to security vulnerability reports

A maintainer has write access to the repository. There is currently one maintainer. Additional maintainers can be added over time (see [Becoming a Maintainer](#becoming-a-maintainer)).

---

### Contributor

Anyone who opens an issue, submits a PR, or participates in discussions is a contributor.

Responsibilities:
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- Sign the [CLA](CLA.md) before their first PR is merged and use `git commit -s` (DCO sign-off) on every commit — see [CONTRIBUTING.md](CONTRIBUTING.md#signing-the-cla)
- Respond to review feedback within a reasonable time (2 weeks)
- Write tests and documentation for their changes

Contributors do not have write access to the repository. They work via forks and pull requests.

---

### Reviewer

A contributor who is regularly active and whose PRs have consistently been of high quality may be invited to review other contributors' PRs.

Responsibilities:
- Review PRs for correctness, tests, style, and license compliance
- Leave constructive, specific feedback
- Not merge PRs — only approve or request changes

A reviewer does not have write access. Merging is always done by a maintainer.

---

## Decision Making

### Day-to-day decisions

The maintainer makes routine decisions independently:
- Labelling and triaging issues
- Merging or closing PRs
- Releasing patch versions (0.1.x)

### Feature decisions

For significant new features, the maintainer opens a GitHub issue with the `enhancement` label and invites public comment for at least 7 days before implementation begins.

### Breaking changes

Any change that removes or renames a public API:
- Requires a GitHub issue discussed for at least 14 days
- Requires a `breaking change` label on the PR
- Results in a minor version bump (0.x.0)
- Must include a migration guide in the PR description

### Disputes

If a contributor disagrees with a decision:
1. Comment on the relevant issue or PR with a clear rationale
2. If unresolved, email sreejap974@gmail.com
3. The maintainer makes the final call

---

## Releases

| Version type | Trigger | Who |
|-------------|---------|-----|
| Patch (0.1.x) | Bug fixes, small improvements | Maintainer, as needed |
| Minor (0.x.0) | New features, non-breaking additions | Maintainer, after review period |
| Major (x.0.0) | Breaking API changes | Maintainer, after extended review |

Steps for a release:
1. Update `CHANGELOG.md` — move items from `[Unreleased]` to the new version section
2. Bump the version in `python/pyproject.toml` and `java/pom.xml`
3. Tag the commit: `git tag v0.x.y`
4. Push the tag: `git push origin v0.x.y`
5. Create a GitHub Release with the changelog notes

---

## Becoming a Maintainer

A contributor can be invited to become a maintainer if they:
- Have had at least 5 PRs merged
- Are active on issues and reviews over at least 2 months
- Demonstrate good judgement and alignment with the project's goals

The current maintainer extends the invitation. The candidate must accept and sign a private maintainer agreement via email.

---

## Stepping Down

A maintainer who can no longer fulfil their responsibilities should:
1. Announce this in a GitHub Discussion with at least 2 weeks notice
2. Help transition ownership by identifying a replacement contributor
3. Transfer admin access before stepping down

If a maintainer becomes unreachable and the project is inactive for more than 3 months, any contributor may open an issue to discuss transferring stewardship.

---

## Code of Conduct Enforcement

Code of Conduct violations are handled by the maintainer privately via email (sreejap974@gmail.com).

| Severity | Action |
|---------|--------|
| First offence, minor | Private warning |
| Repeat or moderate | Temporary ban from issues/PRs |
| Severe or repeated | Permanent ban and removal of any access |

Decisions on bans are final.

---

## Changes to This Document

Changes to this governance document follow the same process as breaking changes — a GitHub issue open for at least 14 days, then a PR by the maintainer.
