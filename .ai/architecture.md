# BerTele2 Architecture

This document describes the complete architecture of BerTele2. It is the authoritative reference for how subsystems fit together.

## Overview

BerTele2 is a **self-hosted Telegram MTProto gateway**. It exposes Telegram capabilities through a unified REST + WebSocket API, processes media through a pluggable pipeline, and connects to external automation platforms via connectors and plugins.

```mermaid
flowchart TB
    subgraph Clients
        Dashboard[React Dashboard]
        API[External API Clients]
        Webhooks[Webhook Consumers]
    end

    subgraph Gateway[BerTele2 Gateway]
        FastAPI[FastAPI App]
        Security[Security Layer]
        Router[API v1 Router]
        EventBus[Event Bus]
        SessionEngine[Session Engine]
        TelegramEngine[Telegram Engine]
        MediaEngine[Media Engine]
        Pipeline[Message Pipeline]
        PluginSDK[Plugin SDK]
        DashboardSvc[Dashboard Service]
    end

    subgraph External
        MTProto[Telegram MTProto]
        GoWA[GoWA Connector]
        N8N[n8n Connector]
        Storage[Storage Providers]
    end

    Dashboard --> FastAPI
    API --> FastAPI
    Webhooks --> FastAPI
    FastAPI --> Security
    FastAPI --> Router
    Router --> SessionEngine
    Router --> TelegramEngine
    Router --> MediaEngine
    Router --> DashboardSvc
    TelegramEngine --> EventBus
    MediaEngine --> EventBus
    PluginSDK --> EventBus
    TelegramEngine --> MTProto
    MediaEngine --> Storage
    PluginSDK --> GoWA
    PluginSDK --> N8N
    TelegramEngine --> Pipeline
```

## Session Engine

Manages Telegram session lifecycle: create, connect, disconnect, reconnect, delete. Uses a repository for persistence, a cache for fast access, and a pool of Telethon clients.

```mermaid
flowchart LR
    API[Session API] --> Manager[SessionManager]
    Manager --> Repo[SessionRepository]
    Manager --> Cache[SessionCache]
    Manager --> Clients[TelegramClient Pool]
    Clients --> MTProto[Telegram MTProto]
```

See [context/core.md](context/core.md) and [context/telegram.md](context/telegram.md).

## Telegram Engine

Wraps Telethon to provide dialogs, messages, entity resolution, and media download. It owns the client pool and the message pipeline.

```mermaid
flowchart LR
    TelegramEngine[TelegramEngine]
    TelegramEngine --> ClientPool[TelegramClientPool]
    TelegramEngine --> Dialogs[TelegramDialogService]
    TelegramEngine --> Messages[TelegramMessageService]
    TelegramEngine --> Resolver[TelegramEntityResolver]
    TelegramEngine --> Dispatcher[TelegramEventDispatcher]
    Dispatcher --> Pipeline[MessagePipeline]
    Pipeline --> EventBus[Event Bus]
```

See [context/telegram.md](context/telegram.md).

## GoWA Connector

Connects BerTele2 to GoWA (WhatsApp gateway) for sending media. Includes a config, sender, mapper, and service layer.

```mermaid
flowchart LR
    API[GoWA Media API] --> Service[GoWAMediaService]
    Service --> Sender[GoWAMediaSender]
    Sender --> GoWA[GoWA Gateway]
    Service --> Config[GoWAConfig]
    Service --> Resource[MediaResource]
```

See [context/gowa.md](context/gowa.md).

## Media Engine

Handles media resources: models, storage providers, and the media pipeline.

```mermaid
flowchart LR
    MediaService[MediaService]
    MediaService --> Pipeline[MediaPipeline]
    Pipeline --> Steps[Pipeline Steps]
    Steps --> Storage[Storage Providers]
    Storage --> Local[Local Storage]
    Storage --> Memory[Memory Storage]
```

See [context/media.md](context/media.md) and [context/storage.md](context/storage.md).

## Media Pipeline

A pluggable pipeline that processes media through ordered steps: validation, hashing, MIME detection, metadata extraction, and storage.

