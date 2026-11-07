
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.logging import get_logger
from app.models.base import User
from app.schemas.auth import CaseCreate, CaseOut, CaseUpdate, EvidenceOut, MatchOut, Message
from app.services.audit_service import log_audit
from app.services.case_service import (
    can_access_case,
    create_case,
    create_evidence,
    create_match,
    delete_case,
    get_case,
    list_cases,
    update_case,
)
from app.services.evidence_service import validate_upload_file

logger = get_logger("app.api.cases")

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/", response_model=list[CaseOut])
def list_cases_endpoint(
    current_user: User = Depends(require_permission("cases:read")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> list[CaseOut]:
    cases = list_cases(db)
    if current_user.role == "reporter":
        cases = [c for c in cases if c.created_by == current_user.id]
    return cases


@router.post("/", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case_endpoint(
    payload: CaseCreate,
    current_user: User = Depends(require_permission("cases:create")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> CaseOut:
    case = create_case(db, payload, created_by=current_user.id)
    log_audit(db, actor_id=current_user.id, action="case.create", entity="case", entity_id=case.id, ip=getattr(request.client, "host", None) if request and request.client else None)
    logger.info("Case created", extra={"request_id": getattr(request.state, "request_id", "-") if request else "-", "actor_id": current_user.id, "entity": "case", "entity_id": case.id})
    return case


@router.get("/{case_id}", response_model=CaseOut)
def get_case_endpoint(
    case_id: int,
    current_user: User = Depends(require_permission("cases:read")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> CaseOut:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")
    return case


@router.put("/{case_id}", response_model=CaseOut)
def update_case_endpoint(
    case_id: int,
    payload: CaseUpdate,
    current_user: User = Depends(require_permission("cases:update")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> CaseOut:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")
    updated = update_case(db, case, payload)
    log_audit(db, actor_id=current_user.id, action="case.update", entity="case", entity_id=case.id, ip=getattr(request.client, "host", None) if request and request.client else None)
    return updated


@router.delete("/{case_id}", response_model=Message)
def delete_case_endpoint(
    case_id: int,
    current_user: User = Depends(require_permission("cases:delete")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> Message:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")
    delete_case(db, case)
    log_audit(db, actor_id=current_user.id, action="case.delete", entity="case", entity_id=case.id, ip=getattr(request.client, "host", None) if request and request.client else None)
    return Message(message="Case deleted")


@router.post("/{case_id}/evidence", response_model=EvidenceOut, status_code=status.HTTP_201_CREATED)
def add_evidence(
    case_id: int,
    file: UploadFile = File(...),
    type: str = Form("photo"),
    quality_score: float | None = Form(None),
    current_user: User = Depends(require_permission("evidence:upload")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> EvidenceOut:
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
    import os

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    safe_name = f"{case_id}_{file.filename or 'evidence'}"
    file_path = os.path.join(upload_dir, safe_name)
    with open(file_path, "wb") as f:
        f.write(contents)

    from app.schemas.auth import EvidenceCreate
    evidence = create_evidence(db, EvidenceCreate(case_id=case_id, type=type, quality_score=quality_score), file_path=file_path, uploaded_by=current_user.id)
    log_audit(db, actor_id=current_user.id, action="evidence.upload", entity="evidence", entity_id=evidence.id, ip=getattr(request.client, "host", None) if request and request.client else None)
    return evidence


@router.get("/{case_id}/matches", response_model=list[MatchOut])
def list_matches_endpoint(
    case_id: int,
    current_user: User = Depends(require_permission("cases:read")),
    db: Session = Depends(get_db),
) -> list[MatchOut]:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")
    from app.services.case_service import list_matches
    return list_matches(db, case_id)


@router.post("/{case_id}/match/run", response_model=MatchOut)
def run_match_endpoint(
    case_id: int,
    payload: dict[str, Any],
    current_user: User = Depends(require_permission("match:run")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> MatchOut:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    if not can_access_case(current_user, case):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your case")

    from app.schemas.auth import MatchCreate
    source_evidence_id: int = int(payload["source_evidence_id"])
    score = float(payload.get("score", 0.5))
    candidate_person_id: int | None = payload.get("candidate_person_id")
    match = create_match(db, MatchCreate(case_id=case_id, source_evidence_id=source_evidence_id, candidate_person_id=candidate_person_id, score=score))
    log_audit(db, actor_id=current_user.id, action="match.run", entity="match", entity_id=match.id, ip=getattr(request.client, "host", None) if request and request.client else None)
    return match
