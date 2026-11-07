# API Specification (FastAPI)

## Auth
- POST /auth/register → new user (reporter self-registration)
- POST /auth/login → JWT (access+refresh)
- POST /auth/mfa/verify
- POST /auth/refresh

## Users (RBAC: admin)
- GET/POST/PUT/DELETE /users

## Reporter (Family & Community Support)
- POST /reporter/cases → create case as reporter (submit missing person report + photos/evidence)
- POST /reporter/cases/{id}/evidence → upload additional evidence to own case
- GET /reporter/cases/{id}/status → view own case status & match results (read-only)


## Verify
- POST /verify/local — upload photo → 1:N search against local DB → ranked matches
- POST /verify/global — upload photo → web reverse-image search → similar faces across web
- POST /verify/kinship — upload 2 photos → Siamese kin score + confidence

## Cases
- GET /cases, POST /cases, GET /cases/{id}, PUT /cases/{id}, DELETE /cases/{id}
- POST /cases/{id}/evidence (multipart)
- GET /cases/{id}/matches
- POST /cases/{id}/match/run

## ML
- POST /ml/detect
- POST /ml/embed
- POST /ml/verify (kinship)
- POST /ml/search (1:N)

## Audit
- GET /audit?case_id=&actor=

## Standards
REST, JSON, Pydantic validation, OpenAPI auto-docs, rate limiting, RBAC middleware, request ID tracing.
