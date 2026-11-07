"""Tests for MFA module."""
import base64

import pyotp

from app.security.mfa import generate_totp_secret, totp_uri, verify_totp


class TestGenerateTotpSecret:
    def test_generates_base32_secret(self):
        secret = generate_totp_secret()
        base64.b32decode(secret)  # raises if invalid
        assert len(secret) > 0

    def test_generates_different_secrets(self):
        assert generate_totp_secret() != generate_totp_secret()


class TestTotpUri:
    def test_totp_uri_contains_email_and_secret(self):
        uri = totp_uri("user@example.com", "JBSWY3DPEHPK3PXP")
        assert "user%40example.com" in uri
        assert "JBSWY3DPEHPK3PXP" in uri
        assert "issuer=FMPPI" in uri


class TestVerifyTotp:
    def test_verify_valid_code(self):
        secret = pyotp.random_base32()
        code = pyotp.TOTP(secret).now()
        assert verify_totp(secret, code) is True

    def test_verify_invalid_code(self):
        secret = pyotp.random_base32()
        assert verify_totp(secret, "000000") is False

    def test_verify_empty_secret(self):
        assert verify_totp("", "000000") is False
