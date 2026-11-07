"""Tests for user service with DB."""
from app.services.user_service import (
    create_user,
    delete_user,
    get_user,
    get_user_by_email,
    list_users,
    update_user,
)


class TestUserService:
    def test_create_and_get_user(self, db):
        user = create_user(db, email="a@example.com", password="Secret1234", role="investigator")
        assert user.id is not None
        assert user.email == "a@example.com"

        fetched = get_user(db, user.id)
        assert fetched is not None
        assert fetched.email == "a@example.com"

    def test_get_user_not_found(self, db):
        assert get_user(db, 99999) is None

    def test_get_user_by_email(self, db):
        create_user(db, email="b@example.com", password="Secret1234", role="reviewer")
        found = get_user_by_email(db, "b@example.com")
        assert found is not None
        assert found.email == "b@example.com"

    def test_get_user_by_email_not_found(self, db):
        assert get_user_by_email(db, "none@example.com") is None

    def test_list_users(self, db):
        create_user(db, email="c@example.com", password="Secret1234", role="reporter")
        create_user(db, email="d@example.com", password="Secret1234", role="investigator")
        users = list_users(db)
        assert len(users) >= 2

    def test_update_user(self, db):
        user = create_user(db, email="e@example.com", password="Secret1234", role="reporter")
        updated = update_user(db, user, role="investigator", is_active=False, mfa_enabled=True)
        assert updated.role == "investigator"
        assert updated.is_active is False
        assert updated.mfa_enabled is True

    def test_delete_user(self, db):
        user = create_user(db, email="f@example.com", password="Secret1234", role="reporter")
        delete_user(db, user)
        assert get_user(db, user.id) is None

    def test_create_user_duplicate_email(self, db):
        create_user(db, email="dup@example.com", password="Secret1234", role="reporter")
        try:
            create_user(db, email="dup@example.com", password="Secret1234", role="reporter")
            raise AssertionError("Expected ValueError")
        except ValueError as exc:
            assert "Email already registered" in str(exc)
