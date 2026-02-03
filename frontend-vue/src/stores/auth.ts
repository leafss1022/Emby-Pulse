import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/services'
import type { User } from '@/types'

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const user = ref<User | null>(null)
    const isLoading = ref(false)

    // Getters
    const isAuthenticated = computed(() => !!user.value)
    const username = computed(() => user.value?.username || null)
    const userId = computed(() => user.value?.user_id || null)
    const isAdmin = computed(() => user.value?.is_admin || false)

    // Actions
    async function login(
      serverId: string,
      username: string,
      password: string
    ): Promise<boolean> {
      isLoading.value = true
      try {
        const response = await authApi.login(serverId, username, password)
        if (response.data.authenticated && response.data.user) {
          user.value = response.data.user
          return true
        }
        return false
      } catch (error) {
        console.error('Login failed:', error)
        return false
      } finally {
        isLoading.value = false
      }
    }

    async function logout() {
      try {
        await authApi.logout()
      } catch (error) {
        console.error('Logout failed:', error)
      } finally {
        user.value = null
      }
    }

    async function checkAuth() {
      isLoading.value = true
      try {
        const response = await authApi.checkAuth()
        if (response.data.authenticated && response.data.user) {
          user.value = response.data.user
        } else {
          user.value = null
        }
      } catch (error) {
        console.error('Check auth failed:', error)
        user.value = null
      } finally {
        isLoading.value = false
      }
    }

    return {
      // State
      user,
      isLoading,
      // Getters
      isAuthenticated,
      username,
      userId,
      isAdmin,
      // Actions
      login,
      logout,
      checkAuth,
    }
  },
  {
    persist: {
      storage: localStorage,
      paths: ['user'],
    } as any,
  }
)
