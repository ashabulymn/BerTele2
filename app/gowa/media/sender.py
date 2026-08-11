from __future__ import annotations

import logging
from typing import Any

from app.gowa.media.exceptions import (
    GoWAMediaSendError,
    GoWAUnsupportedMedia,
    GoWAValidationError,
    sanitize_error_message,
)
from app.gowa.media.mapper import map_media_resource_to_gowa_payload
from app.media.pipeline.interfaces import MediaResource
from plugins.gowa.client import GoWAClient
from plugins.gowa.config import GoWAConfig

logger = logging.getLogger("app.gowa.media.sender")


class GoWAMediaSender:
    """Transport-only sender for media resources via GoWA.

    This sender does not perform any media processing. It receives
    MediaResource objects from the pipeline and sends them to a WhatsApp
    chat identified by ``device_id`` and ``chat_id`` using the existing
    GoWA connector.

    Authentication is owned by the GoWA connector (``GoWAClient`` /
    ``GoWAConfig``). This sender never receives or stores connection
    credentials.
    """

    def __init__(
        self,
        *,
        gowa_client: GoWAClient | None = None,
        config: GoWAConfig | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config or GoWAConfig()
        self.gowa_client = gowa_client or GoWAClient(config=self.config)
        self.logger = logger or logging.getLogger("app.gowa.media.sender")

    async def send(self, resource: MediaResource, device_id: str, chat_id: str) -> dict[str, Any]:
        """Send a media resource to a WhatsApp chat.

        Args:
            resource: The media resource from the pipeline.
            device_id: The GoWA device that owns the chat.
            chat_id: The WhatsApp chat identifier to send to.

        Returns:
            A dictionary with delivery result information.

        Raises:
            GoWAValidationError: If the resource or target is invalid.
            GoWAUnsupportedMedia: If the media type is not supported.
            GoWAMediaSendError: If sending fails.
        """
        self._validate_resource(resource)
        self._validate_target(device_id, chat_id)

        try:
            payload = map_media_resource_to_gowa_payload(resource)
            payload["to"] = chat_id
            payload.setdefault("metadata", {})["device_id"] = device_id

            self.logger.info(
                "Sending media via GoWA",
                extra={
                    "media_id": resource.metadata.id,
                    "media_type": resource.metadata.type.value,
                    "device_id": device_id,
                    "chat_id": chat_id,
                    "storage_key": resource.storage_key,
                },
            )

            result = await self.gowa_client.send_message(payload)

            self.logger.info(
                "Media sent successfully via GoWA",
                extra={
                    "media_id": resource.metadata.id,
                    "device_id": device_id,
                    "chat_id": chat_id,
                    "message_id": result.get("message_id"),
                },
            )

            return {
                "status": "sent",
                "media_id": resource.metadata.id,
                "device_id": device_id,
                "chat_id": chat_id,
                "message_id": result.get("message_id"),
                "provider": "gowa",
                "metadata": result,
            }

        except GoWAUnsupportedMedia:
            raise
        except Exception as exc:
            sanitized = sanitize_error_message(str(exc))
            self.logger.error(
                "Failed to send media via GoWA",
                extra={
                    "media_id": resource.metadata.id,
                    "device_id": device_id,
                    "chat_id": chat_id,
                    "error": sanitized,
                },
            )
            raise GoWAMediaSendError(f"Failed to send media: {sanitized}") from exc

    def _validate_resource(self, resource: MediaResource) -> None:
        """Validate the media resource before sending.

        Args:
            resource: The media resource to validate.

        Raises:
            GoWAValidationError: If the resource is invalid.
        """
        if not resource.storage_key:
            raise GoWAValidationError("Media resource must have a storage_key")

        if resource.content is None:
            raise GoWAValidationError("Media resource must contain media content")

        if not resource.ready:
            raise GoWAValidationError("Media resource is not ready for sending")

        if not resource.metadata.mime_type:
            raise GoWAValidationError("Media resource must have a mime_type")

        if resource.metadata.size < 0:
            raise GoWAValidationError("Media resource size must be non-negative")

        if resource.metadata.size > self.config.max_upload_size:
            raise GoWAValidationError(
                f"Media resource size exceeds the GoWA maximum upload size "
                f"({self.config.max_upload_size} bytes)"
            )

    def _validate_target(self, device_id: str, chat_id: str) -> None:
        """Validate the send target identifiers.

        Args:
            device_id: The GoWA device identifier.
            chat_id: The WhatsApp chat identifier.

        Raises:
            GoWAValidationError: If either identifier is missing.
        """
        if not device_id or not str(device_id).strip():
            raise GoWAValidationError("device_id is required to send media")

        if not chat_id or not str(chat_id).strip():
            raise GoWAValidationError("chat_id is required to send media")