
from sqlalchemy.orm import Session

from app.logging import get_logger
from app.models.base import User
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.mfa import generate_totp_secret, totp_uri, verify_totp
from app.security.password import verify_password

logger = get_logger("app.services.auth")


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def issue_tokens(user: User) -> dict:
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(refresh_token_str: str) -> dict | None:
    payload = decode_token(refresh_token_str)
    if not payload or payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    return {"access_token": create_access_token(subject=str(user_id)), "token_type": "bearer"}


def setup_mfa(db: Session, user: User) -> dict:
    secret = generate_totp_secret()
    user.mfa_secret = secret
    user.mfa_enabled = True
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("MFA setup", extra={"request_id": "system", "actor_id": user.id})
    return {"secret": secret, "provisioning_url": totp_uri(user.email, secret)}


def verify_mfa(db: Session, email: str, code: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.mfa_secret:
        return None
    if not verify_totp(user.mfa_secret, code):
        return None
    logger.info("MFA verified", extra={"request_id": "system", "actor_id": user.id})
    return user
