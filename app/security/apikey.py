from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass(slots=True)
class APIKeyRecord:
    id: int
    name: str
    user_id: int
    prefix: str
    key_hash: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    last_used_at: datetime | None = None


class APIKeyManager:
    def __init__(self) -> None:
        self._keys: dict[str, APIKeyRecord] = {}
        self._next_id = 1

    @staticmethod
    def generate_key() -> str:
        token = secrets.token_urlsafe(32)
        return f"bertele_{token}"

    @staticmethod
    def hash_key(key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def create(self, user_id: int, name: str, *, expires_in_days: int | None = None) -> tuple[str, APIKeyRecord]:
        raw_key = self.generate_key()
        key_hash = self.hash_key(raw_key)
        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now(UTC) + timedelta(days=expires_in_days)
        entry = APIKeyRecord(
            id=self._next_id,
            name=name,
            user_id=user_id,
            prefix=raw_key[:12],
            key_hash=key_hash,
            expires_at=expires_at,
        )
        self._next_id += 1
        self._keys[raw_key] = entry
        return raw_key, entry

    def list_for_user(self, user_id: int) -> list[APIKeyRecord]:
        return [entry for entry in self._keys.values() if entry.user_id == user_id and entry.is_active]

    def list_all(self) -> list[APIKeyRecord]:
        return [entry for entry in self._keys.values() if entry.is_active]

    def revoke(self, key_id: int) -> bool:
        for key, entry in list(self._keys.items()):
            if entry.id == key_id:
                entry.is_active = False
                del self._keys[key]
                return True
        return False

    def find_by_raw_key(self, raw_key: str) -> APIKeyRecord | None:
        entry = self._keys.get(raw_key)
        if entry is None:
            return None
        if entry.expires_at and datetime.now(UTC) > entry.expires_at:
            self.revoke(entry.id)
            return None
        entry.last_used_at = datetime.now(UTC)
        return entry
