from __future__ import annotations

from dataclasses import dataclass, field

from app.media.pipeline.context import MediaPipelineContext
from app.media.pipeline.interfaces import MediaPipelineStep, MediaResource


@dataclass(slots=True)
class MediaPipeline:
    steps: list[MediaPipelineStep] = field(default_factory=list)

    async def process(self, context: MediaPipelineContext) -> MediaResource:
        for step in self.steps:
            if not context.is_step_enabled(step.name):
                context.logger.debug("Skipping disabled media pipeline step: %s", step.name)
                continue
            context.logger.debug("Running media pipeline step: %s", step.name)
            await step.execute(context)

        if context.media_metadata is None:
            raise RuntimeError("Media pipeline did not generate metadata")
        if context.storage_key is None:
            raise RuntimeError("Media pipeline did not store media")

        return MediaResource(
            metadata=context.media_metadata,
            storage_key=context.storage_key,
            ready=True,
        )
