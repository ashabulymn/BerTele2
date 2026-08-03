from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.pipeline.context import PipelineContext
from app.pipeline.handler import HandlerRegistration, PipelineHandler
from app.pipeline.middleware import PipelineMiddleware
from app.pipeline.result import PipelineResult


@dataclass
class MessagePipeline:
    logger: logging.Logger
    dependencies: dict[str, Any] = field(default_factory=dict)
    _middleware: list[PipelineMiddleware] = field(default_factory=list, init=False)
    _handlers: list[HandlerRegistration] = field(default_factory=list, init=False)

    def register_dependency(self, name: str, value: Any) -> None:
        self.dependencies[name] = value

    def register_middleware(self, middleware: PipelineMiddleware) -> PipelineMiddleware:
        self._middleware.append(middleware)
        return middleware

    def register_handler(
        self,
        handler: PipelineHandler,
        *,
        predicate: Callable[[PipelineContext], bool] | None = None,
        name: str | None = None,
    ) -> PipelineHandler:
        self._handlers.append(HandlerRegistration(handler=handler, predicate=predicate, name=name))
        return handler

    async def dispatch(self, update: Any, *, session_id: str = "default", client: Any | None = None) -> PipelineResult:
        context = PipelineContext(
            update=update,
            session_id=session_id,
            client=client,
            dependencies=dict(self.dependencies),
        )
        result = PipelineResult()
        try:
            for middleware in self._middleware:
                await middleware.before(context)

            for registration in self._handlers:
                if not registration.matches(context):
                    continue
                result.output = await registration.handler(context)
                result.handled = True
                context.handled = True
                break
            else:
                self.logger.debug("No pipeline handler matched update", extra={"session_id": session_id})

            for middleware in reversed(self._middleware):
                await middleware.after(context, result.output)
            return result
        except Exception as exc:
            context.errors.append(exc)
            result.errors.append(exc)
            for middleware in reversed(self._middleware):
                try:
                    await middleware.on_error(context, exc)
                except Exception:
                    self.logger.exception("Pipeline middleware error handler failed")
            self.logger.exception("Message pipeline failed", extra={"session_id": session_id})
            return result

