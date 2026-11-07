from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str | None = Field(default="reporter")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class MFASetup(BaseModel):
    secret: str
    provisioning_url: str


class MFAVerify(BaseModel):
    email: EmailStr
    code: str


class UserOut(BaseModel):
    id: int
    email: str
    role: str
    mfa_enabled: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "reporter"
    is_active: bool = True


class UserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    mfa_enabled: bool | None = None


class Message(BaseModel):
    message: str


class CaseBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    status: str = "open"


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: str | None = None


class CaseOut(CaseBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    age: int | None = Field(default=None, ge=0, le=150)
    descriptors: str | None = None
    photo_refs: str | None = None


class PersonCreate(PersonBase):
    case_id: int


class PersonOut(PersonBase):
    id: int
    case_id: int

    class Config:
        from_attributes = True


class EvidenceBase(BaseModel):
    type: str = "photo"
    quality_score: float | None = Field(default=None, ge=0, le=1)


class EvidenceCreate(EvidenceBase):
    case_id: int


class EvidenceOut(EvidenceBase):
    id: int
    case_id: int
    file_path: str
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class MatchBase(BaseModel):
    score: float = Field(ge=0, le=1)
    model_version: str | None = None
    status: str = "pending"


class MatchCreate(MatchBase):
    case_id: int
    source_evidence_id: int
    candidate_person_id: int | None = None


class MatchOut(MatchBase):
    id: int
    case_id: int
    source_evidence_id: int
    candidate_person_id: int | None
    verified_by: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class KinshipPairBase(BaseModel):
    person_a_id: int
    person_b_id: int
    relation: str = Field(min_length=1, max_length=100)
    score: float = Field(ge=0, le=1)


class KinshipPairCreate(KinshipPairBase):
    case_id: int


class KinshipPairOut(KinshipPairBase):
    id: int
    case_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogOut(BaseModel):
    id: int
    actor_id: int | None
    action: str
    entity: str
    entity_id: int | None
    timestamp: datetime
    ip: str | None

    class Config:
        from_attributes = True


class LocalVerifyRequest(BaseModel):
    case_id: int | None = None


class LocalVerifyResult(BaseModel):
    matches: list[dict]


class GlobalVerifyResult(BaseModel):
    matches: list[dict]


class KinshipVerifyRequest(BaseModel):
    case_id: int | None = None
    person_a_id: int | None = None
    person_b_id: int | None = None


class KinshipVerifyResult(BaseModel):
    score: float
    is_kin: bool
    confidence: float
    relation: str | None = None


class MatchRunRequest(BaseModel):
    case_id: int
    source_evidence_id: int


class MatchRunResult(BaseModel):
    match_id: int
    score: float
    status: str
