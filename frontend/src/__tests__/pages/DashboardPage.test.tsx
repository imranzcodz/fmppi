import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, cleanup } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { DashboardPage } from '../../pages/DashboardPage'
import { useAuth } from '../../auth/AuthContext'
import type { AuthContextType } from '../../auth/AuthContext'
import type { Role } from '../../types'

const mockUseAuth = vi.mocked(useAuth)

vi.mock('../../auth/AuthContext', () => ({ useAuth: vi.fn() }))
vi.mock('../../api/casesApi', () => ({ casesApi: { list: vi.fn() } }))

import { casesApi } from '../../api/casesApi'
const mockList = vi.mocked(casesApi.list)

const authValue = (role: string): AuthContextType => ({
  user: { id: 'u1', email: 'a@b.c', role: role as unknown as Role, createdAt: 't' },
  loading: false,
  isAuthenticated: true,
  hasRole: vi.fn(() => true),
  hasAnyRole: vi.fn(() => true),
  login: vi.fn(), mfaVerify: vi.fn(), register: vi.fn(), logout: vi.fn(),
})

describe('DashboardPage', () => {
  beforeEach(() => {
    mockUseAuth.mockReset()
    mockList.mockReset()
  })
  afterEach(() => {
    vi.restoreAllMocks()
    cleanup()
  })

  it('renders cases list for investigator', async () => {
    mockUseAuth.mockReturnValue(authValue('investigator'))
    mockList.mockResolvedValue([
      { id: 'c1', title: 'Missing person', status: 'open', createdBy: 'u1', createdAt: 't1', updatedAt: 't1' },
    ])
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    await vi.waitFor(() => expect(screen.getByText('Missing person')).toBeInTheDocument())
    expect(mockList).toHaveBeenCalledTimes(1)
  })

  it('filters cases to owned ones for reporter', async () => {
    mockUseAuth.mockReturnValue(authValue('reporter'))
    mockList.mockResolvedValue([
      { id: 'c1', title: 'Own case', status: 'open', createdBy: 'u1', createdAt: 't1', updatedAt: 't1' },
      { id: 'c2', title: "Other's case", status: 'open', createdBy: 'u2', createdAt: 't2', updatedAt: 't2' },
    ])
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    )
    await vi.waitFor(() => expect(screen.getByText('Own case')).toBeInTheDocument())
    expect(screen.queryByText("Other's case")).not.toBeInTheDocument()
  })
})
