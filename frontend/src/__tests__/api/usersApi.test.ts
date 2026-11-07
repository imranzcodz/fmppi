import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { AxiosInstance } from 'axios'

vi.mock('../../api/axiosInstance', () => {
  const get = vi.fn()
  const post = vi.fn()
  const put = vi.fn()
  const del = vi.fn()
  const api: AxiosInstance = {
    get,
    post,
    put,
    delete: del,
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  } as unknown as AxiosInstance
  return { default: api, api }
})

import { api as mockApi } from '../../api/axiosInstance'
import { usersApi } from '../../api/usersApi'

const mockGet = mockApi.get as unknown as ReturnType<typeof vi.fn>
const mockPost = mockApi.post as unknown as ReturnType<typeof vi.fn>
const mockPut = mockApi.put as unknown as ReturnType<typeof vi.fn>
const mockDelete = mockApi.delete as unknown as ReturnType<typeof vi.fn>

describe('usersApi', () => {
  beforeEach(() => {
    mockGet.mockReset()
    mockPost.mockReset()
    mockPut.mockReset()
    mockDelete.mockReset()
  })

  it('list calls GET /users', async () => {
    mockGet.mockResolvedValue({ data: [{ id: '1', email: 'a@b.c', role: 'admin', createdAt: 't' }] })
    const res = await usersApi.list()
    expect(mockGet).toHaveBeenCalledWith('/users')
    expect(res[0].role).toBe('admin')
  })

  it('create calls POST /users', async () => {
    mockPost.mockResolvedValue({ data: { id: '2', email: 'r@b.c', role: 'reporter', createdAt: 't' } })
    const res = await usersApi.create({ email: 'r@b.c', password: 'pw', role: 'reporter' })
    expect(mockPost).toHaveBeenCalledWith('/users', { email: 'r@b.c', password: 'pw', role: 'reporter' })
    expect(res.role).toBe('reporter')
  })

  it('update calls PUT /users/:id', async () => {
    mockPut.mockResolvedValue({ data: { id: '1', email: 'a@b.c', role: 'investigator', createdAt: 't' } })
    const res = await usersApi.update('1', { role: 'investigator' })
    expect(mockPut).toHaveBeenCalledWith('/users/1', { role: 'investigator' })
    expect(res.role).toBe('investigator')
  })

  it('remove calls DELETE /users/:id', async () => {
    mockDelete.mockResolvedValue({ data: undefined })
    await usersApi.remove('1')
    expect(mockDelete).toHaveBeenCalledWith('/users/1')
  })
})
