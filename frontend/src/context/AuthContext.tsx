import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import * as authApi from '../api/auth'
import { getMe } from '../api/photos'
import { getErrorMessage } from '../api/client'
import type { User } from '../types'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (
    username: string,
    email: string,
    password: string,
  ) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      return
    }
    try {
      const me = await getMe()
      setUser(me)
    } catch {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }, [])

  useEffect(() => {
    refreshUser().finally(() => setIsLoading(false))
  }, [refreshUser])

  const login = useCallback(
    async (email: string, password: string) => {
      const token = await authApi.login(email, password)
      localStorage.setItem('access_token', token.access_token)
      await refreshUser()
    },
    [refreshUser],
  )

  const register = useCallback(
    async (username: string, email: string, password: string) => {
      await authApi.register(username, email, password)
      await login(email, password)
    },
    [login],
  )

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } catch {
      // Token may already be invalid
    } finally {
      localStorage.removeItem('access_token')
      setUser(null)
    }
  }, [])

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export { getErrorMessage }
