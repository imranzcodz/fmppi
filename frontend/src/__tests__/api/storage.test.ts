import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { storage } from '../../api/storage'

describe('storage', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })
  afterEach(() => {
    sessionStorage.clear()
  })

  it('get/set access token', () => {
    expect(storage.getAccessToken()).toBeNull()
    storage.setAccessToken('at123')
    expect(storage.getAccessToken()).toBe('at123')
  })

  it('get/set refresh token', () => {
    expect(storage.getRefreshToken()).toBeNull()
    storage.setRefreshToken('rt123')
    expect(storage.getRefreshToken()).toBe('rt123')
  })

  it('clear removes both tokens', () => {
    storage.setAccessToken('at')
    storage.setRefreshToken('rt')
    storage.clear()
    expect(storage.getAccessToken()).toBeNull()
    expect(storage.getRefreshToken()).toBeNull()
  })
})
