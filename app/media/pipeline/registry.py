from __future__ import annotations

from dataclasses import dataclass, field

from app.media.pipeline.interfaces import MediaPipelineStep


@dataclass(slots=True)
class PipelineRegistry:
    _steps: dict[str, MediaPipelineStep] = field(default_factory=dict)

    def register(self, step: MediaPipelineStep) -> None:
        self._steps[step.name] = step

    def get(self, name: str) -> MediaPipelineStep:
        return self._steps[name]

    def list_steps(self) -> list[str]:
        return list(self._steps)

    def values(self) -> list[MediaPipelineStep]:
        return list(self._steps.values())
