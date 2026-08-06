# Context: Event Bus

This document describes the event bus subsystem of BerTele2.

## Purpose

The event bus decouples subsystems by allowing them to publish and subscribe to typed events without direct dependencies.

## Architecture

```mermaid
flowchart LR
    Publisher[EventPublisher] --> Queue[EventQueue]
    Queue --> Dispatcher[EventDispatcher]
    Dispatcher --> Registry[EventRegistry]
    Registry --> Subscribers[Subscribers]
```

## Main Components

- **`Event`** — Base class for all events.
- **`EventBroker`** — Facade that wires publisher, dispatcher, registry, and queue.
- **`EventPublisher`** — Publishes events to the queue.
- **`EventDispatcher`** — Dispatches events from the queue to subscribers.
- **`EventRegistry`** — Registers event types and subscribers.
- **`EventQueue`** — In-process queue for events.
- **`EventSubscriber`** — Interface for subscribers.
- **`Subscription`** — Represents a subscription.
- **`EventHandler`** — Callable handler for events.

## Built-in Events

- **`PipelineDispatchStarted`** — Published when a pipeline dispatch starts.
- **`PipelineDispatchCompleted`** — Published when a pipeline dispatch completes.
- **`PipelineDispatchFailed`** — Published when a pipeline dispatch fails.

## Dependencies

- None (self-contained).

## Extension Points

- Define new event types by subclassing `Event`.
- Subscribe handlers via the broker.
- Publish events from any subsystem.

## Known Limitations

- In-process only; no persistence or replay.
- Single-process dispatch.

## Future Roadmap

- Persistent event log.
- Cross-process event bus.
- Event replay.

---

## Related Documents

- [architecture.md](../architecture.md) — System architecture.
- [telegram.md](telegram.md) — Pipeline events.
- [plugins.md](plugins.md) — Plugin event access.
- [decisions/ADR-0005-event-driven.md](../decisions/ADR-0005-event-driven.md) — Event-driven decision.