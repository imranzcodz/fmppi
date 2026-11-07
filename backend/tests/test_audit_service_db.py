"""Tests for audit service with DB."""
from app.models.base import AuditLog, User
from app.services.audit_service import list_audit, log_audit


class TestAuditService:
    def test_log_and_list_audit(self, db):
        user = User(email="audit@example.com", password_hash="x", role="admin")
        db.add(user)
        db.commit()

        entry = log_audit(db, actor_id=user.id, action="case.create", entity="case", entity_id=1, ip="127.0.0.1")
        assert entry.id is not None
        assert entry.action == "case.create"

        logs = list_audit(db)
        assert len(logs) >= 1

    def test_list_audit_filter_by_case(self, db):
        user = User(email="audit2@example.com", password_hash="x", role="admin")
        db.add(user)
        db.commit()
        log_audit(db, actor_id=user.id, action="case.create", entity="case", entity_id=42)
        logs = list_audit(db, case_id=42)
        assert len(logs) >= 1

    def test_list_audit_filter_by_actor(self, db):
        user = User(email="audit3@example.com", password_hash="x", role="admin")
        db.add(user)
        db.commit()
        log_audit(db, actor_id=user.id, action="case.read", entity="case", entity_id=1)
        logs = list_audit(db, actor_id=user.id)
        assert len(logs) >= 1

    def test_list_audit_empty(self, db):
        logs = list_audit(db)
        assert isinstance(logs, list)
