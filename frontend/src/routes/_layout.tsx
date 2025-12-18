import { Outlet, NavLink, Navigate } from 'react-router'
import {
  LayoutDashboard,
  Brain,
  Box,
  BarChart3,
  Database,
  MapPin,
  History,
  Settings,
  Activity,
  Command,
  LogOut,
  Loader2
} from 'lucide-react'
import { useTraining } from '../context/TrainingContext'
import { useAuth } from '../context/AuthContext'
import { ThemeToggle } from '../components/ThemeToggle'
import { Button } from '../components/ui/button'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Training', href: '/training', icon: Brain },
  { name: 'Models', href: '/models', icon: Box },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'History', href: '/history', icon: History },
  { name: 'Events', href: '/events', icon: Database },
  { name: 'Map', href: '/locations', icon: MapPin },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function AppLayout() {
  const { status } = useTraining()
  const { isAuthenticated, isLoading, user, logout } = useAuth()

  // Show loading while checking auth state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border">
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            <span className="text-lg font-semibold">VioNER</span>
          </div>
          <ThemeToggle />
        </div>

        {/* Command Palette Trigger */}
        <div className="px-4 py-2">
          <Button
            variant="outline"
            className="w-full justify-start text-sm text-muted-foreground"
            onClick={() => {
              const event = new KeyboardEvent('keydown', {
                key: 'k',
                metaKey: true,
                bubbles: true,
              })
              document.dispatchEvent(event)
            }}
          >
            <Command className="mr-2 h-4 w-4" />
            Search...
            <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
              <span className="text-xs">⌘</span>K
            </kbd>
          </Button>
        </div>

        <nav className="flex flex-col gap-1 p-4">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.name}
              {item.name === 'Training' && status.isRunning && (
                <span className="ml-auto h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              )}
            </NavLink>
          ))}
        </nav>

        {/* Training Status */}
        {status.isRunning && (
          <div className="absolute bottom-20 left-4 right-4 rounded-lg bg-primary/10 p-3">
            <div className="flex items-center gap-2 text-sm">
              <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <span className="font-medium">Training Active</span>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Epoch {status.currentEpoch}/{status.totalEpochs}
            </div>
            <div className="mt-1 h-1.5 rounded-full bg-primary/20">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${(status.currentEpoch / status.totalEpochs) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* User Info & Logout */}
        <div className="absolute bottom-0 left-0 right-0 border-t border-border p-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={logout} title="Logout">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="pl-64">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
