# Data Model

## Entities
- **User**: id, email, password_hash, role (admin/investigator/reviewer/reporter), mfa_secret, created_at
- **Case**: id, title, status (open/in-progress/closed), created_by, created_at, updated_at
- **Person**: id, case_id, name, age, descriptors, photo_refs[]
- **Evidence**: id, case_id, file_path, type (photo/cctv), quality_score, uploaded_by
- **Match**: id, case_id, source_evidence_id, candidate_person_id, score, model_version, verified_by, status
- **KinshipPair**: id, case_id, person_a, person_b, relation, score
- **AuditLog**: id, actor_id, action, entity, timestamp, ip

## Relationships
User 1..* Case; Case 1..* Person/Evidence/Match; Match → Person, Evidence

## Storage
MySQL (cPanel-compatible) for structured data; object storage/cPanel file storage for images; model artifacts in MLflow registry.
- Use InnoDB, utf8mb4; migrations via Alembic
- Indexes on case_id, user_id, status, created_at
