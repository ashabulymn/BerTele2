from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TelegramReconnectPolicy:
    initial_delay: float = 1.0
    max_delay: float = 30.0
    max_attempts: int = 5

    def delay_for(self, attempt: int) -> float:
        return min(self.initial_delay * (2**max(attempt - 1, 0)), self.max_delay)
