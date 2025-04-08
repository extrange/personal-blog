---
date: 2025-04-08
categories:
  - Programming
---

# My Git Workflow

This is my preferred Git workflow for projects.

<!-- more -->

## Branches

- `main`
- `dev` (default)
- Feature branches as necessary (merged to `dev`).

**Renovate pushes updates to `dev`.** This lets us do fast-forward merges to `main`, keeping the history clean.

**CI checks (linting, static analysis, tests) run on pushes to `dev`.**

**Deployment is triggered on pushes to `main`.**

**Deployment artifacts are triggered on tag pushes to `main`.** A Github Release is also created. Together with [Semantic Versioning] and [Conventional Commits], this lets us keep track of what changes are included in each release (which is deployed to production). _Ideally, there should be a separate production/staging branch which deploys to the respective environments, if at all possible._

[Semantic Versioning]: https://semver.org/
[Conventional Commits]: https://www.conventionalcommits.org/en/v1.0.0/
