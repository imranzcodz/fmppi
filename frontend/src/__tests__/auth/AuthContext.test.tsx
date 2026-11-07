import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, cleanup } from '@testing-library/react'
import { AuthProvider, useAuth } from '../../auth/AuthContext'
import { storage } from '../../api/storage'

vi.mock('../../api/authApi', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../api/authApi')>()
  return {
    ...actual,
    authApi: { ...actual.authApi, login: vi.fn() },
  }
})

import { authApi } from '../../api/authApi'
const mockLogin = vi.mocked(authApi.login)

const Harness = () => {
  const { user, isAuthenticated, loading, login, logout } = useAuth()
  if (loading) return <span data-testid="loading">loading</span>
  return (
    <div>
      <span data-testid="state">{isAuthenticated ? 'auth' : 'anon'}</span>
      {!isAuthenticated && (
        <button data-testid="login" onClick={() => login({ email: 'a@b.c', password: 'pw' })}>Login</button>
      )}
      {isAuthenticated && (
        <>
          <span data-testid="email">{user?.email}</span>
          <span data-testid={user.role}>{user.role}</span>
          <button data-testid="logout" onClick={logout}>Logout</button>
        </>
      )}
    </div>
  )
}

describe('AuthProvider', () => {
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
  })
  afterEach(() => {
    vi.restoreAllMocks()
    cleanup()
  })

  it('starts unauthenticated with no tokens', () => {
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    )
    expect(screen.getByTestId('state').textContent).toBe('anon')
    expect(storage.getAccessToken()).toBeNull()
  })

  it('logs in, stores tokens in session storage, and logs out', async () => {
    render(
      <AuthProvider>
        <Harness />
      </AuthProvider>
    )
    fireEvent.click(screen.getByTestId('login'))
    await vi.waitFor(() => expect(screen.getByTestId('state').textContent).toBe('auth'))
    expect(screen.getByTestId('email').textContent).toBe('a@b.c')
    expect(screen.getByTestId('reporter').textContent).toBe('reporter')
    expect(storage.getAccessToken()).toBe('at')
    expect(storage.getRefreshToken()).toBe('rt')

    fireEvent.click(screen.getByTestId('logout'))
    await vi.waitFor(() => expect(screen.getByTestId('state').textContent).toBe('anon'))
    expect(storage.getAccessToken()).toBeNull()
    expect(storage.getRefreshToken()).toBeNull()
  })
})
