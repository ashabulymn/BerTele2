# BerTele2 Git Workflow

This document defines the git workflow for BerTele2.

## Branch Strategy

- **`main`** — stable, release-ready branch.
- **Feature branches** — one per Epic: `epic/<id>-<short-name>`.
- **Bugfix branches** — `fix/<short-name>`.
- **Refactor branches** — `refactor/<short-name>`.

## Commit Style

Use **Conventional Commits**:

```
<type>(<scope>): <description>
```

Types:

| Type | Purpose |
| --- | --- |
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `refactor` | Refactoring |
| `test` | Tests |
| `chore` | Maintenance |
| `build` | Build/deps |
| `ci` | CI config |

Examples:

```
feat(media): add S3 storage provider
fix(telegram): handle reconnect timeout
docs(ai): introduce BerTele2 AI Development Kit
test(events): add broker integration tests
```

## Patch Generation

After committing an Epic:

```bash
mkdir -p patches
git diff HEAD~1 HEAD > patches/epic-<id>.patch
```

Verify the patch applies cleanly on a fresh checkout.

## Push Workflow

```bash
git push origin $(git branch --show-current)
```

## Merge Strategy

- Use **squash merge** for feature branches into `main`.
- Keep the commit history clean and linear.
- Resolve conflicts carefully; do not force-push shared branches.

## Versioning

Follow **Semantic Versioning** (MAJOR.MINOR.PATCH):

- **MAJOR** — breaking changes.
- **MINOR** — backward-compatible features.
- **PATCH** — backward-compatible bug fixes.

See [release.md](release.md) for the release process.

---

## Related Documents

- [workflow.md](workflow.md) — Development workflow.
- [release.md](release.md) — Release process.
- [roadmap.md](roadmap.md) — Milestones and epics.