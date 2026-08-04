from __future__ import annotations

import hashlib
import mimetypes
import re
from pathlib import Path

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_RESERVED_WINDOWS_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def calculate_sha256(content: bytes) -> str:
    """Return the SHA-256 hex digest for content bytes."""
    return hashlib.sha256(content).hexdigest()


def sanitize_filename(filename: str | None, *, fallback: str = "media") -> str:
    """Return a filesystem-neutral filename safe for storage providers."""
    raw_name = Path(filename or fallback).name.strip().replace(" ", "_")
    sanitized = _UNSAFE_FILENAME_CHARS.sub("_", raw_name).strip("._")
    if not sanitized:
        sanitized = fallback

    stem = Path(sanitized).stem.upper()
    if stem in _RESERVED_WINDOWS_NAMES:
        sanitized = f"{sanitized}_file"

    return sanitized[:255]


def detect_extension(filename: str | None, mime_type: str | None = None) -> str | None:
    """Detect a lowercase file extension from a filename or mime type."""
    if filename:
        suffix = Path(filename).suffix.lower().lstrip(".")
        if suffix:
            return suffix
    if mime_type:
        extension = mimetypes.guess_extension(mime_type, strict=False)
        if extension:
            return extension.lower().lstrip(".")
    return None


def detect_mime_type(filename: str | None = None, content: bytes | None = None) -> str:
    """Detect a mime type using standard library filename and content hints."""
    if filename:
        guessed_type, _ = mimetypes.guess_type(filename, strict=False)
        if guessed_type:
            return guessed_type

    if content:
        if content.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if content.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if content.startswith(b"GIF87a") or content.startswith(b"GIF89a"):
            return "image/gif"
        if content.startswith(b"%PDF-"):
            return "application/pdf"
        if content.startswith(b"ID3"):
            return "audio/mpeg"
        if len(content) >= 12 and content[4:8] == b"ftyp":
            return "video/mp4"

    return "application/octet-stream"
