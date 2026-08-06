# ADR-0001: Project Vision

## Status

Accepted

## Context

BerTele2 needed a clear vision to guide development. The project is a self-hosted Telegram MTProto gateway that connects Telegram to external automation platforms.

## Decision

Adopt the vision of a **self-hosted Telegram MTProto gateway** with:

- A unified REST + WebSocket API.
- A pluggable media pipeline.
- An event-driven architecture.
- A plugin SDK for connectors.
- A dashboard for observability.
- Strong security (JWT, API keys, roles).

## Consequences

- Development is guided by a clear, consistent vision.
- New features are evaluated against the vision.
- The architecture supports extensibility and observability.

## Alternatives Considered

- **Cloud-only gateway**: Rejected — self-hosting is a core requirement.
- **Monolithic single-purpose app**: Rejected — extensibility is required.
- **No dashboard**: Rejected — observability is a goal.

---

## Related Documents

- [project.md](../project.md) — Project vision.
- [architecture.md](../architecture.md) — System architecture.