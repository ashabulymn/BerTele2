from __future__ import annotations


class SecurityError(Exception):
    """Base class for security errors."""


class AuthenticationError(SecurityError):
    """Raised when credentials are missing or invalid."""


class AuthorizationError(SecurityError):
    """Raised when a user lacks the required permission."""


class InvalidTokenError(AuthenticationError):
    """Raised when the provided JWT is malformed or expired."""


class APIKeyError(AuthenticationError):
    """Raised when an API key is invalid or expired."""
