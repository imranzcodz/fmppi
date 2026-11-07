# FMPPI — Ethics & Privacy

## Scope
Missing-person identification involves sensitive biometric data. This document defines handling rules.

## Data Minimization
- Collect only images/metadata needed for matching.
- No biometric templates stored longer than case retention period.
- Evidence file names hashed; PII redacted from logs.

## Consent & Compliance
- IRB/ethics review before using human subject datasets (KinFaceW, LFW, YouTubeFaceDB, CCTV).
- Record dataset licenses and consent provenance.
- Comply with GDPR/local data-protection laws; right to erasure supported.

## Retention
- Case evidence retained per jurisdictional policy; auto-purge after retention expiry.
- Audit logs immutable; access restricted to admin/reviewer roles.

## Fairness & Bias
- Evaluate accuracy across demographics (age, gender, ethnicity).
- Fairness audit each sprint; document parity gaps.
- Confidence thresholds calibrated to minimize false positives in missing-person context.

## Security
- RBAC: Admin / Investigator / Reviewer.
- JWT + MFA for auth; TLS in transit; encryption at rest.
- Rate limiting, input validation, file type/size limits on uploads.
- Audit log of all case/evidence/match/view actions.

## Use Limitations
- FMPPI is a decision-support tool; final identification requires human review.
- Global-verify (web search) results are indicative only, not proof.
