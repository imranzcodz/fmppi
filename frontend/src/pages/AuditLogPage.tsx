import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { auditApi } from '../api/auditApi'
import type { AuditLog } from '../types'
import { Table } from '../components/ui/Table'

export const AuditLogPage = (): React.ReactNode => {
  const { user } = useAuth()
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    auditApi.list().then(setLogs).catch(() => setError('Failed to load audit log')).finally(() => setLoading(false))
  }, [])

  const isReviewerOrAdmin = user?.role === 'admin' || user?.role === 'reviewer'
  if (!isReviewerOrAdmin) return <div className="text-center text-red-600">Access denied: auditors only.</div>

  if (loading) return <div className="text-gray-500">Loading audit log...</div>

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
        <p className="text-gray-600">Immutable record of case, evidence, and match actions.</p>
      </div>
      <Table
        columns={[
          { key: 'timestamp', label: 'Timestamp' },
          { key: 'actorName', label: 'Actor' },
          { key: 'action', label: 'Action' },
          { key: 'entity', label: 'Entity' },
          { key: 'ip', label: 'IP' },
        ]}
        data={logs}
        rowKey="id"
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  )
}
