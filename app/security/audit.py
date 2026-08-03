from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class AuditEntry:
    action: str
    resource: str
    actor_id: int | None = None
    details: dict[str, object] = field(default_factory=dict)
    status: str = "success"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class AuditLogger:
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    def log(
        self,
        *,
        action: str,
        resource: str,
        actor_id: int | None = None,
        details: dict[str, object] | None = None,
        status: str = "success",
    ) -> AuditEntry:
        entry = AuditEntry(
            action=action,
            resource=resource,
            actor_id=actor_id,
            details=details or {},
            status=status,
        )
        self.entries.append(entry)
        return entry

    def list_entries(self) -> list[dict[str, object]]:
        return [asdict(entry) for entry in self.entries]
