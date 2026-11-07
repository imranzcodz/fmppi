// API endpoint constants (base path, no host).
// Host is configured via API_BASE_URL env var at runtime.

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const ENDPOINTS = {
  auth: {
    register: "/auth/register",
    login: "/auth/login",
    mfaVerify: "/auth/mfa/verify",
    refresh: "/auth/refresh",
  },
  users: {
    list: "/users",
  },
  reporter: {
    cases: "/reporter/cases",
    caseStatus: (id: string) => `/reporter/cases/${id}/status`,
    evidence: (id: string) => `/reporter/cases/${id}/evidence`,
  },
  verify: {
    local: "/verify/local",
    global: "/verify/global",
    kinship: "/verify/kinship",
  },
  cases: {
    list: "/cases",
    detail: (id: string) => `/cases/${id}`,
    evidence: (id: string) => `/cases/${id}/evidence`,
    matches: (id: string) => `/cases/${id}/matches`,
    runMatch: (id: string) => `/cases/${id}/match/run`,
  },
  ml: {
    detect: "/ml/detect",
    embed: "/ml/embed",
    verify: "/ml/verify",
    search: "/ml/search",
  },
  audit: {
    list: "/audit",
  },
} as const;
