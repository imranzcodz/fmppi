import { createContext, useContext, useState, type ReactNode } from 'react'
import { storage } from '../api/storage'
import { authApi, setAuthSession } from '../api/authApi'
import type { User, LoginRequest, RegisterRequest } from '../types'

export interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (data: LoginRequest) => Promise<void>
  mfaVerify: (data: { email: string; code: string }) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  hasRole: (role: string) => boolean
  hasAnyRole: (...roles: string[]) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = (): AuthContextType => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}

export const AuthProvider = ({ children }: { children: ReactNode }): ReactNode => {
  const [user, setUser] = useState<User | null>(() => {
    const token = storage.getAccessToken()
    if (!token) return null
    try {
      return JSON.parse(sessionStorage.getItem('fmppi_user') ?? 'null')
    } catch {
      return null
    }
  })

  const login = async (data: LoginRequest): Promise<void> => {
    const res = await authApi.login(data)
    setAuthSession(res)
    sessionStorage.setItem('fmppi_user', JSON.stringify(res.user))
    setUser(res.user)
    if (res.mfaRequired) {
      throw new MfaRequiredError()
    }
  }

  const mfaVerify = async (data: { email: string; code: string }): Promise<void> => {
    const res = await authApi.mfaVerify(data)
    setAuthSession(res)
    sessionStorage.setItem('fmppi_user', JSON.stringify(res.user))
    setUser(res.user)
  }

  const register = async (data: RegisterRequest): Promise<void> => {
    const res = await authApi.register(data)
    sessionStorage.setItem('fmppi_user', JSON.stringify(res.user))
  }

  const logout = (): void => {
    storage.clear()
    sessionStorage.removeItem('fmppi_user')
    setUser(null)
    window.location.href = '/login'
  }

  const hasRole = (role: string): boolean => user?.role === role || user?.role === 'admin'

  const hasAnyRole = (...roles: string[]): boolean => roles.some((r) => hasRole(r))

  const ctx: AuthContextType = {
    user,
    loading: false,
    isAuthenticated: !!user,
    login,
    mfaVerify,
    register,
    logout,
    hasRole,
    hasAnyRole,
  }

  return <AuthContext.Provider value={ctx}>{children}</AuthContext.Provider>
}

class MfaRequiredError extends Error {
  constructor() {
    super('MFA required')
    this.name = 'MfaRequiredError'
  }
}

export { MfaRequiredError }
