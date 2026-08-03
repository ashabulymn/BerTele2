from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"
    AUDITOR = "auditor"
    API_WRITER = "api_writer"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: {
        "users:read",
        "users:write",
        "apikeys:read",
        "apikeys:write",
        "auth:read",
        "audit:read",
    },
    Role.USER: {"users:read", "auth:read"},
    Role.AUDITOR: {"audit:read", "auth:read"},
    Role.API_WRITER: {"apikeys:read", "apikeys:write", "auth:read"},
}


def normalize_roles(roles: Iterable[str] | str | None) -> set[str]:
    if roles is None:
        return {Role.USER.value}
    if isinstance(roles, str):
        values = [item.strip() for item in roles.split(",") if item.strip()]
    else:
        values = [str(item).strip() for item in roles if str(item).strip()]
    return {value.lower() for value in values} if values else {Role.USER.value}


def role_permissions(roles: Iterable[str] | str | None) -> set[str]:
    permissions: set[str] = set()
    for role in normalize_roles(roles):
        permissions.update(ROLE_PERMISSIONS.get(Role(role), set()))
    return permissions
