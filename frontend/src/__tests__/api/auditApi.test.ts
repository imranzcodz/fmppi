import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { AxiosInstance } from 'axios'

vi.mock('../../api/axiosInstance', () => {
  const get = vi.fn()
  const api: AxiosInstance = {
    get,
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  } as unknown as AxiosInstance
  return { default: api, api }
})

import { api as mockApi } from '../../api/axiosInstance'
import { auditApi } from '../../api/auditApi'

const mockGet = mockApi.get as unknown as ReturnType<typeof vi.fn>

describe('auditApi', () => {
  beforeEach(() => {
    mockGet.mockReset()
  })

  it('list calls GET /audit with params', async () => {
    mockGet.mockResolvedValue({ data: [{ id: 'a1', actorId: 'u1', action: 'case.create', entity: 'case', entityId: 'c1', timestamp: 't' }] })
    const res = await auditApi.list({ caseId: 'c1', actor: 'u1', page: 1, limit: 10 })
    expect(mockGet).toHaveBeenCalledWith('/audit', { params: { caseId: 'c1', actor: 'u1', page: 1, limit: 10 } })
    expect(res[0].action).toBe('case.create')
  })

  it('list calls GET /audit without params', async () => {
    mockGet.mockResolvedValue({ data: [] })
    const res = await auditApi.list()
    expect(mockGet).toHaveBeenCalledWith('/audit', expect.objectContaining({ params: undefined }))
    expect(res).toEqual([])
  })
})
