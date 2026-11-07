from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

FAKE_USERS = {
    "admin-token": {"username": "admin", "role": "admin"},
    "investigator-token": {"username": "investigator", "role": "investigator"},
    "reviewer-token": {"username": "reviewer", "role": "reviewer"},
    "reporter-token": {"username": "reporter", "role": "reporter"},
}

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = FAKE_USERS.get(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_role(role: str):
    def dependency(user=Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="forbidden",
            )
        return user
    return dependency

def require_any_role(*roles: str):
    def dependency(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="forbidden",
            )
        return user
    return dependency
