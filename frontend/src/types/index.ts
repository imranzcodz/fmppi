export type Role = 'admin' | 'investigator' | 'reviewer' | 'reporter'

export type CaseStatus = 'open' | 'in-progress' | 'closed'

export type EvidenceType = 'photo' | 'cctv'

export type MatchStatus = 'pending' | 'verified' | 'rejected'

export interface User {
  id: string
  email: string
  role: Role
  mfaEnabled?: boolean
  createdAt: string
}

export interface Case {
  id: string
  title: string
  status: CaseStatus
  createdBy: string
  createdAt: string
  updatedAt: string
}

export interface Person {
  id: string
  caseId: string
  name: string
  age?: number
  descriptors?: string
  photoRefs: string[]
}

export interface Evidence {
  id: string
  caseId: string
  filePath: string
  type: EvidenceType
  qualityScore?: number
  uploadedBy: string
}

export interface Match {
  id: string
  caseId: string
  sourceEvidenceId: string
  candidatePersonId: string
  score: number
  modelVersion: string
  verifiedBy?: string
  status: MatchStatus
}

export interface KinshipPair {
  id: string
  caseId: string
  personA: string
  personB: string
  relation?: string
  score: number
}

export interface AuditLog {
  id: string
  actorId: string
  action: string
  entity: string
  timestamp: string
  ip?: string
  actorName?: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  accessToken: string
  refreshToken: string
  user: User
  mfaRequired: boolean
}

export interface MfaVerifyRequest {
  email: string
  code: string
}

export interface MfaVerifyResponse {
  accessToken: string
  refreshToken: string
  user: User
}

export interface RegisterRequest {
  email: string
  password: string
  role?: Role
}

export interface RegisterResponse {
  user: User
}

export interface VerifyMatch {
  candidateId: string
  candidateName?: string
  score: number
  caseId?: string
  sourceUrl?: string
}

export interface VerifyResponse {
  matches: VerifyMatch[]
}

export interface KinshipResponse {
  score: number
  isKin: boolean
  confidence: number
}

export interface Pagination {
  page?: number
  limit?: number
}
