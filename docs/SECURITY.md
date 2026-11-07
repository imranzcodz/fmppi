# Security & Compliance

## Auth
- JWT (short-lived access + refresh), MFA (TOTP), password hashing (bcrypt/argon2)

## RBAC
- Roles: admin, investigator, reviewer, reporter
- Permissions enforced at API middleware + UI route guards

## Data Protection
- TLS in transit; encryption at rest for DB & evidence
- Data minimization, retention policy, consent tracking
- PII redaction in logs

## AppSec
- OWASP top-10 checklist, SAST/DAST in CI
- Input validation (Pydantic), file type/size limits, rate limiting
- CSRF protection, secure headers, CORS allowlist

## Audit
- Immutable audit log of all case/evidence/match actions
