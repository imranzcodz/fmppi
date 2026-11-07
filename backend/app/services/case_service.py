from sqlalchemy.orm import Session

from app.models.base import Case, Evidence, KinshipPair, Match, Person, User
from app.schemas.auth import (
    CaseCreate,
    CaseUpdate,
    EvidenceCreate,
    KinshipPairCreate,
    MatchCreate,
    PersonCreate,
)


def create_case(db: Session, payload: CaseCreate, created_by: int) -> Case:
    case = Case(title=payload.title, status=payload.status, created_by=created_by)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def get_case(db: Session, case_id: int) -> Case | None:
    return db.query(Case).filter(Case.id == case_id).first()


def list_cases(db: Session):
    return db.query(Case).all()


def update_case(db: Session, case: Case, payload: CaseUpdate) -> Case:
    if payload.title is not None:
        case.title = payload.title
    if payload.status is not None:
        case.status = payload.status
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def delete_case(db: Session, case: Case) -> None:
    db.delete(case)
    db.commit()


def create_person(db: Session, payload: PersonCreate) -> Person:
    person = Person(
        case_id=payload.case_id,
        name=payload.name,
        age=payload.age,
        descriptors=payload.descriptors,
        photo_refs=payload.photo_refs,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def create_evidence(db: Session, payload: EvidenceCreate, file_path: str, uploaded_by: int) -> Evidence:
    evidence = Evidence(
        case_id=payload.case_id,
        file_path=file_path,
        type=payload.type,
        quality_score=payload.quality_score,
        uploaded_by=uploaded_by,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


def list_evidence(db: Session, case_id: int):
    return db.query(Evidence).filter(Evidence.case_id == case_id).all()


def create_match(db: Session, payload: MatchCreate) -> Match:
    match = Match(
        case_id=payload.case_id,
        source_evidence_id=payload.source_evidence_id,
        candidate_person_id=payload.candidate_person_id,
        score=payload.score,
        model_version=payload.model_version,
        status=payload.status,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def list_matches(db: Session, case_id: int):
    return db.query(Match).filter(Match.case_id == case_id).all()


def create_kinship_pair(db: Session, payload: KinshipPairCreate) -> KinshipPair:
    pair = KinshipPair(
        case_id=payload.case_id,
        person_a_id=payload.person_a_id,
        person_b_id=payload.person_b_id,
        relation=payload.relation,
        score=payload.score,
    )
    db.add(pair)
    db.commit()
    db.refresh(pair)
    return pair


def list_kinship_pairs(db: Session, case_id: int):
    return db.query(KinshipPair).filter(KinshipPair.case_id == case_id).all()


def can_access_case(user: User, case: Case) -> bool:
    if user.role == "admin":
        return True
    if user.role in ("investigator", "reviewer"):
        return True
    # reporter can only access own cases
    return case.created_by == user.id
