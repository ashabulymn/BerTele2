# Media Pipeline

The media pipeline is the single entry point for media processing. Connectors such as Telegram, GoWA, Discord, Slack, Matrix, and Email should pass media bytes plus connector context into `MediaPipeline` instead of orchestrating validation, hashing, metadata generation, or storage themselves.

## Lifecycle

The default pipeline runs asynchronously in this order:

1. `validation` checks size limits.
2. `hash` calculates the SHA-256 digest.
3. `mime_detection` detects and validates the MIME type.
4. `metadata` creates the typed `MediaMetadata` model.
5. `storage` persists the media through the configured storage provider.

Successful execution returns a `MediaResource` containing metadata, storage key, and readiness state. Exceptions raised by a step are propagated to the caller.

## Context

`MediaPipelineContext` carries connector-neutral execution state:

- `connector` and `source` identify where the media came from.
- `storage_provider` stores the processed media.
- `payload` contains the normalized media request.
- `content` contains media bytes.
- `metadata`, `temporary_path`, `configuration`, `logger`, and `extensions` support future expansion.

## Builder

Pipelines are composed with `MediaPipelineBuilder`:

```python
pipeline = (
    MediaPipelineBuilder()
    .add_step(ValidationStep())
    .add_step(HashStep())
    .add_step(MimeDetectionStep())
    .add_step(MetadataStep())
    .add_step(StorageStep())
    .build()
)
```

The builder preserves insertion order, which is the execution order.

## Registry

`PipelineRegistry` stores reusable steps by name:

```python
registry = PipelineRegistry()
registry.register(MyPluginStep())
```

Plugins can register new `MediaPipelineStep` implementations during startup. Application composition can then append registered steps to the builder without changing `MediaPipeline`.

## Configuration

Individual steps can be controlled through `MediaPipelineContext.configuration`:

```python
configuration = {"disabled_steps": {"hash"}}
configuration = {"enabled_steps": {"validation", "metadata", "storage"}}
```

`enabled_steps` acts as an allowlist. If it is not provided, `disabled_steps` is used as a denylist.

## API

- `GET /media/pipeline` returns the active pipeline entry point, default order, and storage provider.
- `GET /media/pipeline/steps` returns each default step with its execution order.
