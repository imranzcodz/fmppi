import api from './axiosInstance'
import type { Case, Person, Evidence, Match, Pagination } from '../types'

export const casesApi = {
  list: (params?: Pagination) =>
    api.get<Case[]>('/cases', { params }).then((r) => r.data),

  get: (id: string) => api.get<Case>(`/cases/${id}`).then((r) => r.data),

  create: (data: { title: string }) =>
    api.post<Case>('/cases', data).then((r) => r.data),

  update: (id: string, data: Partial<Case>) =>
    api.put<Case>(`/cases/${id}`, data).then((r) => r.data),

  remove: (id: string) => api.delete<void>(`/cases/${id}`).then((r) => r.data),

  uploadEvidence: (caseId: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<Evidence>(`/cases/${caseId}/evidence`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data)
  },

  getMatches: (caseId: string) =>
    api.get<Match[]>(`/cases/${caseId}/matches`).then((r) => r.data),

  runMatch: (caseId: string) =>
    api.post<{ matches: Match[] }>(`/cases/${caseId}/match/run`).then((r) => r.data),

  getPersons: (caseId: string) => api.get<Person[]>(`/cases/${caseId}/persons`).then((r) => r.data),
}
