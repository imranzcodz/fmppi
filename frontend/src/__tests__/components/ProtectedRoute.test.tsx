import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ProtectedRoute } from '../../components/auth/ProtectedRoute'
import { useAuth } from '../../auth/AuthContext'
import type { Role } from '../../types'

const mockUseAuth = vi.mocked(useAuth)
const mockNavigate = vi.fn()

vi.mock('../../auth/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  MemoryRouter: (props: { children: React.ReactNode }) => <>{props.children}</>,
}))

const authValue = (authenticated: boolean, role: Role) => ({
  user: authenticated ? { id: '1', email: 'a@b.c', role, createdAt: 't' } : null,
  loading: false,
  isAuthenticated: authenticated,
  hasRole: vi.fn((r: string) => r === role),
  hasAnyRole: vi.fn((...roles: string[]) => roles.includes(role)),
  login: vi.fn(), mfaVerify: vi.fn(), register: vi.fn(), logout: vi.fn(),
})

describe('ProtectedRoute', () => {
  beforeEach(() => {
    mockUseAuth.mockReset()
    mockNavigate.mockReset()
  })
  afterEach(() => {
    vi.restoreAllMocks()
    cleanup()
  })

  it('renders children when authenticated with an allowed role', () => {
    mockUseAuth.mockReturnValue(authValue(true, 'admin'))
    mockNavigate.mockImplementation(() => {})
    render(
      <MemoryRouter>
        <ProtectedRoute allowedRoles={['admin', 'investigator']}><span data-testid="inner">inner</span></ProtectedRoute>
      </MemoryRouter>
    )
    expect(screen.getByTestId('inner')).toBeInTheDocument()
    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('navigates to /login when not authenticated', () => {
    mockUseAuth.mockReturnValue(authValue(false, 'reporter'))
    render(
      <MemoryRouter>
        <ProtectedRoute allowedRoles={['admin']}><span data-testid="inner">inner</span></ProtectedRoute>
      </MemoryRouter>
    )
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  it('navigates to /unauthorized when role not allowed', () => {
    mockUseAuth.mockReturnValue(authValue(true, 'reporter'))
    render(
      <MemoryRouter>
        <ProtectedRoute allowedRoles={['admin']}><span data-testid="inner">inner</span></ProtectedRoute>
      </MemoryRouter>
    )
    expect(mockNavigate).toHaveBeenCalledWith('/unauthorized')
  })
})
