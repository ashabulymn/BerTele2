from __future__ import annotations

import hashlib
import hmac


class WebhookSigner:
    def sign(self, secret: str, payload: bytes) -> str:
        digest = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
        return digest.hexdigest()
