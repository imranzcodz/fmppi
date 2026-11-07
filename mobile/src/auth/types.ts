// Auth domain types (JWT + MFA)

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  tokens: TokenPayload | null;
  user: User | null;
  error: string | null;
}

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: "admin" | "investigator" | "reporter";
}

export interface LoginForm {
  email: string;
  password: string;
}

export interface MfaForm {
  userId: string;
  code: string;
}

export interface BiometricConsent {
  prompted: boolean;
  granted: boolean;
  notAsked: boolean;
}
