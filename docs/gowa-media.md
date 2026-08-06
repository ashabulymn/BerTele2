# GoWA Media Sender

## Architecture

The GoWA Media Sender is a transport-only component that integrates the Media Pipeline with the GoWA (WhatsApp) connector. It follows a clean separation of concerns:

```
Media Pipeline → MediaResource → GoWAMediaSender → GoWAClient → WhatsApp
```

### Components

1. **GoWAMediaSender** (`app/gowa/media/sender.py`)
   - Transport-only sender
   - Receives `MediaResource` objects from the pipeline
   - Validates resources before sending
   - Delegates to GoWA client for actual transmission

2. **GoWAMediaMapper** (`app/gowa/media/mapper.py`)
   - Maps `MediaMetadata` to GoWA payload format
   - Handles type conversion (BerTele2 → GoWA)
   - Preserves metadata in payload

3. **GoWAMediaService** (`app/gowa/media/service.py`)
   - Service layer for business logic
   - Configuration validation
   - Error translation (GoWA → BerTele2 exceptions)

## Sender Flow

```
1. Receive MediaResource from pipeline
2. Validate resource (storage_key, ready, mime_type, size)
3. Map MediaMetadata to GoWA payload
4. Set recipient in payload
5. Call GoWAClient.send_message()
6. Return delivery result
```

### Example Flow

```python
from app.gowa.media.service import GoWAMediaService
from app.media.pipeline.interfaces import MediaResource

service = GoWAMediaService()

# MediaResource comes from the pipeline
resource: MediaResource = await pipeline.process(...)

# Send to WhatsApp
result = await service.send_media(resource, recipient="15551234567")
# {
#     "status": "sent",
#     "media_id": "...",
#     "recipient": "15551234567",
#     "message_id": "gowa-...",
#     "provider": "gowa",
#     "metadata": {...}
# }
```

## Payload Mapping

### Supported Media Types

| BerTele2 Type | GoWA Type | Notes |
|--------------|-----------|-------|
| `photo` | `image` | |
| `video` | `video` | |
| `audio` | `audio` | |
| `voice` | `audio` | Mapped to audio |
| `sticker` | `image` | Mapped to image |
| `animation` | `video` | Mapped to video |
| `document` | `document` | |

### Payload Structure

```python
{
    "type": "image",  # GoWA media type
    "to": "15551234567",  # Recipient (set by sender)
    "media_url": "photo/abc-123",  # Storage key from pipeline
    "mime_type": "image/jpeg",
    "filename": "photo.jpg",
    "caption": "Optional caption",
    "metadata": {
        "media_id": "uuid",
        "size": 102400,
        "created_at": "2024-01-01T00:00:00Z",
        # Optional fields:
        "dimensions": {"width": 1920, "height": 1080},
        "duration": 30.5
    }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOWA_ENABLED` | Enable/disable GoWA connector | `true` |
| `GOWA_BASE_URL` | GoWA API base URL | `http://localhost:8080` |
| `GOWA_API_KEY` | API key for authentication | `None` |
| `GOWA_TIMEOUT_SECONDS` | Request timeout | `15.0` |
| `GOWA_MAX_RETRIES` | Maximum retry attempts | `3` |
| `GOWA_BACKOFF_FACTOR` | Exponential backoff factor | `1.5` |
| `GOWA_MAX_BACKOFF` | Maximum backoff delay | `30.0` |
| `GOWA_USE_MOCK_TRANSPORT` | Use mock transport for testing | `true` |
| `GOWA_MAX_UPLOAD_SIZE` | Maximum media upload size in bytes | `52428800` (50 MB) |
| `GOWA_UPLOAD_TIMEOUT` | Media upload timeout in seconds | `30.0` |
| `GOWA_RETRY_COUNT` | Media upload retry count | `3` |

### Example Configuration

```python
from plugins.gowa.config import GoWAConfig

config = GoWAConfig(
    enabled=True,
    base_url="https://gowa.example.com",
    api_key="your-api-key",
    timeout_seconds=20.0,
    max_retries=5,
    use_mock_transport=False,
)
```

## API Endpoints

### POST /gowa/media/send

Send a media resource to a WhatsApp recipient.

**Request:**
```json
{
    "media_id": "uuid-of-processed-media",
    "recipient": "15551234567"
}
```

**Response:**
```json
{
    "status": "sent",
    "media_id": "uuid",
    "recipient": "15551234567",
    "message_id": "gowa-image-12345",
    "provider": "gowa",
    "metadata": {
        "status": "accepted",
        "provider": "gowa",
        "message_id": "gowa-image-12345"
    }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid resource or configuration
- `422 Unprocessable Entity`: Unsupported media type
- `500 Internal Server Error`: Sending failed
- `501 Not Implemented`: Media resource retrieval not yet implemented

### GET /gowa/media/capabilities

Return GoWA media sending capabilities.

**Response:**
```json
{
    "supported_types": ["photo", "video", "audio", "voice", "sticker", "document"],
    "max_upload_size": null,
    "features": {
        "caption": true,
        "voice_note": true,
        "sticker": true,
        "document": true
    }
}
```

## Future Media Bridge Integration

The sender is designed to be extended for future media bridges:

1. **Telegram Bridge**: Add a bridge module that converts Telegram media to MediaResource
2. **Direct Upload**: Support direct media upload without pipeline processing
3. **Batch Sending**: Add batch operations for multiple recipients
4. **Media Conversion**: Integrate with FFmpeg for format conversion (out of scope for current epic)

### Extension Points

- Add new media types by extending `_map_media_type()` in `mapper.py`
- Add preprocessing by extending `GoWAMediaSender.send()` before mapping
- Add post-processing by extending after `gowa_client.send_message()`

## Error Handling

### Exception Hierarchy

```
GoWAMediaError (base)
├── GoWAValidationError
│   └── Invalid resource or configuration
├── GoWAUnsupportedMedia
│   └── Unsupported media type
└── GoWAMediaSendError
    └── Sending failed
```

### Error Translation

The service layer translates GoWA errors into BerTele2 exceptions:

- HTTP errors → `GoWAMediaSendError`
- Validation errors → `GoWAValidationError`
- Unsupported types → `GoWAUnsupportedMedia`

## Testing

See `tests/gowa_media/` for test coverage:

- Payload mapping tests
- Sender success/failure tests
- Configuration validation tests
- Service layer tests

## Out of Scope

The following features are explicitly out of scope for this epic:

- Telegram bridge implementation
- Media conversion/resizing
- FFmpeg integration
- Compression
- Encryption
- Retry queue (handled by GoWA client)