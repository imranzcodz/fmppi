"""Tests for case service with DB."""
from app.schemas.auth import (
    CaseCreate,
    CaseUpdate,
    EvidenceCreate,
    KinshipPairCreate,
    MatchCreate,
    PersonCreate,
)
from app.services.case_service import (
    can_access_case,
    create_case,
    create_evidence,
    create_kinship_pair,
    create_match,
    create_person,
    delete_case,
    get_case,
    list_cases,
    list_evidence,
    list_kinship_pairs,
    list_matches,
    update_case,
)


class TestCaseService:
    def test_crud_cycle(self, db):
        case = create_case(db, CaseCreate(title="Test", status="open"), created_by=1)
        assert case.id is not None
        assert case.title == "Test"
        assert case.status == "open"

        fetched = get_case(db, case.id)
        assert fetched is not None
        assert fetched.id == case.id

        updated = update_case(db, fetched, CaseUpdate(title="New", status="closed"))
        assert updated.title == "New"
        assert updated.status == "closed"

        deleted = delete_case(db, updated)
        assert deleted is None
        assert get_case(db, case.id) is None

    def test_list_cases(self, db):
        create_case(db, CaseCreate(title="A", status="open"), created_by=1)
        create_case(db, CaseCreate(title="B", status="open"), created_by=1)
        cases = list_cases(db)
        assert len(cases) >= 2

    def test_can_access_case_admin(self, db):
        from app.models.base import User

        admin = User(email="admin@example.com", password_hash="x", role="admin")
        db.add(admin)
        db.commit()
        case = create_case(db, CaseCreate(title="X", status="open"), created_by=2)
        assert can_access_case(admin, case) is True

    def test_can_access_case_reporter_owner(self, db):
        from app.models.base import User

        reporter = User(email="rep@example.com", password_hash="x", role="reporter")
        db.add(reporter)
        db.commit()
        case = create_case(db, CaseCreate(title="X", status="open"), created_by=reporter.id)
        assert can_access_case(reporter, case) is True

    def test_can_access_case_reporter_not_owner(self, db):
        from app.models.base import User

        reporter = User(email="rep2@example.com", password_hash="x", role="reporter")
        db.add(reporter)
        db.commit()
        case = create_case(db, CaseCreate(title="X", status="open"), created_by=999)
        assert can_access_case(reporter, case) is False

    def test_create_person(self, db):
        case = create_case(db, CaseCreate(title="P", status="open"), created_by=1)
        person = create_person(
            db,
            PersonCreate(
                case_id=case.id,
                name="John Doe",
                age=30,
                descriptors="tall",
                photo_refs="ref1",
            ),
        )
        assert person.id is not None
        assert person.name == "John Doe"
        assert person.age == 30

    def test_create_and_list_evidence(self, db):
        case = create_case(db, CaseCreate(title="E", status="open"), created_by=1)
        ev = create_evidence(
            db,
            EvidenceCreate(case_id=case.id, type="cctv", quality_score=0.8),
            file_path="/uploads/1_evidence.jpg",
            uploaded_by=1,
        )
        assert ev.id is not None
        evs = list_evidence(db, case.id)
        assert len(evs) >= 1

    def test_create_and_list_match(self, db):
        case = create_case(db, CaseCreate(title="M", status="open"), created_by=1)
        match = create_match(
            db,
            MatchCreate(case_id=case.id, source_evidence_id=1, candidate_person_id=None, score=0.9),
        )
        assert match.id is not None
        assert match.score == 0.9
        matches = list_matches(db, case.id)
        assert len(matches) >= 1

    def test_create_and_list_kinship_pair(self, db):
        case = create_case(db, CaseCreate(title="K", status="open"), created_by=1)
        person_a = create_person(db, PersonCreate(case_id=case.id, name="Parent", age=40))
        person_b = create_person(db, PersonCreate(case_id=case.id, name="Child", age=15))
        pair = create_kinship_pair(
            db,
            KinshipPairCreate(
                case_id=case.id,
                person_a_id=person_a.id,
                person_b_id=person_b.id,
                relation="parent-child",
                score=0.85,
            ),
        )
        assert pair.id is not None
        pairs = list_kinship_pairs(db, case.id)
        assert len(pairs) >= 1
