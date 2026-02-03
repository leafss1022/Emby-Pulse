import axios from 'axios'
import router from '@/router'
import { useAuthStore } from '@/stores'

const axiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 401处理标记，避免重复跳转
let isRedirecting = false

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 401 错误，触发登出逻辑
    if (error.response?.status === 401 && !isRedirecting) {
      isRedirecting = true

      // 清除认证状态
      const authStore = useAuthStore()
      authStore.user = null

      // 清除sessionStorage（避免持久化的user数据导致循环）
      sessionStorage.removeItem('auth')

      // 跳转到登录页（使用router.push避免页面刷新）
      const currentPath = router.currentRoute.value.fullPath
      if (currentPath !== '/login') {
        router.push({
          name: 'Login',
          query: { redirect: currentPath }
        }).finally(() => {
          // 跳转完成后重置标记
          setTimeout(() => {
            isRedirecting = false
          }, 1000)
        })
      } else {
        isRedirecting = false
      }
    }

    // 其他错误处理
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default axiosInstance
