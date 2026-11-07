from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.logging import get_logger
from app.models.base import User
from app.schemas.auth import (
    MFASetup,
    MFAVerify,
    Token,
    TokenRefresh,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.services.auth_service import authenticate_user, issue_tokens, setup_mfa, verify_mfa

logger = get_logger("app.api.auth")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db), request: Request = None) -> UserOut:
    from app.services.user_service import create_user

    # Reporter self-registration: force reporter role.
    try:
        user = create_user(db, email=payload.email, password=payload.password, role="reporter")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    logger.info("User registered", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": user.id})
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db), request: Request = None) -> Token:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        logger.warning("Failed login attempt", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "email": payload.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    tokens = issue_tokens(user)
    logger.info("User login", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": user.id})
    return tokens


@router.post("/mfa/verify")
def mfa_verify(payload: MFAVerify, db: Session = Depends(get_db), request: Request = None) -> dict:
    user = verify_mfa(db, payload.email, payload.code)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
    tokens = issue_tokens(user)
    logger.info("MFA verify success", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": user.id})
    return tokens


@router.post("/mfa/setup", response_model=MFASetup)
def mfa_setup(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db), request: Request = None) -> MFASetup:
    result = setup_mfa(db, current_user)
    logger.info("MFA setup requested", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id})
    return result


@router.post("/refresh", response_model=Token)
def refresh(payload: TokenRefresh, request: Request = None) -> Token:
    payload_decoded = decode_token(payload.refresh_token)
    if not payload_decoded or payload_decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user_id = payload_decoded.get("sub")
    tokens = {
        "access_token": create_access_token(subject=str(user_id)),
        "refresh_token": create_refresh_token(subject=str(user_id)),
        "token_type": "bearer",
    }
    logger.info("Token refreshed", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-"})
    return tokens


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_active_user)) -> UserOut:
    return current_user
