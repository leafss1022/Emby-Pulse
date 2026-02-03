import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { serversApi } from '@/services'
import type { Server, ServerConfig } from '@/types'

export const useServerStore = defineStore(
  'server',
  () => {
    // State
    const servers = ref<Server[]>([])
    const currentServerId = ref<string | null>(null)
    const loading = ref(false)

    // Getters
    const currentServer = computed(() =>
      servers.value.find((s) => s.id === currentServerId.value) || null
    )

    const defaultServer = computed(() =>
      servers.value.find((s) => s.is_default) || servers.value[0] || null
    )

    const serverCount = computed(() => servers.value.length)

    // Actions
    async function fetchServers() {
      loading.value = true
      try {
        const response = await serversApi.getServers()
        servers.value = response.data.servers || []

        // 如果没有当前服务器，设置默认服务器
        if (!currentServerId.value && defaultServer.value) {
          currentServerId.value = defaultServer.value.id
        }
      } catch (error) {
        console.error('Failed to fetch servers:', error)
        servers.value = []
      } finally {
        loading.value = false
      }
    }

    function setCurrentServer(serverId: string) {
      const server = servers.value.find((s) => s.id === serverId)
      if (server) {
        currentServerId.value = serverId
        // 设置 cookie（后端需要）
        document.cookie = `server_id=${serverId}; path=/; max-age=${7 * 24 * 60 * 60}`
      }
    }

    async function addServer(config: ServerConfig): Promise<Server | null> {
      try {
        const response = await serversApi.addServer(config)
        const newServer = response.data
        servers.value.push(newServer)

        // 如果是第一个服务器或设置为默认，自动选中
        if (servers.value.length === 1 || newServer.is_default) {
          setCurrentServer(newServer.id)
        }

        return newServer
      } catch (error) {
        console.error('Failed to add server:', error)
        return null
      }
    }

    async function updateServer(
      id: string,
      config: ServerConfig
    ): Promise<Server | null> {
      try {
        const response = await serversApi.updateServer(id, config)
        const updatedServer = response.data
        const index = servers.value.findIndex((s) => s.id === id)

        if (index !== -1) {
          servers.value[index] = updatedServer
        }

        // 如果更新的是当前服务器，刷新当前服务器
        if (currentServerId.value === id) {
          currentServerId.value = updatedServer.id
        }

        return updatedServer
      } catch (error) {
        console.error('Failed to update server:', error)
        return null
      }
    }

    async function deleteServer(id: string): Promise<boolean> {
      try {
        await serversApi.deleteServer(id)
        servers.value = servers.value.filter((s) => s.id !== id)

        // 如果删除的是当前服务器，切换到默认服务器
        if (currentServerId.value === id) {
          if (defaultServer.value) {
            setCurrentServer(defaultServer.value.id)
          } else {
            currentServerId.value = null
          }
        }

        return true
      } catch (error) {
        console.error('Failed to delete server:', error)
        return false
      }
    }

    return {
      // State
      servers,
      currentServerId,
      loading,
      // Getters
      currentServer,
      defaultServer,
      serverCount,
      // Actions
      fetchServers,
      setCurrentServer,
      addServer,
      updateServer,
      deleteServer,
    }
  },
  {
    persist: {
      storage: localStorage,
      paths: ['currentServerId'],
    } as any,
  }
)
