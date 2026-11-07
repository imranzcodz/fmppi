from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.logging import get_logger
from app.models.base import User
from app.services.verify_service import global_verify, kinship_verify, local_verify

logger = get_logger("app.api.verify")

router = APIRouter(prefix="/verify", tags=["verify"])


def _read_upload(file: UploadFile) -> bytes:
    data = file.file.read()
    file.file.seek(0)
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")
    return data


@router.post("/local")
def verify_local(
    file: UploadFile = File(...),
    case_id: int | None = None,
    current_user: User = Depends(require_permission("verify:local")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> dict:
    image_bytes = _read_upload(file)
    result = local_verify(image_bytes, case_id=case_id, db=db)
    logger.info("Verify local", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id, "case_id": case_id})
    return result


@router.post("/global")
def verify_global(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("verify:global")),
    request: Request = None,
) -> dict:
    image_bytes = _read_upload(file)
    result = global_verify(image_bytes)
    logger.info("Verify global", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id})
    return result


@router.post("/kinship")
def verify_kinship(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    current_user: User = Depends(require_permission("verify:kinship")),
    request: Request = None,
) -> dict:
    image_a = _read_upload(file_a)
    image_b = _read_upload(file_b)
    result = kinship_verify(image_a, image_b)
    logger.info("Verify kinship", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id})
    return result
