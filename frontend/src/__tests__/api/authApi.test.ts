import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { AxiosInstance } from 'axios'

vi.mock('../../api/axiosInstance', () => {
  const post = vi.fn()
  const api: AxiosInstance = {
    post,
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  } as unknown as AxiosInstance
  return { default: api, api }
})

import { api as mockApi } from '../../api/axiosInstance'
import { authApi } from '../../api/authApi'

const mockPost = mockApi.post as unknown as ReturnType<typeof vi.fn>

describe('authApi', () => {
  beforeEach(() => {
    mockPost.mockReset()
  })

  it('login posts credentials and returns tokens', async () => {
    mockPost.mockResolvedValue({ data: { accessToken: 'at', refreshToken: 'rt', user: { id: '1', email: 'a@b.c', role: 'reporter', createdAt: 't' }, mfaRequired: false } })
    const res = await authApi.login({ email: 'a@b.c', password: 'pw' })
    expect(mockPost).toHaveBeenCalledWith('/auth/login', { email: 'a@b.c', password: 'pw' })
    expect(res.accessToken).toBe('at')
    expect(res.mfaRequired).toBe(false)
  })

  it('mfaVerify posts email and code', async () => {
    mockPost.mockResolvedValue({ data: { accessToken: 'at', refreshToken: 'rt', user: { id: '1', email: 'a@b.c', role: 'reporter', createdAt: 't' } } })
    await authApi.mfaVerify({ email: 'a@b.c', code: '123456' })
    expect(mockPost).toHaveBeenCalledWith('/auth/mfa/verify', { email: 'a@b.c', code: '123456' })
  })

  it('refresh posts refresh token', async () => {
    mockPost.mockResolvedValue({ data: { accessToken: 'at2' } })
    await authApi.refresh('rt')
    expect(mockPost).toHaveBeenCalledWith('/auth/refresh', { refresh: 'rt' })
  })

  it('register posts new user', async () => {
    mockPost.mockResolvedValue({ data: { user: { id: '2', email: 'r@b.c', role: 'reporter', createdAt: 't' } } })
    await authApi.register({ email: 'r@b.c', password: 'pw', role: 'reporter' })
    expect(mockPost).toHaveBeenCalledWith('/auth/register', { email: 'r@b.c', password: 'pw', role: 'reporter' })
  })
})
