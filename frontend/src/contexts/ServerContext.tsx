import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api } from '@/services/api'

export interface Server {
  id: string
  name: string
  emby_url: string
  playback_db?: string
  users_db?: string
  auth_db?: string
  emby_api_key?: string
  is_default: boolean
}

interface ServerContextType {
  servers: Server[]
  currentServer: Server | null
  isLoading: boolean
  setCurrentServer: (server: Server | null) => void
  refreshServers: () => Promise<void>
}

const ServerContext = createContext<ServerContextType | null>(null)

export function ServerProvider({ children }: { children: ReactNode }) {
  const [servers, setServers] = useState<Server[]>([])
  const [currentServer, setCurrentServerState] = useState<Server | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshServers = async () => {
    try {
      const data = await api.getServers()
      const loadedServers = data.servers
      setServers(loadedServers)
      
      // 如果没有当前服务器，设置默认服务器
      if (loadedServers.length > 0) {
        const serverIdFromCookie = document.cookie
          .split('; ')
          .find(row => row.startsWith('server_id='))
          ?.split('=')[1]

        if (serverIdFromCookie) {
          const server = loadedServers.find(s => s.id === serverIdFromCookie)
          if (server && !currentServer) {
            setCurrentServerState(server)
            return
          }
        }

        if (!currentServer) {
          const defaultServer = loadedServers.find(s => s.is_default) || loadedServers[0]
          if (defaultServer) {
            setCurrentServerState(defaultServer)
            document.cookie = `server_id=${defaultServer.id}; path=/; max-age=${7 * 24 * 60 * 60}`
          }
        }
      }
    } catch (error) {
      console.error('Failed to load servers:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const setCurrentServer = (server: Server | null) => {
    setCurrentServerState(server)
    if (server) {
      // 保存到 cookie
      document.cookie = `server_id=${server.id}; path=/; max-age=${7 * 24 * 60 * 60}`
    } else {
      // 清除 cookie
      document.cookie = 'server_id=; path=/; max-age=0'
    }
  }

  useEffect(() => {
    refreshServers()
  }, [])

  return (
    <ServerContext.Provider value={{ servers, currentServer, isLoading, setCurrentServer, refreshServers }}>
      {children}
    </ServerContext.Provider>
  )
}

export function useServer() {
  const context = useContext(ServerContext)
  if (!context) {
    throw new Error('useServer must be used within ServerProvider')
  }
  return context
}

