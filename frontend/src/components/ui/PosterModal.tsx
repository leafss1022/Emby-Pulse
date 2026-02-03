import { useState, useEffect } from 'react'
import { Modal } from './Modal'
import { Film, Play, User, Clock, Timer, Image, RectangleHorizontal, Monitor, Smartphone } from 'lucide-react'
import { formatDateTime, formatHours } from '@/lib/utils'

export interface PosterModalData {
  title: string
  posterUrl?: string
  backdropUrl?: string
  itemName?: string
  playCount?: number
  durationHours?: number
  username?: string
  time?: string
  rank?: number
  overview?: string
  client?: string
  device?: string
}

interface PosterModalProps {
  data: PosterModalData | null
  onClose: () => void
}

type ImageMode = 'poster' | 'backdrop'

export function PosterModal({ data, onClose }: PosterModalProps) {
  const [imageError, setImageError] = useState(false)
  const [imageMode, setImageMode] = useState<ImageMode>('poster')

  // 数据变化时重置状态
  useEffect(() => {
    setImageError(false)
    // 如果有 backdrop 默认显示横版，否则显示竖版
    setImageMode(data?.backdropUrl ? 'backdrop' : 'poster')
  }, [data?.posterUrl, data?.backdropUrl])

  if (!data) return null

  const posterUrl = data.posterUrl
    ? `${data.posterUrl}?maxHeight=900&maxWidth=600`
    : undefined

  const backdropUrl = data.backdropUrl
    ? `${data.backdropUrl}?maxHeight=720&maxWidth=1280`
    : undefined

  const currentImageUrl = imageMode === 'backdrop' ? backdropUrl : posterUrl
  const hasBackdrop = !!backdropUrl
  const hasPoster = !!posterUrl
  const canSwitch = hasBackdrop && hasPoster

  return (
    <Modal open onClose={onClose}>
      <div className="relative overflow-hidden rounded-2xl bg-content1 border border-[var(--color-border)] shadow-[0_8px_32px_rgba(0,0,0,0.12)] dark:shadow-[0_8px_40px_rgba(0,0,0,0.5)] dark:bg-gradient-to-br dark:from-content1 dark:to-[var(--color-card-gradient-end)]">
        {/* 顶部高光线 */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[var(--color-border)] to-transparent" />
        {/* 海报区域 */}
        <div className="relative bg-[var(--color-content2)]">
          {currentImageUrl && !imageError ? (
            <img
              src={currentImageUrl}
              alt={data.title}
              className={`w-full object-contain ${
                imageMode === 'backdrop'
                  ? 'max-h-[40vh] aspect-video'
                  : 'max-h-[50vh]'
              }`}
              onError={() => setImageError(true)}
            />
          ) : (
            <div className={`w-full flex items-center justify-center bg-[var(--color-content2)] ${
              imageMode === 'backdrop'
                ? 'aspect-video max-h-[40vh]'
                : 'aspect-[2/3] max-h-[50vh]'
            }`}>
              <Film className="w-16 h-16 text-zinc-600" />
            </div>
          )}

          {/* 排名角标 */}
          {data.rank && (
            <div className="absolute top-4 left-4 w-10 h-10 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center text-lg font-bold text-white shadow-lg">
              {data.rank}
            </div>
          )}

          {/* 切换按钮 */}
          {canSwitch && (
            <div className="absolute top-4 right-4 flex gap-1 bg-black/50 backdrop-blur-sm rounded-lg p-1">
              <button
                onClick={() => {
                  setImageError(false)
                  setImageMode('poster')
                }}
                className={`p-1.5 rounded-md transition-colors ${
                  imageMode === 'poster'
                    ? 'bg-white/20 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
                title="竖版海报"
              >
                <Image className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  setImageError(false)
                  setImageMode('backdrop')
                }}
                className={`p-1.5 rounded-md transition-colors ${
                  imageMode === 'backdrop'
                    ? 'bg-white/20 text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
                title="横版背景"
              >
                <RectangleHorizontal className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* 信息区域 */}
        <div className="p-5">
          <h3 className="text-xl font-bold text-foreground mb-1">{data.title}</h3>

          {data.itemName && data.itemName !== data.title && (
            <p className="text-sm text-[var(--color-text-muted)] mb-2">{data.itemName}</p>
          )}

          {data.overview && (
            <p className="text-sm text-[var(--color-text-muted)] leading-relaxed mt-3 mb-4 line-clamp-4">
              {data.overview}
            </p>
          )}

          {/* 统计信息 */}
          <div className="space-y-3 mt-4">
            {data.playCount !== undefined && data.playCount > 0 && (
              <div className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Play className="w-4 h-4 text-blue-400" />
                </div>
                <span className="text-[var(--color-text-muted)]">
                  播放 <span className="text-blue-400 font-semibold">{data.playCount}</span> 次
                </span>
              </div>
            )}

            {data.durationHours !== undefined && data.durationHours > 0 && (
              <div className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Timer className="w-4 h-4 text-purple-400" />
                </div>
                <span className="text-[var(--color-text-muted)]">
                  累计 <span className="text-purple-400 font-semibold">{formatHours(data.durationHours)}</span>
                </span>
              </div>
            )}

            {data.username && (
              <div className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                  <User className="w-4 h-4 text-green-400" />
                </div>
                <span className="text-[var(--color-text-muted)]">{data.username}</span>
              </div>
            )}

            {data.client && (
              <div className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                  <Monitor className="w-4 h-4 text-cyan-400" />
                </div>
                <span className="text-[var(--color-text-muted)]">{data.client}</span>
              </div>
            )}

            {data.device && (
              <div className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-pink-500/20 flex items-center justify-center">
                  <Smartphone className="w-4 h-4 text-pink-400" />
                </div>
                <span className="text-[var(--color-text-muted)]">{data.device}</span>
              </div>
            )}

            {data.time && (
              <div className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center">
                  <Clock className="w-4 h-4 text-amber-400" />
                </div>
                <span className="text-[var(--color-text-muted)]">{formatDateTime(data.time)}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Modal>
  )
}
