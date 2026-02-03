// API Response Types

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

// UI Types
export interface PosterCardOptions {
  showRank?: boolean
  rank?: number
  showPlayCount?: boolean
  showUser?: boolean
  showTime?: boolean
  showEpisode?: boolean
}

// Filter Types
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
