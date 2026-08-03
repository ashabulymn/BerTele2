from __future__ import annotations

import hashlib
import hmac
import secrets


class PasswordHasher:
    """Password hashing utilities based on PBKDF2-HMAC-SHA256."""

    algorithm = "pbkdf2_sha256"
    iterations = 200_000

    @staticmethod
    def _hash(password: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PasswordHasher.iterations)

    @classmethod
    def hash_password(cls, password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = cls._hash(password, salt)
        return f"{cls.algorithm}${salt.hex()}${digest.hex()}"

    @classmethod
    def verify_password(cls, password: str, encoded_password: str) -> bool:
        if not encoded_password or "$" not in encoded_password:
            return False

        algorithm, salt_hex, digest_hex = encoded_password.split("$", 2)
        if algorithm != cls.algorithm:
            return False

        try:
            salt = bytes.fromhex(salt_hex)
            digest = bytes.fromhex(digest_hex)
        except ValueError:
            return False

        candidate = cls._hash(password, salt)
        return hmac.compare_digest(candidate, digest)
