import api from './axiosInstance'
import { storage } from './storage'
import type { LoginRequest, LoginResponse, MfaVerifyRequest, MfaVerifyResponse, RegisterRequest, RegisterResponse } from '../types'

export const authApi = {
  login: (data: LoginRequest): Promise<LoginResponse> =>
    api.post('/auth/login', data).then((r) => r.data),

  mfaVerify: (data: MfaVerifyRequest): Promise<MfaVerifyResponse> =>
    api.post('/auth/mfa/verify', data).then((r) => r.data),

  refresh: (refresh: string): Promise<{ accessToken: string; refreshToken?: string }> =>
    api.post('/auth/refresh', { refresh }).then((r) => r.data),

  register: (data: RegisterRequest): Promise<RegisterResponse> =>
    api.post('/auth/register', data).then((r) => r.data),
}

export const setAuthSession = (data: LoginResponse | MfaVerifyResponse): void => {
  storage.setAccessToken(data.accessToken)
  if (data.refreshToken) storage.setRefreshToken(data.refreshToken)
}
