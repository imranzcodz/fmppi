// Shared API types for FMPPI mobile client.
// Contract mirrors docs/API_SPEC.md (FastAPI backend).
// These types are shared between mobile and backend clients.

export type Json = Record<string, unknown>;

// ---------------------------------------------------------------------------
// Common
// ---------------------------------------------------------------------------

export interface Pagination {
  page?: number;
  page_size?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
  request_id?: string;
}

// ---------------------------------------------------------------------------
// Auth  (POST /auth/register, /auth/login, /auth/mfa/verify, /auth/refresh)
// ---------------------------------------------------------------------------

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  role?: "admin" | "investigator" | "reporter";
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MfaVerifyRequest {
  user_id: string;
  code: string;
}

export interface MfaVerifyResponse {
  verified: boolean;
  access_token?: string;
  refresh_token?: string;
}

export interface RefreshResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenPayload {
  access_token: string;
  refresh_token: string;
}

// ---------------------------------------------------------------------------
// Verify  (POST /verify/local, POST /verify/kinship)
// ---------------------------------------------------------------------------

export interface MatchResult {
  case_id: string;
  person_id?: string;
  similarity: number;
  bbox?: [number, number, number, number];
  thumbnail_url?: string;
  case_title?: string;
  created_at?: string;
}

export interface LocalVerifyRequest {
  // probe photo (multipart file). Carried as FormData, not JSON body.
  probe_photo_uri: string;
  probe_photo_mime_type: string;
  probe_photo_file_name: string;
  top_k?: number;
  min_similarity?: number;
}

export interface LocalVerifyResponse {
  query_id: string;
  matches: MatchResult[];
  searched_at: string;
}

export interface KinshipVerifyRequest {
  photo1_uri: string;
  photo2_uri: string;
  photo1_mime_type: string;
  photo2_mime_type: string;
  photo1_file_name: string;
  photo2_file_name: string;
}

export interface KinshipVerifyResponse {
  pair_id: string;
  kin_score: number; // 0..1
  confidence: number; // 0..1
  related: boolean;
  verified_at: string;
}

// ---------------------------------------------------------------------------
// Cases  (GET/POST /cases, GET/PUT/DELETE /cases/{id}, evidence, matches)
// ---------------------------------------------------------------------------

export type CaseRole = "admin" | "investigator" | "reporter";

export interface Case {
  id: string;
  title: string;
  description?: string;
  status: "open" | "closed" | "archived";
  created_by: string;
  created_by_role: CaseRole;
  created_at: string;
  updated_at: string;
  match_count?: number;
}

export interface CreateCaseRequest {
  title: string;
  description?: string;
  probe_photo_uri?: string;
}

export interface CaseListResponse extends PaginatedResponse<Case> {}

export interface CaseDetail extends Case {
  evidence_count: number;
  matches: MatchResult[];
}

export interface UploadEvidenceRequest {
  case_id: string;
  file_uri: string;
  file_mime_type: string;
  file_name: string;
}

export interface UploadEvidenceResponse {
  evidence_id: string;
  case_id: string;
  file_url: string;
  uploaded_at: string;
}

export interface RunMatchRequest {
  case_id: string;
  probe_photo_uri: string;
  top_k?: number;
}

export interface RunMatchResponse {
  match_run_id: string;
  case_id: string;
  matches: MatchResult[];
  ran_at: string;
}

// ---------------------------------------------------------------------------
// ML (internal, exposed via verify endpoints)
// ---------------------------------------------------------------------------

export interface DetectRequest {
  image_uri: string;
}

export interface DetectResponse {
  faces: Array<{
    bbox: [number, number, number, number];
    confidence: number;
  }>;
}

export interface EmbedResponse {
  embedding_id: string;
  dimension: number;
}

export interface VerifyKinshipMlRequest {
  embedding1_id: string;
  embedding2_id: string;
}

export interface VerifyKinshipMlResponse {
  kin_score: number;
  confidence: number;
}

export interface SearchMlRequest {
  embedding_id: string;
  top_k?: number;
  min_similarity?: number;
}

export interface SearchMlResponse {
  matches: MatchResult[];
}

// ---------------------------------------------------------------------------
// Audit
// ---------------------------------------------------------------------------

export interface AuditEntry {
  id: string;
  case_id?: string;
  actor: string;
  action: string;
  created_at: string;
  meta?: Json;
}

export interface AuditQuery {
  case_id?: string;
  actor?: string;
  page?: number;
  page_size?: number;
}
