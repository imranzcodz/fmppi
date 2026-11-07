import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { casesApi } from '../api/casesApi'
import { Button } from '../components/ui/Button'

export const ReporterCaseSubmitPage = (): React.ReactNode => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setFiles(Array.from(e.target.files ?? []))
  }

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await casesApi.create({ title })
      const newCase = (await casesApi.list()).find((c) => c.title === title)
      for (const file of files) {
        if (newCase) await casesApi.uploadEvidence(newCase.id, file)
      }
      setSuccess(true)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Case submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <div className="max-w-lg bg-white p-6 rounded-lg border border-green-200 shadow-sm text-center">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Case submitted</h2>
        <p className="text-gray-600 mb-4">Your missing person report has been created and is pending investigator review.</p>
        <Button variant="primary" onClick={() => navigate('/dashboard')} className="w-full">
          Go to dashboard
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-lg space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Submit Missing Person Report</h1>
      <p className="text-gray-600">As a reporter ({user?.role}), you can create a case and upload evidence photos.</p>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Case title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Evidence photos</label>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit" variant="primary" loading={submitting} className="w-full">
          Submit case
        </Button>
      </form>
    </div>
  )
}
