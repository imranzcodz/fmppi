# FMPPI — Mobile App Spec (Phase 2)

## Scope
React Native MVP for field investigators: search, capture, view matches.

## Features
- Camera capture / gallery select for probe photo
- local-verify: upload photo → 1:N search → ranked matches
- kinship-verify: two photos → kin score + confidence
- Case list/detail view (RBAC-filtered)
- Login with JWT + MFA
- Offline queue for capture; sync on reconnect

## Tech
- React Native + Expo
- Native camera/image picker
- Axios + JWT interceptors to FastAPI backend
- Secure storage for tokens

## Deliverables
- Mobile app APK/IPA (add-on phase)
- API contract shared with backend (`/verify/local`, `/verify/kinship`, `/cases`)
- Biometric consent prompt before capture
