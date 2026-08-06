# BerTele2 Module Map

This document describes every module in the BerTele2 project: purpose, dependencies, public APIs, and future plans.

## Application Modules (`app/`)

### `app/api`

- **Purpose**: REST API layer (v1 endpoints).
- **Dependencies**: All service modules.
- **Public APIs**: Routers for auth, apikeys, users, health, meta, dialogs, telegram, messages, sessions, webhooks, media, telegram-media, gowa-media.
- **Future plans**: Versioned API expansion.

### `app/core`

- **Purpose**: Core configuration, container, and shared utilities.
- **Dependencies**: Pydantic, pydantic-settings.
- **Public APIs**: `Settings`, `get_settings`, `AppContainer`.
- **Future plans**: Centralized logging config.

### `app/dashboard`

- **Purpose**: Dashboard service (overview, logs, metrics) and realtime WebSocket.
- **Dependencies**: Security.
- **Public APIs**: `DashboardService`, `DashboardRealtimeManager`.
- **Future plans**: Real metrics data.

### `app/events`

- **Purpose**: In-process event bus.
- **Dependencies**: None (self-contained).
- **Public APIs**: `EventBroker`, `EventPublisher`, `EventDispatcher`, `EventRegistry`, `EventQueue`, `Event`, `Subscription`.
- **Future plans**: Persistent event log.

### `app/gowa`

- **Purpose**: GoWA media service (send media to WhatsApp).
- **Dependencies**: `app.media`, `plugins.gowa.config`.
- **Public APIs**: `GoWAMediaService`, `GoWAMediaSender`, `GoWAMediaMapper`.
- **Future plans**: Receive media from GoWA.

### `app/integrations`

- **Purpose**: External integrations (webhooks).
- **Dependencies**: `app.events`.
- **Public APIs**: `WebhookManager`, `WebhookDispatcher`, `WebhookRepository`.
- **Future plans**: More integration types.

### `app/media`

- **Purpose**: Media engine — models, storage providers, pipeline.
- **Dependencies**: None (self-contained).
- **Public APIs**: `MediaService`, `MediaResource`, `MediaPipeline`, `MediaPipelineBuilder`, `StorageProvider`, `StorageFactory`, `LocalStorageProvider`, `MemoryStorageProvider`.
- **Future plans**: S3/GCS providers.

### `app/middleware`

- **Purpose**: HTTP middleware.
- **Dependencies**: Starlette.
- **Public APIs**: Middleware classes.
- **Future plans**: Rate limiting.

### `app/models`

- **Purpose**: SQLAlchemy ORM models.
- **Dependencies**: SQLAlchemy.
- **Public APIs**: Model classes.
- **Future plans**: Migration coverage.

### `app/pipeline`

- **Purpose**: Message pipeline (middleware + handlers).
- **Dependencies**: `app.events`.
- **Public APIs**: `MessagePipeline`, `PipelineContext`, `PipelineResult`, `PipelineMiddleware`, `PipelineHandler`.
- **Future plans**: More built-in handlers.

### `app/plugins`

- **Purpose**: Plugin SDK.
- **Dependencies**: `app.events`.
- **Public APIs**: `PluginBase`, `PluginManager`, `PluginManifest`, `PluginContext`, `HookRegistry`, `PluginLoader`, `PluginRegistry`.
- **Future plans**: Plugin marketplace.

### `app/schemas`

- **Purpose**: Pydantic schemas for API.
- **Dependencies**: Pydantic.
- **Public APIs**: Schema classes.
- **Future plans**: Versioned schemas.

### `app/security`

- **Purpose**: Authentication, authorization, API keys, audit.
- **Dependencies**: JWT, hashing.
- **Public APIs**: `SecurityService`, `require_authentication`, `require_permissions`, `UserRecord`, `APIKeyManager`, `AuditLogger`.
- **Future plans**: Persistent user store.

### `app/services`

- **Purpose**: Shared services (e.g., `TelegramService`).
- **Dependencies**: Various.
- **Public APIs**: Service classes.
- **Future plans**: Consolidation.

### `app/session`

- **Purpose**: Session engine.
- **Dependencies**: Telethon, repository.
- **Public APIs**: `SessionManager`, `SessionRepository`, `SessionCache`, `SessionRecord`, `SessionState`.
- **Future plans**: Multi-tenant sessions.

### `app/telegram`

- **Purpose**: Telegram engine — client pool, dialogs, messages, dispatcher, media.
- **Dependencies**: Telethon, `app.pipeline`, `app.events`, `app.media`.
- **Public APIs**: `TelegramEngine`, `TelegramClientPool`, `TelegramDialogService`, `TelegramMessageService`, `TelegramEntityResolver`, `TelegramEventDispatcher`, `TelegramMediaService`.
- **Future plans**: More media types.

### `app/utils`

- **Purpose**: Shared utilities.
- **Dependencies**: None.
- **Public APIs**: Utility functions.
- **Future plans**: Consolidation.

### `app/workers`

- **Purpose**: Background workers.
- **Dependencies**: Various.
- **Public APIs**: Worker classes.
- **Future plans**: Worker pool.

## Plugin Modules (`plugins/`)

### `plugins/gowa`

- **Purpose**: GoWA connector plugin.
- **Dependencies**: `app.gowa`, `app.media`.
- **Public APIs**: `GoWAConfig`.
- **Future plans**: Full GoWA integration.

### `plugins/n8n`

- **Purpose**: n8n connector plugin.
- **Dependencies**: FastAPI.
- **Public APIs**: `router`, `connector`, `require_n8n_auth`.
- **Future plans**: More n8n actions.

## Frontend (`dashboard/`)

- **Purpose**: React + TypeScript dashboard.
- **Dependencies**: React, Vite.
- **Public APIs**: Dashboard UI.
- **Future plans**: Real-time charts.

## Tests (`tests/`)

- **Purpose**: Test suite.
- **Dependencies**: pytest.
- **Public APIs**: Fixtures.
- **Future plans**: Integration tests.

---

## Related Documents

- [architecture.md](architecture.md) — System architecture.
- [context/](context/) — Per-subsystem deep dives.
- [roadmap.md](roadmap.md) — Future plans.