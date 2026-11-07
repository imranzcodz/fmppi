
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_permission
from app.models.base import User
from app.services.audit_service import list_audit

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=list[dict])
def list_audit_endpoint(
    case_id: int | None = Query(None),
    actor_id: int | None = Query(None),
    current_user: User = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
    request: Request = None,
) -> list[dict]:
    logs = list_audit(db, case_id=case_id, actor_id=actor_id)
    return [
        {
            "id": entry.id,
            "actor_id": entry.actor_id,
            "action": entry.action,
            "entity": entry.entity,
            "entity_id": entry.entity_id,
            "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
            "ip": entry.ip,
        }
        for entry in logs
    ]
