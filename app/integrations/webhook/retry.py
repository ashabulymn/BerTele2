from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class WebhookRetryPolicy:
    base_delay_seconds: int = 5
    max_delay_seconds: int = 300
    max_attempts: int = 5

    def delay_for_attempt(self, attempt_count: int) -> timedelta:
        seconds = min(self.base_delay_seconds * (2 ** max(attempt_count - 1, 0)), self.max_delay_seconds)
        return timedelta(seconds=seconds)
