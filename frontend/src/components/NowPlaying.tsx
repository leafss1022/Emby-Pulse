import { useState } from 'react'
import { Card } from '@/components/ui'
import { Progress } from '@/components/ui/Progress'
import { useNowPlaying } from '@/hooks/useStats'
import { formatDuration } from '@/lib/utils'
import { Film, Play, Pause } from 'lucide-react'

function NowPlayingCard({ item }: { item: import('@/types').NowPlayingItem }) {
  const [imageError, setImageError] = useState(false)

  return (
    <div className="flex gap-4 p-3 rounded-xl bg-content1/50 backdrop-blur">
      <div className="w-16 h-24 rounded-lg overflow-hidden bg-content2 flex-shrink-0 relative">
        {item.poster_url && !imageError ? (
          <img
            src={item.poster_url}
            alt=""
            className="w-full h-full object-cover"
            loading="lazy"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Film className="w-6 h-6 opacity-20" />
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0 flex flex-col justify-between py-1">
        <div>
          <p className="font-medium text-sm truncate" title={item.item_name}>
            {item.item_name}
          </p>
          <p className="text-xs text-[var(--color-text-muted)] mt-1">{item.user_name}</p>
          <p className="text-xs text-[var(--color-text-secondary)]">
            {item.device_name} · {item.client}
          </p>
        </div>
        <div className="mt-2">
          <div className="flex items-center gap-2 mb-1">
            <div
              className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-xs ${
                item.is_paused
                  ? 'bg-warning/20 text-warning'
                  : 'bg-success/20 text-success'
              }`}
            >
              {item.is_paused ? (
                <Pause className="w-3 h-3" />
              ) : (
                <Play className="w-3 h-3" />
              )}
              <span>{item.is_paused ? '已暂停' : '播放中'}</span>
            </div>
            <span className="text-xs text-[var(--color-text-secondary)]">
              {formatDuration(item.position_seconds)} / {formatDuration(item.runtime_seconds)}
            </span>
          </div>
          <Progress value={item.progress} />
        </div>
      </div>
    </div>
  )
}

export function NowPlaying() {
  const { data, loading } = useNowPlaying(10000)

  if (loading || !data || data.now_playing.length === 0) {
    return null
  }

  return (
    <div className="mb-6 fade-in">
      <Card className="p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative flex items-center justify-center">
            <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-success opacity-75" />
            <span className="relative inline-flex rounded-full h-3 w-3 bg-success" />
          </div>
          <h3 className="font-semibold">正在播放</h3>
          <span className="text-xs text-[var(--color-text-secondary)]">{data.now_playing.length} 个会话</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.now_playing.map((item, index) => (
            <NowPlayingCard key={`${item.user_name}-${item.item_name}-${index}`} item={item} />
          ))}
        </div>
      </Card>
    </div>
  )
}
