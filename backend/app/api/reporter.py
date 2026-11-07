
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.logging import get_logger
from app.models.base import User
from app.schemas.auth import CaseCreate, CaseOut, EvidenceOut
from app.services.case_service import can_access_case, create_case, create_evidence, get_case
from app.services.evidence_service import validate_upload_file

logger = get_logger("app.api.reporter")

router = APIRouter(prefix="/reporter", tags=["reporter"])


def _require_reporter(current_user: User) -> User:
    if current_user.role != "reporter":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reporter only")
    return current_user


@router.post("/cases", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def reporter_create_case(
    title: str = Form(...),
    status: str = Form("open"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None,
) -> CaseOut:
    _require_reporter(current_user)
    case = create_case(db, CaseCreate(title=title, status=status), created_by=current_user.id)
    logger.info("Reporter case created", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id, "entity": "case", "entity_id": case.id})
    return case


@router.post("/cases/{case_id}/evidence", response_model=EvidenceOut, status_code=status.HTTP_201_CREATED)
def reporter_upload_evidence(
    case_id: int,
    file: UploadFile = File(...),
    type: str = Form("photo"),
    quality_score: float | None = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None,
) -> EvidenceOut:
    _require_reporter(current_user)
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")

    try:
        validate_upload_file(file)
        contents = file.file.read()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    # In production write to object storage; here we persist under ./uploads
    import os

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = f"{case_id}_{file.filename or 'evidence'}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    from app.schemas.auth import EvidenceCreate
    evidence = create_evidence(db, EvidenceCreate(case_id=case_id, type=type, quality_score=quality_score), file_path=file_path, uploaded_by=current_user.id)
    logger.info("Evidence uploaded", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id, "entity": "evidence", "entity_id": evidence.id})
    return evidence


@router.get("/cases/{case_id}/status", response_model=CaseOut)
def reporter_case_status(
    case_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> CaseOut:
    _require_reporter(current_user)
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")
    return case