```mermaid
flowchart LR
    Input[Media Input] --> Validation[ValidationStep]
    Validation --> Hash[HashStep]
    Hash --> Mime[MimeDetectionStep]
    Mime --> Metadata[MetadataStep]
    Metadata --> Storage[StorageStep]
    Storage --> Output[MediaResource]
```

See [context/media.md](context/media.md).

## Storage Providers

Pluggable storage backends behind a common `StorageProvider` interface. Currently: local filesystem and in-memory.

```mermaid
flowchart LR
    StorageProvider[StorageProvider Interface]
    StorageProvider --> Local[LocalStorageProvider]
    StorageProvider --> Memory[MemoryStorageProvider]
    StorageProvider --> Factory[StorageFactory]
```

See [context/storage.md](context/storage.md).

## Event Bus

An in-process event bus with publisher, dispatcher, registry, and queue. Subsystems communicate by publishing and subscribing to typed events.

```mermaid
flowchart LR
    Publisher[EventPublisher] --> Queue[EventQueue]
    Queue --> Dispatcher[EventDispatcher]
    Dispatcher --> Registry[EventRegistry]
    Registry --> Subscribers[Subscribers]
```

See [context/eventbus.md](context/eventbus.md).

## Automation Engine

Planned subsystem for workflow automation (triggers, actions, conditions, scheduler). Not yet implemented; documented as an extension point.

See [context/automation.md](context/automation.md).

## Plugin SDK

Allows third-party connectors and automations via a stable plugin interface: `PluginBase`, `PluginManifest`, `PluginManager`, and hook registry.

```mermaid
flowchart LR
    PluginManager[PluginManager]
    PluginManager --> Loader[PluginLoader]
    PluginManager --> Registry[PluginRegistry]
    PluginManager --> Hooks[HookRegistry]
    PluginManager --> EventBus[Event Bus]
    PluginBase[PluginBase] --> Manifest[PluginManifest]
    PluginBase --> Context[PluginContext]
```

See [context/plugins.md](context/plugins.md).

## Dashboard

Provides overview, logs, and metrics via REST endpoints and a WebSocket for real-time updates. Frontend is a React + TypeScript app.

```mermaid
flowchart LR
    DashboardSvc[DashboardService] --> Overview[Overview]
    DashboardSvc --> Logs[Logs]
    DashboardSvc --> Metrics[Metrics]
    Realtime[DashboardRealtimeManager] --> WS[WebSocket]
    React[React Dashboard] --> REST[REST API]
    React --> WS
```

See [context/dashboard.md](context/dashboard.md).

## Connector Architecture

Connectors (GoWA, n8n) are plugins that bridge BerTele2 to external services. They expose REST endpoints and subscribe to events.

```mermaid
flowchart LR
    Connector[Connector Plugin]
    Connector --> REST[REST Endpoints]
    Connector --> EventBus[Event Bus]
    Connector --> External[External Service]
```

See [context/plugins.md](context/plugins.md) and [context/gowa.md](context/gowa.md).

## Dependency Injection

Dependencies are wired explicitly via a container (`app/core/container.py`) and constructor injection. Services receive their dependencies as constructor arguments; no global singletons.

See [context/core.md](context/core.md) and [decisions/ADR-0006-dependency-injection.md](decisions/ADR-0006-dependency-injection.md).

## Configuration

Configuration uses Pydantic Settings with a `BERTELE2_` environment prefix. Each subsystem (GoWA, n8n, Telegram) has its own settings class.

See [context/core.md](context/core.md).

## Future Extensions

- **Automation Engine**: workflow triggers, actions, conditions, scheduler.
- **More Storage Providers**: S3, GCS, Azure Blob.
- **More Connectors**: additional messaging platforms.
- **Worker Pool**: background task processing.
- **Multi-tenant**: per-tenant isolation.

See [roadmap.md](roadmap.md).

---

## Related Documents

- [project.md](project.md) — Vision and goals.
- [module-map.md](module-map.md) — Module-level details.
- [context/](context/) — Per-subsystem deep dives.
- [decisions/](decisions/) — Architecture Decision Records.