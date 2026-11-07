import api from './axiosInstance'
import type { AuditLog } from '../types'

export const auditApi = {
  list: (params?: { caseId?: string; actor?: string; page?: number; limit?: number }) =>
    api.get<AuditLog[]>('/audit', { params }).then((r) => r.data),
}
