# BerTele2 Development Rules

These are **mandatory** rules for all development on BerTele2. Every Epic, bugfix, refactor, and release must comply.

## Core Rules

1. **One Epic = One Responsibility.** Each Epic addresses a single, well-defined responsibility. No scope creep.

2. **No Unrelated Refactoring.** Do not refactor code unrelated to the current Epic. If you find an issue, note it in the technical debt backlog ([roadmap.md](roadmap.md)) and address it in a separate Epic.

3. **Backward Compatibility.** Never break public APIs without a deprecation cycle. Additive changes are preferred.

4. **Use Interfaces.** Depend on abstractions, not concrete implementations. Define `Protocol` or ABC interfaces for extension points.

5. **Prefer Composition.** Compose small, focused units rather than deep inheritance hierarchies.

6. **Use Dependency Injection.** Wire dependencies explicitly via constructor injection. Avoid global singletons and module-level mutable state.

7. **No Duplicated Logic.** Reuse shared services and utilities. If logic is needed in two places, extract it.

8. **No Circular Imports.** Keep module boundaries clean. Import at the top of the module; use `TYPE_CHECKING` for type-only imports.

9. **Keep Modules Independent.** Each subsystem should be self-contained and communicate via interfaces or the event bus.

10. **Test Every Behavior.** Every public behavior must have a test. See [testing.md](testing.md).

11. **Document Changes.** Update the AI SDK and relevant docs when behavior changes.

12. **Follow Coding Standards.** All code must follow [coding-standards.md](coding-standards.md).

## Additional Rules

- **No secrets in code.** Use environment variables and `.env`.
- **No silent failures.** Log errors and raise domain-specific exceptions.
- **No dead code.** Remove unused imports, functions, and files.
- **No broad `except Exception`** without handling or re-raising.
- **Keep functions small.** Prefer many small functions over one large one.
- **Name things clearly.** Use descriptive names that convey intent.

## Enforcement

- Code reviews check compliance with these rules. See [review-checklist.md](review-checklist.md).
- CI runs tests and linters.
- AI agents must follow these rules when contributing.

---

## Related Documents

- [coding-standards.md](coding-standards.md) — Style and conventions.
- [workflow.md](workflow.md) — Development workflow.
- [review-checklist.md](review-checklist.md) — Review checklist.
- [roadmap.md](roadmap.md) — Technical debt backlog.