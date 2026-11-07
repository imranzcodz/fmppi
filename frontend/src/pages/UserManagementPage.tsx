import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { usersApi } from '../api/usersApi'
import type { User, Role } from '../types'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Table } from '../components/ui/Table'

export const UserManagementPage = (): React.ReactNode => {
  const { user } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<Role>('reporter')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    usersApi.list().then(setUsers).catch(() => setError('Failed to load users')).finally(() => setLoading(false))
  }, [])

  if (user?.role !== 'admin') return <div className="text-center text-red-600">Access denied: administrators only.</div>

  const handleCreate = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setError('')
    try {
      await usersApi.create({ email, password, role })
      setSuccess('User created')
      setEmail('')
      setPassword('')
      setRole('reporter')
      const updated = await usersApi.list()
      setUsers(updated)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create user')
    }
  }

  const handleDelete = async (id: string): Promise<void> => {
    if (!window.confirm('Delete this user?')) return
    await usersApi.remove(id)
    setUsers(users.filter((u) => u.id !== id))
  }

  if (loading) return <div className="text-gray-500">Loading users...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <p className="text-gray-600">Admin-only: create and remove users.</p>
      </div>

      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm space-y-4">
        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <div className="flex items-end">
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {['admin', 'investigator', 'reviewer', 'reporter'].map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          <Button type="submit" variant="primary" className="w-full">Create user</Button>
        </form>
        {error && <p className="text-sm text-red-600">{error}</p>}
        {success && <p className="text-sm text-green-600">{success}</p>}
      </div>

      <Table
        columns={[
          { key: 'email', label: 'Email' },
          { key: 'role', label: 'Role' },
          { key: 'mfaEnabled', label: 'MFA' },
          { key: 'createdAt', label: 'Created' },
          { key: 'actions', label: 'Actions' },
        ]}
        data={users}
        renderCell={(row, key) => {
          if (key === 'mfaEnabled') return row.mfaEnabled ? 'Enabled' : 'Disabled'
          if (key === 'role') return row.role
          if (key === 'actions') {
            return (
              <Button variant="danger" onClick={() => handleDelete(String(row.id))}>Delete</Button>
            )
          }
          return row[key]
        }}
        rowKey="id"
      />
    </div>
  )
}
