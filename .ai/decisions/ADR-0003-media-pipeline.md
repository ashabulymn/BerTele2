# ADR-0003: Media Pipeline

## Status

Accepted

## Context

BerTele2 needs to process media consistently (download, validate, hash, detect MIME, extract metadata, store). A pluggable pipeline is required so steps can be added or reordered without modifying the core.

## Decision

Adopt a **pluggable media pipeline** with:

- `MediaPipeline` — executes ordered processing steps.
- `MediaPipelineStep` — interface for steps.
- `MediaPipelineBuilder` — builds pipelines with configured steps.
- `PipelineRegistry` — registers and looks up steps.
- `MediaResource` — the unit of media flowing through the pipeline.

Default steps: validation, hashing, MIME detection, metadata extraction, storage.

## Consequences

- Media processing is consistent and extensible.
- Steps can be added, removed, or reordered.
- The pipeline is testable in isolation.
- Requires careful ordering of steps.

## Alternatives Considered

- **Monolithic media handler**: Rejected — not extensible.
- **Hardcoded processing chain**: Rejected — not configurable.
- **No pipeline**: Rejected — consistency is required.

---

## Related Documents

- [context/media.md](../context/media.md) — Media subsystem.
- [context/storage.md](../context/storage.md) — Storage providers.
- [architecture.md](../architecture.md) — System architecture.