from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="reporter", index=True)
    mfa_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    cases = relationship("Case", back_populates="creator", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="uploader")


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open", index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    creator = relationship("User", back_populates="cases")
    persons = relationship("Person", back_populates="case", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="case", cascade="all, delete-orphan")
    kinship_pairs = relationship("KinshipPair", back_populates="case", cascade="all, delete-orphan")


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    descriptors: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    photo_refs: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string

    case = relationship("Case", back_populates="persons")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # photo | cctv
    quality_score: Mapped[float | None] = mapped_column(nullable=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case = relationship("Case", back_populates="evidence")
    uploader = relationship("User", back_populates="evidence")
    source_matches = relationship("Match", back_populates="source_evidence", foreign_keys="[Match.source_evidence_id]")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False, index=True)
    source_evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id"), nullable=False, index=True)
    candidate_person_id: Mapped[int | None] = mapped_column(ForeignKey("persons.id"), nullable=True, index=True)
    score: Mapped[float] = mapped_column(nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case = relationship("Case", back_populates="matches")
    source_evidence = relationship("Evidence", back_populates="source_matches", foreign_keys=[source_evidence_id])
    candidate_person = relationship("Person", foreign_keys=[candidate_person_id])


class KinshipPair(Base):
    __tablename__ = "kinship_pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False, index=True)
    person_a_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), nullable=False, index=True)
    person_b_id: Mapped[int] = mapped_column(ForeignKey("persons.id"), nullable=False, index=True)
    relation: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    case = relationship("Case", back_populates="kinship_pairs")
    person_a = relationship("Person", foreign_keys=[person_a_id])
    person_b = relationship("Person", foreign_keys=[person_b_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    entity: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
