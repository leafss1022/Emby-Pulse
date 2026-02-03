/**
 * 应用常量配置
 */

// ========== 图片尺寸配置 ==========
export const IMAGE_SIZES = {
  /** 海报 - 大尺寸 (内容列表) */
  POSTER_LARGE: { maxHeight: 720, maxWidth: 480 },
  /** 海报 - 中等尺寸 (收藏列表) */
  POSTER_MEDIUM: { maxHeight: 300, maxWidth: 200 },
  /** 海报 - 小尺寸 (正在播放/缩略图) */
  POSTER_SMALL: { maxHeight: 192, maxWidth: 128 },
  /** 背景图尺寸 */
  BACKDROP: { maxHeight: 720, maxWidth: 1280 },
} as const

// ========== 数据刷新时间配置 (毫秒) ==========
export const REFRESH_INTERVALS = {
  /** 正在播放数据刷新间隔: 5 秒 */
  NOW_PLAYING: 5000,
  /** 统计数据刷新间隔: 30 秒 */
  STATS: 30000,
} as const

// ========== 分页/列表限制配置 ==========
export const LIST_LIMITS = {
  /** 热门内容默认显示数量 */
  TOP_CONTENT: 16,
  /** 播放排行默认显示数量 */
  PLAY_RANKING: 18,
  /** 历史记录默认显示数量 */
  HISTORY_DEFAULT: 48,
  /** 历史记录搜索显示数量 */
  HISTORY_SEARCH: 100,
} as const

// ========== 时间格式化配置 ==========
export const DATE_FORMATS = {
  /** 完整日期时间 */
  FULL: 'YYYY-MM-DD HH:mm:ss',
  /** 日期 */
  DATE: 'YYYY-MM-DD',
  /** 时间 */
  TIME: 'HH:mm:ss',
} as const

// ========== 动画时长配置 (毫秒) ==========
export const ANIMATION_DURATIONS = {
  /** 淡入动画 */
  FADE_IN: 400,
  /** 卡片悬停 */
  HOVER: 300,
  /** Toast 显示时长 */
  TOAST: 3000,
} as const

// ========== API 端点配置 ==========
export const API_ENDPOINTS = {
  /** 海报 API */
  POSTER: '/api/poster',
  /** 背景图 API */
  BACKDROP: '/api/backdrop',
} as const

// ========== 缓存配置 ==========
export const CACHE_KEYS = {
  /** 服务器 ID 缓存 */
  SERVER_ID: 'emby-stats-server-id',
  /** 筛选条件缓存 */
  FILTER: 'emby-stats-filter',
} as const

// ========== 表单验证规则 ==========
export const VALIDATION_RULES = {
  /** 必填字段 */
  required: (v: string | number | boolean | null | undefined) => {
    if (typeof v === 'number') return true
    if (typeof v === 'boolean') return true
    return !!v || '此字段为必填项'
  },
  /** 必须为正数 */
  positiveNumber: (v: number | string) => {
    const num = typeof v === 'string' ? parseFloat(v) : v
    return (typeof num === 'number' && num > 0) || '必须大于 0'
  },
  /** 必须为数字 ID */
  numeric: (v: string) => /^\d+$/.test(v) || '请输入有效的数字 ID',
  /** 邮箱格式 */
  email: (v: string) => {
    if (!v) return true
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || '请输入有效的邮箱地址'
  },
  /** 最小长度 */
  minLength: (min: number) => (v: string) => {
    if (!v) return true
    return v.length >= min || `最少需要 ${min} 个字符`
  },
  /** 最大长度 */
  maxLength: (max: number) => (v: string) => {
    if (!v) return true
    return v.length <= max || `最多允许 ${max} 个字符`
  },
  /** URL 格式 */
  url: (v: string) => {
    if (!v) return true
    try {
      new URL(v)
      return true
    } catch {
      return '请输入有效的 URL'
    }
  },
} as const
