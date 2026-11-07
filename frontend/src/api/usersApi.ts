import api from './axiosInstance'
import type { User, Role } from '../types'

export const usersApi = {
  list: () => api.get<User[]>('/users').then((r) => r.data),

  create: (data: { email: string; password: string; role: Role }) =>
    api.post<User>('/users', data).then((r) => r.data),

  update: (id: string, data: Partial<User>) =>
    api.put<User>(`/users/${id}`, data).then((r) => r.data),

  remove: (id: string) => api.delete<void>(`/users/${id}`).then((r) => r.data),
}
