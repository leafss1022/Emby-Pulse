import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { statsApi } from '@/services'
import type { FilterOptionsData } from '@/types'

export const useFilterStore = defineStore(
  'filter',
  () => {
    // State
    const days = ref(30)
    const startDate = ref<string | null>(null)
    const endDate = ref<string | null>(null)
    const users = ref<string[]>([])
    const clients = ref<string[]>([])
    const devices = ref<string[]>([])
    const itemTypes = ref<string[]>([])
    const playbackMethods = ref<string[]>([])
    const options = ref<FilterOptionsData | null>(null)

    // Getters
    const hasActiveFilters = computed(() => {
      return (
        days.value !== 30 ||
        startDate.value !== null ||
        endDate.value !== null ||
        users.value.length > 0 ||
        clients.value.length > 0 ||
        devices.value.length > 0 ||
        itemTypes.value.length > 0 ||
        playbackMethods.value.length > 0
      )
    })

    const activeFilterCount = computed(() => {
      let count = 0
      if (days.value !== 30) count++
      if (startDate.value || endDate.value) count++
      if (users.value.length > 0) count++
      if (clients.value.length > 0) count++
      if (devices.value.length > 0) count++
      if (itemTypes.value.length > 0) count++
      if (playbackMethods.value.length > 0) count++
      return count
    })

    const buildQueryParams = computed(() => {
      const params: Record<string, any> = {}

      if (days.value) params.days = days.value
      if (startDate.value) params.start_date = startDate.value
      if (endDate.value) params.end_date = endDate.value
      if (users.value.length) params.users = users.value.join(',')
      if (clients.value.length) params.clients = clients.value.join(',')
      if (devices.value.length) params.devices = devices.value.join(',')
      if (itemTypes.value.length) params.item_types = itemTypes.value.join(',')
      if (playbackMethods.value.length)
        params.playback_methods = playbackMethods.value.join(',')

      return params
    })

    // Actions
    async function fetchFilterOptions(serverId: string) {
      try {
        const response = await statsApi.getFilterOptions(serverId)
        options.value = response.data
      } catch (error) {
        console.error('Failed to fetch filter options:', error)
        options.value = null
      }
    }

    function clearFilters() {
      days.value = 30
      startDate.value = null
      endDate.value = null
      users.value = []
      clients.value = []
      devices.value = []
      itemTypes.value = []
      playbackMethods.value = []
    }

    function setDays(value: number) {
      days.value = value
      // 当设置 days 时，清空日期范围
      startDate.value = null
      endDate.value = null
    }

    function setDateRange(start: string | null, end: string | null) {
      startDate.value = start
      endDate.value = end
      // 当设置日期范围时，清空 days
      if (start || end) {
        days.value = 0
      }
    }

    return {
      // State
      days,
      startDate,
      endDate,
      users,
      clients,
      devices,
      itemTypes,
      playbackMethods,
      options,
      // Getters
      hasActiveFilters,
      activeFilterCount,
      buildQueryParams,
      // Actions
      fetchFilterOptions,
      clearFilters,
      setDays,
      setDateRange,
    }
  },
  {
    persist: {
      storage: localStorage,
      paths: [
        'days',
        'startDate',
        'endDate',
        'users',
        'clients',
        'devices',
        'itemTypes',
        'playbackMethods',
      ],
    } as any,
  }
)
