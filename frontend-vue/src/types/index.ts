// ========== 服务器相关 ==========

export interface Server {
  id: string
  name: string
  emby_url: string
  playback_db?: string
  users_db?: string
  auth_db?: string
  emby_api_key?: string
  is_default: boolean
}

export interface ServerConfig {
  name: string
  emby_url: string
  playback_db: string
  users_db: string
  auth_db: string
  emby_api_key?: string
  is_default?: boolean
}

export interface ServersResponse {
  servers: Server[]
}

// ========== 认证相关 ==========

export interface User {
  user_id: string
  username: string
  is_admin: boolean
}

export interface Session {
  session_id: string
  user_id: string
  username: string
  is_admin: boolean
  expires: number
}

export interface LoginResponse {
  authenticated: boolean
  user?: User
}

export interface CheckAuthResponse {
  authenticated: boolean
  user?: User
}

// ========== API 响应类型 ==========

export interface OverviewData {
  total_plays: number
  total_duration_hours: number
  unique_users: number
  unique_items: number
}

export interface TrendItem {
  date: string
  plays: number
  duration_hours: number
}

export interface TrendData {
  trend: TrendItem[]
}

export interface HourlyItem {
  day: number
  hour: number
  count: number
}

export interface HourlyData {
  hourly: HourlyItem[]
}

export interface ShowItem {
  show_name: string
  poster_url?: string
  backdrop_url?: string
  play_count: number
  duration_hours: number
  overview?: string
  item_id?: number
}

export interface TopShowsData {
  top_shows: ShowItem[]
}

export interface ContentItem {
  item_name: string
  name?: string
  show_name?: string
  poster_url?: string
  backdrop_url?: string
  play_count: number
  duration_hours: number
  overview?: string
  item_id?: number
}

export interface TopContentData {
  top_content: ContentItem[]
}

export interface UserItem {
  username: string
  play_count: number
  duration_hours: number
  last_play?: string
}

export interface UsersData {
  users: UserItem[]
}

export interface ClientItem {
  client: string
  play_count: number
}

export interface ClientsData {
  clients: ClientItem[]
}

export interface PlaybackMethodItem {
  method: string
  play_count: number
}

export interface PlaybackMethodsData {
  methods: PlaybackMethodItem[]
}

export interface DeviceItem {
  device: string
  client: string
  play_count: number
}

export interface DevicesData {
  devices: DeviceItem[]
}

export interface RecentItem {
  item_name: string
  name?: string
  show_name?: string
  poster_url?: string
  backdrop_url?: string
  username: string
  time: string
  overview?: string
  client?: string
  device?: string
  item_id?: number
  duration_minutes?: number
}

export interface RecentData {
  recent: RecentItem[]
  total_count?: number
  total_duration_seconds?: number
}

export interface NowPlayingItem {
  item_name: string
  poster_url?: string
  user_name: string
  device_name: string
  client: string
  is_paused: boolean
  position_seconds: number
  runtime_seconds: number
  progress: number
}

export interface NowPlayingData {
  now_playing: NowPlayingItem[]
}

// ========== UI 类型 ==========

export interface PosterCardOptions {
  showRank?: boolean
  rank?: number
  showPlayCount?: boolean
  showUser?: boolean
  showTime?: boolean
  showEpisode?: boolean
}

// ========== 筛选相关 ==========

export interface NameMappingItem {
  original: string
  display: string
}

export interface FilterOptionsData {
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

// ========== 内容详情 ==========

export interface ContentDetailStats {
  total_plays: number
  total_duration_seconds: number
  total_duration_hours: number
  unique_users: number
  first_play: string | null
  last_play: string | null
}

export interface PlayRecord {
  time: string
  username: string
  user_id: string
  item_id: number
  item_name: string
  item_type: string
  client: string
  device: string
  duration_minutes: number
  method: string
}

export interface ContentDetailData {
  item_id: number
  item_name: string
  show_name: string
  item_type: string
  poster_url?: string
  backdrop_url?: string
  overview?: string
  stats: ContentDetailStats
  play_records: PlayRecord[]
}

// ========== 文件浏览 ==========

export interface FileEntry {
  name: string
  path: string
  is_dir: boolean
  size: number
  modified: number
}

export interface FileBrowserResponse {
  cwd: string
  parent?: string | null
  entries: FileEntry[]
}

// ========== 收藏相关 ==========

export interface FavoriteUser {
  user_id: string
  username: string
}

export interface FavoriteItem {
  item_id: string
  name: string
  type: string
  year?: number
  overview?: string
  favorite_count: number
  users: FavoriteUser[]
  has_poster: boolean
  series_id?: string
  series_name?: string
}

// 用户收藏的单个项目（不含 users 和 favorite_count）
export interface UserFavoriteItem {
  item_id: string
  name: string
  type: string
  year?: number
  overview?: string
  has_poster: boolean
  series_id?: string
  series_name?: string
}

// 按用户分组的收藏数据
export interface UserFavorites {
  user_id: string
  username: string
  favorites: UserFavoriteItem[]
  favorite_count: number
}

export interface FavoritesData {
  items: FavoriteItem[]
  users_favorites: UserFavorites[]
  total_users: number
  users_with_favorites: number
}

// ========== 报告相关 ==========

export interface TelegramConfig {
  enabled: boolean
  bot_token: string
  chat_id: string
  proxy?: string
}

export interface ScheduleItemConfig {
  enabled: boolean
  cron: string
}

export interface ScheduleConfig {
  daily: ScheduleItemConfig
  weekly: ScheduleItemConfig
  monthly: ScheduleItemConfig
  yearly: ScheduleItemConfig
}

export interface ReportConfig {
  telegram: TelegramConfig
  schedule: ScheduleConfig
  users: string[]
  content_count: number
}

export interface ReportConfigResponse {
  config: ReportConfig
  all_users: Array<{ user_id: string; username: string }>
  server_id: string
}

export interface TgBotConfig {
  enabled: boolean
  bot_token_masked?: string
  bot_token_configured: boolean
  default_period: string
  is_running: boolean
}

export interface TgBindingUser {
  tg_user_id: string
  tg_username: string | null
  tg_first_name: string | null
  server_id: string
  emby_user_id: string
  emby_username: string
  created_at: string
  server_name?: string
}

export interface TgBindingsResponse {
  bindings: TgBindingUser[]
  total: number
}

// ========== 名称映射 ==========

export interface NameMappings {
  clients?: Record<string, string>
  devices?: Record<string, string>
}

// ========== API 查询参数 ==========

/**
 * 统计 API 通用查询参数
 */
export interface StatsQueryParams {
  server_id?: string
  days?: number
  start_date?: string
  end_date?: string
  users?: string
  clients?: string
  devices?: string
  item_types?: string
  playback_methods?: string
  limit?: number
  offset?: number
  search?: string
  q?: string
}
