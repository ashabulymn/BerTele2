from __future__ import annotations


class GoWAMediaError(Exception):
    """Base exception for GoWA media sender failures."""


class GoWAValidationError(GoWAMediaError):
    """Raised when media resource validation fails."""


class GoWAUnsupportedMedia(GoWAMediaError):
    """Raised when a media type is not supported by GoWA."""


class GoWAMediaSendError(GoWAMediaError):
    """Raised when media sending fails."""