from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PipelineContext:
    update: Any
    session_id: str = "default"
    client: Any | None = None
    dependencies: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    handled: bool = False
    errors: list[BaseException] = field(default_factory=list)

    def get(self, name: str, default: Any = None) -> Any:
        return self.dependencies.get(name, default)

