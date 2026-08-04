from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.media.models import MediaMetadata, MediaPrepareRequest
from app.media.providers.base import StorageProvider


@dataclass(slots=True)
class MediaPipelineContext:
    connector: str
    source: str
    storage_provider: StorageProvider
    payload: MediaPrepareRequest
    content: bytes
    metadata: dict[str, Any] = field(default_factory=dict)
    temporary_path: Path | None = None
    configuration: dict[str, Any] = field(default_factory=dict)
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__))
    extensions: dict[str, Any] = field(default_factory=dict)
    sha256: str | None = None
    mime_type: str | None = None
    media_metadata: MediaMetadata | None = None
    storage_key: str | None = None

    def is_step_enabled(self, step_name: str) -> bool:
        enabled_steps = self.configuration.get("enabled_steps")
        disabled_steps = self.configuration.get("disabled_steps", ())
        if enabled_steps is not None:
            return step_name in set(enabled_steps)
        return step_name not in set(disabled_steps)
