from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PipelineResult:
    handled: bool = False
    output: Any = None
    errors: list[BaseException] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

