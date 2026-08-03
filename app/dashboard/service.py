from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class DashboardService:
    def overview(self) -> dict[str, Any]:
        return {
            "platform": "BerTele2",
            "generated_at": datetime.now(UTC).isoformat(),
            "stats": {
                "sessions": {"total": 8, "connected": 3, "disconnected": 5},
                "dialogs": {"total": 124, "active": 18},
                "messages": {"total": 4821, "today": 395},
                "webhooks": {"total": 12, "active": 9},
                "plugins": {"total": 5, "enabled": 4},
                "api_keys": {"total": 6, "active": 6},
            },
            "health": {"status": "healthy", "uptime_seconds": 86400},
            "cards": [
                {"label": "Sessions", "value": "8", "trend": "+12%"},
                {"label": "Dialogs", "value": "124", "trend": "+5%"},
                {"label": "Messages", "value": "4.8k", "trend": "+18%"},
                {"label": "Latency", "value": "184ms", "trend": "-9ms"},
            ],
            "alerts": [{"level": "info", "message": "System operating normally"}],
        }

    def logs(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "INFO",
                    "service": "gateway",
                    "message": "Telegram session connected successfully",
                },
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "WARN",
                    "service": "webhook",
                    "message": "Webhook retry queued for delayed delivery",
                },
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "level": "ERROR",
                    "service": "plugins",
                    "message": "Connector timeout recovered via fallback route",
                },
            ],
            "total": 3,
        }

    def metrics(self) -> dict[str, Any]:
        now = datetime.now(UTC)
        points = [
            {"time": (now.timestamp() - 3600000 + (idx * 600000)) / 1000, "value": 90 + (idx * 11) % 40}
            for idx in range(12)
        ]
        return {
            "series": [
                {"name": "requests", "points": points},
                {"name": "latency", "points": [{"time": item["time"], "value": 110 + idx * 8} for idx, item in enumerate(points)]},
            ],
            "summary": {"requests_per_minute": 184, "average_latency_ms": 186, "error_rate": 0.3},
        }
