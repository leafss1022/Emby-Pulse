/**
 * 格式化播放时长
 * @param seconds 秒数
 * @returns 格式化的时长字符串 (如 "2小时30分钟" 或 "45分钟")
 */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

/**
 * 格式化日期
 * @param date 日期字符串或 Date 对象
 * @returns 格式化的日期字符串
 */
export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('zh-CN')
}

/**
 * 格式化日期时间
 * @param date 日期字符串或 Date 对象
 * @returns 格式化的日期时间字符串
 */
export function formatDateTime(date: string | Date): string {
  return new Date(date).toLocaleString('zh-CN')
}

/**
 * 格式化数字（添加千分位）
 * @param num 数字
 * @returns 格式化的数字字符串
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

/**
 * 格式化字节大小
 * @param bytes 字节数
 * @returns 格式化的大小字符串 (如 "1.5 GB")
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

/**
 * 格式化百分比
 * @param value 数值
 * @param total 总数
 * @param decimals 小数位数
 * @returns 百分比字符串
 */
export function formatPercentage(
  value: number,
  total: number,
  decimals: number = 1
): string {
  if (total === 0) return '0%'
  return `${((value / total) * 100).toFixed(decimals)}%`
}

/**
 * 延迟执行
 * @param ms 毫秒数
 * @returns Promise
 */
export function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * 防抖函数
 * @param fn 要执行的函数
 * @param wait 等待时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null

  return function (this: any, ...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => fn.apply(this, args), wait)
  }
}

/**
 * 节流函数
 * @param fn 要执行的函数
 * @param wait 等待时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  wait: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function (this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      fn.apply(this, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), wait)
    }
  }
}

/**
 * 给 URL 追加 server_id 参数
 * @param url 原始URL
 * @param serverId 服务器ID
 * @returns 添加了server_id参数的URL
 */
export function appendServerId(
  url: string | undefined,
  serverId: string | undefined
): string | undefined {
  if (!url || !serverId) return url
  if (url.includes('server_id=')) return url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}server_id=${serverId}`
}

/**
 * 给海报URL添加完整参数（server_id + 尺寸）
 * @param url 海报URL（如 /api/poster/xxx）
 * @param serverId 服务器ID
 * @param maxHeight 最大高度（默认720）
 * @param maxWidth 最大宽度（默认480）
 * @returns 完整的海报URL
 */
export function getPosterUrl(
  url: string | undefined,
  serverId: string | undefined,
  maxHeight: number = 720,
  maxWidth: number = 480
): string | undefined {
  if (!url) return url

  const params = new URLSearchParams()
  if (serverId) params.set('server_id', serverId)
  params.set('maxHeight', String(maxHeight))
  params.set('maxWidth', String(maxWidth))

  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}${params.toString()}`
}

/**
 * 给背景图URL添加完整参数（server_id + 尺寸）
 * @param url 背景图URL（如 /api/backdrop/xxx）
 * @param serverId 服务器ID
 * @param maxHeight 最大高度（默认720）
 * @param maxWidth 最大宽度（默认1280）
 * @returns 完整的背景图URL
 */
export function getBackdropUrl(
  url: string | undefined,
  serverId: string | undefined,
  maxHeight: number = 720,
  maxWidth: number = 1280
): string | undefined {
  if (!url) return url

  const params = new URLSearchParams()
  if (serverId) params.set('server_id', serverId)
  params.set('maxHeight', String(maxHeight))
  params.set('maxWidth', String(maxWidth))

  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}${params.toString()}`
}
