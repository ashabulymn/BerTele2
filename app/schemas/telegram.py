from __future__ import annotations

from app.schemas import dialogs as dialog_schemas
from app.schemas.common import APIModel

DialogInfo = dialog_schemas.DialogInfo
DialogPeer = dialog_schemas.DialogPeer
ForwardMessageRequest = dialog_schemas.ForwardMessageRequest
ForwardMessageResponse = dialog_schemas.ForwardMessageResponse
ListDialogsResponse = dialog_schemas.ListDialogsResponse
ListMessagesResponse = dialog_schemas.ListMessagesResponse
MessageInfo = dialog_schemas.MessageInfo
SendMessageRequest = dialog_schemas.SendMessageRequest
SendMessageResponse = dialog_schemas.SendMessageResponse


class UserInfo(APIModel):
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    is_bot: bool
