from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum
from typing import ClassVar


class Permission(StrEnum):
    USERS_READ = "users:read"
    USERS_WRITE = "users:write"
    APIKEYS_READ = "apikeys:read"
    APIKEYS_WRITE = "apikeys:write"
    AUTH_READ = "auth:read"
    AUDIT_READ = "audit:read"


class Permissions:
    USERS_READ = Permission.USERS_READ.value
    USERS_WRITE = Permission.USERS_WRITE.value
    APIKEYS_READ = Permission.APIKEYS_READ.value
    APIKEYS_WRITE = Permission.APIKEYS_WRITE.value
    AUTH_READ = Permission.AUTH_READ.value
    AUDIT_READ = Permission.AUDIT_READ.value
    ALL: ClassVar[set[str]] = {
        USERS_READ,
        USERS_WRITE,
        APIKEYS_READ,
        APIKEYS_WRITE,
        AUTH_READ,
        AUDIT_READ,
    }


def permissions_for_roles(roles: Iterable[str] | str | None) -> set[str]:
    if roles is None:
        return set()
    if isinstance(roles, str):
        role_values = [item.strip() for item in roles.split(",") if item.strip()]
    else:
        role_values = [str(item).strip() for item in roles if str(item).strip()]
    permissions: set[str] = set()
    for role in role_values:
        role = role.lower()
        if role == "admin":
            permissions.update({
                Permission.USERS_READ.value,
                Permission.USERS_WRITE.value,
                Permission.APIKEYS_READ.value,
                Permission.APIKEYS_WRITE.value,
                Permission.AUTH_READ.value,
                Permission.AUDIT_READ.value,
            })
        elif role == "api_writer":
            permissions.update({Permission.APIKEYS_READ.value, Permission.APIKEYS_WRITE.value, Permission.AUTH_READ.value})
        elif role == "auditor":
            permissions.update({Permission.AUDIT_READ.value, Permission.AUTH_READ.value})
        elif role == "user":
            permissions.update({Permission.USERS_READ.value, Permission.AUTH_READ.value})
    return permissions


def user_has_permission(user_roles: Iterable[str] | str | None, permission: str | Permission) -> bool:
    required = str(permission)
    return required in permissions_for_roles(user_roles)
