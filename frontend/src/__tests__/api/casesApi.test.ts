import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { AxiosInstance } from 'axios'

vi.mock('../../api/axiosInstance', () => {
  const post = vi.fn()
  const get = vi.fn()
  const put = vi.fn()
  const del = vi.fn()
  const api: AxiosInstance = {
    post,
    get,
    put,
    delete: del,
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  } as unknown as AxiosInstance
  return { default: api, api }
})

import { api as mockApi } from '../../api/axiosInstance'
import { casesApi } from '../../api/casesApi'

const mockPost = mockApi.post as unknown as ReturnType<typeof vi.fn>
const mockGet = mockApi.get as unknown as ReturnType<typeof vi.fn>
const mockPut = mockApi.put as unknown as ReturnType<typeof vi.fn>
const mockDelete = mockApi.delete as unknown as ReturnType<typeof vi.fn>

describe('casesApi', () => {
  beforeEach(() => {
    mockPost.mockReset()
    mockGet.mockReset()
    mockPut.mockReset()
    mockDelete.mockReset()
  })

  it('list calls GET /cases', async () => {
    mockGet.mockResolvedValue({ data: [{ id: '1', title: 'Case', status: 'open', createdBy: 'u', createdAt: 't', updatedAt: 't' }] })
    const res = await casesApi.list({ page: 1, limit: 10 })
    expect(mockGet).toHaveBeenCalledWith('/cases', { params: { page: 1, limit: 10 } })
    expect(res[0].id).toBe('1')
  })

  it('get calls GET /cases/:id', async () => {
    mockGet.mockResolvedValue({ data: { id: '1', title: 'Case', status: 'open', createdBy: 'u', createdAt: 't', updatedAt: 't' } })
    const res = await casesApi.get('1')
    expect(mockGet).toHaveBeenCalledWith('/cases/1')
    expect(res.id).toBe('1')
  })

  it('create calls POST /cases', async () => {
    mockPost.mockResolvedValue({ data: { id: '2', title: 'New', status: 'open', createdBy: 'u', createdAt: 't', updatedAt: 't' } })
    const res = await casesApi.create({ title: 'New' })
    expect(mockPost).toHaveBeenCalledWith('/cases', { title: 'New' })
    expect(res.id).toBe('2')
  })

  it('update calls PUT /cases/:id', async () => {
    mockPut.mockResolvedValue({ data: { id: '1', title: 'Updated', status: 'open', createdBy: 'u', createdAt: 't', updatedAt: 't' } })
    const res = await casesApi.update('1', { title: 'Updated' })
    expect(mockPut).toHaveBeenCalledWith('/cases/1', { title: 'Updated' })
    expect(res.title).toBe('Updated')
  })

  it('remove calls DELETE /cases/:id', async () => {
    mockDelete.mockResolvedValue({ data: undefined })
    await casesApi.remove('1')
    expect(mockDelete).toHaveBeenCalledWith('/cases/1')
  })

  it('uploadEvidence posts FormData', async () => {
    mockPost.mockResolvedValue({ data: { id: 'e1', caseId: '1', filePath: '/uploads/1_img.jpg', type: 'photo', uploadedBy: 'u' } })
    const file = new File(['fake'], 'img.jpg', { type: 'image/jpeg' })
    const res = await casesApi.uploadEvidence('1', file)
    expect(mockPost).toHaveBeenCalled()
    const callArgs = mockPost.mock.calls[0]
    expect(callArgs[0]).toBe('/cases/1/evidence')
    expect(callArgs[2]?.headers?.['Content-Type']).toBe('multipart/form-data')
    expect(res.id).toBe('e1')
  })

  it('getMatches calls GET /cases/:id/matches', async () => {
    mockGet.mockResolvedValue({ data: [{ id: 'm1', caseId: '1', sourceEvidenceId: 'e1', candidatePersonId: 'p1', score: 0.9, modelVersion: 'v1', status: 'pending' }] })
    const res = await casesApi.getMatches('1')
    expect(mockGet).toHaveBeenCalledWith('/cases/1/matches')
    expect(res[0].score).toBe(0.9)
  })

  it('runMatch calls POST /cases/:id/match/run', async () => {
    mockPost.mockResolvedValue({ data: { matches: [] } })
    await casesApi.runMatch('1')
    expect(mockPost).toHaveBeenCalledWith('/cases/1/match/run')
  })

  it('getPersons calls GET /cases/:id/persons', async () => {
    mockGet.mockResolvedValue({ data: [{ id: 'p1', caseId: '1', name: 'John', age: 30, descriptors: null, photoRefs: [] }] })
    const res = await casesApi.getPersons('1')
    expect(mockGet).toHaveBeenCalledWith('/cases/1/persons')
    expect(res[0].name).toBe('John')
  })
})
