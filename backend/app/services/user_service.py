from sqlalchemy.orm import Session

from app.models.base import User
from app.security.password import hash_password


def create_user(db: Session, email: str, password: str, role: str = "reporter", is_active: bool = True) -> User:
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise ValueError("Email already registered")
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def list_users(db: Session):
    return db.query(User).all()


def update_user(db: Session, user: User, role: str | None = None, is_active: bool | None = None, mfa_enabled: bool | None = None) -> User:
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    if mfa_enabled is not None:
        user.mfa_enabled = mfa_enabled
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()
