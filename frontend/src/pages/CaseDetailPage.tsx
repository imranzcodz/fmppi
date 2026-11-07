import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { casesApi } from '../api/casesApi'
import type { Case, Match } from '../types'
import { Button } from '../components/ui/Button'
import { StatusBadge } from '../components/layout/AppLayout'
import { Table } from '../components/ui/Table'

export const CaseDetailPage = (): React.ReactNode => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState<Case | null>(null)
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    Promise.all([casesApi.get(id), casesApi.getMatches(id)]).then(
      ([c, m]) => {
        if (cancelled) return
        setCaseData(c)
        setMatches(m)
        setLoading(false)
      },
      () => {
        if (cancelled) return
        setLoading(false)
      }
    )
    return () => { cancelled = true }
  }, [id])

  const canUpload = user?.role === 'admin' || user?.role === 'investigator' || (user?.role === 'reporter' && caseData?.createdBy === user.id)

  if (loading) return <div className="text-gray-500">Loading case...</div>
  if (!caseData) return <div className="text-gray-500">Case not found</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{caseData.title}</h1>
          <p className="text-gray-600">Case {caseData.id}</p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={caseData.status} />
          {canUpload && (
            <Button variant="secondary" onClick={() => navigate(`/cases/${id}/evidence`)} className="w-full">
              Upload Evidence
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">Case info</h3>
          <p className="text-sm text-gray-600"><strong>Status:</strong> {caseData.status}</p>
          <p className="text-sm text-gray-600"><strong>Created by:</strong> {caseData.createdBy}</p>
          <p className="text-sm text-gray-600"><strong>Created at:</strong> {caseData.createdAt}</p>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">Actions</h3>
          <div className="space-y-2">
            <Button variant="secondary" onClick={() => navigate(-1)} className="w-full">
              Back to cases
            </Button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <h3 className="px-6 py-3 text-sm font-semibold text-gray-500 uppercase border-b border-gray-100">Matches ({matches.length})</h3>
        <Table
          columns={[
            { key: 'candidatePersonId', label: 'Candidate' },
            { key: 'score', label: 'Score' },
            { key: 'modelVersion', label: 'Model' },
            { key: 'status', label: 'Status' },
          ]}
          data={matches}
          renderCell={(row, key) => {
            if (key === 'score') return `${Math.round(Number(row.score) * 100)}%`
            if (key === 'status') return <StatusBadge status={row.status} />
            return row[key]
          }}
          rowKey="id"
        />
      </div>
    </div>
  )
}
