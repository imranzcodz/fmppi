import api from './axiosInstance'
import type { VerifyResponse, KinshipResponse } from '../types'

export const verifyApi = {
  local: (file: File) => {
    const form = new FormData()
    form.append('image', file)
    return api.post<VerifyResponse>('/verify/local', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },

  global: (file: File) => {
    const form = new FormData()
    form.append('image', file)
    return api.post<VerifyResponse>('/verify/global', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },

  kinship: (photo1: File, photo2: File) => {
    const form = new FormData()
    form.append('photo1', photo1)
    form.append('photo2', photo2)
    return api.post<KinshipResponse>('/verify/kinship', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },
}
