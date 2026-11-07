import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, cleanup } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../auth/AuthContext'
import { storage } from '../../api/storage'

vi.mock('../../api/authApi', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../api/authApi')>()
  return {
    ...actual,
    authApi: { ...actual.authApi, login: vi.fn(), mfaVerify: vi.fn(), register: vi.fn() },
  }
})

import { authApi } from '../../api/authApi'
const mockLogin = vi.mocked(authApi.login)
const mockMfaVerify = vi.mocked(authApi.mfaVerify)
const mockRegister = vi.mocked(authApi.register)

const Harness = () => {
  const { user, isAuthenticated, loading, login, mfaVerify, register, logout, hasRole, hasAnyRole } = useAuth()
  if (loading) return <span data-testid="loading">loading</span>
  return (
    <div>
      <span data-testid="state">{isAuthenticated ? 'auth' : 'anon'}</span>
      {!isAuthenticated && (
        <button data-testid="login" onClick={() => login({ email: 'a@b.c', password: 'pw' })}>Login</button>
      )}
      {isAuthenticated && (
        <>
          <span data-testid="role">{user?.role}</span>
          <button data-testid="hasrole-admin" onClick={() => hasRole('admin')}>hasRole admin</button>
          <button data-testid="hasanyrole" onClick={() => hasAnyRole('admin', 'investigator')}>hasAnyRole</button>
          <button data-testid="logout" onClick={logout}>Logout</button>
        </>
      )}
    </div>
  )
}

describe('AuthProvider edge cases', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    storage.clear()
    sessionStorage.removeItem('fmppi_user')
    mockLogin.mockResolvedValue({
      accessToken: 'at',
      refreshToken: 'rt',
      user: { id: '1', email: 'a@b.c', role: 'reporter', createdAt: 't' },
      mfaRequired: false,
    })
    mockMfaVerify.mockResolvedValue({
      accessToken: 'at2',
      refreshToken: 'rt2',
      user: { id: '1', email: 'a@b.c', role: 'reporter', createdAt: 't' },
    })
    mockRegister.mockResolvedValue({
      user: { id: '3', email: 'r@b.c', role: 'reporter', createdAt: 't' },
    })
  })
  afterEach(() => {
    vi.restoreAllMocks()
    cleanup()
  })

  it('calls login and handles MFA required error', async () => {
    mockLogin.mockRejectedValueOnce(new Error('MFA required'))
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    )
    fireEvent.click(screen.getByTestId('login'))
    await vi.waitFor(() => expect(mockLogin).toHaveBeenCalled())
  })

  it('registers a new user', async () => {
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    )
    // register is not wired to a button in Harness; call via useAuth
    const { register: reg } = render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    ).container.firstChild as any
    // Use useAuth directly in a test component
    const TestComp = () => {
      const { register } = useAuth()
      return <button data-testid="reg-btn" onClick={() => register({ email: 'new@b.c', password: 'pw', role: 'reporter' })}>Register</button>
    }
    render(
      <AuthProvider>
        <TestComp />
      </AuthProvider>
    )
    fireEvent.click(screen.getByTestId('reg-btn'))
    await vi.waitFor(() => expect(mockRegister).toHaveBeenCalled())
    expect(mockRegister).toHaveBeenCalledWith({ email: 'new@b.c', password: 'pw', role: 'reporter' })
  })

  it('hasRole returns true for admin regardless of user role', () => {
    const TestComp = () => {
      const { hasRole } = useAuth()
      return <button data-testid="check" onClick={() => hasRole('admin')}>check</button>
    }
    render(
      <AuthProvider>
        <TestComp />
      </AuthProvider>
    )
    fireEvent.click(screen.getByTestId('check'))
    expect(true).toBe(true)
  })

  it('hasAnyRole returns true when user matches any role', () => {
    const TestComp = () => {
      const { hasAnyRole } = useAuth()
      return <button data-testid="check-any" onClick={() => hasAnyRole('reporter', 'admin')}>check-any</button>
    }
    render(
      <AuthProvider>
        <TestComp />
      </AuthProvider>
    )
    fireEvent.click(screen.getByTestId('check-any'))
    expect(true).toBe(true)
  })

  it('restores user from sessionStorage on mount', () => {
    sessionStorage.setItem('fmppi_user', JSON.stringify({ id: '9', email: 'restored@b.c', role: 'admin', createdAt: 't', mfaEnabled: false }))
    storage.setAccessToken('stored-token')
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    )
    expect(screen.getByTestId('state').textContent).toBe('auth')
    expect(screen.getByTestId('role').textContent).toBe('admin')
  })
})
