# ADR-0004: Storage Provider

## Status

Accepted

## Context

BerTele2 needs to store media resources. Different deployments may require different storage backends (local filesystem, memory, cloud). A common interface is required so backends can be swapped.

## Decision

Adopt a **pluggable storage provider** architecture with:

- `StorageProvider` — interface for storage backends.
- `LocalStorageProvider` — local filesystem storage.
- `MemoryStorageProvider` — in-memory storage (testing/dev).
- `StorageFactory` — creates providers based on configuration.

## Consequences

- Storage backends are swappable.
- New providers (S3, GCS) can be added without modifying the core.
- The factory centralizes provider selection.
- Requires consistent provider behavior.

## Alternatives Considered

- **Hardcoded local storage**: Rejected — not portable.
- **Single cloud provider**: Rejected — not flexible.
- **No abstraction**: Rejected — portability is required.

---

## Related Documents

- [context/storage.md](../context/storage.md) — Storage subsystem.
- [context/media.md](../context/media.md) — Media pipeline.
- [architecture.md](../architecture.md) — System architecture.