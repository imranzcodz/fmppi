import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { storage } from './storage'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  headers: { 'Content-Type': 'application/json' },
})

let isRefreshing = false
let refreshPromise: Promise<string | null> | null = null

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = storage.getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (!isRefreshing) {
        isRefreshing = true
        refreshPromise = (async () => {
          try {
            const refresh = storage.getRefreshToken()
            if (!refresh) return null
            const base = api.defaults.baseURL ?? ''
            const { data } = await axios.post<{ accessToken: string; refreshToken?: string }>(
              `${base.replace(/\/$/, '')}/auth/refresh`,
              { refresh }
            )
            if (data.accessToken) storage.setAccessToken(data.accessToken)
            if (data.refreshToken) storage.setRefreshToken(data.refreshToken)
            return data.accessToken
          } catch {
            return null
          } finally {
            isRefreshing = false
          }
        })()
      }

      const token = await refreshPromise
      if (!token) {
        storage.clear()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      originalRequest._retry = true
      originalRequest.headers.Authorization = `Bearer ${token}`
      return api(originalRequest)
    }

    return Promise.reject(error)
  }
)

export default api
