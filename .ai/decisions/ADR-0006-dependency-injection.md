# ADR-0006: Dependency Injection

## Status

Accepted

## Context

BerTele2 services need to be testable, decoupled, and configurable. Global singletons and module-level mutable state make testing and extension difficult.

## Decision

Adopt **constructor-based dependency injection**:

- Services receive their dependencies as constructor arguments.
- Use `dataclass` or explicit `__init__` for wiring.
- Use a composition root (`AppContainer`) to wire the application.
- Avoid global singletons and module-level mutable state.
- Use `Protocol` or ABC interfaces for extension points.

## Consequences

- Services are testable in isolation (mock dependencies).
- Dependencies are explicit and discoverable.
- The composition root centralizes wiring.
- Requires discipline to avoid global state.

## Alternatives Considered

- **Global singletons**: Rejected — hard to test and extend.
- **Service locator**: Rejected — hides dependencies.
- **No DI**: Rejected — tight coupling.

---

## Related Documents

- [context/core.md](../context/core.md) — Core subsystem.
- [coding-standards.md](../coding-standards.md) — DI conventions.
- [development-rules.md](../development-rules.md) — Mandatory rules.
- [architecture.md](../architecture.md) — System architecture.