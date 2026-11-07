# Testing Strategy

## Levels
- Unit: pytest (backend/ml), Jest (frontend)
- Integration: API + DB (testcontainers)
- E2E: Playwright (web flows)
- ML regression: golden datasets, metric gates

## Coverage
- Backend & ML wrappers ≥80% (G1)
- Frontend ≥70%

## Quality Gates (CI)
- Lint (ruff/flake8, eslint)
- Type check (mypy/tsc)
- Security scan (bandit, npm audit)
- ML metric gates (G2-G4)

## Test Data
- Synthetic fixtures; anonymized samples; no real PII in repo
