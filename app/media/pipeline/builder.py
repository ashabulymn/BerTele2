from __future__ import annotations

from dataclasses import dataclass, field

from app.media.pipeline.interfaces import MediaPipelineStep
from app.media.pipeline.pipeline import MediaPipeline


@dataclass(slots=True)
class MediaPipelineBuilder:
    _steps: list[MediaPipelineStep] = field(default_factory=list)

    def add_step(self, step: MediaPipelineStep) -> MediaPipelineBuilder:
        self._steps.append(step)
        return self

    def build(self) -> MediaPipeline:
        return MediaPipeline(steps=list(self._steps))
