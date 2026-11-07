import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export const MfaPage = (): React.ReactNode => {
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { mfaVerify } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await mfaVerify({ email, code })
      navigate('/dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'MFA verification failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <h2 className="mb-6 text-2xl font-bold text-gray-900 text-center">Multi-Factor Authentication</h2>
        <p className="mb-6 text-sm text-gray-600 text-center">Enter the 6-digit code from your authenticator app</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Verification code" type="text" maxLength={6} value={code} onChange={(e) => setCode(e.target.value)} required />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" variant="primary" loading={loading} className="w-full">
            Verify
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600">
          <a href="/login" className="text-indigo-600 hover:text-indigo-500 font-medium">Back to sign in</a>
        </p>
      </div>
    </div>
  )
}
