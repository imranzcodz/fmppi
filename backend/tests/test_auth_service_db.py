"""Tests for auth service with DB."""
from app.services.auth_service import (
    authenticate_user,
    issue_tokens,
    refresh_access_token,
    setup_mfa,
    verify_mfa,
)


class TestAuthService:
    def test_authenticate_user_success(self, db):
        user = create_user_in_db(db, "auth@example.com", "Secret1234", "reporter")
        found = authenticate_user(db, "auth@example.com", "Secret1234")
        assert found is not None
        assert found.id == user.id

    def test_authenticate_user_wrong_password(self, db):
        create_user_in_db(db, "auth2@example.com", "Secret1234", "reporter")
        found = authenticate_user(db, "auth2@example.com", "WrongPassword")
        assert found is None

    def test_authenticate_user_unknown(self, db):
        found = authenticate_user(db, "none@example.com", "Secret1234")
        assert found is None

    def test_authenticate_user_inactive(self, db):
        create_user_in_db(db, "inactive@example.com", "Secret1234", "reporter", is_active=False)
        found = authenticate_user(db, "inactive@example.com", "Secret1234")
        assert found is None

    def test_issue_tokens(self, db):
        user = create_user_in_db(db, "tok@example.com", "Secret1234", "reporter")
        tokens = issue_tokens(user)
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

    def test_refresh_access_token(self, db):
        user = create_user_in_db(db, "ref@example.com", "Secret1234", "reporter")
        tokens = issue_tokens(user)
        refreshed = refresh_access_token(tokens["refresh_token"])
        assert refreshed is not None
        assert "access_token" in refreshed

    def test_refresh_invalid_token(self, db):
        assert refresh_access_token("invalid.token.here") is None

    def test_setup_mfa(self, db):
        user = create_user_in_db(db, "mfasetup@example.com", "Secret1234", "reporter")
        result = setup_mfa(db, user)
        assert "secret" in result
        assert "provisioning_url" in result
        assert user.mfa_enabled is True
        assert user.mfa_secret is not None

    def test_verify_mfa_success(self, db):
        import pyotp

        user = create_user_in_db(db, "mfaverify@example.com", "Secret1234", "reporter")
        setup_mfa(db, user)
        code = pyotp.TOTP(user.mfa_secret).now()
        found = verify_mfa(db, "mfaverify@example.com", code)
        assert found is not None

    def test_verify_mfa_invalid_code(self, db):
        user = create_user_in_db(db, "mfafail@example.com", "Secret1234", "reporter")
        setup_mfa(db, user)
        found = verify_mfa(db, "mfafail@example.com", "000000")
        assert found is None


def create_user_in_db(db, email, password, role="reporter", is_active=True):
    from app.services.user_service import create_user

    return create_user(db, email=email, password=password, role=role, is_active=is_active)
