import { computed, type ComputedRef, type Ref } from 'vue'
import { useServerStore } from '@/stores'
import { getPosterUrl } from '@/utils'
import { IMAGE_SIZES } from '@/constants'

export type PosterSize = 'small' | 'medium' | 'large' | 'custom'

interface PosterSizeConfig {
  maxHeight: number
  maxWidth: number
}

const SIZE_PRESETS: Record<Exclude<PosterSize, 'custom'>, PosterSizeConfig> = {
  small: IMAGE_SIZES.POSTER_SMALL,
  medium: IMAGE_SIZES.POSTER_MEDIUM,
  large: IMAGE_SIZES.POSTER_LARGE,
}

/**
 * 海报 URL 处理 Composable
 * 统一处理海报 URL 的 server_id 和尺寸参数
 */
export function usePosterUrl() {
  const serverStore = useServerStore()

  /**
   * 获取处理后的海报 URL
   * @param posterUrl 原始海报 URL
   * @param size 尺寸预设 ('small' | 'medium' | 'large') 或 'custom'
   * @param customSize 自定义尺寸 (当 size 为 'custom' 时使用)
   */
  function getUrl(
    posterUrl: string | undefined | null,
    size: PosterSize = 'large',
    customSize?: PosterSizeConfig
  ): string | undefined {
    if (!posterUrl) return undefined

    const sizeConfig = size === 'custom' && customSize
      ? customSize
      : SIZE_PRESETS[size as Exclude<PosterSize, 'custom'>] || SIZE_PRESETS.large

    return getPosterUrl(
      posterUrl,
      serverStore.currentServer?.id,
      sizeConfig.maxHeight,
      sizeConfig.maxWidth
    )
  }

  /**
   * 为列表项批量添加处理后的海报 URL
   * @param items 包含 poster_url 字段的列表
   * @param size 尺寸预设
   * @param customSize 自定义尺寸
   */
  function withPosterUrls<T extends { poster_url?: string | null }>(
    items: T[],
    size: PosterSize = 'large',
    customSize?: PosterSizeConfig
  ): (T & { poster_url?: string })[] {
    return items.map(item => ({
      ...item,
      poster_url: getUrl(item.poster_url, size, customSize)
    }))
  }

  /**
   * 创建响应式的海报 URL 列表
   * @param items 响应式列表
   * @param size 尺寸预设
   * @param customSize 自定义尺寸
   */
  function useItemsWithPosterUrls<T extends { poster_url?: string | null }>(
    items: Ref<T[]>,
    size: PosterSize = 'large',
    customSize?: PosterSizeConfig
  ): ComputedRef<(T & { poster_url?: string })[]> {
    return computed(() => withPosterUrls(items.value, size, customSize))
  }

  /**
   * 创建响应式的单个海报 URL
   * @param posterUrl 响应式海报 URL
   * @param size 尺寸预设
   * @param customSize 自定义尺寸
   */
  function usePosterUrlComputed(
    posterUrl: Ref<string | undefined | null> | ComputedRef<string | undefined | null>,
    size: PosterSize = 'large',
    customSize?: PosterSizeConfig
  ): ComputedRef<string | undefined> {
    return computed(() => getUrl(posterUrl.value, size, customSize))
  }

  /**
   * 直接构建海报 URL (用于收藏页面等需要手动拼接的场景)
   * @param itemId 内容 ID
   * @param size 尺寸预设
   * @param customSize 自定义尺寸
   */
  function buildPosterUrl(
    itemId: string,
    size: PosterSize = 'large',
    customSize?: PosterSizeConfig
  ): string {
    const sizeConfig = size === 'custom' && customSize
      ? customSize
      : SIZE_PRESETS[size as Exclude<PosterSize, 'custom'>] || SIZE_PRESETS.large

    return `/api/poster/${itemId}?maxHeight=${sizeConfig.maxHeight}&maxWidth=${sizeConfig.maxWidth}&server_id=${serverStore.currentServer?.id}`
  }

  return {
    getUrl,
    withPosterUrls,
    useItemsWithPosterUrls,
    usePosterUrlComputed,
    buildPosterUrl,
    SIZE_PRESETS,
  }
}
