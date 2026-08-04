# Telegram Media Downloader

Epic 16 adds a Telegram-only media downloader that converts Telegram file references into Media Engine metadata. It does not add WhatsApp media sending, upload bridging, thumbnails, transforms, encryption, or storage providers.

## Architecture

The implementation lives in `app/telegram/media/`:

- `client.py` wraps Telegram file metadata lookup and streamed downloads behind a testable protocol.
- `mapper.py` maps Telegram media objects into `MediaPrepareRequest`.
- `downloader.py` streams bytes, calculates SHA-256, detects MIME type, and returns a `MediaResource`.
- `service.py` composes the downloader with the existing `TelegramService` and `MediaService`.
- `router.py` exposes `/telegram/media/download` and `/telegram/media/{id}`.

The downloader uses `MediaService` for validation, metadata creation, and storage-key preparation. It only uses the existing storage abstraction boundary and does not introduce a storage provider.

## Download Flow

1. The API receives a Telegram media object or file reference payload.
2. `TelegramMediaMapper` converts the Telegram object into a media preparation request.
3. `TelegramMediaClient` requests Telegram file metadata.
4. `TelegramMediaDownloader` streams the file in configured chunks.
5. Each chunk updates the SHA-256 digest and total byte count.
6. The downloader detects or carries forward the MIME type.
7. `MediaService.create_streamed_metadata` validates the media and creates typed `MediaMetadata`.
8. `MediaService.prepare_download` creates a deterministic storage key for the future storage provider.

## Metadata Mapping

Supported media types:

- Photo
- Video
- Document
- Audio
- Voice
- Animation
- Sticker

The mapper accepts plain dictionaries and Telethon-like objects. New media types can be added by extending `TelegramMediaMapper._detect_type` and, if needed, `MediaType` in the Media Engine.

## Storage Abstraction

Epic 16 does not persist content. The returned `MediaResource` includes metadata and a storage key so Epic 17 can plug in a concrete `MediaStorageProvider` without changing Telegram download semantics.

`GET /telegram/media/{id}` returns mocked metadata until a persistent metadata and content store exists.

## Future Upload Pipeline

The future upload pipeline should consume `MediaResource`, persist streamed content through a concrete storage provider, and pass stored media descriptors to WhatsApp or other channel-specific upload implementations. That work belongs outside this epic.
