from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database
import models
import schemas
import auth

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FMPPI API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/cases", response_model=schemas.CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(
    case: schemas.CaseCreate,
    db: Session = Depends(database.get_db),
    user=Depends(auth.require_any_role("admin", "investigator", "reviewer")),
):
    existing = db.query(models.Case).filter(models.Case.case_number == case.case_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="case number exists")
    db_case = models.Case(**case.model_dump())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

@app.get("/cases", response_model=list[schemas.CaseOut])
def list_cases(
    db: Session = Depends(database.get_db),
    user=Depends(auth.get_current_user),
):
    return db.query(models.Case).all()

@app.get("/cases/{case_id}", response_model=schemas.CaseOut)
def get_case(
    case_id: int,
    db: Session = Depends(database.get_db),
    user=Depends(auth.get_current_user),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="case not found")
    return case

@app.post("/cases/{case_id}/evidences", response_model=schemas.EvidenceOut, status_code=status.HTTP_201_CREATED)
def add_evidence(
    case_id: int,
    evidence: schemas.EvidenceCreate,
    db: Session = Depends(database.get_db),
    user=Depends(auth.require_any_role("admin", "investigator")),
):
    case = db.query(models.Case).filter(models.Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="case not found")
    db_evidence = models.Evidence(**evidence.model_dump(), case_id=case_id)
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

@app.post("/verify", response_model=schemas.VerifyResponse)
def verify(request: schemas.VerifyRequest):
    match = request.probe_image == request.gallery_image
    return {"match": match, "confidence": 1.0 if match else 0.0}

@app.get("/rbac/admin-only")
def admin_only(user=Depends(auth.require_role("admin"))):
    return {"ok": True}

@app.get("/rbac/investigator-or-above")
def investigator_or_above(user=Depends(auth.require_any_role("admin", "investigator"))):
    return {"ok": True}

@app.get("/rbac/reporter-only")
def reporter_only(user=Depends(auth.require_role("reporter"))):
    return {"ok": True}
