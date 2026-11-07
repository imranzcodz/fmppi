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
import { verifyApi } from '../../api/verifyApi'

const mockPost = mockApi.post as unknown as ReturnType<typeof vi.fn>

describe('verifyApi', () => {
  beforeEach(() => mockPost.mockReset())

  it('local posts image as multipart', async () => {
    const file = new File(['x'], 'probe.jpg', { type: 'image/jpeg' })
    mockPost.mockResolvedValue({ data: { matches: [{ candidateId: 'p1', score: 0.92 }] } })
    const res = await verifyApi.local(file)
    expect(mockPost).toHaveBeenCalledWith('/verify/local', expect.any(FormData), { headers: { 'Content-Type': 'multipart/form-data' } })
    expect(res.matches[0].score).toBe(0.92)
  })

  it('global posts image as multipart', async () => {
    const file = new File(['x'], 'probe.jpg', { type: 'image/jpeg' })
    mockPost.mockResolvedValue({ data: { matches: [{ candidateId: 'w1', score: 0.8, sourceUrl: 'http://example.com/img.jpg' }] } })
    const res = await verifyApi.global(file)
    expect(mockPost).toHaveBeenCalledWith('/verify/global', expect.any(FormData), { headers: { 'Content-Type': 'multipart/form-data' } })
    expect(res.matches[0].sourceUrl).toBe('http://example.com/img.jpg')
  })

  it('kinship posts two photos', async () => {
    const a = new File(['a'], 'a.jpg', { type: 'image/jpeg' })
    const b = new File(['b'], 'b.jpg', { type: 'image/jpeg' })
    mockPost.mockResolvedValue({ data: { score: 0.87, isKin: true, confidence: 0.9 } })
    const res = await verifyApi.kinship(a, b)
    const form = mockPost.mock.calls[0][1] as FormData
    expect(form.get('photo1')).toBe(a)
    expect(form.get('photo2')).toBe(b)
    expect(res.isKin).toBe(true)
  })
})
