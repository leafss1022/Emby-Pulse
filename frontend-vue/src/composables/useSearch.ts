import { ref, computed, type Ref, type ComputedRef } from 'vue'

type SearchableValue = string | number | boolean | null | undefined

interface UseSearchOptions<T> {
  /** 搜索字段，支持嵌套路径如 'user.name' */
  searchFields: (keyof T | string)[]
  /** 是否区分大小写，默认 false */
  caseSensitive?: boolean
  /** 最小搜索字符数，默认 0 */
  minLength?: number
}

/**
 * 搜索过滤 Composable
 * 统一处理列表搜索过滤逻辑
 */
export function useSearch<T extends Record<string, unknown>>(
  items: Ref<T[]>,
  options: UseSearchOptions<T>
) {
  const searchInput = ref('')
  const searchQuery = ref('')

  const {
    searchFields,
    caseSensitive = false,
    minLength = 0
  } = options

  /** 是否正在搜索（有有效搜索词） */
  const isSearching = computed(() => {
    const query = searchQuery.value.trim()
    return query.length >= minLength && query.length > 0
  })

  /**
   * 获取嵌套对象的值
   */
  function getNestedValue(obj: Record<string, unknown>, path: string): SearchableValue {
    const keys = path.split('.')
    let value: unknown = obj
    for (const key of keys) {
      if (value == null || typeof value !== 'object') return undefined
      value = (value as Record<string, unknown>)[key]
    }
    return value as SearchableValue
  }

  /**
   * 检查单个项是否匹配搜索词
   */
  function matchItem(item: T, query: string): boolean {
    const normalizedQuery = caseSensitive ? query : query.toLowerCase()

    return searchFields.some(field => {
      const value = getNestedValue(item as Record<string, unknown>, String(field))
      if (value == null) return false

      const strValue = String(value)
      const normalizedValue = caseSensitive ? strValue : strValue.toLowerCase()

      return normalizedValue.includes(normalizedQuery)
    })
  }

  /** 过滤后的列表 */
  const filteredItems: ComputedRef<T[]> = computed(() => {
    if (!isSearching.value) return items.value

    const query = searchQuery.value.trim()
    return items.value.filter(item => matchItem(item, query))
  })

  /** 搜索结果数量 */
  const resultCount = computed(() => filteredItems.value.length)

  /** 执行搜索（将输入框的值设为搜索词） */
  function handleSearch() {
    searchQuery.value = searchInput.value
  }

  /** 清除搜索 */
  function clearSearch() {
    searchInput.value = ''
    searchQuery.value = ''
  }

  /** 直接设置搜索词（实时搜索场景） */
  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  return {
    /** 搜索输入框绑定值 */
    searchInput,
    /** 当前生效的搜索词 */
    searchQuery,
    /** 是否正在搜索 */
    isSearching,
    /** 过滤后的列表 */
    filteredItems,
    /** 搜索结果数量 */
    resultCount,
    /** 执行搜索 */
    handleSearch,
    /** 清除搜索 */
    clearSearch,
    /** 直接设置搜索词 */
    setSearchQuery,
  }
}

/**
 * 简单搜索 Composable (实时过滤，无需点击搜索按钮)
 * 适用于输入即搜索的场景
 */
export function useSimpleSearch<T extends Record<string, unknown>>(
  items: Ref<T[]>,
  searchFields: (keyof T | string)[],
  caseSensitive = false
) {
  const searchQuery = ref('')

  const isSearching = computed(() => searchQuery.value.trim().length > 0)

  const filteredItems: ComputedRef<T[]> = computed(() => {
    const query = searchQuery.value.trim()
    if (!query) return items.value

    const normalizedQuery = caseSensitive ? query : query.toLowerCase()

    return items.value.filter(item => {
      return searchFields.some(field => {
        const value = (item as Record<string, unknown>)[String(field)]
        if (value == null) return false

        const strValue = String(value)
        const normalizedValue = caseSensitive ? strValue : strValue.toLowerCase()

        return normalizedValue.includes(normalizedQuery)
      })
    })
  })

  function clearSearch() {
    searchQuery.value = ''
  }

  return {
    searchQuery,
    isSearching,
    filteredItems,
    clearSearch,
  }
}
