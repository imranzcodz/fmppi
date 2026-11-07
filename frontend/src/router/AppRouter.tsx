import { createBrowserRouter, type RouteObject, Outlet } from 'react-router-dom'
import { AuthProvider, useAuth } from '../auth/AuthContext'
import { ProtectedRoute } from '../components/auth/ProtectedRoute'
import { AppLayout } from '../components/layout/AppLayout'
import { LoginPage } from '../pages/LoginPage'
import { MfaPage } from '../pages/MfaPage'
import { RegisterPage } from '../pages/RegisterPage'
import { DashboardPage } from '../pages/DashboardPage'
import { CaseDetailPage } from '../pages/CaseDetailPage'
import { EvidenceUploadPage } from '../pages/EvidenceUploadPage'
import { LocalVerifyPage, GlobalVerifyPage } from '../pages/LocalVerifyPage'
import { KinshipVerifyPage } from '../pages/KinshipVerifyPage'
import { ReporterCaseSubmitPage } from '../pages/ReporterCaseSubmitPage'
import { ReporterCaseStatusPage } from '../pages/ReporterCaseStatusPage'
import { AuditLogPage } from '../pages/AuditLogPage'
import { UserManagementPage } from '../pages/UserManagementPage'
import { UnauthorizedPage, NotFoundPage } from '../pages/UnauthorizedPage'

const ROLES: Record<string, string[]> = {
  ADMIN: ['admin'],
  ADMIN_INV: ['admin', 'investigator'],
  ADMIN_INV_REP: ['admin', 'investigator', 'reporter'],
  ADMIN_REVIEWER: ['admin', 'reviewer'],
  ALL: ['admin', 'investigator', 'reviewer', 'reporter'],
  REPORTER: ['reporter'],
}

const layoutItems = [
  { href: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard', roles: ROLES.ALL },
  { href: '/cases', label: 'Cases', icon: 'FileText', roles: ROLES.ADMIN_INV },
  { href: '/verify/local', label: 'Local Verify', icon: 'Search', roles: ROLES.ADMIN_INV },
  { href: '/verify/global', label: 'Global Verify', icon: 'Search', roles: ROLES.ADMIN_INV },
  { href: '/verify/kinship', label: 'Kinship Verify', icon: 'Users', roles: ROLES.ADMIN_INV },
  { href: '/audit', label: 'Audit Log', icon: 'Activity', roles: ROLES.ADMIN_REVIEWER },
  { href: '/users', label: 'User Management', icon: 'Users', roles: ROLES.ADMIN },
]

const AppRouter = () => {
  const { user } = useAuth()
  const items = layoutItems.filter((i) => !i.roles || i.roles.includes(String(user?.role ?? 'reporter')))

  const routes: RouteObject = {
    path: '/',
    element: (
      <AuthProvider>
        <AppLayout items={items} user={user ?? null} onLogout={() => {}}>
          <Outlet />
        </AppLayout>
      </AuthProvider>
    ),
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'mfa', element: <MfaPage /> },
      { path: 'register', element: <RegisterPage /> },
      { path: 'unauthorized', element: <UnauthorizedPage /> },
      {
        path: 'dashboard',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ALL}>
            <DashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'cases',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_INV}>
            <DashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'cases/:id',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_INV_REP}>
            <CaseDetailPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'cases/:id/evidence',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_INV_REP}>
            <EvidenceUploadPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'verify/local',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_INV}>
            <LocalVerifyPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'verify/global',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_INV}>
            <GlobalVerifyPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'verify/kinship',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_INV}>
            <KinshipVerifyPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'reporter/cases/submit',
        element: (
          <ProtectedRoute allowedRoles={ROLES.REPORTER}>
            <ReporterCaseSubmitPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'reporter/cases/:id/status',
        element: (
          <ProtectedRoute allowedRoles={ROLES.REPORTER}>
            <ReporterCaseStatusPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'audit',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN_REVIEWER}>
            <AuditLogPage />
          </ProtectedRoute>
        ),
      },
      {
        path: 'users',
        element: (
          <ProtectedRoute allowedRoles={ROLES.ADMIN}>
            <UserManagementPage />
          </ProtectedRoute>
        ),
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  }

  return createBrowserRouter([routes])
}

export default AppRouter
