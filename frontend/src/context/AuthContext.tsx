import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'

interface User {
  id: string
  email: string
  name: string
  role: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  register: (email: string, password: string, name: string) => Promise<boolean>
  logout: () => void
  refreshToken: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_URL = '/api/auth'
const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Load auth state from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const storedUser = localStorage.getItem(USER_KEY)

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  // Persist auth state to localStorage
  const persistAuth = useCallback((token: string, user: User) => {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    setToken(token)
    setUser(user)
  }, [])

  const clearAuth = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }, [])

  const login = useCallback(async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_URL}/login/json`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        toast.error(error.detail || 'Login failed')
        return false
      }

      const data = await response.json()
      persistAuth(data.access_token, data.user)
      toast.success(`Welcome back, ${data.user.name}!`)
      return true
    } catch (error) {
      toast.error('Login failed. Please try again.')
      return false
    }
  }, [persistAuth])

  const register = useCallback(async (
    email: string,
    password: string,
    name: string
  ): Promise<boolean> => {
    try {
      const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name }),
      })

      if (!response.ok) {
        const error = await response.json()
        toast.error(error.detail || 'Registration failed')
        return false
      }

      toast.success('Account created! Please log in.')
      return true
    } catch (error) {
      toast.error('Registration failed. Please try again.')
      return false
    }
  }, [])

  const logout = useCallback(() => {
    clearAuth()
    toast.success('Logged out successfully')
  }, [clearAuth])

  const refreshToken = useCallback(async () => {
    if (!token) return

    try {
      const response = await fetch(`${API_URL}/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      })

      if (!response.ok) {
        clearAuth()
        return
      }

      const data = await response.json()
      persistAuth(data.access_token, data.user)
    } catch {
      clearAuth()
    }
  }, [token, persistAuth, clearAuth])

  // Auto-refresh token periodically
  useEffect(() => {
    if (!token) return

    // Refresh every 23 hours (token expires in 24h)
    const interval = setInterval(() => {
      refreshToken()
    }, 23 * 60 * 60 * 1000)

    return () => clearInterval(interval)
  }, [token, refreshToken])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Helper to add auth header to API calls
export function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}
