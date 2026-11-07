import { describe, it, expect } from 'vitest'
import { MfaRequiredError } from '../../auth/AuthContext'

describe('MfaRequiredError', () => {
  it('is an Error with name MfaRequiredError and message', () => {
    const err = new MfaRequiredError()
    expect(err).toBeInstanceOf(Error)
    expect(err.name).toBe('MfaRequiredError')
    expect(err.message).toBe('MFA required')
  })
})
