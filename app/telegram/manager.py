from __future__ import annotations

import logging
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.config import Settings
from app.events import (
    EventBroker,
    PipelineDispatchCompleted,
    PipelineDispatchFailed,
    PipelineDispatchStarted,
)
from app.pipeline.filters import update_has_text, update_is_incoming
from app.pipeline.message_pipeline import MessagePipeline
from app.pipeline.middleware import BasePipelineMiddleware
from app.schemas.dialogs import (
    DialogInfo,
    ListDialogsResponse,
    ListMessagesResponse,
    SendMessageResponse,
)
from app.schemas.telegram import UserInfo
from app.telegram.client import TelegramClientPool
from app.telegram.dialogs import TelegramDialogService
from app.telegram.dispatcher import TelegramEventDispatcher
from app.telegram.entities import TelegramEntityResolver
from app.telegram.messages import TelegramMessageService
from app.telegram.session import TelegramSessionRegistry


@dataclass
class TelegramEngine:
    settings: Settings
    logger: logging.Logger

    def __post_init__(self) -> None:
        self.session_registry = TelegramSessionRegistry(settings=self.settings)
        self.client_pool = TelegramClientPool(registry=self.session_registry, logger=self.logger)
        self.entity_resolver = TelegramEntityResolver(client_pool=self.client_pool)
        self.dialogs = TelegramDialogService(client_pool=self.client_pool, entity_resolver=self.entity_resolver)
        self.messages = TelegramMessageService(client_pool=self.client_pool, entity_resolver=self.entity_resolver)
        self.event_broker = EventBroker(logger=self.logger)
        self.event_broker.subscribe(PipelineDispatchStarted, self._log_event, name="pipeline.started")
        self.event_broker.subscribe(PipelineDispatchCompleted, self._log_event, name="pipeline.completed")
        self.event_broker.subscribe(PipelineDispatchFailed, self._log_event, name="pipeline.failed")
        self.message_pipeline = MessagePipeline(logger=self.logger, event_broker=self.event_broker)
        self.message_pipeline.register_dependency("telegram_engine", self)
        self.message_pipeline.register_middleware(BasePipelineMiddleware())
        self.message_pipeline.register_handler(
            self._log_incoming_message,
            predicate=lambda context: update_is_incoming(context) and update_has_text(context),
            name="telegram.log_incoming_message",
        )
        self.dispatcher = TelegramEventDispatcher(
            client_pool=self.client_pool,
            pipeline=self.message_pipeline,
            logger=self.logger,
        )

    async def connect(self) -> None:
        await self.client_pool.connect()
        self.event_broker.start()
        await self.dispatcher.attach()

    async def disconnect(self) -> None:
        await self.client_pool.disconnect()
        await self.event_broker.stop()

    def _require_client(self) -> None:
        if not self.client_pool.configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Telegram client is not configured",
            )

    async def get_me(self) -> UserInfo:
        self._require_client()
        me = await self.client_pool.call(lambda client: client.get_me(), action="get me")
        return UserInfo(
            id=me.id,
            username=getattr(me, "username", None),
            first_name=getattr(me, "first_name", None),
            last_name=getattr(me, "last_name", None),
            phone=getattr(me, "phone", None),
            is_bot=bool(getattr(me, "bot", False)),
        )

    async def list_dialogs(self, limit: int = 50, offset: int = 0) -> ListDialogsResponse:
        self._require_client()
        return await self.dialogs.list_dialogs(limit=limit, offset=offset)

    async def get_dialog(self, dialog_id: int) -> DialogInfo:
        self._require_client()
        return await self.dialogs.get_dialog(dialog_id)

    async def list_messages(self, dialog_id: int, limit: int = 50, offset: int = 0) -> ListMessagesResponse:
        self._require_client()
        return await self.messages.list_messages(dialog_id=dialog_id, limit=limit, offset=offset)

    async def send_message(self, peer: str, message: str) -> SendMessageResponse:
        self._require_client()
        return await self.messages.send_message(peer, message)

    async def forward_messages(self, from_peer: str, to_peer: str, message_ids: list[int]):
        self._require_client()
        return await self.messages.forward_messages(from_peer, to_peer, message_ids)

    async def _log_incoming_message(self, context) -> None:
        message = getattr(context.update, "message", None)
        self.logger.info(
            "Incoming Telegram message",
            extra={
                "session_id": context.session_id,
                "message_id": getattr(message, "id", None),
                "chat_id": getattr(getattr(context.update, "chat", None), "id", None),
            },
        )

    async def _log_event(self, event) -> None:
        self.logger.info("Event dispatched", extra={"event_name": event.name, "event_type": event.type_name})
