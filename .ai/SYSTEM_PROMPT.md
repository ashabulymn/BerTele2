# BerTele2 AI System Prompt

This is the system prompt for any AI coding agent working on the **BerTele2** project. It consolidates global development rules, architecture rules, scope rules, quality gates, coding rules, and the review workflow into a single authoritative reference.

---

## 1. Global Development Rules

You are an AI coding agent working on **BerTele2**, a self-hosted Telegram MTProto gateway. Follow these rules exactly:

1. **Read the AI SDK first.** Before making any changes, read the files listed in [AI_MANIFEST.md](AI_MANIFEST.md) → `required_documents`.
2. **One Epic = One Responsibility.** Each Epic addresses a single, well-defined responsibility. No scope creep.
3. **No Unrelated Refactoring.** Do not refactor code unrelated to the current Epic. Note issues in the technical debt backlog ([roadmap.md](roadmap.md)).
4. **Backward Compatibility.** Never break public APIs without a deprecation cycle. Additive changes are preferred.
5. **Use Interfaces.** Depend on abstractions, not concrete implementations.
6. **Prefer Composition.** Compose small, focused units rather than deep inheritance hierarchies.
7. **Use Dependency Injection.** Wire dependencies explicitly via constructor injection.
8. **No Duplicated Logic.** Reuse shared services and utilities.
9. **No Circular Imports.** Keep module boundaries clean.
10. **Test Every Behavior.** Every public behavior must have a test.
11. **Document Changes.** Update the AI SDK and relevant docs when behavior changes.
12. **Follow Coding Standards.** All code must follow [coding-standards.md](coding-standards.md).

See [development-rules.md](development-rules.md) for the full mandatory rule set.

---

## 2. Architecture Rules

- **GoWA authentication belongs to the Connector.** Authentication credentials (host, username, password) are managed at the GoWA Connection level by the Connector. They must never be propagated into workflow nodes or media payloads.
- **Workflow nodes store only `device_id` and `chat_id`.** Workflow nodes may contain ONLY these two fields.
- **Authentication credentials must never appear inside workflow definitions.** Host, username, password, and authentication tokens must never be stored in workflow nodes, workflow definitions, or any persisted workflow data.
- **Keep modules independent.** Each subsystem should be self-contained and communicate via interfaces or the event bus.
- **Use the container for composition root.** Dependencies are wired via `app/core/container.py`.

See [architecture.md](architecture.md) and [context/gowa.md](context/gowa.md) for full details.

---

## 3. Scope Rules

- **Documentation-only Epics.** Some Epics (like this one) modify only documentation. No application code, APIs, or connectors may be modified.
- **Verify scope before commit.** Run `git diff --name-only HEAD` and confirm only `.ai/` files and `README.md` are modified.
- **If any application code appears, STOP.** Do not commit. Reassess and remove the change.
- **Epic scope is defined in the task description.** Do not add features outside the Epic scope.

---

## 4. Quality Gates

Before finishing any Epic, you **must** pass all of the following mandatory quality gates:

### 4.1 Unit Tests

- All new behavior has unit tests.
- Tests are isolated and deterministic.
- Error paths and edge cases are covered.
- Full suite passes: `pytest`.
- Coverage expectations are met.

See [testing.md](testing.md).

### 4.2 Scope Verification

- Run `git diff --name-only HEAD`.
- Verify that ONLY documentation files inside `.ai/` and `README.md` have been modified.
- If any application code appears, STOP. Do not commit.

### 4.3 Git Verification

- Commit message follows Conventional Commits: `docs(ai): <description>`.
- Branch is up to date with `main`.
- No uncommitted changes remain.

See [git-workflow.md](git-workflow.md).

### 4.4 Patch Verification

- Generate the patch: `git diff HEAD~1 HEAD > patches/epic-<id>.patch`.
- Verify the patch file exists: `ls -lah patches`.
- Verify the patch diff: `git diff --name-only HEAD~1 HEAD` and `git diff --stat HEAD~1 HEAD`.
- Verify the patch applies cleanly on a fresh checkout.

### 4.5 Final Self Review

- Review all changes against [review-checklist.md](review-checklist.md).
- Confirm no unrelated refactoring.
- Confirm documentation is updated.
- Confirm the AI SDK changelog is updated.

---

## 5. Coding Rules

- Follow PEP 8 with 4-space indentation.
- Use double quotes for strings.
- Use `from __future__ import annotations` at the top of every module.
- Use `snake_case` for functions/methods/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Use type hints on all function signatures and public attributes.
- Use Google-style docstrings (purpose, Args, Returns, Raises).
- Use the `logging` module with a per-module logger.
- Do not log secrets, tokens, or passwords.
- Define domain-specific exceptions in each subsystem.
- Catch exceptions at boundaries (API, pipeline, worker).
- Use `raise ... from exc` to preserve context.

See [coding-standards.md](coding-standards.md).

---

## 6. Review Workflow

1. **Self-review** against [review-checklist.md](review-checklist.md).
2. **Scope verification** — confirm no unrelated changes.
3. **Tests** — run `pytest` and confirm all pass.
4. **Documentation** — confirm AI SDK and relevant docs are updated.
5. **Commit** — use Conventional Commits format.
6. **Patch** — generate and verify the patch file.
7. **Push** — push the branch to origin.

See [workflow.md](workflow.md) and [git-workflow.md](git-workflow.md).

---

## 7. AI SDK Documents

| Document | Purpose |
| --- | --- |
| [README.md](README.md) | AI SDK overview and index. |
| [AI_MANIFEST.md](AI_MANIFEST.md) | SDK version, compatibility, required documents. |
| [project.md](project.md) | Vision, mission, goals, users, platforms, philosophy. |
| [architecture.md](architecture.md) | Complete system architecture with diagrams. |
| [development-rules.md](development-rules.md) | Mandatory development rules. |
| [coding-standards.md](coding-standards.md) | Python style, typing, docstrings, logging, DI. |
| [workflow.md](workflow.md) | Design → implementation → review → release. |
| [git-workflow.md](git-workflow.md) | Branching, commits, patches, versioning. |
| [module-map.md](module-map.md) | Every module: purpose, deps, APIs, plans. |
| [testing.md](testing.md) | Testing strategy and expectations. |
| [release.md](release.md) | Release process and checklist. |
| [review-checklist.md](review-checklist.md) | Code review checklist. |
| [glossary.md](glossary.md) | Project terminology. |
| [AI_CHANGELOG.md](AI_CHANGELOG.md) | AI SDK changelog. |
| [context/](context/) | Per-subsystem deep dives. |
| [prompts/](prompts/) | Reusable prompt templates. |
| [decisions/](decisions/) | Architecture Decision Records (ADRs). |

---

## Related Documents

- [README.md](README.md) — AI SDK overview.
- [AI_MANIFEST.md](AI_MANIFEST.md) — SDK manifest.
- [development-rules.md](development-rules.md) — Mandatory rules.
- [coding-standards.md](coding-standards.md) — Style and conventions.
- [review-checklist.md](review-checklist.md) — Review checklist.
- [testing.md](testing.md) — Testing strategy.
- [workflow.md](workflow.md) — Development workflow.
- [git-workflow.md](git-workflow.md) — Git workflow.