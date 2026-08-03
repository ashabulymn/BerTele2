from __future__ import annotations

from dataclasses import dataclass, field

from app.session.model import SessionRecord


@dataclass
class SessionCache:
    _records: dict[int, SessionRecord] = field(default_factory=dict)

    def get(self, session_id: int) -> SessionRecord | None:
        return self._records.get(session_id)

    def set(self, record: SessionRecord) -> None:
        self._records[record.id] = record

    def delete(self, session_id: int) -> None:
        self._records.pop(session_id, None)

    def all(self) -> list[SessionRecord]:
        return list(self._records.values())

