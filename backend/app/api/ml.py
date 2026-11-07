from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import require_permission
from app.logging import get_logger
from app.models.base import User
from app.services.verify_service import kinship_verify, local_verify

logger = get_logger("app.api.ml")

router = APIRouter(prefix="/ml", tags=["ml"])


def _read_upload(file: UploadFile) -> bytes:
    data = file.file.read()
    file.file.seek(0)
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    return data


@router.post("/detect")
def ml_detect(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("verify:local")),
) -> dict:
    # Placeholder: face detection boxes stub
    return {"boxes": [], "count": 0, "model_version": "yoloface-stub"}


@router.post("/embed")
def ml_embed(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("verify:local")),
) -> dict:
    image_bytes = _read_upload(file)
    import hashlib

    digest = hashlib.sha256(image_bytes).hexdigest()
    vector = [int(digest[i:i + 2], 16) / 255.0 for i in range(0, 64, 2)]
    return {"embedding": vector, "dim": len(vector), "model_version": "facenet-stub"}


@router.post("/verify")
def ml_verify(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    current_user: User = Depends(require_permission("verify:kinship")),
) -> dict:
    result = kinship_verify(_read_upload(file_a), _read_upload(file_b))
    return result


@router.post("/search")
def ml_search(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("verify:local")),
) -> dict:
    return local_verify(_read_upload(file))
