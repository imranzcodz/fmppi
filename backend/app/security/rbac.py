from collections.abc import Iterable

from app.logging import get_logger

logger = get_logger("app.security.rbac")

ROLE_HIERARCHY = {
    "reporter": 1,
    "reviewer": 2,
    "investigator": 3,
    "admin": 4,
}

ROLE_PERMISSIONS = {
    "reporter": {"cases:create", "cases:read_own", "evidence:upload_own"},
    "reviewer": {"cases:read", "evidence:read", "verify:local", "verify:global", "verify:kinship"},
    "investigator": {
        "cases:create",
        "cases:read",
        "cases:update",
        "cases:delete",
        "evidence:upload",
        "match:run",
        "verify:local",
        "verify:global",
        "verify:kinship",
    },
    "admin": {
        "users:read",
        "users:create",
        "users:update",
        "users:delete",
        "cases:create",
        "cases:read",
        "cases:update",
        "cases:delete",
        "evidence:upload",
        "evidence:read",
        "match:run",
        "verify:local",
        "verify:global",
        "verify:kinship",
        "audit:read",
    },
}


def has_role(user_role: str, required_roles: Iterable[str]) -> bool:
    return user_role in set(required_roles)


def has_permission(user_role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(user_role, set())
