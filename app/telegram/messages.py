from __future__ import annotations

from dataclasses import dataclass

from app.schemas.dialogs import (
    ForwardMessageResponse,
    ListMessagesResponse,
    MessageInfo,
    SendMessageResponse,
)
from app.telegram.client import TelegramClientPool
from app.telegram.entities import TelegramEntityResolver


@dataclass
class TelegramMessageService:
    client_pool: TelegramClientPool
    entity_resolver: TelegramEntityResolver

    def _message_info(self, message, dialog_id: int) -> MessageInfo:
        fwd_from = getattr(message, "fwd_from", None)
        return MessageInfo(
            id=message.id,
            dialog_id=dialog_id,
            sender_id=getattr(message, "sender_id", None),
            text=getattr(message, "message", None),
            date=getattr(message, "date", None),
            out=bool(getattr(message, "out", False)),
            grouped_id=getattr(message, "grouped_id", None),
            reply_to_msg_id=getattr(getattr(message, "reply_to", None), "reply_to_msg_id", None),
            fwd_from=fwd_from.to_dict() if hasattr(fwd_from, "to_dict") else None,
            raw=message.to_dict() if hasattr(message, "to_dict") else {},
        )

    async def send_message(self, peer: str, message: str) -> SendMessageResponse:
        entity = await self.entity_resolver.resolve(peer)
        sent = await self.client_pool.call(lambda client: client.send_message(entity, message), action=f"send message to {peer}")
        return SendMessageResponse(message_id=sent.id, peer=peer)

    async def forward_messages(self, from_peer: str, to_peer: str, message_ids: list[int]) -> ForwardMessageResponse:
        source = await self.entity_resolver.resolve(from_peer)
        target = await self.entity_resolver.resolve(to_peer)
        await self.client_pool.call(lambda client: client.forward_messages(target, message_ids, source), action=f"forward messages from {from_peer} to {to_peer}")
        return ForwardMessageResponse(message_ids=message_ids, from_peer=from_peer, to_peer=to_peer)

    async def list_messages(self, dialog_id: int, limit: int = 50, offset: int = 0) -> ListMessagesResponse:
        entity = await self.entity_resolver.resolve(dialog_id)

        async def _load(client):
            items = []
            async for message in client.iter_messages(entity, limit=limit, offset_id=offset or None):
                items.append(message)
            return items

        messages = await self.client_pool.call(_load, action=f"list messages for {dialog_id}")
        items = [self._message_info(message, dialog_id) for message in messages]
        return ListMessagesResponse(items=items, total=offset + len(items), limit=limit, offset=offset)
