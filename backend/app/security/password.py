import hashlib

from app.config import settings
from app.logging import get_logger

logger = get_logger("app.security.password")


def hash_password(password: str) -> str:
    if settings.PASSWORD_SCHEME == "argon2":
        try:
            import argon2  # type: ignore

            hasher = argon2.PasswordHasher()
            return hasher.hash(password)
        except ImportError:  # pragma: no cover - fallback when argon2 not installed
            logger.warning("argon2 not installed, falling back to bcrypt")
    # bcrypt fallback / default
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    scheme = settings.PASSWORD_SCHEME
    if scheme == "argon2" and hashed_password.startswith("$argon2"):
        try:
            import argon2  # type: ignore

            hasher = argon2.PasswordHasher()
            hasher.verify(hashed_password, plain_password)
            return True
        except Exception:
            return False
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)
    return pwd_context.verify(plain_password, hashed_password)


def hash_secret(secret: str) -> str:
    """One-way hash for TOTP secrets stored at rest."""
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()
