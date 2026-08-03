from __future__ import annotations

from app.security.apikey import APIKeyManager
from app.security.audit import AuditEntry, AuditLogger
from app.security.auth import (
    SecurityService,
    UserRecord,
    require_authentication,
    require_permissions,
)
from app.security.exceptions import (
    APIKeyError,
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    SecurityError,
)
from app.security.hashing import PasswordHasher
from app.security.jwt import JWTManager
from app.security.models import APIKey, AuditLog, User
from app.security.permissions import (
    Permission,
    Permissions,
    permissions_for_roles,
    user_has_permission,
)
from app.security.roles import Role, normalize_roles

__all__ = [
    "APIKey",
    "APIKeyError",
    "APIKeyManager",
    "AuditEntry",
    "AuditLog",
    "AuditLogger",
    "AuthenticationError",
    "AuthorizationError",
    "InvalidTokenError",
    "JWTManager",
    "PasswordHasher",
    "Permission",
    "Permissions",
    "Role",
    "SecurityError",
    "SecurityService",
    "User",
    "UserRecord",
    "normalize_roles",
    "permissions_for_roles",
    "require_authentication",
    "require_permissions",
    "user_has_permission",
]
