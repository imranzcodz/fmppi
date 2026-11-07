"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-11-07 08:55:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="reporter"),
        sa.Column("mfa_secret", sa.Text(), nullable=True),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)

    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="open"),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cases_status"), "cases", ["status"], unique=False)
    op.create_index(op.f("ix_cases_created_by"), "cases", ["created_by"], unique=False)

    op.create_table(
        "persons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("descriptors", sa.Text(), nullable=True),
        sa.Column("photo_refs", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_persons_case_id"), "persons", ["case_id"], unique=False)

    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("file_path", sa.String(length=512), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_evidence_case_id"), "evidence", ["case_id"], unique=False)
    op.create_index(op.f("ix_evidence_type"), "evidence", ["type"], unique=False)
    op.create_index(op.f("ix_evidence_uploaded_by"), "evidence", ["uploaded_by"], unique=False)

    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("source_evidence_id", sa.Integer(), nullable=False),
        sa.Column("candidate_person_id", sa.Integer(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=100), nullable=True),
        sa.Column("verified_by", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.ForeignKeyConstraint(["candidate_person_id"], ["persons.id"], ),
        sa.ForeignKeyConstraint(["source_evidence_id"], ["evidence.id"], ),
        sa.ForeignKeyConstraint(["verified_by"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matches_case_id"), "matches", ["case_id"], unique=False)
    op.create_index(op.f("ix_matches_source_evidence_id"), "matches", ["source_evidence_id"], unique=False)
    op.create_index(op.f("ix_matches_candidate_person_id"), "matches", ["candidate_person_id"], unique=False)
    op.create_index(op.f("ix_matches_status"), "matches", ["status"], unique=False)

    op.create_table(
        "kinship_pairs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("person_a_id", sa.Integer(), nullable=False),
        sa.Column("person_b_id", sa.Integer(), nullable=False),
        sa.Column("relation", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ),
        sa.ForeignKeyConstraint(["person_a_id"], ["persons.id"], ),
        sa.ForeignKeyConstraint(["person_b_id"], ["persons.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_kinship_pairs_case_id"), "kinship_pairs", ["case_id"], unique=False)
    op.create_index(op.f("ix_kinship_pairs_person_a_id"), "kinship_pairs", ["person_a_id"], unique=False)
    op.create_index(op.f("ix_kinship_pairs_person_b_id"), "kinship_pairs", ["person_b_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("entity", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_actor_id"), "audit_logs", ["actor_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity"), "audit_logs", ["entity"], unique=False)
    op.create_index(op.f("ix_audit_logs_timestamp"), "audit_logs", ["timestamp"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("kinship_pairs")
    op.drop_table("matches")
    op.drop_table("evidence")
    op.drop_table("persons")
    op.drop_table("cases")
    op.drop_table("users")
