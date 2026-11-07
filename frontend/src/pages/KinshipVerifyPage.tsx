import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { verifyApi } from '../api/verifyApi'
import { Button } from '../components/ui/Button'

export const KinshipVerifyPage = (): React.ReactNode => {
  const { user } = useAuth()
  const [photo1, setPhoto1] = useState<File | null>(null)
  const [photo2, setPhoto2] = useState<File | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<{ score: number; isKin: boolean; confidence: number } | null>(null)
  const canRun = user?.role === 'admin' || user?.role === 'investigator'

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    if (!photo1 || !photo2) return
    setError('')
    setRunning(true)
    setResult(null)
    try {
      const res = await verifyApi.kinship(photo1, photo2)
      setResult(res)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Kinship verification failed')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Kinship Verify</h1>
        <p className="text-gray-600">Compare two photos to determine kin probability via the FMPPI Siamese verifier.</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Photo 1</label>
            <input type="file" accept="image/*" onChange={(e) => setPhoto1(e.target.files?.[0] ?? null)} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Photo 2</label>
            <input type="file" accept="image/*" onChange={(e) => setPhoto2(e.target.files?.[0] ?? null)} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
          </div>
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <Button type="submit" variant="primary" loading={running} disabled={!photo1 || !photo2 || !canRun} className="w-full">
          Verify kinship
        </Button>
        {!canRun && <p className="text-xs text-gray-500 mt-2">You do not have permission to run kinship verification.</p>}
      </form>

      {result && (
        <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm text-center">
          <h3 className="text-sm font-semibold text-gray-500 uppercase mb-3">Result</h3>
          <div className="text-4xl font-bold mb-2">{result.isKin ? 'KIN' : 'NON-KIN'}</div>
          <p className="text-sm text-gray-600">Score: {Math.round(result.score * 100)}% &nbsp;|&nbsp; Confidence: {Math.round(result.confidence * 100)}%</p>
        </div>
      )}
    </div>
  )
}
