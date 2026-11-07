import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { casesApi } from '../api/casesApi'
import { Button } from '../components/ui/Button'

export const EvidenceUploadPage = (): React.ReactNode => {
  const { id } = useParams<{ id: string }>()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const canUpload = user?.role === 'admin' || user?.role === 'investigator' || (user?.role === 'reporter')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setFile(e.target.files?.[0] ?? null)
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    if (!file || !id) return
    setError('')
    setUploading(true)
    try {
      await casesApi.uploadEvidence(id, file)
      setSuccess(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  if (!id) return <div className="text-gray-500">Invalid case</div>

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Upload Evidence</h1>
      <p className="text-gray-600">Case {id}</p>

      {!success ? (
        <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Evidence file (photo / CCTV)</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" variant="primary" loading={uploading} disabled={!file || !canUpload} className="w-full">
            Upload evidence
          </Button>
          {!canUpload && <p className="text-xs text-gray-500 mt-2">You do not have permission to upload evidence to this case.</p>}
        </form>
      ) : (
        <div className="bg-white p-6 rounded-lg border border-green-200 shadow-sm text-center">
          <p className="text-green-700 font-medium mb-3">Evidence uploaded successfully.</p>
          <Button variant="secondary" onClick={() => navigate(`/cases/${id}`)} className="w-full">
            Back to case
          </Button>
        </div>
      )}
    </div>
  )
}
