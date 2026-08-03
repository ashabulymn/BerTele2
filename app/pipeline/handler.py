from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from app.pipeline.context import PipelineContext


class PipelineHandler(Protocol):
    async def __call__(self, context: PipelineContext) -> object: ...


@dataclass(slots=True)
class HandlerRegistration:
    handler: PipelineHandler
    predicate: Callable[[PipelineContext], bool] | None = None
    name: str | None = None

    def matches(self, context: PipelineContext) -> bool:
        return self.predicate(context) if self.predicate is not None else True
