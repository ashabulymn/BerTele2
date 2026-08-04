from __future__ import annotations


class MediaError(Exception):
    """Base exception for media engine failures."""


class MediaNotFound(MediaError):
    """Raised when media metadata or content cannot be found."""


class UnsupportedMedia(MediaError):
    """Raised when a media type, extension, or mime type is unsupported."""


class MediaTooLarge(MediaError):
    """Raised when media content exceeds the configured size limit."""


class StorageError(MediaError):
    """Raised when a storage provider fails."""
