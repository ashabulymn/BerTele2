"""Actions for the Automation Engine (Epic A2).

An action is a side effect executed when a trigger fires. Actions are
registered by name and executed by the engine with the event payload.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol

from app.automation.exceptions import ActionError, UnknownActionError
from app.gowa.media.exceptions import GoWAMediaError
from app.gowa.media.service import GoWAMediaService
from app.media.models import MediaMetadata, MediaType
from app.media.pipeline.interfaces import MediaResource

logger = logging.getLogger("app.automation.actions")


class Action(Protocol):
    """Interface implemented by automation actions."""

    name: str

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute the action against the event payload.

        Args:
            payload: The event payload that fired the trigger.

        Returns:
            A result dictionary describing the action outcome.
        """
        ...


@dataclass
class GoWASendMediaAction:
    """Send a media resource to a WhatsApp chat via GoWA.

    The action expects the following keys in the event payload:

    - ``media_id``: identifier of the processed media resource.
    - ``device_id``: the GoWA device that owns the chat.
    - ``chat_id``: the WhatsApp chat identifier to send to.
    - ``metadata``: a dict with the media metadata (``type``, ``mime_type``,
      ``size``, ``sha256``, ``filename``, ``caption``).
    - ``storage_key``: the storage key of the media resource.

    Connection credentials are never accepted here; authentication lives in
    the GoWA connector.
    """

    name: str = "gowa.send_media"
    service: GoWAMediaService | None = None

    def __post_init__(self) -> None:
        self.service = self.service or GoWAMediaService()

    async def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        resource = self._build_resource(payload)
        device_id = self._require(payload, "device_id")
        chat_id = self._require(payload, "chat_id")
        try:
            return await self.service.send_media(resource, device_id, chat_id)
        except GoWAMediaError as exc:
            raise ActionError(str(exc)) from exc

    def _build_resource(self, payload: dict[str, Any]) -> MediaResource:
        metadata_raw = payload.get("metadata")
        if not isinstance(metadata_raw, dict):
            raise ActionError("Action payload must include a 'metadata' dict")

        media_type = metadata_raw.get("type")
        try:
            media_type_enum = MediaType(media_type)
        except (TypeError, ValueError) as exc:
            raise ActionError(f"Unsupported media type '{media_type}'") from exc

        metadata = MediaMetadata(
            type=media_type_enum,
            mime_type=self._require(metadata_raw, "mime_type"),
            size=int(self._require(metadata_raw, "size")),
            sha256=self._require(metadata_raw, "sha256"),
            filename=metadata_raw.get("filename"),
            caption=metadata_raw.get("caption"),
        )
        return MediaResource(
            metadata=metadata,
            storage_key=self._require(payload, "storage_key"),
            content=payload.get("content"),
            ready=bool(payload.get("ready", True)),
        )

    @staticmethod
    def _require(data: dict[str, Any], key: str) -> Any:
        value = data.get(key)
        if value is None or value == "":
            raise ActionError(f"Action payload is missing required field '{key}'")
        return value


@dataclass
class ActionRegistry:
    """Registry of named actions."""

    _actions: dict[str, Action] = field(default_factory=dict)

    def register(self, action: Action) -> None:
        """Register an action by its name.

        Args:
            action: The action to register.

        Raises:
            ValueError: If an action with the same name is already registered.
        """
        if action.name in self._actions:
            raise ValueError(f"Action '{action.name}' is already registered")
        self._actions[action.name] = action
        logger.info("Registered automation action", extra={"action_name": action.name})

    def get(self, name: str) -> Action:
        """Return a registered action by name.

        Raises:
            UnknownActionError: If no action with that name is registered.
        """
        try:
            return self._actions[name]
        except KeyError as exc:
            raise UnknownActionError(f"Unknown action '{name}'") from exc

    def all(self) -> list[Action]:
        """Return all registered actions."""
        return list(self._actions.values())