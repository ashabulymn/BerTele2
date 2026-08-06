# Context: GoWA

This document describes the GoWA connector subsystem of BerTele2.

## Purpose

The GoWA connector bridges BerTele2 to GoWA (a WhatsApp gateway) for sending media to WhatsApp recipients.

## Architecture

```mermaid
flowchart LR
    API[GoWA Media API] --> Service[GoWAMediaService]
    Service --> Sender[GoWAMediaSender]
    Sender --> GoWA[GoWA Gateway]
    Service --> Config[GoWAConfig]
    Service --> Resource[MediaResource]
```

## Main Components

- **`GoWAConfig`** — Configuration for the GoWA connector (base URL, API key, timeouts, retries).
- **`GoWAMediaService`** — Service layer that validates config and invokes the sender.
- **`GoWAMediaSender`** — Sends media to the GoWA gateway.
- **`GoWAMediaMapper`** — Maps media resources to GoWA payloads.
- **`GoWAMediaError`** — Base exception for GoWA media errors.
- **`GoWAMediaSendError`** — Raised when sending fails.
- **`GoWAUnsupportedMedia`** — Raised for unsupported media types.
- **`GoWAValidationError`** — Raised for invalid configuration or input.

## Dependencies

- `app.media` (MediaResource)
- `plugins.gowa.config` (GoWAConfig)

## Extension Points

- Add new media types supported by GoWA.
- Add receive-media capabilities.

## Known Limitations

- Send-only currently.
- Mock transport available for development.

## Future Roadmap

- Receive media from GoWA.
- Delivery status webhooks.
- More media types.

---

## Related Documents

- [architecture.md](../architecture.md) — System architecture.
- [media.md](media.md) — Media resources.
- [plugins.md](plugins.md) — Plugin SDK.
- [decisions/ADR-0002-plugin-architecture.md](../decisions/ADR-0002-plugin-architecture.md) — Plugin decision.