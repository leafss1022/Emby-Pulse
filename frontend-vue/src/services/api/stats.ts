import axios from '../axios'
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
  ContentDetailData,
  FilterOptionsData,
  FavoritesData,
  FileBrowserResponse,
  ReportConfig,
  ReportConfigResponse,
  TgBotConfig,
  TgBindingUser,
  TgBindingsResponse,
  NameMappings,
  StatsQueryParams,
} from '@/types'

export const statsApi = {
  /**
   * 获取总览统计数据
   */
  getOverview: (params: StatsQueryParams) =>
    axios.get<OverviewData>('/overview', { params }),

  /**
   * 获取趋势数据
   */
  getTrend: (params: StatsQueryParams) =>
    axios.get<TrendData>('/trend', { params }),

  /**
   * 获取按小时统计数据（热力图）
   */
  getHourly: (params: StatsQueryParams) =>
    axios.get<HourlyData>('/hourly', { params }),

  /**
   * 获取热门内容
   */
  getTopContent: (params: StatsQueryParams) =>
    axios.get<TopContentData>('/top-content', { params }),

  /**
   * 获取热门剧集
   */
  getTopShows: (params: StatsQueryParams) =>
    axios.get<TopShowsData>('/top-shows', { params }),

  /**
   * 获取用户统计数据
   */
  getUsers: (params: StatsQueryParams) =>
    axios.get<UsersData>('/users', { params }),

  /**
   * 获取客户端统计数据
   */
  getClients: (params: StatsQueryParams) =>
    axios.get<ClientsData>('/clients', { params }),

  /**
   * 获取播放方式统计数据
   */
  getPlaybackMethods: (params: StatsQueryParams) =>
    axios.get<PlaybackMethodsData>('/playback-methods', { params }),

  /**
   * 获取设备统计数据
   */
  getDevices: (params: StatsQueryParams) =>
    axios.get<DevicesData>('/devices', { params }),

  /**
   * 获取最近播放记录
   */
  getRecent: (params: StatsQueryParams) =>
    axios.get<RecentData>('/recent', { params }),

  /**
   * 获取正在播放的内容
   */
  getNowPlaying: (params: StatsQueryParams) =>
    axios.get<NowPlayingData>('/now-playing', { params }),

  /**
   * 获取内容详情
   */
  getContentDetail: (params: StatsQueryParams & { item_id: string }) =>
    axios.get<ContentDetailData>('/content-detail', { params }),

  /**
   * 获取筛选选项
   */
  getFilterOptions: (serverId: string) =>
    axios.get<FilterOptionsData>('/filter-options', {
      params: { server_id: serverId },
    }),

  /**
   * 获取收藏统计数据
   */
  getFavorites: (params: StatsQueryParams) =>
    axios.get<FavoritesData>('/favorites', { params }),
}

/**
 * 媒体资源 API
 */
export const mediaApi = {
  /**
   * 获取海报 URL
   * @param itemId 内容ID
   * @param serverId 服务器ID
   * @param maxHeight 最大高度（默认720）
   * @param maxWidth 最大宽度（默认480）
   */
  getPosterUrl: (
    itemId: string | number,
    serverId?: string,
    maxHeight: number = 720,
    maxWidth: number = 480
  ) => {
    const params = new URLSearchParams()
    if (serverId) params.set('server_id', serverId)
    params.set('maxHeight', String(maxHeight))
    params.set('maxWidth', String(maxWidth))
    return `/api/poster/${itemId}?${params.toString()}`
  },

  /**
   * 获取背景图 URL
   * @param itemId 内容ID
   * @param serverId 服务器ID
   * @param maxHeight 最大高度（默认720）
   * @param maxWidth 最大宽度（默认1280）
   */
  getBackdropUrl: (
    itemId: string | number,
    serverId?: string,
    maxHeight: number = 720,
    maxWidth: number = 1280
  ) => {
    const params = new URLSearchParams()
    if (serverId) params.set('server_id', serverId)
    params.set('maxHeight', String(maxHeight))
    params.set('maxWidth', String(maxWidth))
    return `/api/backdrop/${itemId}?${params.toString()}`
  },
}

/**
 * 文件浏览 API
 */
export const filesApi = {
  /**
   * 浏览文件
   */
  browseFiles: (path: string = '/') =>
    axios.get<FileBrowserResponse>('/files', { params: { path } }),
}

/**
 * 报告 API
 */
export const reportApi = {
  /**
   * 获取报告配置
   */
  getReportConfig: (serverId: string) =>
    axios.get<ReportConfigResponse>('/report/config', { params: { server_id: serverId } }),

  /**
   * 保存报告配置
   */
  saveReportConfig: (serverId: string, config: ReportConfig) =>
    axios.post('/report/config', config, { params: { server_id: serverId } }),

  /**
   * 预览报告
   */
  previewReport: (serverId: string, period: string, userId?: string) => {
    const params: { server_id: string; period: string; user_id?: string } = { server_id: serverId, period }
    if (userId) params.user_id = userId
    return axios.get('/report/preview', { params, responseType: 'blob' })
  },

  /**
   * 手动发送报告
   */
  sendReport: (serverId: string, period: string, userId?: string) => {
    const params: { server_id: string; period: string; user_id?: string } = { server_id: serverId, period }
    if (userId) params.user_id = userId
    return axios.post('/report/send', null, { params })
  },

  /**
   * 获取 TG 绑定用户列表
   */
  getBindings: (serverId: string) =>
    axios.get<TgBindingsResponse>('/tg-bot/bindings', {
      params: { server_id: serverId },
    }),

  /**
   * 删除 TG 绑定
   */
  deleteBinding: (serverId: string, tgUserId: string) =>
    axios.delete(`/tg-bot/bindings/${tgUserId}`, {
      params: { server_id: serverId },
    }),

  /**
   * 测试报告推送（Telegram）
   */
  testReportPush: (botToken: string, chatId: string) =>
    axios.post('/report/test-push', { bot_token: botToken, chat_id: chatId }),
}

/**
 * Telegram Bot API
 */
export const tgBotApi = {
  /**
   * 获取 Bot 配置
   */
  getTgBotConfig: () => axios.get<TgBotConfig>('/tg-bot/config'),

  /**
   * 保存 Bot 配置
   */
  saveTgBotConfig: (config: TgBotConfig) =>
    axios.post('/tg-bot/config', config),
}

/**
 * 名称映射 API
 */
export const nameMappingApi = {
  /**
   * 获取名称映射
   */
  getNameMappings: () => axios.get<NameMappings>('/name-mappings'),

  /**
   * 保存名称映射
   */
  saveNameMappings: (mappings: NameMappings) =>
    axios.post('/name-mappings', mappings),
}
