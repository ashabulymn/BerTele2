from __future__ import annotations

import logging
from typing import Any

from app.gowa.media.exceptions import GoWAMediaError, GoWAMediaSendError, GoWAUnsupportedMedia, GoWAValidationError
from app.gowa.media.sender import GoWAMediaSender
from app.media.pipeline.interfaces import MediaResource
from plugins.gowa.config import GoWAConfig

logger = logging.getLogger("app.gowa.media.service")


class GoWAMediaService:
    """Service layer for sending media via GoWA.

    Responsibilities:
    - Validate sender configuration
    - Invoke GoWAMediaSender
    - Handle delivery results
    - Translate GoWA errors into BerTele2 exceptions
    """

    def __init__(
        self,
        *,
        config: GoWAConfig | None = None,
        sender: GoWAMediaSender | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config or GoWAConfig()
        self.sender = sender or GoWAMediaSender(config=self.config)
        self.logger = logger or logging.getLogger("app.gowa.media.service")

    async def send_media(self, resource: MediaResource, recipient: str) -> dict[str, Any]:
        """Send a media resource to a WhatsApp recipient.

        Args:
            resource: The media resource from the pipeline.
            recipient: The WhatsApp recipient number.

        Returns:
            A dictionary with delivery result information.

        Raises:
            GoWAValidationError: If the resource or configuration is invalid.
            GoWAUnsupportedMedia: If the media type is not supported.
            GoWAMediaSendError: If sending fails.
        """
        self._validate_configuration()

        try:
            result = await self.sender.send(resource, recipient)
            return result

        except GoWAValidationError:
            raise
        except GoWAUnsupportedMedia:
            raise
        except GoWAMediaSendError:
            raise
        except Exception as exc:
            self.logger.error(
                "Unexpected error in GoWA media service",
                extra={
                    "media_id": resource.metadata.id,
                    "recipient": recipient,
                    "error": str(exc),
                },
            )
            raise GoWAMediaSendError(f"Unexpected error sending media: {exc}") from exc

    def _validate_configuration(self) -> None:
        """Validate the service configuration.

        Raises:
            GoWAValidationError: If the configuration is invalid.
        """
        if not self.config.enabled:
            raise GoWAValidationError("GoWA connector is not enabled")

        if not self.config.base_url:
            raise GoWAValidationError("GoWA base_url is not configured")

        if self.config.max_upload_size <= 0:
            raise GoWAValidationError("GoWA max_upload_size must be positive")

        if self.config.upload_timeout <= 0:
            raise GoWAValidationError("GoWA upload_timeout must be positive")

        if self.config.retry_count < 0:
            raise GoWAValidationError("GoWA retry_count must be non-negative")

        if self.config.use_mock_transport:
            self.logger.warning("GoWA media service is using mock transport")
