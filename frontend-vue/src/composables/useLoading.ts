import { ref } from 'vue'

/**
 * Loading 状态管理 Composable
 * @param initialState 初始状态
 * @returns Loading 相关方法和状态
 */
export function useLoading(initialState: boolean = false) {
  const loading = ref(initialState)

  function start() {
    loading.value = true
  }

  function stop() {
    loading.value = false
  }

  function toggle() {
    loading.value = !loading.value
  }

  /**
   * 包装异步函数，自动管理 loading 状态
   * @param fn 异步函数
   * @returns Promise
   */
  async function withLoading<T>(fn: () => Promise<T>): Promise<T> {
    start()
    try {
      return await fn()
    } finally {
      stop()
    }
  }

  return {
    loading,
    start,
    stop,
    toggle,
    withLoading,
  }
}
