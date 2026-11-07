import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { AxiosInstance } from 'axios'

vi.mock('../../api/axiosInstance', () => {
  const post = vi.fn()
  const get = vi.fn()
  const put = vi.fn()
  const del = vi.fn()
  const api: AxiosInstance = {
    post, get, put, delete: del,
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  } as unknown as AxiosInstance
  return { default: api, api }
})

import { api as mockApi } from '../../api/axiosInstance'
import { casesApi } from '../../api/casesApi'

const mockPost = mockApi.post as unknown as ReturnType<typeof vi.fn>
const mockGet = mockApi.get as unknown as ReturnType<typeof vi.fn>
const mockPut = mockApi.put as unknown as ReturnType<typeof vi.fn>
const mockDelete = (mockApi as unknown as { delete: unknown }).delete as unknown as ReturnType<typeof vi.fn>

describe('casesApi', () => {
  beforeEach(() => {
    mockPost.mockReset()
    mockGet.mockReset()
    mockPut.mockReset()
    mockDelete.mockReset()
  })

  it('list fetches cases', async () => {
    mockGet.mockResolvedValue({ data: [{ id: '1', title: 'Case 1', status: 'open', createdBy: 'u1', createdAt: 't', updatedAt: 't' }] })
    const res = await casesApi.list({ page: 1, limit: 10 })
    expect(mockGet).toHaveBeenCalledWith('/cases', { params: { page: 1, limit: 10 } })
    expect(res[0].title).toBe('Case 1')
  })

  it('get fetches a case', async () => {
    mockGet.mockResolvedValue({ data: { id: '1', title: 'Case 1', status: 'open', createdBy: 'u1', createdAt: 't', updatedAt: 't' } })
    const res = await casesApi.get('1')
    expect(mockGet).toHaveBeenCalledWith('/cases/1')
    expect(res.id).toBe('1')
  })

  it('create posts a case', async () => {
    mockPost.mockResolvedValue({ data: { id: '1', title: 'New', status: 'open', createdBy: 'u1', createdAt: 't', updatedAt: 't' } })
    const res = await casesApi.create({ title: 'New' })
    expect(mockPost).toHaveBeenCalledWith('/cases', { title: 'New' })
    expect(res.id).toBe('1')
  })

  it('uploadEvidence posts multipart form', async () => {
    const file = new File(['x'], 'photo.jpg', { type: 'image/jpeg' })
    mockPost.mockResolvedValue({ data: { id: 'e1', caseId: '1', filePath: '/s/photo.jpg', type: 'photo' } })
    const res = await casesApi.uploadEvidence('1', file)
    expect(mockPost).toHaveBeenCalledWith('/cases/1/evidence', expect.any(FormData), { headers: { 'Content-Type': 'multipart/form-data' } })
    expect(res.type).toBe('photo')
  })

  it('runMatch posts match run', async () => {
    mockPost.mockResolvedValue({ data: { matches: [] } })
    await casesApi.runMatch('1')
    expect(mockPost).toHaveBeenCalledWith('/cases/1/match/run')
  })
})
