import { useState } from 'react'
import { Film } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'
import { PosterModal, type PosterModalData } from './PosterModal'

interface PosterCardProps {
  title: string
  posterUrl?: string
  backdropUrl?: string
  itemName?: string
  rank?: number
  playCount?: number
  durationHours?: number
  username?: string
  time?: string
  showEpisode?: boolean
  overview?: string
  client?: string
  device?: string
}

export function PosterCard({
  title,
  posterUrl,
  backdropUrl,
  itemName,
  rank,
  playCount,
  durationHours,
  username,
  time,
  showEpisode,
  overview,
  client,
  device,
}: PosterCardProps) {
  const [imageError, setImageError] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)

  // 解析剧集信息 S01E02 格式
  let episodeInfo = ''
  if (showEpisode && itemName?.includes(' - ')) {
    const parts = itemName.split(' - ')
    if (parts.length >= 2) {
      const match = parts[1].match(/s(\d+)e(\d+)/i)
      if (match) {
        episodeInfo = `S${match[1]}E${match[2]}`
      }
    }
  }

  const displayTitle = episodeInfo ? `${title} ${episodeInfo}` : title

  const modalData: PosterModalData = {
    title: displayTitle,
    posterUrl,
    backdropUrl,
    itemName,
    playCount,
    durationHours,
    username,
    time,
    rank,
    overview,
    client,
    device,
  }

  return (
    <>
      <div
        className="relative rounded-xl overflow-hidden bg-zinc-800 aspect-[2/3] cursor-pointer transition-transform duration-200 hover:scale-105"
        onClick={() => setModalOpen(true)}
      >
        {/* 海报图片 */}
        {posterUrl && !imageError && (
          <img
            src={posterUrl}
            alt={title}
            loading="lazy"
            className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        )}

        {/* 占位图 */}
        {(!posterUrl || imageError || !imageLoaded) && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-800">
            <Film className="w-8 h-8 text-zinc-600" />
          </div>
        )}

        {/* 排名角标 */}
        {rank && (
          <div className="absolute top-2 left-2 w-6 h-6 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center text-xs font-bold text-white">
            {rank}
          </div>
        )}

        {/* 播放次数角标 */}
        {playCount !== undefined && playCount > 0 && (
          <div className="absolute top-2 right-2 bg-blue-500 text-white px-1.5 py-0.5 rounded text-[10px] font-semibold">
            {playCount}次
          </div>
        )}

        {/* 底部信息栏 */}
        <div className="absolute bottom-0 left-0 right-0 p-2 pt-8 bg-gradient-to-t from-black/90 to-transparent">
          <p className="text-xs font-medium text-white line-clamp-2 leading-tight">
            {displayTitle}
          </p>
          {username && (
            <p className="text-[10px] text-zinc-300 mt-0.5 truncate">{username}</p>
          )}
          {time && (
            <p className="text-[10px] text-zinc-400">{formatDateTime(time)}</p>
          )}
        </div>
      </div>

      {/* 弹窗 */}
      {modalOpen && (
        <PosterModal data={modalData} onClose={() => setModalOpen(false)} />
      )}
    </>
  )
}
