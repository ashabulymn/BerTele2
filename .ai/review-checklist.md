# BerTele2 Code Review Checklist

Use this checklist when reviewing any code change on BerTele2.

## Quality Gates

Before finishing any Epic, you **must** pass all of the following mandatory quality gates:

- [ ] **Unit Tests** — All new behavior has unit tests; full suite passes (`pytest`).
- [ ] **Scope Verification** — Run `git diff --name-only HEAD`; only `.ai/` files and `README.md` may be modified.
- [ ] **Git Verification** — Commit message follows Conventional Commits; branch is up to date.
- [ ] **Patch Verification** — Generate and verify the patch file.
- [ ] **Final Self Review** — Review against this checklist.

See [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) for the full quality gate definitions.

## Architecture

- [ ] Change matches the Epic scope (no unrelated refactoring).
- [ ] Follows the architecture in [architecture.md](architecture.md).
- [ ] Uses interfaces and dependency injection.
- [ ] Keeps modules independent (no circular imports).
- [ ] No duplicated logic.

## SOLID

- [ ] **S**ingle Responsibility: each class/function has one job.
- [ ] **O**pen/Closed: extension without modification.
- [ ] **L**iskov: subclasses are substitutable.
- [ ] **I**nterface Segregation: small, focused interfaces.
- [ ] **D**ependency Inversion: depend on abstractions.

## Testing

- [ ] New behavior has unit tests.
- [ ] Tests are isolated and deterministic.
- [ ] Error paths and edge cases are covered.
- [ ] Full suite passes (`pytest`).
- [ ] Coverage expectations are met.

## Documentation

- [ ] Docstrings are accurate (Google style).
- [ ] AI SDK and relevant docs are updated.
- [ ] ADR added for significant decisions.
- [ ] CHANGELOG updated if behavior changed.
- [ ] AI CHANGELOG updated if AI SDK changed.

## Performance

- [ ] No obvious performance regressions.
- [ ] No blocking I/O in async paths.
- [ ] No unbounded memory growth.

## Security

- [ ] No secrets in code or logs.
- [ ] Input is validated.
- [ ] Authentication/authorization is enforced where needed.
- [ ] No SQL injection or unsafe deserialization.

## Maintainability

- [ ] Code is readable and well-named.
- [ ] Functions are small and focused.
- [ ] No dead code or unused imports.
- [ ] Follows [coding-standards.md](coding-standards.md).
- [ ] Follows [development-rules.md](development-rules.md).

---

## Related Documents

- [development-rules.md](development-rules.md) — Mandatory rules.
- [coding-standards.md](coding-standards.md) — Style and conventions.
- [testing.md](testing.md) — Testing strategy.
- [SYSTEM_PROMPT.md](SYSTEM_PROMPT.md) — System prompt and quality gates.
- [prompts/review-template.md](prompts/review-template.md) — Review prompt template.