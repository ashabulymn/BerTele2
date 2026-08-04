# Storage Providers

BerTele2 media storage is provider-based. `MediaService` depends on the
`StorageProvider` interface and delegates persistence to the configured provider.
Provider-specific behavior lives under `app/media/providers/`, so future backends can
be added without changing media service workflows.

## Configuration

Storage is configured through the standard `BERTELE2_` settings prefix:

- `MEDIA_PROVIDER`: active provider name. Supported values are `local` and `memory`.
- `MEDIA_STORAGE_PATH`: root directory for local storage.
- `MEDIA_MAX_SIZE`: maximum accepted object size in bytes.
- `MEDIA_ALLOWED_EXTENSIONS`: comma-separated extension allow list for local storage.

## Provider Lifecycle

Providers implement:

- `save(content, metadata)`
- `load(storage_key)`
- `delete(storage_key)`
- `exists(storage_key)`
- `get_url(storage_key)`
- `metadata(storage_key)`

`StorageFactory.create()` owns provider construction. Current examples:

```python
StorageFactory.create("memory")
StorageFactory.create("local")
```

Future providers such as `minio` or `s3` should implement `StorageProvider` and be
registered in the factory.

## Memory Provider

`MemoryStorageProvider` stores objects in process memory using the content sha256 as
the storage key. It is intended for unit tests, local development, benchmarks, and CI.
Data is lost when the process exits.

## Local Provider

`LocalStorageProvider` stores objects on disk using this structure:

```text
<storage_path>/
  yyyy/
    mm/
      <sha256>
```

The original filename is never used as the storage key. When the same content already
exists at the computed path, the provider returns the existing storage key and does not
rewrite the file.

The provider validates maximum file size and, when metadata includes a filename,
checks the file extension against the configured allow list.

## API

The media API exposes storage status:

- `GET /media/storage/provider`
- `GET /media/storage/info`

With the default API prefix these are available under `/api/v1`.
