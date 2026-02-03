import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api, setAuthErrorHandler } from '@/services/api'

interface AuthContextType {
  isAuthenticated: boolean
  isLoading: boolean
  username: string | null
  login: (username: string, password: string) => Promise<{ success: boolean; message?: string }>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [username, setUsername] = useState<string | null>(null)

  // 检查登录状态
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const data = await api.checkAuth()
        setIsAuthenticated(data.authenticated)
        setUsername(data.username || null)
      } catch {
        setIsAuthenticated(false)
        setUsername(null)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()

    // 设置认证错误处理器
    setAuthErrorHandler(() => {
      setIsAuthenticated(false)
      setUsername(null)
    })
  }, [])

  const login = async (username: string, password: string) => {
    const result = await api.login(username, password)
    if (result.success) {
      setIsAuthenticated(true)
      setUsername(result.username || username)
    }
    return result
  }

  const logout = async () => {
    await api.logout()
    setIsAuthenticated(false)
    setUsername(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, isLoading, username, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
