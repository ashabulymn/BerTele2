# Media Engine Foundation

The Media Engine provides reusable primitives for future media handling in BerTele2. It defines typed metadata models, validation, filename and mime helpers, hashing, and a storage provider interface without implementing any concrete transfer or persistence backend.

## Architecture

- `app/media/models.py` defines common metadata and typed media models for photos, videos, audio, voice, stickers, animations, and documents.
- `app/media/service.py` validates media, detects mime types, calculates SHA-256 hashes, sanitizes filenames, and prepares upload/download operation descriptors.
- `app/media/storage.py` defines the abstract storage provider contract for future backends.
- `app/media/router.py` exposes mocked API endpoints for supported types, metadata lookup, and deletion.
- `app/media/utils.py` contains reusable helpers for hashing, filename sanitization, extension detection, and mime detection.

## Responsibilities

The foundation is intentionally limited to deterministic preparation work. It does not download from Telegram, upload to Telegram, send WhatsApp media, generate thumbnails, resize content, compress files, encrypt content, or persist media bytes.

## Media Lifecycle

1. A future connector receives media bytes and source metadata.
2. `MediaService.create_metadata()` normalizes the filename, detects or accepts the mime type, validates size/type compatibility, and calculates the content hash.
3. `MediaService.prepare_upload()` returns a media id, typed metadata, and a storage key descriptor for a future storage provider.
4. `MediaService.prepare_download()` returns the same operation descriptor for known metadata.
5. A later storage provider will use the `MediaStorageProvider` interface to save, load, delete, and check media content.

## Future Storage Providers

Storage backends can implement `MediaStorageProvider` for local disk, MinIO, S3, Redis-backed cache layers, or other object stores in later epics. The current epic only defines the interface, so no backend-specific dependencies or configuration are required.

## Future Downloader and Uploader Integration

Telegram and WhatsApp integrations should treat the Media Engine as a preparation layer. Downloaders can pass bytes and source metadata into `MediaService`; uploaders can consume `MediaMetadata` and storage descriptors once real storage exists.
