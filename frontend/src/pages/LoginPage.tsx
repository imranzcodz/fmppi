import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { MfaRequiredError } from '../auth/AuthContext'

export const LoginPage = (): React.ReactNode => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login({ email, password })
      navigate('/dashboard')
    } catch (err: unknown) {
      if (err instanceof MfaRequiredError) {
        navigate('/mfa')
        return
      }
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <h2 className="mb-6 text-2xl font-bold text-gray-900 text-center">Sign in to FMPPI</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="text-sm text-red-600">{error}</p>}
          <Button type="submit" variant="primary" loading={loading} className="w-full">
            Sign in
          </Button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-600">
          New reporter? <a href="/register" className="text-indigo-600 hover:text-indigo-500 font-medium">Register here</a>
        </p>
      </div>
    </div>
  )
}
