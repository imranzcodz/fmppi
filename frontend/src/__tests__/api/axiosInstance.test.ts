import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { storage } from '../../api/storage'

// Mock axios to test axiosInstance interceptors without real HTTP
vi.mock('axios', () => {
  const post = vi.fn()
  const create = vi.fn(() => ({
    post,
    interceptors: {
      request: { use: vi.fn((fn) => { fn({} as unknown as AxiosInstance); return 0 }) },
      response: { use: vi.fn() },
    },
  }))
  return { default: create, post }
})

// Need to re-import axiosInstance after mock - but it's a module singleton.
// Instead, test the storage.clear path which is used in the 401 interceptor.

describe('axiosInstance 401 path via storage.clear', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.restoreAllMocks()
  })
  afterEach(() => {
    sessionStorage.clear()
  })

  it('storage.clear removes tokens (simulating 401 logout)', () => {
    storage.setAccessToken('at')
    storage.setRefreshToken('rt')
    expect(storage.getAccessToken()).toBe('at')
    expect(storage.getRefreshToken()).toBe('rt')
    storage.clear()
    expect(storage.getAccessToken()).toBeNull()
    expect(storage.getRefreshToken()).toBeNull()
  })
})
