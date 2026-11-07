"""Tests for password module."""
from app.security.password import hash_password, hash_secret, verify_password


class TestHashPassword:
    def test_hash_and_verify(self):
        pw = "Secret1234"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_hash_different_each_time(self):
        pw = "Secret1234"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2


class TestHashSecret:
    def test_hash_secret_deterministic(self):
        secret = "my-totp-secret"
        h1 = hash_secret(secret)
        h2 = hash_secret(secret)
        assert h1 == h2
        assert len(h1) == 64  # sha256 hex

    def test_hash_secret_changes_with_input(self):
        assert hash_secret("a") != hash_secret("b")
