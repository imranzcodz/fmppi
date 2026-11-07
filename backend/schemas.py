from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CaseBase(BaseModel):
    case_number: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=200)
    status: Optional[str] = "open"

class CaseCreate(CaseBase):
    pass

class CaseOut(CaseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EvidenceBase(BaseModel):
    file_name: str = Field(min_length=1)
    file_type: str = Field(min_length=1)
    size_bytes: int = Field(ge=0)

class EvidenceCreate(EvidenceBase):
    pass

class EvidenceOut(EvidenceBase):
    id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

class VerifyRequest(BaseModel):
    probe_image: str
    gallery_image: str

class VerifyResponse(BaseModel):
    match: bool
    confidence: float
