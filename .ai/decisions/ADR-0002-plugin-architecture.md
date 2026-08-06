# ADR-0002: Plugin Architecture

## Status

Accepted

## Context

BerTele2 needs to support third-party connectors and automations (GoWA, n8n, and future platforms). A stable plugin interface is required so extensions can be added without modifying the core.

## Decision

Adopt a **Plugin SDK** with:

- `PluginBase` — base class with lifecycle and manifest.
- `PluginManifest` — metadata and compatibility.
- `PluginContext` — runtime context (config, logger, event access).
- `PluginManager` — loads, starts, stops, and reloads plugins.
- `PluginLoader` — loads plugins from paths.
- `PluginRegistry` — registers and looks up plugins.
- `HookRegistry` — registers and dispatches hooks.

Plugins communicate with the core via the event bus and hooks.

## Consequences

- Third-party extensions are isolated and versioned.
- The core remains stable and extensible.
- Plugins can subscribe to events and register hooks.
- Requires careful lifecycle management.

## Alternatives Considered

- **Hardcoded connectors**: Rejected — not extensible.
- **Microservice per connector**: Rejected — too heavy for in-process needs.
- **No plugin system**: Rejected — extensibility is a goal.

---

## Related Documents

- [context/plugins.md](../context/plugins.md) — Plugin subsystem.
- [context/eventbus.md](../context/eventbus.md) — Event bus.
- [architecture.md](../architecture.md) — System architecture.