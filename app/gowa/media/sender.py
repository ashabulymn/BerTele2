from __future__ import annotations

import logging
from typing import Any

from app.gowa.media.exceptions import GoWAMediaSendError, GoWAUnsupportedMedia, GoWAValidationError
from app.gowa.media.mapper import map_media_resource_to_gowa_payload
from app.media.pipeline.interfaces import MediaResource
from plugins.gowa.client import GoWAClient
from plugins.gowa.config import GoWAConfig

logger = logging.getLogger("app.gowa.media.sender")


class GoWAMediaSender:
    """Transport-only sender for media resources via GoWA.

    This sender does not perform any media processing. It receives
    MediaResource objects from the pipeline and sends them to WhatsApp
    using the existing GoWA connector.
    """

    def __init__(
        self,
        *,
        gowa_client: GoWAClient | None = None,
        config: GoWAConfig | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.gowa_client = gowa_client or GoWAClient(config=config)
        self.config = config
        self.logger = logger or logging.getLogger("app.gowa.media.sender")

    async def send(self, resource: MediaResource, recipient: str) -> dict[str, Any]:
        """Send a media resource to a WhatsApp recipient.

        Args:
            resource: The media resource from the pipeline.
            recipient: The WhatsApp recipient number.

        Returns:
            A dictionary with delivery result information.

        Raises:
            GoWAValidationError: If the resource is invalid.
            GoWAUnsupportedMedia: If the media type is not supported.
            GoWAMediaSendError: If sending fails.
        """
        self._validate_resource(resource)

        try:
            payload = map_media_resource_to_gowa_payload(resource)
            payload["to"] = recipient

            self.logger.info(
                "Sending media via GoWA",
                extra={
                    "media_id": resource.metadata.id,
                    "media_type": resource.metadata.type.value,
                    "recipient": recipient,
                    "storage_key": resource.storage_key,
                },
            )

            result = await self.gowa_client.send_message(payload)

            self.logger.info(
                "Media sent successfully via GoWA",
                extra={
                    "media_id": resource.metadata.id,
                    "recipient": recipient,
                    "message_id": result.get("message_id"),
                },
            )

            return {
                "status": "sent",
                "media_id": resource.metadata.id,
                "recipient": recipient,
                "message_id": result.get("message_id"),
                "provider": "gowa",
                "metadata": result,
            }

        except GoWAUnsupportedMedia:
            raise
        except Exception as exc:
            self.logger.error(
                "Failed to send media via GoWA",
                extra={
                    "media_id": resource.metadata.id,
                    "recipient": recipient,
                    "error": str(exc),
                },
            )
            raise GoWAMediaSendError(f"Failed to send media: {exc}") from exc

    def _validate_resource(self, resource: MediaResource) -> None:
        """Validate the media resource before sending.

        Args:
            resource: The media resource to validate.

        Raises:
            GoWAValidationError: If the resource is invalid.
        """
        if not resource.storage_key:
            raise GoWAValidationError("Media resource must have a storage_key")

        if not resource.ready:
            raise GoWAValidationError("Media resource is not ready for sending")

        if not resource.metadata.mime_type:
            raise GoWAValidationError("Media resource must have a mime_type")

        if resource.metadata.size < 0:
            raise GoWAValidationError("Media resource size must be non-negative")