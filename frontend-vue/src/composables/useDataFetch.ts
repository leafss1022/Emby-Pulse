import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useServerStore, useFilterStore } from '@/stores'

/**
 * 通用数据获取 Composable
 * 自动处理 loading 状态、服务器和筛选器变化监听
 *
 * @param fetchFn 数据获取函数
 * @param options 配置选项
 * @returns loading 状态和刷新函数
 */
export function useDataFetch<T = any>(
  fetchFn: () => Promise<T>,
  options: {
    /**
     * 是否立即执行(mounted 时)
     * @default true
     */
    immediate?: boolean
    /**
     * 是否监听筛选器变化
     * @default true
     */
    watchFilter?: boolean
    /**
     * 自动刷新间隔(毫秒), 0 表示不自动刷新
     * @default 0
     */
    refreshInterval?: number
  } = {}
) {
  const {
    immediate = true,
    watchFilter = true,
    refreshInterval = 0,
  } = options

  const serverStore = useServerStore()
  const filterStore = useFilterStore()

  const loading = ref(false)
  const error = ref<Error | null>(null)

  let refreshTimer: ReturnType<typeof setInterval> | null = null

  /**
   * 执行数据获取
   */
  async function fetch() {
    if (!serverStore.currentServer) return

    loading.value = true
    error.value = null
    try {
      await fetchFn()
    } catch (err) {
      error.value = err as Error
      console.error('Data fetch error:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 启动自动刷新
   */
  function startRefresh() {
    if (refreshInterval > 0) {
      refreshTimer = setInterval(fetch, refreshInterval)
    }
  }

  /**
   * 停止自动刷新
   */
  function stopRefresh() {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  // 监听服务器和筛选器变化
  if (watchFilter) {
    watch(
      () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
      () => {
        fetch()
      },
      { deep: true }
    )
  } else {
    // 只监听服务器变化
    watch(
      () => serverStore.currentServer?.id,
      () => {
        fetch()
      }
    )
  }

  // 自动刷新
  if (refreshInterval > 0) {
    onMounted(() => {
      startRefresh()
    })

    // 组件卸载时清理定时器
    onUnmounted(() => {
      stopRefresh()
    })
  }

  // 首次加载
  if (immediate) {
    onMounted(() => {
      fetch()
    })
  }

  return {
    loading,
    error,
    refresh: fetch,
    startRefresh,
    stopRefresh,
  }
}
