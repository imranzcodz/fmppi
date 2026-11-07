"""Tests for JWT module."""
from app.config import get_settings, settings
from app.security.jwt import create_access_token, create_refresh_token, decode_token


class TestCreateAccessToken:
    def test_access_token_encodes_subject_and_type(self):
        token = create_access_token(subject="42")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_access_token_custom_expiry(self):
        from datetime import timedelta

        token = create_access_token(subject="1", expires_delta=timedelta(minutes=5))
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"


class TestCreateRefreshToken:
    def test_refresh_token_encodes_subject_and_type(self):
        token = create_refresh_token(subject="7")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "7"
        assert payload["type"] == "refresh"


class TestDecodeToken:
    def test_decode_invalid_token_returns_none(self):
        assert decode_token("not.a.valid.token") is None
        assert decode_token("") is None
        assert decode_token("abc.def.ghi") is None

    def test_decode_wrong_secret_returns_none(self):
        from jose import jwt

        from app.config import settings

        wrong_token = jwt.encode(
            {"sub": "1", "type": "access"},
            "wrong-secret",
            algorithm=settings.ALGORITHM,
        )
        assert decode_token(wrong_token) is None
