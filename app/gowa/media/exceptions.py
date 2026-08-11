from __future__ import annotations

import re

_SENSITIVE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bearer_basic", re.compile(r"(?:bearer|basic)\s+\S+", re.IGNORECASE)),
    ("api_key", re.compile(r"(?:api[_-]?key)\s*[=:]\s*\S+", re.IGNORECASE)),
    ("password", re.compile(r"password\s*[=:]\s*\S+", re.IGNORECASE)),
    ("token", re.compile(r"(?:token)\s*[=:]\s*\S+", re.IGNORECASE)),
    (
        "authorization",
        re.compile(r"authorization\s*[=:]\s*.+", re.IGNORECASE),
    ),
]


def sanitize_error_message(message: str) -> str:
    """Redact sensitive credentials from an external error message.

    GoWA transport errors must never surface passwords, API keys,
    bearer tokens or Authorization headers. This helper removes such
    values before they reach logs or exception messages.
    """
    sanitized = message or ""
    for _name, pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


class GoWAMediaError(Exception):
    """Base exception for GoWA media sender failures."""


class GoWAValidationError(GoWAMediaError):
    """Raised when media resource validation fails."""


class GoWAUnsupportedMedia(GoWAMediaError):
    """Raised when a media type is not supported by GoWA."""


class GoWAMediaSendError(GoWAMediaError):
    """Raised when media sending fails."""