import { useAuth } from '../../auth/AuthContext'
import { useNavigate } from 'react-router-dom'
import { Badge } from '../ui/Badge'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

export const ProtectedRoute = ({ children, allowedRoles }: ProtectedRouteProps): React.ReactNode => {
  const { loading, isAuthenticated, hasRole } = useAuth()
  const navigate = useNavigate()

  if (loading) return null

  if (!isAuthenticated) {
    navigate('/login')
    return null
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const allowed = allowedRoles.some((r) => hasRole(r))
    if (!allowed) {
      navigate('/unauthorized')
      return null
    }
  }

  return children
}

export const RoleBadge = ({ role }: { role: string }): React.ReactNode => {
  return <Badge variant={role}>{role}</Badge>
}
