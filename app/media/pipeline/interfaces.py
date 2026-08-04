from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.media.models import MediaMetadata

if TYPE_CHECKING:
    from app.media.pipeline.context import MediaPipelineContext


@dataclass(slots=True)
class MediaResource:
    metadata: MediaMetadata
    storage_key: str
    content: bytes | None = None
    ready: bool = True


class MediaPipelineStep(ABC):
    """Interface implemented by media pipeline processing steps."""

    name: str

    @abstractmethod
    async def execute(self, context: MediaPipelineContext) -> None:
        """Run the step against the pipeline context."""
