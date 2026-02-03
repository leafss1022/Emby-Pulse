import { ref } from 'vue'
import type { AxiosResponse } from 'axios'

/**
 * 通用 API 调用 Composable
 * @param apiFunc API 函数
 * @returns 包含 data、loading、error 和 execute 方法的对象
 */
export function useApi<T>(
  apiFunc: (...args: any[]) => Promise<AxiosResponse<T>>
) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  async function execute(...args: any[]): Promise<T | null> {
    loading.value = true
    error.value = null

    try {
      const response = await apiFunc(...args)
      data.value = response.data
      return response.data
    } catch (e) {
      error.value = e as Error
      console.error('API Error:', e)
      return null
    } finally {
      loading.value = false
    }
  }

  function reset() {
    data.value = null
    error.value = null
    loading.value = false
  }

  return {
    data,
    loading,
    error,
    execute,
    reset,
  }
}
