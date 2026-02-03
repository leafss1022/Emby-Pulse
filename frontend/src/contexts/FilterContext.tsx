import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { api } from '@/services/api'
import { useAuth } from '@/contexts/AuthContext'

export interface NameMappingItem {
  original: string
  display: string
}

export interface FilterOptions {
  users: { id: string; name: string }[]
  clients: NameMappingItem[]
  devices: NameMappingItem[]
  item_types: string[]
  playback_methods: string[]
  date_range: {
    min: string | null
    max: string | null
  }
}

export interface FilterState {
  // 日期筛选
  days: number
  startDate: string | null
  endDate: string | null
  useDateRange: boolean
  // 多选筛选
  selectedUsers: string[]
  selectedClients: string[]
  selectedDevices: string[]
  selectedItemTypes: string[]
  selectedPlaybackMethods: string[]
}

interface FilterContextType {
  // 状态
  filters: FilterState
  options: FilterOptions | null
  optionsLoading: boolean
  // 是否有筛选条件
  hasActiveFilters: boolean
  activeFilterCount: number
  // 操作
  setDays: (days: number) => void
  setDateRange: (start: string | null, end: string | null) => void
  setUseDateRange: (use: boolean) => void
  setSelectedUsers: (users: string[]) => void
  setSelectedClients: (clients: string[]) => void
  setSelectedDevices: (devices: string[]) => void
  setSelectedItemTypes: (types: string[]) => void
  setSelectedPlaybackMethods: (methods: string[]) => void
  clearFilters: () => void
  refreshOptions: () => Promise<void>
  // 构建查询参数
  buildQueryParams: () => Record<string, string>
}

const defaultFilters: FilterState = {
  days: 7,
  startDate: null,
  endDate: null,
  useDateRange: false,
  selectedUsers: [],
  selectedClients: [],
  selectedDevices: [],
  selectedItemTypes: [],
  selectedPlaybackMethods: [],
}

const FilterContext = createContext<FilterContextType | undefined>(undefined)

export function FilterProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth()

  const [filters, setFilters] = useState<FilterState>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('emby-stats-filters')
      if (saved) {
        try {
          return { ...defaultFilters, ...JSON.parse(saved) }
        } catch {
          return defaultFilters
        }
      }
    }
    return defaultFilters
  })

  const [options, setOptions] = useState<FilterOptions | null>(null)
  const [optionsLoading, setOptionsLoading] = useState(true)

  // 持久化筛选状态
  useEffect(() => {
    localStorage.setItem('emby-stats-filters', JSON.stringify(filters))
  }, [filters])

  // 加载筛选选项
  const refreshOptions = useCallback(async () => {
    if (!isAuthenticated) {
      setOptionsLoading(false)
      return
    }
    setOptionsLoading(true)
    try {
      const data = await api.getFilterOptions()
      setOptions(data)
    } catch (error) {
      console.error('Failed to load filter options:', error)
    } finally {
      setOptionsLoading(false)
    }
  }, [isAuthenticated])

  // 当登录状态变化时加载筛选选项
  useEffect(() => {
    if (isAuthenticated) {
      refreshOptions()
    } else {
      setOptions(null)
    }
  }, [isAuthenticated, refreshOptions])

  // 计算活动筛选数量
  const activeFilterCount =
    (filters.useDateRange && (filters.startDate || filters.endDate) ? 1 : 0) +
    filters.selectedUsers.length +
    filters.selectedClients.length +
    filters.selectedDevices.length +
    filters.selectedItemTypes.length +
    filters.selectedPlaybackMethods.length

  const hasActiveFilters = activeFilterCount > 0

  // 操作方法
  const setDays = useCallback((days: number) => {
    setFilters(prev => ({ ...prev, days, useDateRange: false }))
  }, [])

  const setDateRange = useCallback((start: string | null, end: string | null) => {
    setFilters(prev => ({ ...prev, startDate: start, endDate: end, useDateRange: true }))
  }, [])

  const setUseDateRange = useCallback((use: boolean) => {
    setFilters(prev => ({ ...prev, useDateRange: use }))
  }, [])

  const setSelectedUsers = useCallback((users: string[]) => {
    setFilters(prev => ({ ...prev, selectedUsers: users }))
  }, [])

  const setSelectedClients = useCallback((clients: string[]) => {
    setFilters(prev => ({ ...prev, selectedClients: clients }))
  }, [])

  const setSelectedDevices = useCallback((devices: string[]) => {
    setFilters(prev => ({ ...prev, selectedDevices: devices }))
  }, [])

  const setSelectedItemTypes = useCallback((types: string[]) => {
    setFilters(prev => ({ ...prev, selectedItemTypes: types }))
  }, [])

  const setSelectedPlaybackMethods = useCallback((methods: string[]) => {
    setFilters(prev => ({ ...prev, selectedPlaybackMethods: methods }))
  }, [])

  const clearFilters = useCallback(() => {
    setFilters(prev => ({
      ...defaultFilters,
      days: prev.days, // 保留天数设置
    }))
  }, [])

  // 构建 API 查询参数
  const buildQueryParams = useCallback(() => {
    const params: Record<string, string> = {}

    if (filters.useDateRange) {
      if (filters.startDate) params.start_date = filters.startDate
      if (filters.endDate) params.end_date = filters.endDate
    } else {
      params.days = String(filters.days)
    }

    if (filters.selectedUsers.length > 0) {
      params.users = filters.selectedUsers.join(',')
    }
    if (filters.selectedClients.length > 0) {
      params.clients = filters.selectedClients.join(',')
    }
    if (filters.selectedDevices.length > 0) {
      params.devices = filters.selectedDevices.join(',')
    }
    if (filters.selectedItemTypes.length > 0) {
      params.item_types = filters.selectedItemTypes.join(',')
    }
    if (filters.selectedPlaybackMethods.length > 0) {
      params.playback_methods = filters.selectedPlaybackMethods.join(',')
    }

    return params
  }, [filters])

  return (
    <FilterContext.Provider
      value={{
        filters,
        options,
        optionsLoading,
        hasActiveFilters,
        activeFilterCount,
        setDays,
        setDateRange,
        setUseDateRange,
        setSelectedUsers,
        setSelectedClients,
        setSelectedDevices,
        setSelectedItemTypes,
        setSelectedPlaybackMethods,
        clearFilters,
        refreshOptions,
        buildQueryParams,
      }}
    >
      {children}
    </FilterContext.Provider>
  )
}

export function useFilter() {
  const context = useContext(FilterContext)
  if (context === undefined) {
    throw new Error('useFilter must be used within a FilterProvider')
  }
  return context
}
