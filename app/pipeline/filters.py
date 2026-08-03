from __future__ import annotations

from collections.abc import Callable

from app.pipeline.context import PipelineContext


def update_has_text(context: PipelineContext) -> bool:
    message = getattr(context.update, "message", None)
    return bool(getattr(message, "message", None))


def update_is_incoming(context: PipelineContext) -> bool:
    message = getattr(context.update, "message", None)
    return bool(message) and not bool(getattr(message, "out", False))


def and_(*predicates: Callable[[PipelineContext], bool]) -> Callable[[PipelineContext], bool]:
    def _predicate(context: PipelineContext) -> bool:
        return all(predicate(context) for predicate in predicates)

    return _predicate

