import type {
  OverviewData,
  TrendData,
  HourlyData,
  TopShowsData,
  TopContentData,
  UsersData,
  ClientsData,
  PlaybackMethodsData,
  DevicesData,
  RecentData,
  NowPlayingData,
  FilterOptionsData,
} from '@/types'

const API_BASE = '/api'

// 认证状态变更回调
let onAuthError: (() => void) | null = null

export function setAuthErrorHandler(handler: () => void) {
  onAuthError = handler
}

// 筛选参数类型
export type FilterParams = Record<string, string>

// 构建带筛选参数的查询字符串
function buildQueryString(params: FilterParams): string {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.set(key, value)
    }
  }
  return searchParams.toString()
}

async function fetchAPI<T>(endpoint: string, params?: FilterParams): Promise<T> {
  let url = `${API_BASE}${endpoint}`
  if (params && Object.keys(params).length > 0) {
    const queryString = buildQueryString(params)
    url += (endpoint.includes('?') ? '&' : '?') + queryString
  }

  const res = await fetch(url)
  if (!res.ok) {
    // 401 错误触发认证失败
    if (res.status === 401) {
      onAuthError?.()
    }
    throw new Error(`API error: ${res.status}`)
  }
  return res.json()
}

export const api = {
  getOverview: (params: FilterParams = {}): Promise<OverviewData> =>
    fetchAPI('/overview', params),

  getTrend: (params: FilterParams = {}): Promise<TrendData> =>
    fetchAPI('/trend', params),

  getHourly: (params: FilterParams = {}): Promise<HourlyData> =>
    fetchAPI('/hourly', params),

  getTopShows: (params: FilterParams = {}, limit = 16): Promise<TopShowsData> =>
    fetchAPI('/top-shows', { ...params, limit: String(limit) }),

  getTopContent: (params: FilterParams = {}, limit = 18): Promise<TopContentData> =>
    fetchAPI('/top-content', { ...params, limit: String(limit) }),

  getUsers: (params: FilterParams = {}): Promise<UsersData> =>
    fetchAPI('/users', params),

  getClients: (params: FilterParams = {}): Promise<ClientsData> =>
    fetchAPI('/clients', params),

  getPlaybackMethods: (params: FilterParams = {}): Promise<PlaybackMethodsData> =>
    fetchAPI('/playback-methods', params),

  getDevices: (params: FilterParams = {}): Promise<DevicesData> =>
    fetchAPI('/devices', params),

  getRecent: (params: FilterParams = {}, limit = 48, offset = 0): Promise<RecentData> =>
    fetchAPI('/recent', { ...params, limit: String(limit), offset: String(offset) }),

  getNowPlaying: (): Promise<NowPlayingData> =>
    fetchAPI('/now-playing'),

  getFilterOptions: (): Promise<FilterOptionsData> =>
    fetchAPI('/filter-options'),

  // 认证相关
  checkAuth: async (): Promise<{ authenticated: boolean; username?: string }> => {
    const res = await fetch(`${API_BASE}/auth/check`)
    return res.json()
  },

  login: async (username: string, password: string): Promise<{ success: boolean; username?: string; message?: string }> => {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      const data = await res.json()
      return { success: false, message: data.detail || '登录失败' }
    }
    return res.json()
  },

  logout: async (): Promise<void> => {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST' })
  },

  // 名称映射相关
  getNameMappings: async (): Promise<{ clients: Record<string, string>; devices: Record<string, string> }> => {
    const res = await fetch(`${API_BASE}/name-mappings`)
    return res.json()
  },

  saveNameMappings: async (mappings: { clients: Record<string, string>; devices: Record<string, string> }): Promise<{ status: string; message: string }> => {
    const res = await fetch(`${API_BASE}/name-mappings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(mappings),
    })
    return res.json()
  },

  reloadNameMappings: async (): Promise<{ status: string; message: string }> => {
    const res = await fetch(`${API_BASE}/name-mappings/reload`, { method: 'POST' })
    return res.json()
  },
}

export default api
