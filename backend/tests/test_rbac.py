"""Tests for RBAC module."""
from app.security.rbac import has_permission, has_role


class TestHasRole:
    def test_has_role_matching(self):
        assert has_role("admin", ["admin", "investigator"]) is True
        assert has_role("investigator", ["admin", "investigator"]) is True
        assert has_role("reporter", ["admin"]) is False
        assert has_role("unknown", ["admin"]) is False


class TestHasPermission:
    def test_has_permission_granted(self):
        assert has_permission("admin", "audit:read") is True
        assert has_permission("investigator", "match:run") is True
        assert has_permission("reporter", "cases:create") is True

    def test_has_permission_denied(self):
        assert has_permission("reporter", "audit:read") is False
        assert has_permission("reviewer", "cases:delete") is False
        assert has_permission("unknown", "any:permission") is False

    def test_role_hierarchy_values(self):
        from app.security.rbac import ROLE_HIERARCHY

        assert ROLE_HIERARCHY["reporter"] < ROLE_HIERARCHY["reviewer"]
        assert ROLE_HIERARCHY["reviewer"] < ROLE_HIERARCHY["investigator"]
        assert ROLE_HIERARCHY["investigator"] < ROLE_HIERARCHY["admin"]

    def test_role_permissions_coverage(self):
        from app.security.rbac import ROLE_PERMISSIONS

        assert "audit:read" in ROLE_PERMISSIONS["admin"]
        assert "users:delete" in ROLE_PERMISSIONS["admin"]
        assert "cases:delete" not in ROLE_PERMISSIONS["reviewer"]
        assert "verify:kinship" in ROLE_PERMISSIONS["reviewer"]
        assert "verify:kinship" not in ROLE_PERMISSIONS["reporter"]
