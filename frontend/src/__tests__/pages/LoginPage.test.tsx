import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, cleanup } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { LoginPage } from '../../pages/LoginPage'
import { useAuth } from '../../auth/AuthContext'
import type { AuthContextType } from '../../auth/AuthContext'
import { MfaRequiredError } from '../../auth/AuthContext'

const mockUseAuth = vi.mocked(useAuth)
const mockNavigate = vi.fn()

vi.mock('../../auth/AuthContext', () => ({
  useAuth: vi.fn(),
  MfaRequiredError: class MfaRequiredError extends Error {
    constructor() { super('MFA required'); this.name = 'MfaRequiredError'; }
  },
}))
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  MemoryRouter: (props: { children: React.ReactNode }) => <>{props.children}</>,
}))

describe('LoginPage', () => {
  beforeEach(() => {
    mockUseAuth.mockReset()
    mockNavigate.mockReset()
  })
  afterEach(() => {
    vi.restoreAllMocks()
    cleanup()
  })

  it('calls login with credentials and navigates to dashboard on success', async () => {
    const login = vi.fn().mockResolvedValue(undefined)
    mockUseAuth.mockReturnValue({ login } as unknown as AuthContextType)
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.c' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pw' } })
    fireEvent.click(screen.getAllByRole('button', { name: /sign in/i })[0])

    await vi.waitFor(() => expect(login).toHaveBeenCalledWith({ email: 'a@b.c', password: 'pw' }))
    expect(mockNavigate).toHaveBeenCalledWith('/dashboard')
  })

  it('navigates to /mfa when MFA is required', async () => {
    const login = vi.fn().mockRejectedValue(new MfaRequiredError())
    mockUseAuth.mockReturnValue({ login } as unknown as AuthContextType)
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.c' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pw' } })
    fireEvent.click(screen.getAllByRole('button', { name: /sign in/i })[0])

    await vi.waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/mfa'))
  })

  it('shows error when login fails', async () => {
    const login = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
    mockUseAuth.mockReturnValue({ login } as unknown as AuthContextType)
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    )

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'a@b.c' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pw' } })
    fireEvent.click(screen.getAllByRole('button', { name: /sign in/i })[0])

    await vi.waitFor(() => expect(screen.getByText('Invalid credentials')).toBeInTheDocument())
  })
})
