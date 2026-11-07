from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.logging import get_logger
from app.models.base import User
from app.schemas.auth import Message, UserCreate, UserOut, UserUpdate
from app.services.user_service import create_user, delete_user, get_user, list_users, update_user

logger = get_logger("app.api.users")

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserOut])
def list_users_endpoint(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
    request: Request = None,
) -> list[UserOut]:
    return list_users(db)


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    payload: UserCreate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
    request: Request = None,
) -> UserOut:
    try:
        user = create_user(db, email=payload.email, password=payload.password, role=payload.role, is_active=payload.is_active)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    logger.info("User created", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id, "target_id": user.id})
    return user


@router.get("/{user_id}", response_model=UserOut)
def get_user_endpoint(
    user_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
) -> UserOut:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user_endpoint(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
) -> UserOut:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return update_user(db, user, role=payload.role, is_active=payload.is_active, mfa_enabled=payload.mfa_enabled)


@router.delete("/{user_id}", response_model=Message)
def delete_user_endpoint(
    user_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
) -> Message:
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself")
    delete_user(db, user)
    return Message(message="User deleted")
