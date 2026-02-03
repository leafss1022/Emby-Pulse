import { useState, useMemo } from 'react'
import { Card, PosterCard, PosterGridSkeleton } from '@/components/ui'
import { useRecent } from '@/hooks/useStats'
import type { FilterParams } from '@/services/api'
import { Search, X, Film } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'

interface HistoryProps {
  filterParams: FilterParams
}

// 列表项组件
function HistoryListItem({ item }: { item: any }) {
  const [imageError, setImageError] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)

  return (
    <div className="flex items-center gap-4 p-3 rounded-lg bg-[var(--color-content2)] hover:bg-[var(--color-content3)] transition-colors">
      {/* 小封面 */}
      <div className="relative w-12 h-16 flex-shrink-0 rounded-md overflow-hidden bg-zinc-800">
        {item.poster_url && !imageError ? (
          <img
            src={item.poster_url}
            alt={item.item_name}
            loading="lazy"
            className={`w-full h-full object-cover transition-opacity duration-300 ${
              imageLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        ) : null}
        {(!item.poster_url || imageError || !imageLoaded) && (
          <div className="absolute inset-0 flex items-center justify-center">
            <Film className="w-5 h-5 text-zinc-600" />
          </div>
        )}
      </div>

      {/* 内容信息 */}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm text-[var(--color-foreground)] truncate">
          {item.item_name}
        </p>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-[var(--color-text-muted)]">
          <span>{item.username}</span>
          <span>{formatDateTime(item.time)}</span>
          {item.duration_minutes > 0 && (
            <span>{item.duration_minutes} 分钟</span>
          )}
        </div>
      </div>

      {/* 右侧信息 */}
      <div className="flex-shrink-0 text-right text-xs text-[var(--color-text-muted)]">
        <p>{item.client}</p>
        <p className="mt-0.5">{item.device}</p>
      </div>
    </div>
  )
}

export function History({ filterParams }: HistoryProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchInput, setSearchInput] = useState('')

  // 构建查询参数：搜索时使用全库范围，否则使用筛选器的时间范围
  const historyParams = useMemo(() => {
    const params: FilterParams = { ...filterParams }
    if (searchQuery.trim()) {
      // 搜索时移除时间限制，使用全库范围
      delete params.days
      delete params.start_date
      delete params.end_date
      params.search = searchQuery.trim()
    }
    return params
  }, [filterParams, searchQuery])

  const { data: recentData, loading } = useRecent(historyParams, searchQuery ? 100 : 48)

  const items = recentData?.recent ?? []
  const isSearching = !!searchQuery.trim()

  const handleSearch = () => {
    setSearchQuery(searchInput)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  const clearSearch = () => {
    setSearchInput('')
    setSearchQuery('')
  }

  return (
    <Card className="p-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <h3 className="font-semibold">最近播放</h3>
        {/* 搜索框 */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--color-text-muted)]" />
            <input
              type="text"
              value={searchInput}
              onChange={e => setSearchInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="搜索内容名称..."
              className="w-full pl-9 pr-8 py-2 text-sm rounded-lg border border-[var(--color-border)] bg-[var(--color-content2)] text-[var(--color-foreground)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-primary"
            />
            {searchInput && (
              <button
                onClick={clearSearch}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-[var(--color-text-muted)] hover:text-[var(--color-foreground)]"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <button
            onClick={handleSearch}
            className="px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            搜索
          </button>
        </div>
      </div>
      {searchQuery && (
        <div className="mb-4 text-sm text-[var(--color-text-muted)]">
          搜索结果："{searchQuery}" {!loading && `(${items.length} 条记录)`}
        </div>
      )}
      {loading ? (
        isSearching ? (
          // 搜索时的列表骨架屏
          <div className="space-y-2">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-[var(--color-content2)]">
                <div className="w-12 h-16 rounded-md bg-zinc-700 animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-48 bg-zinc-700 rounded animate-pulse" />
                  <div className="h-3 w-32 bg-zinc-700 rounded animate-pulse" />
                </div>
                <div className="space-y-1">
                  <div className="h-3 w-16 bg-zinc-700 rounded animate-pulse" />
                  <div className="h-3 w-20 bg-zinc-700 rounded animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <PosterGridSkeleton count={24} />
        )
      ) : items.length === 0 ? (
        <p className="text-center text-default-400 py-8">
          {searchQuery ? '未找到匹配的播放记录' : '暂无播放记录'}
        </p>
      ) : isSearching ? (
        // 搜索结果：列表展示
        <div className="space-y-2">
          {items.map((item, index) => (
            <HistoryListItem
              key={`search-${item.item_name}-${item.time}-${index}`}
              item={item}
            />
          ))}
        </div>
      ) : (
        // 默认：海报网格展示
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-4">
          {items.map((item, index) => (
            <PosterCard
              key={`recent-${item.item_name}-${item.time}-${index}`}
              title={item.show_name || item.name || item.item_name}
              posterUrl={item.poster_url}
              backdropUrl={item.backdrop_url}
              itemName={item.item_name}
              username={item.username}
              time={item.time}
              showEpisode
              overview={item.overview}
              client={item.client}
              device={item.device}
            />
          ))}
        </div>
      )}
    </Card>
  )
}
