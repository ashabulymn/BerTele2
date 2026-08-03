from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Sequence
from typing import Any

from app.security.exceptions import InvalidTokenError


class JWTManager:
    def __init__(
        self,
        secret_key: str = "bertele2-dev-secret",
        algorithm: str = "HS256",
        access_token_ttl_seconds: int = 3600,
        refresh_token_ttl_seconds: int = 86400 * 7,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_ttl_seconds = access_token_ttl_seconds
        self.refresh_token_ttl_seconds = refresh_token_ttl_seconds

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64url_decode(value: str) -> bytes:
        padding = "=" * ((4 - len(value) % 4) % 4)
        return base64.urlsafe_b64decode(value + padding)

    def _sign(self, signing_input: bytes) -> bytes:
        return hmac.new(self.secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()

    def encode(
        self,
        subject: str,
        *,
        token_type: str,
        roles: Sequence[str] | None = None,
        permissions: Sequence[str] | None = None,
        expires_in_seconds: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        now = int(time.time())
        ttl = expires_in_seconds or (
            self.access_token_ttl_seconds if token_type == "access" else self.refresh_token_ttl_seconds
        )
        payload: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": now + ttl,
            "type": token_type,
            "roles": list(roles or []),
            "permissions": list(permissions or []),
        }
        if extra:
            payload.update(extra)
        header = {"alg": self.algorithm, "typ": "JWT"}
        header_segment = self._b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_segment = self._b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
        signature = self._b64url_encode(self._sign(signing_input))
        return f"{header_segment}.{payload_segment}.{signature}"

    def decode(self, token: str, *, expected_type: str | None = None) -> dict[str, Any]:
        try:
            header_segment, payload_segment, signature = token.split(".")
            signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
            expected = self._b64url_encode(self._sign(signing_input))
            if not hmac.compare_digest(expected, signature):
                raise InvalidTokenError("Token signature is invalid")
            payload = json.loads(self._b64url_decode(payload_segment).decode("utf-8"))
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            raise InvalidTokenError("Token could not be decoded") from exc

        if payload.get("exp", 0) < int(time.time()):
            raise InvalidTokenError("Token has expired")
        if expected_type and payload.get("type") != expected_type:
            raise InvalidTokenError(f"Token type mismatch: expected {expected_type}")
        return payload


def create_access_token(
    subject: str,
    *,
    secret_key: str = "bertele2-dev-secret",
    roles: Sequence[str] | None = None,
    permissions: Sequence[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    manager = JWTManager(secret_key=secret_key)
    return manager.encode(subject, token_type="access", roles=roles, permissions=permissions, extra=extra)


def create_refresh_token(
    subject: str,
    *,
    secret_key: str = "bertele2-dev-secret",
    roles: Sequence[str] | None = None,
    permissions: Sequence[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    manager = JWTManager(secret_key=secret_key)
    return manager.encode(subject, token_type="refresh", roles=roles, permissions=permissions, extra=extra)
