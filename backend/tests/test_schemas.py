"""Tests for schema validation."""
from app.schemas.auth import CaseCreate, CaseOut, EvidenceCreate, UserRegister


class TestSchemas:
    def test_user_register_valid(self):
        schema = UserRegister(email="a@b.com", password="Secret1234", role="reporter")
        assert schema.email == "a@b.com"
        assert schema.password == "Secret1234"
        assert schema.role == "reporter"

    def test_user_register_password_too_short(self):
        import pytest

        with pytest.raises(Exception):
            UserRegister(email="a@b.com", password="short", role="reporter")

    def test_case_create(self):
        case = CaseCreate(title="Test", status="open")
        assert case.title == "Test"
        assert case.status == "open"

    def test_case_create_default_status(self):
        case = CaseCreate(title="Test")
        assert case.status == "open"

    def test_evidence_create(self):
        ev = EvidenceCreate(case_id=1, type="cctv", quality_score=0.5)
        assert ev.case_id == 1
        assert ev.type == "cctv"
        assert ev.quality_score == 0.5
