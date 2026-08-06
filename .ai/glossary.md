# BerTele2 Glossary

This document explains important project terms.

## MediaResource

A unit of media processed by the media engine. Contains metadata, a storage key, and optional content. Produced by the media pipeline.

See [context/media.md](context/media.md).

## Pipeline

A sequence of processing steps applied to an input. Two pipelines exist:

- **Media Pipeline**: processes media (validation, hash, MIME, metadata, storage).
- **Message Pipeline**: processes incoming Telegram updates (middleware + handlers).

See [context/media.md](context/media.md) and [context/telegram.md](context/telegram.md).

## Provider

A pluggable backend behind a common interface. Examples: storage providers (local, memory).

See [context/storage.md](context/storage.md).

## Connector

A plugin that bridges BerTele2 to an external service (GoWA, n8n). Exposes REST endpoints and subscribes to events.

See [context/plugins.md](context/plugins.md) and [context/gowa.md](context/gowa.md).

## Session

A Telegram session representing a connected account. Managed by the session engine with lifecycle states (disconnected, connecting, connected, error).

See [context/core.md](context/core.md) and [context/telegram.md](context/telegram.md).

## Plugin

A self-contained extension built on the Plugin SDK. Has a manifest, lifecycle, and can subscribe to events.

See [context/plugins.md](context/plugins.md).

## Bridge

A component that connects two systems. Connectors act as bridges between BerTele2 and external platforms.

## Automation

A planned subsystem for workflow automation: triggers, actions, conditions, and scheduling.

See [context/automation.md](context/automation.md).

## Workflow

A defined sequence of steps or actions executed by the automation engine (planned).

See [context/automation.md](context/automation.md).

---

## Related Documents

- [project.md](project.md) — Vision and goals.
- [architecture.md](architecture.md) — System architecture.
- [context/](context/) — Per-subsystem deep dives.