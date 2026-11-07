from collections.abc import Iterable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.logging import get_logger
from app.models.base import User
from app.security.jwt import decode_token
from app.security.rbac import has_permission, has_role

logger = get_logger("app.api.deps")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(request: Request, token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None or payload.get("type") != "access":
            raise credentials_exception
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


def require_role(required_roles: Iterable[str]):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_role(current_user.role, required_roles):
            logger.warning(
                "RBAC role denied",
                extra={"actor_id": current_user.id, "role": current_user.role, "required": list(required_roles)},
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return dependency


def require_permission(permission: str):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if not has_permission(current_user.role, permission):
            logger.warning(
                "RBAC permission denied",
                extra={"actor_id": current_user.id, "role": current_user.role, "permission": permission},
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")
        return current_user

    return dependency
