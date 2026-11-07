import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { verifyApi } from '../api/verifyApi'
import { Button } from '../components/ui/Button'
import { Table } from '../components/ui/Table'

type VerifyKind = 'local' | 'global'

interface VerifyPageProps {
  kind: VerifyKind
  title: string
  subtitle: string
  fileLabel: string
}

export const VerifyPage = ({ kind, title, subtitle, fileLabel }: VerifyPageProps): React.ReactNode => {
  const { user } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<{ matches: { candidateId: string; candidateName?: string; score: number; caseId?: string; sourceUrl?: string }[] } | null>(null)

  const canRun = user?.role === 'admin' || user?.role === 'investigator'

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setFile(e.target.files?.[0] ?? null)
    setError('')
    setResult(null)
  }

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    if (!file) return
    setError('')
    setRunning(true)
    setResult(null)
    try {
      const res = kind === 'local' ? await verifyApi.local(file) : await verifyApi.global(file)
      setResult(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Verification failed')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
        <p className="text-gray-600">{subtitle}</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{fileLabel}</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit" variant="primary" loading={running} disabled={!file || !canRun} className="w-full">
          Run {kind} verify
        </Button>
        {!canRun && <p className="text-xs text-gray-500 mt-2">You do not have permission to run {kind} verification.</p>}
      </form>

      {result && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <h3 className="px-6 py-3 text-sm font-semibold text-gray-500 uppercase border-b border-gray-100">Results ({result.matches.length})</h3>
          <Table
            columns={[
              { key: 'candidateName', label: 'Candidate' },
              { key: 'score', label: 'Similarity' },
              { key: 'caseId', label: 'Case' },
              { key: 'sourceUrl', label: 'Source' },
            ]}
            data={result.matches}
            renderCell={(row, key) => {
              if (key === 'score') return `${Math.round(row.score * 100)}%`
              if (key === 'sourceUrl') return row.sourceUrl ? <a href={row.sourceUrl} target="_blank" rel="noopener noreferrer" className="text-indigo-600 text-sm underline">View</a> : '-'
              return row[key]
            }}
            rowKey="candidateId"
          />
        </div>
      )}
    </div>
  )
}

export const LocalVerifyPage = (): React.ReactNode => (
  <VerifyPage
    kind="local"
    title="Local Verify"
    subtitle="1:N face search against local evidence database"
    fileLabel="Upload probe photo"
  />
)

export const GlobalVerifyPage = (): React.ReactNode => (
  <VerifyPage
    kind="global"
    title="Global Verify"
    subtitle="Web reverse-image search for similar faces"
    fileLabel="Upload probe photo"
  />
)
