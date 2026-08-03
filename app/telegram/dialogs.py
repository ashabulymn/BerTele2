from __future__ import annotations

from dataclasses import dataclass

from telethon.tl.types import Channel, Chat, User

from app.schemas.dialogs import DialogInfo, DialogPeer, ListDialogsResponse
from app.telegram.client import TelegramClientPool
from app.telegram.entities import TelegramEntityResolver


@dataclass
class TelegramDialogService:
    client_pool: TelegramClientPool
    entity_resolver: TelegramEntityResolver

    def _peer_type(self, entity: object) -> str:
        if isinstance(entity, User):
            return "bot" if getattr(entity, "bot", False) else "user"
        if isinstance(entity, Channel):
            return "supergroup" if getattr(entity, "megagroup", False) else "channel"
        if isinstance(entity, Chat):
            return "group"
        return "unknown"

    def _dialog_info(self, dialog) -> DialogInfo:
        entity = dialog.entity
        peer = DialogPeer(
            id=dialog.id,
            type=self._peer_type(entity),
            title=getattr(entity, "title", None) or getattr(dialog, "title", None),
            username=getattr(entity, "username", None),
            first_name=getattr(entity, "first_name", None),
            last_name=getattr(entity, "last_name", None),
            is_bot=bool(getattr(entity, "bot", False)) if isinstance(entity, User) else None,
        )
        return DialogInfo(
            id=dialog.id,
            peer=peer,
            name=getattr(dialog, "name", None),
            unread_count=getattr(dialog, "unread_count", None),
            folder_id=getattr(dialog, "folder_id", None),
            pinned=bool(getattr(dialog, "pinned", False)),
            archived=bool(getattr(dialog, "archived", False)),
            raw=dialog.to_dict() if hasattr(dialog, "to_dict") else {},
        )

    async def list_dialogs(self, limit: int = 50, offset: int = 0) -> ListDialogsResponse:
        async def _load(client):
            items = []
            async for dialog in client.iter_dialogs(limit=limit + offset):
                items.append(dialog)
            return items

        dialogs = await self.client_pool.call(_load, action="list dialogs")
        sliced = dialogs[offset : offset + limit]
        return ListDialogsResponse(items=[self._dialog_info(d) for d in sliced], total=len(dialogs), limit=limit, offset=offset)

    async def get_dialog(self, dialog_id: int) -> DialogInfo:
        entity = await self.entity_resolver.resolve(dialog_id)
        dialogs = await self.client_pool.call(lambda client: client.get_dialogs(), action=f"get dialog {dialog_id}")
        for dialog in dialogs:
            if getattr(dialog, "id", None) == dialog_id:
                return self._dialog_info(dialog)
        return DialogInfo(
            id=dialog_id,
            peer=DialogPeer(
                id=dialog_id,
                type=self._peer_type(entity),
                title=getattr(entity, "title", None),
                username=getattr(entity, "username", None),
                first_name=getattr(entity, "first_name", None),
                last_name=getattr(entity, "last_name", None),
                is_bot=bool(getattr(entity, "bot", False)) if isinstance(entity, User) else None,
            ),
            raw=entity.to_dict() if hasattr(entity, "to_dict") else {},
        )
