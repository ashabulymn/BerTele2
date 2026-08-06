# ADR-0005: Event-Driven Architecture

## Status

Accepted

## Context

BerTele2 subsystems (Telegram, media, plugins, webhooks) need to communicate without tight coupling. A decoupled communication mechanism is required.

## Decision

Adopt an **event-driven architecture** with an in-process event bus:

- `EventBroker` — facade wiring publisher, dispatcher, registry, and queue.
- `EventPublisher` — publishes events.
- `EventDispatcher` — dispatches events to subscribers.
- `EventRegistry` — registers event types and subscribers.
- `EventQueue` — in-process queue.
- Typed events (e.g., `PipelineDispatchStarted`, `PipelineDispatchCompleted`, `PipelineDispatchFailed`).

## Consequences

- Subsystems are decoupled.
- New subscribers can be added without modifying publishers.
- Events provide observability.
- Requires careful event design and error handling.

## Alternatives Considered

- **Direct method calls**: Rejected — tight coupling.
- **Message queue (external)**: Rejected — too heavy for in-process needs.
- **No event system**: Rejected — decoupling is required.

---

## Related Documents

- [context/eventbus.md](../context/eventbus.md) — Event bus subsystem.
- [context/telegram.md](../context/telegram.md) — Pipeline events.
- [context/plugins.md](../context/plugins.md) — Plugin event access.
- [architecture.md](../architecture.md) — System architecture.