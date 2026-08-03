from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import Settings


@dataclass(slots=True)
class TelegramSession:
    session_id: str
    api_id: int
    api_hash: str
    session_string: str | None = None
    phone_number: str | None = None
    bot_token: str | None = None


@dataclass
class TelegramSessionRegistry:
    settings: Settings
    _sessions: dict[str, TelegramSession] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.settings.telegram_api_id and self.settings.telegram_api_hash:
            self.register(
                TelegramSession(
                    session_id="default",
                    api_id=self.settings.telegram_api_id,
                    api_hash=self.settings.telegram_api_hash,
                    session_string=self.settings.telegram_session_string,
                    phone_number=self.settings.telegram_phone_number,
                    bot_token=self.settings.telegram_bot_token,
                )
            )

    def register(self, session: TelegramSession) -> None:
        self._sessions[session.session_id] = session

    def all(self) -> list[TelegramSession]:
        return list(self._sessions.values())

    def get(self, session_id: str = "default") -> TelegramSession:
        return self._sessions[session_id]

    def configured(self) -> bool:
        return bool(self._sessions)
