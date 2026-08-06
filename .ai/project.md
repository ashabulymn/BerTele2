# BerTele2 Project

## Vision

BerTele2 is a **self-hosted Telegram MTProto gateway** that connects Telegram to external automation platforms (n8n, GoWA, and future connectors). It provides a unified API, media pipeline, event bus, plugin SDK, and dashboard so that developers can build messaging automation without managing raw MTProto complexity.

## Mission

Provide a reliable, extensible, and observable bridge between Telegram and the automation ecosystem, with a clean architecture that any AI agent or human developer can extend safely.

## Goals

- **Unified API**: Expose Telegram capabilities (sessions, dialogs, messages, media) through a consistent REST + WebSocket API.
- **Media Pipeline**: Process media (download, validate, hash, detect MIME, store) through a pluggable pipeline.
- **Event-Driven**: Decouple subsystems via an internal event bus.
- **Plugin SDK**: Allow third-party connectors and automations via a stable plugin interface.
- **Observability**: Provide dashboard overview, logs, and metrics.
- **Security**: JWT + API key authentication, role-based permissions, audit logging.
- **AI-Friendly**: Document everything so any AI agent can contribute safely.

## Target Users

- Developers building Telegram-based automation.
- Teams integrating Telegram with n8n, GoWA, or custom connectors.
- Self-hosters who want a private messaging gateway.
- AI coding agents that extend the codebase.

## Supported Platforms

- **Runtime**: Python 3.11+ (FastAPI, Telethon, Pydantic v2).
- **Database**: SQLAlchemy + Alembic (SQLite for dev, PostgreSQL for production).
- **Frontend**: React + TypeScript dashboard (Vite).
- **Deployment**: Docker / docker-compose.

## Long-Term Roadmap

See [roadmap.md](roadmap.md) for milestones, epics, and release targets.

## Project Philosophy

1. **One Epic = One Responsibility.** Keep changes focused.
2. **Backward Compatibility.** Never break public APIs without a deprecation cycle.
3. **Interfaces Over Implementations.** Depend on abstractions.
4. **Composition Over Inheritance.** Prefer small composable units.
5. **Dependency Injection.** Wire dependencies explicitly; avoid global state.
6. **No Duplicated Logic.** Reuse shared services and utilities.
7. **No Circular Imports.** Keep module boundaries clean.
8. **Documented by Default.** Code, architecture, and decisions are documented.
9. **Tested by Default.** Every behavior has a test.
10. **AI-Friendly.** The AI SDK is the authoritative reference for development.

---

## Related Documents

- [README.md](README.md) — AI SDK overview and index.
- [architecture.md](architecture.md) — System architecture.
- [roadmap.md](roadmap.md) — Milestones and epics.
- [glossary.md](glossary.md) — Terminology.
- [decisions/ADR-0001-project-vision.md](decisions/ADR-0001-project-vision.md) — Vision decision record.