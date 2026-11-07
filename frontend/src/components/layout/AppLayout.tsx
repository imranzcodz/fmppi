import type { User } from '../../types'
import { Shield, LogOut } from 'lucide-react'
import { Badge } from '../ui/Badge'

const iconMap: Record<string, React.ComponentType<React.SVGProps<SVGSVGElement>>> = {
  Shield, LogOut,
}

export interface NavItem {
  href: string
  label: string
  icon: string
  roles?: readonly string[]
}

export const Sidebar = ({ items, onItemSelect, onLogout }: { items: NavItem[]; onItemSelect: (href: string) => void; onLogout: () => void }): React.ReactNode => (
  <aside className="w-64 bg-gray-900 text-white">
    <div className="p-6">
      <div className="flex items-center gap-2">
        <Shield className="h-6 w-6 text-indigo-400" />
        <span className="font-semibold text-lg tracking-tight">FMPPI</span>
      </div>
      <nav className="mt-8 space-y-1">
        {items.map((item) => {
          const Icon = iconMap[item.icon] || Shield
          return (
            <a
              key={item.href}
              href={item.href}
              onClick={() => onItemSelect(item.href)}
              className={[
                'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                'text-gray-300 hover:bg-gray-800 hover:text-white',
              ].join(' ')}
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </a>
          )
        })}
      </nav>
    </div>
    <div className="p-6 border-t border-gray-800">
      <button onClick={() => onLogout()} className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors">
        <LogOut className="h-5 w-5" />
        Logout
      </button>
    </div>
  </aside>
)

export const TopBar = ({ user, onLogout }: { user: User | null; onLogout: () => void }): React.ReactNode => (
  <header className="sticky top-0 z-20 bg-white border-b border-gray-200">
    <div className="flex items-center justify-between px-4 py-3">
      <div className="flex items-center gap-3">
        <Shield className="h-5 w-5 text-indigo-600" />
        <span className="font-semibold text-gray-900">FMPPI</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-gray-600 truncate max-w-xs">
          {user?.email} <span className="ml-2 text-[10px] uppercase tracking-wider bg-gray-100 text-gray-500 px-2 py-0.5 rounded">{user?.role}</span>
        </span>
        <button onClick={onLogout} className="text-sm text-red-600 hover:text-red-800 font-medium">
          Logout
        </button>
      </div>
    </div>
  </header>
)

export const AppLayout = ({ children, items, user, onLogout }: { children: React.ReactNode; items: NavItem[]; user: User | null; onLogout: () => void }): React.ReactNode => (
  <div className="flex h-screen bg-gray-50 overflow-hidden">
    <Sidebar items={items} onItemSelect={() => {}} onLogout={onLogout} />
    <div className="flex-1 flex flex-col overflow-hidden">
      <TopBar user={user} onLogout={onLogout} />
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  </div>
)

export const StatusBadge = ({ status }: { status: string }): React.ReactNode => {
  return <Badge variant={status}>{status}</Badge>
}
