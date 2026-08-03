from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.pipeline.context import PipelineContext


class PipelineMiddleware(Protocol):
    async def before(self, context: PipelineContext) -> None: ...

    async def after(self, context: PipelineContext, result: Any | None = None) -> None: ...

    async def on_error(self, context: PipelineContext, error: BaseException) -> None: ...


@dataclass(slots=True)
class BasePipelineMiddleware:
    async def before(self, context: PipelineContext) -> None:
        return None

    async def after(self, context: PipelineContext, result: Any | None = None) -> None:
        return None

    async def on_error(self, context: PipelineContext, error: BaseException) -> None:
        return None

