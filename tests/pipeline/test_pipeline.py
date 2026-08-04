from __future__ import annotations

import pytest

from app.media.exceptions import MediaTooLarge
from app.media.models import MediaPrepareRequest, MediaType
from app.media.pipeline import (
    HashStep,
    MediaPipelineBuilder,
    MediaPipelineContext,
    MediaPipelineStep,
    MetadataStep,
    MimeDetectionStep,
    PipelineRegistry,
    StorageStep,
    ValidationStep,
)
from app.media.providers.memory import MemoryStorageProvider


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"


def make_context(
    content: bytes = b"%PDF-1.7",
    *,
    configuration: dict[str, object] | None = None,
) -> MediaPipelineContext:
    return MediaPipelineContext(
        connector="test",
        source="unit",
        storage_provider=MemoryStorageProvider(),
        payload=MediaPrepareRequest(type=MediaType.DOCUMENT, filename="doc.pdf"),
        content=content,
        configuration=configuration or {},
    )


@pytest.mark.anyio
async def test_pipeline_execution_stores_media() -> None:
    context = make_context()
    pipeline = (
        MediaPipelineBuilder()
        .add_step(ValidationStep())
        .add_step(HashStep())
        .add_step(MimeDetectionStep())
        .add_step(MetadataStep())
        .add_step(StorageStep())
        .build()
    )

    resource = await pipeline.process(context)

    assert resource.metadata.mime_type == "application/pdf"
    assert resource.metadata.sha256 == context.sha256
    assert resource.storage_key == context.sha256
    assert await context.storage_provider.exists(resource.storage_key)


@pytest.mark.anyio
async def test_custom_steps_can_mutate_context() -> None:
    class CustomStep(MediaPipelineStep):
        name = "custom"

        async def execute(self, context: MediaPipelineContext) -> None:
            context.metadata["custom"] = True

    context = make_context()
    pipeline = (
        MediaPipelineBuilder()
        .add_step(CustomStep())
        .add_step(ValidationStep())
        .add_step(HashStep())
        .add_step(MimeDetectionStep())
        .add_step(MetadataStep())
        .add_step(StorageStep())
        .build()
    )

    await pipeline.process(context)

    assert context.metadata["custom"] is True


def test_registry_registers_custom_steps() -> None:
    registry = PipelineRegistry()
    step = ValidationStep()

    registry.register(step)

    assert registry.get("validation") is step
    assert registry.list_steps() == ["validation"]


def test_builder_preserves_step_order() -> None:
    pipeline = MediaPipelineBuilder().add_step(ValidationStep()).add_step(HashStep()).build()

    assert [step.name for step in pipeline.steps] == ["validation", "hash"]


@pytest.mark.anyio
async def test_failure_propagates_from_step() -> None:
    context = make_context(b"toolong", configuration={"max_media_size": 3})
    pipeline = MediaPipelineBuilder().add_step(ValidationStep()).build()

    with pytest.raises(MediaTooLarge):
        await pipeline.process(context)


@pytest.mark.anyio
async def test_disabled_steps_are_skipped() -> None:
    context = make_context(configuration={"disabled_steps": {"hash"}})
    pipeline = (
        MediaPipelineBuilder()
        .add_step(HashStep())
        .add_step(MimeDetectionStep())
        .add_step(MetadataStep())
        .add_step(StorageStep())
        .build()
    )

    resource = await pipeline.process(context)

    assert context.sha256 is None
    assert resource.metadata.sha256 == resource.storage_key
