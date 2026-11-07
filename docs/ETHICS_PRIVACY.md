# FMPPI — Ethics & Privacy

## Scope
Missing-person identification involves sensitive biometric data. This document defines handling rules.

## Data Minimization
- Collect only images/metadata needed for matching.
- No biometric templates stored longer than case retention period.
- Evidence file names hashed; PII redacted from logs.

## Consent & Compliance
- IRB/ethics review before using human subject datasets (KinFaceW, LFW, CCTV, ORL_Faces).
- Record dataset licenses and consent provenance.
- Comply with GDPR/local data-protection laws; right to erasure supported.

## Dataset License & Provenance Register

| Dataset | Source | License | Status | Consent Provenance |
|---------|--------|---------|--------|-------------------|
| KinFaceW I & II | https://www.kinfacew.com/ | Research use | Acquired (datasets/kinfacew/) | Academic research license; contact authors for commercial use |
| LFW | https://www.kaggle.com/datasets/jessicali9530/lfw-dataset | Non-commercial research use | Acquired (datasets/lfw/) | Public figures; consent not individually documented - research use only |
| CCTV face detection | https://universe.roboflow.com/cadit/cctv-face-detection | Research use | Acquired (datasets/cctvface/) | Roboflow community dataset; verify per-jurisdiction CCTV rules |
| ORL_Faces | https://cam-orl.co.uk/facedatabase.html | Research use | Acquired (datasets/orl_faces/) | University of Cambridge; academic research use |

## Retention
- Case evidence retained per jurisdictional policy; auto-purge after retention expiry.
- Audit logs immutable; access restricted to admin/reviewer roles.

## Fairness & Bias
- Evaluate accuracy across demographics (age, gender, ethnicity).
- Fairness audit each sprint; document parity gaps.
- Confidence thresholds calibrated to minimize false positives in missing-person context.
- LFW demographic skew noted: predominantly adult, male, Western subjects - supplement with diverse datasets before production.

## Security
- RBAC: Admin / Investigator / Reviewer / Reporter.
- JWT + MFA for auth; TLS in transit; encryption at rest.
- Rate limiting, input validation, file type/size limits on uploads.
- Audit log of all case/evidence/match/view actions.

## Use Limitations
- FMPPI is a decision-support tool; final identification requires human review.
- Global-verify (web search) results are indicative only, not proof.
- Datasets used for training/evaluation are research-only; not for production deployment without full ethics review and dataset re-licensing.
