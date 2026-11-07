import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { casesApi } from '../api/casesApi'
import type { Case } from '../types'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/layout/AppLayout'

export const ReporterCaseStatusPage = (): React.ReactNode => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const [caseData, setCaseData] = useState<Case | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    casesApi.get(id).then(
      (c) => {
        if (user?.role === 'reporter' && c.createdBy !== user.id) {
          setError('You can only view your own cases.')
          return
        }
        setCaseData(c)
      },
      () => setError('Failed to load case status')
    ).finally(() => setLoading(false))
  }, [id, user?.id, user?.role])

  if (loading) return <div className="text-gray-500">Loading case status...</div>
  if (error) return <div className="text-center text-red-600">{error}</div>
  if (!caseData) return <div className="text-gray-500">Case not found</div>

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Case Status</h1>
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <p className="text-sm text-gray-600"><strong>Case ID:</strong> {caseData.id}</p>
        <p className="text-sm text-gray-600"><strong>Title:</strong> {caseData.title}</p>
        <p className="text-sm text-gray-600"><strong>Status:</strong> <StatusBadge status={caseData.status} /></p>
        <p className="text-sm text-gray-600"><strong>Created:</strong> {caseData.createdAt}</p>
        <p className="text-sm text-gray-600"><strong>Updated:</strong> {caseData.updatedAt}</p>
        <p className="text-xs text-gray-400 mt-4">Read-only view for reporters.</p>
      </div>
      <Button variant="secondary" onClick={() => window.location.href = '/dashboard'} className="w-full">
        Back to dashboard
      </Button>
    </div>
  )
}
