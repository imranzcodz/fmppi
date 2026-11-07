import base64

import pyotp

from app.config import settings
from app.logging import get_logger
from app.security.password import hash_secret

logger = get_logger("app.security.mfa")


def generate_totp_secret() -> str:
    return base64.b32encode(os_urandom()).decode("utf-8")


def os_urandom(n: int = 20) -> bytes:
    import os

    return os.urandom(n)


def totp_uri(email: str, secret: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=settings.MFA_ISSUER)


def verify_totp(secret: str, code: str) -> bool:
    try:
        return pyotp.TOTP(secret).verify(code, valid_window=settings.MFA_WINDOW)
    except Exception as exc:
        logger.warning("TOTP verify error", extra={"request_id": "system", "error": str(exc)})
        return False


def hash_totp_secret(secret: str) -> str:
    return hash_secret(secret)
