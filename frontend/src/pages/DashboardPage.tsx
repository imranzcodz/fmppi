import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { casesApi } from '../api/casesApi'
import type { Case } from '../types'
import { StatusBadge } from '../components/layout/AppLayout'
import { Table } from '../components/ui/Table'

export const DashboardPage = (): React.ReactNode => {
  const { user, hasAnyRole } = useAuth()
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    casesApi.list().then(setCases).finally(() => setLoading(false))
  }, [])

  const isReporter = user?.role === 'reporter'
  const visibleCases = isReporter ? cases.filter((c) => c.createdBy === user?.id) : cases

  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'status', label: 'Status' },
    { key: 'createdBy', label: 'Created by' },
    { key: 'createdAt', label: 'Created at' },
  ]

  if (loading) return <div className="text-gray-500">Loading cases...</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Case management</p>
        </div>
        {hasAnyRole('admin', 'investigator') && (
          <Link to="/cases/new" className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
            New Case
          </Link>
        )}
      </div>

      <Table
        columns={columns}
        data={visibleCases}
        renderCell={(row, key) => {
          if (key === 'status') return <StatusBadge status={row.status} />
          if (key === 'title') return <Link to={`/cases/${row.id}`} className="text-indigo-600 hover:underline font-medium">{row.title}</Link>
          return row[key]
        }}
        rowKey="id"
      />

      {visibleCases.length === 0 && (
        <p className="text-sm text-gray-500 text-center">
          {isReporter ? 'You have no cases yet. Submit a case to get started.' : 'No cases available.'}
        </p>
      )}
    </div>
  )
}
