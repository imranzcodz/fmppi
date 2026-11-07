from app.models.base import AuditLog


def log_audit(db, actor_id, action: str, entity: str, entity_id=None, ip=None) -> AuditLog:
    entry = AuditLog(actor_id=actor_id, action=action, entity=entity, entity_id=entity_id, ip=ip)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_audit(db, case_id=None, actor_id=None, limit: int = 100):
    query = db.query(AuditLog)
    if case_id is not None:
        # AuditLog has no case_id; filter by entity_id if it refers to a case
        query = query.filter(AuditLog.entity_id == case_id)
    if actor_id is not None:
        query = query.filter(AuditLog.actor_id == actor_id)
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
