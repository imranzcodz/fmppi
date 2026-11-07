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
  beforeEach(() => {
    mockPost.mockReset()
  })

  it('local posts FormData with image', async () => {
    mockPost.mockResolvedValue({ data: { matches: [] } })
    const file = new File(['fake'], 'face.jpg', { type: 'image/jpeg' })
    const res = await verifyApi.local(file)
    expect(mockPost).toHaveBeenCalled()
    const [url, , config] = mockPost.mock.calls[0]
    expect(url).toBe('/verify/local')
    expect(config?.headers?.['Content-Type']).toBe('multipart/form-data')
    expect(res.matches).toEqual([])
  })

  it('global posts FormData with image', async () => {
    mockPost.mockResolvedValue({ data: { matches: [{ candidateId: 'x', score: 0.95 }] } })
    const file = new File(['fake'], 'face.jpg', { type: 'image/jpeg' })
    const res = await verifyApi.global(file)
    expect(mockPost).toHaveBeenCalled()
    const [url] = mockPost.mock.calls[0]
    expect(url).toBe('/verify/global')
    expect(res.matches[0].score).toBe(0.95)
  })

  it('kinship posts FormData with two photos', async () => {
    mockPost.mockResolvedValue({ data: { score: 0.8, isKin: true, confidence: 0.9 } })
    const f1 = new File(['fake'], 'a.jpg', { type: 'image/jpeg' })
    const f2 = new File(['fake'], 'b.jpg', { type: 'image/jpeg' })
    const res = await verifyApi.kinship(f1, f2)
    expect(mockPost).toHaveBeenCalled()
    const [url, body] = mockPost.mock.calls[0]
    expect(url).toBe('/verify/kinship')
    expect(body.get('photo1')).toBe(f1)
    expect(body.get('photo2')).toBe(f2)
    expect(res.isKin).toBe(true)
    expect(res.confidence).toBe(0.9)
  })
})
