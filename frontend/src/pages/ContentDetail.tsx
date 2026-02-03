import { useState, useEffect } from 'react'
import { Card } from '@/components/ui'
import { api } from '@/services/api'
import type { ContentDetailData } from '@/types'
import { ArrowLeft, Film, Calendar, Clock, Users, Play, Loader2 } from 'lucide-react'
import { formatDateTime, formatEpisodeName } from '@/lib/utils'
import { motion } from 'framer-motion'
import { useServer } from '@/contexts/ServerContext'

// 给 URL 追加 server_id 参数
function appendServerId(url: string | undefined, serverId: string | undefined): string | undefined {
  if (!url || !serverId) return url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}server_id=${serverId}`
}

interface ContentDetailProps {
  itemId?: string
  itemName?: string
  onBack: () => void
}

export function ContentDetail({ itemId, itemName, onBack }: ContentDetailProps) {
  const { currentServer } = useServer()
  const [data, setData] = useState<ContentDetailData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [backdropError, setBackdropError] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        const params: Record<string, string> = {}
        if (itemId) {
          params.item_id = itemId
        } else if (itemName) {
          params.item_name = itemName
        }
        // 添加 server_id 参数
        if (currentServer?.id) {
          params.server_id = currentServer.id
        }
        const result = await api.getContentDetail(params)
        if ('error' in result) {
          setError(result.error)
        } else {
          setData(result)
          // 重置背景图错误状态
          setBackdropError(false)
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : '加载失败'
        setError(message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [itemId, itemName, currentServer?.id])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    )
  }

  if (error || !data) {
    return (
      <Card className="p-5">
        <div className="text-center py-8">
          <p className="text-red-500 mb-4">{error || '未找到内容'}</p>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            返回
          </button>
        </div>
      </Card>
    )
  }

  const { stats, play_records, poster_url, backdrop_url, item_name, show_name, overview } = data

  // 给 URL 追加 server_id
  const finalPosterUrl = appendServerId(poster_url, currentServer?.id)
  const finalBackdropUrl = appendServerId(backdrop_url, currentServer?.id)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 28,
        mass: 0.9
      }}
      className="space-y-3 sm:space-y-4"
    >
      {/* 返回按钮 */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-[var(--color-text-muted)] active:text-foreground transition-colors mb-2 min-h-[44px] px-2 -ml-2"
      >
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm sm:text-base">返回</span>
      </button>

      {/* 内容头部 */}
      <Card className="p-0 overflow-hidden">
        {/* 背景图铺满上方区域（仅桌面端展示，移动端隐藏避免占屏） */}
        {finalBackdropUrl && !backdropError && (
          <div className="relative w-full h-[45vh] min-h-[260px] max-h-[480px] overflow-hidden hidden sm:block">
            <img
              src={finalBackdropUrl}
              alt={show_name}
              className="w-full h-full object-cover"
              onError={() => {
                setBackdropError(true)
              }}
            />
          </div>
        )}

        {/* 内容信息 */}
        <div className="p-4 sm:p-5">
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            {/* 海报 */}
            {finalPosterUrl && (
              <div className="flex-shrink-0 mx-auto sm:mx-0">
                <div className="relative w-24 h-36 sm:w-32 sm:h-48 rounded-lg overflow-hidden bg-zinc-800">
                  <img
                    src={finalPosterUrl}
                    alt={show_name}
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            )}

            {/* 信息 */}
            <div className="flex-1">
              <h2 className="text-xl sm:text-2xl font-bold mb-2 text-center sm:text-left">{show_name || item_name}</h2>
              {/* 当通过 itemId 进入时（查看具体某一集），显示单集名称作为副标题 */}
              {/* 当通过 itemName 进入时（查看整部剧），不显示副标题 */}
              {itemId && show_name && item_name && show_name !== item_name && (
                <p className="text-sm text-[var(--color-text-muted)] mb-3 sm:mb-4 text-center sm:text-left">{formatEpisodeName(item_name)}</p>
              )}

              {/* 统计卡片 */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 mb-3 sm:mb-4">
                <div className="bg-[var(--color-content2)] rounded-lg p-3">
                  <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-1">
                    <Play className="w-4 h-4" />
                    <span className="text-xs">播放次数</span>
                  </div>
                  <p className="text-xl font-bold">{stats.total_plays}</p>
                </div>
                <div className="bg-[var(--color-content2)] rounded-lg p-3">
                  <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-1">
                    <Clock className="w-4 h-4" />
                    <span className="text-xs">总时长</span>
                  </div>
                  <p className="text-xl font-bold">{stats.total_duration_hours.toFixed(1)}h</p>
                </div>
                <div className="bg-[var(--color-content2)] rounded-lg p-3">
                  <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-1">
                    <Users className="w-4 h-4" />
                    <span className="text-xs">观看用户</span>
                  </div>
                  <p className="text-xl font-bold">{stats.unique_users}</p>
                </div>
                <div className="bg-[var(--color-content2)] rounded-lg p-3">
                  <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-1">
                    <Calendar className="w-4 h-4" />
                    <span className="text-xs">最后播放</span>
                  </div>
                  <p className="text-sm font-medium">
                    {stats.last_play ? formatDateTime(stats.last_play).split(' ')[0] : '-'}
                  </p>
                </div>
              </div>

              {/* 简介 */}
              {overview && (
                <div className="mt-4">
                  <p className="text-sm text-[var(--color-text-muted)] leading-relaxed line-clamp-3">
                    {overview}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* 播放记录列表 */}
      <Card className="p-4 sm:p-5">
        <h3 className="font-semibold mb-3 sm:mb-4 text-sm sm:text-base">播放记录 ({play_records.length} 条)</h3>
        {play_records.length === 0 ? (
          <p className="text-center text-[var(--color-text-muted)] py-8">暂无播放记录</p>
        ) : (
          <div className="space-y-2">
            {play_records.map((record, index) => (
              <div
                key={`${record.time}-${record.user_id}-${index}`}
                className="flex items-center gap-3 sm:gap-4 p-2.5 sm:p-3 rounded-lg bg-[var(--color-content2)] active:bg-[var(--color-content3)] transition-colors"
              >
                {/* 小封面 */}
                {finalPosterUrl && (
                  <div className="relative w-12 h-16 flex-shrink-0 rounded-md overflow-hidden bg-zinc-800">
                    <img
                      src={finalPosterUrl}
                      alt={record.item_name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                {!finalPosterUrl && (
                  <div className="relative w-12 h-16 flex-shrink-0 rounded-md overflow-hidden bg-zinc-800 flex items-center justify-center">
                    <Film className="w-5 h-5 text-zinc-600" />
                  </div>
                )}

                {/* 内容信息 */}
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-[var(--color-foreground)] truncate">
                    {formatEpisodeName(record.item_name)}
                  </p>
                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-[var(--color-text-muted)]">
                    <span>{record.username}</span>
                    <span>{formatDateTime(record.time)}</span>
                    {record.duration_minutes > 0 && (
                      <span>{record.duration_minutes} 分钟</span>
                    )}
                  </div>
                </div>

                {/* 右侧信息 */}
                <div className="flex-shrink-0 text-right text-xs text-[var(--color-text-muted)]">
                  <p>{record.client}</p>
                  <p className="mt-0.5">{record.device}</p>
                  {record.method && (
                    <p className="mt-0.5 text-[10px]">{record.method}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </motion.div>
  )
}