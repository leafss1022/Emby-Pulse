import { useState, useMemo } from 'react'
import { Card, Skeleton } from '@/components/ui'
import { useFavorites } from '@/hooks/useStats'
import { useServer } from '@/contexts/ServerContext'
import { Heart, Users, Film, Tv, ChevronDown, ChevronUp, Search, User } from 'lucide-react'
import type { FavoriteItem, UserFavorites, UserFavoriteItem } from '@/types'

type ViewMode = 'users' | 'ranking'
type FilterType = 'all' | 'Movie' | 'Series'

export function Favorites() {
  const { currentServer } = useServer()
  // 将 server_id 作为参数传入，确保服务器切换时数据会刷新
  const { data, loading } = useFavorites({ server_id: currentServer?.id || '' })
  const [viewMode, setViewMode] = useState<ViewMode>('users')
  const [expandedUsers, setExpandedUsers] = useState<Set<string>>(new Set())
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  const [filter, setFilter] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const items = data?.items ?? []
  const usersFavorites = data?.users_favorites ?? []
  const totalUsers = data?.total_users ?? 0
  const usersWithFavorites = data?.users_with_favorites ?? 0

  // 搜索和筛选逻辑
  const filteredUsersFavorites = useMemo(() => {
    return usersFavorites
      .map(user => {
        let filtered = user.favorites
        // 类型筛选
        if (filter !== 'all') {
          filtered = filtered.filter(item => item.type === filter)
        }
        // 搜索筛选
        if (searchQuery.trim()) {
          const query = searchQuery.toLowerCase()
          filtered = filtered.filter(item =>
            item.name.toLowerCase().includes(query) ||
            (item.series_name && item.series_name.toLowerCase().includes(query))
          )
        }
        return { ...user, favorites: filtered, favorite_count: filtered.length }
      })
      .filter(user => {
        // 如果有搜索词，只显示有匹配结果的用户
        if (searchQuery.trim()) {
          return user.favorites.length > 0
        }
        // 如果搜索用户名
        if (searchQuery.trim() && user.username.toLowerCase().includes(searchQuery.toLowerCase())) {
          return true
        }
        return user.favorites.length > 0
      })
  }, [usersFavorites, filter, searchQuery])

  const filteredItems = useMemo(() => {
    let filtered = items
    // 类型筛选
    if (filter !== 'all') {
      filtered = filtered.filter(item => item.type === filter)
    }
    // 搜索筛选
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(item =>
        item.name.toLowerCase().includes(query) ||
        (item.series_name && item.series_name.toLowerCase().includes(query)) ||
        item.users.some(u => u.username.toLowerCase().includes(query))
      )
    }
    return filtered
  }, [items, filter, searchQuery])

  const toggleUserExpand = (userId: string) => {
    setExpandedUsers(prev => {
      const next = new Set(prev)
      if (next.has(userId)) {
        next.delete(userId)
      } else {
        next.add(userId)
      }
      return next
    })
  }

  const toggleItemExpand = (itemId: string) => {
    setExpandedItems(prev => {
      const next = new Set(prev)
      if (next.has(itemId)) {
        next.delete(itemId)
      } else {
        next.add(itemId)
      }
      return next
    })
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'Movie':
        return <Film className="w-4 h-4" />
      case 'Series':
        return <Tv className="w-4 h-4" />
      default:
        return <Heart className="w-4 h-4" />
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'Movie':
        return '电影'
      case 'Series':
        return '剧集'
      default:
        return type
    }
  }

  return (
    <div className="space-y-4">
      {/* 统计概览 */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-pink-500/10">
              <Heart className="w-5 h-5 text-pink-500" />
            </div>
            <div>
              <p className="text-xs text-default-400">收藏内容</p>
              {loading ? (
                <Skeleton className="h-6 w-12 mt-1" />
              ) : (
                <p className="text-xl font-semibold">{items.length}</p>
              )}
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10">
              <Users className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-xs text-default-400">有收藏的用户</p>
              {loading ? (
                <Skeleton className="h-6 w-12 mt-1" />
              ) : (
                <p className="text-xl font-semibold">{usersWithFavorites} / {totalUsers}</p>
              )}
            </div>
          </div>
        </Card>
        <Card className="p-4 col-span-2 sm:col-span-1">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10">
              <Film className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-xs text-default-400">电影 / 剧集</p>
              {loading ? (
                <Skeleton className="h-6 w-16 mt-1" />
              ) : (
                <p className="text-xl font-semibold">
                  {items.filter(i => i.type === 'Movie').length} / {items.filter(i => i.type === 'Series').length}
                </p>
              )}
            </div>
          </div>
        </Card>
      </div>

      {/* 主内容区 */}
      <Card className="p-4 sm:p-5" hover={false}>
        {/* 顶部控制栏 */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 relative z-20">
          {/* 视图切换 Tab */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setViewMode('users')}
              className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 cursor-pointer select-none relative z-10 ${
                viewMode === 'users'
                  ? 'bg-primary text-white'
                  : 'bg-default-100 hover:bg-default-200'
              }`}
            >
              <User className="w-4 h-4" />
              按用户
            </button>
            <button
              type="button"
              onClick={() => setViewMode('ranking')}
              className={`px-4 py-2 text-sm rounded-lg transition-colors flex items-center gap-2 cursor-pointer select-none relative z-10 ${
                viewMode === 'ranking'
                  ? 'bg-primary text-white'
                  : 'bg-default-100 hover:bg-default-200'
              }`}
            >
              <Heart className="w-4 h-4" />
              热门榜单
            </button>
          </div>

          {/* 类型筛选 */}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setFilter('all')}
              className={`px-3 py-1 text-xs rounded-full transition-colors cursor-pointer select-none relative z-10 ${
                filter === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-default-100 hover:bg-default-200'
              }`}
            >
              全部
            </button>
            <button
              type="button"
              onClick={() => setFilter('Movie')}
              className={`px-3 py-1 text-xs rounded-full transition-colors cursor-pointer select-none relative z-10 ${
                filter === 'Movie'
                  ? 'bg-primary text-white'
                  : 'bg-default-100 hover:bg-default-200'
              }`}
            >
              电影
            </button>
            <button
              type="button"
              onClick={() => setFilter('Series')}
              className={`px-3 py-1 text-xs rounded-full transition-colors cursor-pointer select-none relative z-10 ${
                filter === 'Series'
                  ? 'bg-primary text-white'
                  : 'bg-default-100 hover:bg-default-200'
              }`}
            >
              剧集
            </button>
          </div>
        </div>

        {/* 搜索框 */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-default-400" />
          <input
            type="text"
            placeholder={viewMode === 'users' ? '搜索用户或内容...' : '搜索内容或用户...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-default-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        {/* 内容列表 */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-lg" />
            ))}
          </div>
        ) : viewMode === 'users' ? (
          // 按用户视图
          filteredUsersFavorites.length === 0 ? (
            <p className="text-center text-default-400 py-8">
              {searchQuery ? '没有找到匹配的结果' : '暂无收藏数据'}
            </p>
          ) : (
            <div className="space-y-3">
              {filteredUsersFavorites.map((user) => (
                <UserFavoritesCard
                  key={user.user_id}
                  user={user}
                  expanded={expandedUsers.has(user.user_id)}
                  onToggle={() => toggleUserExpand(user.user_id)}
                  getTypeIcon={getTypeIcon}
                  getTypeLabel={getTypeLabel}
                  serverId={currentServer?.id}
                />
              ))}
            </div>
          )
        ) : (
          // 热门榜单视图
          filteredItems.length === 0 ? (
            <p className="text-center text-default-400 py-8">
              {searchQuery ? '没有找到匹配的结果' : '暂无收藏数据'}
            </p>
          ) : (
            <div className="space-y-3">
              {filteredItems.map((item, index) => (
                <FavoriteItemCard
                  key={item.item_id}
                  item={item}
                  rank={index + 1}
                  expanded={expandedItems.has(item.item_id)}
                  onToggle={() => toggleItemExpand(item.item_id)}
                  getTypeIcon={getTypeIcon}
                  getTypeLabel={getTypeLabel}
                  serverId={currentServer?.id}
                />
              ))}
            </div>
          )
        )}
      </Card>
    </div>
  )
}

// 用户收藏卡片组件
interface UserFavoritesCardProps {
  user: UserFavorites
  expanded: boolean
  onToggle: () => void
  getTypeIcon: (type: string) => React.ReactNode
  getTypeLabel: (type: string) => string
  serverId?: string
}

function UserFavoritesCard({ user, expanded, onToggle, getTypeIcon, getTypeLabel, serverId }: UserFavoritesCardProps) {
  const movieCount = user.favorites.filter(f => f.type === 'Movie').length
  const seriesCount = user.favorites.filter(f => f.type === 'Series').length
  // 构建带 server_id 的海报 URL
  const getPosterUrl = (posterId: string, maxHeight: number, maxWidth: number) => {
    const params = new URLSearchParams({ maxHeight: String(maxHeight), maxWidth: String(maxWidth) })
    if (serverId) params.set('server_id', serverId)
    return `/api/poster/${posterId}?${params.toString()}`
  }
  // 显示前 5 个海报
  const previewItems = user.favorites.slice(0, 5)

  return (
    <div className="bg-default-50 rounded-lg overflow-hidden">
      <div
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-default-100 transition-colors"
        onClick={onToggle}
      >
        {/* 用户头像 */}
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0">
          <span className="text-white font-semibold text-sm">
            {user.username.charAt(0).toUpperCase()}
          </span>
        </div>

        {/* 用户信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-sm">{user.username}</h4>
            <span className="text-xs text-default-400">
              收藏 {user.favorite_count} 部
            </span>
          </div>
          <div className="flex items-center gap-3 mt-1 text-xs text-default-400">
            {movieCount > 0 && (
              <span className="flex items-center gap-1">
                <Film className="w-3 h-3" />
                {movieCount} 电影
              </span>
            )}
            {seriesCount > 0 && (
              <span className="flex items-center gap-1">
                <Tv className="w-3 h-3" />
                {seriesCount} 剧集
              </span>
            )}
          </div>
        </div>

        {/* 海报预览 */}
        <div className="hidden sm:flex items-center gap-1">
          {previewItems.map((item) => {
            const posterId = item.series_id || item.item_id
            return (
              <div
                key={item.item_id}
                className="w-8 h-12 rounded overflow-hidden bg-default-200 flex-shrink-0"
              >
                {item.has_poster ? (
                  <img
                    src={getPosterUrl(posterId, 192, 128)}
                    alt={item.name}
                    className="w-full h-full object-cover"
                    loading="lazy"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    {getTypeIcon(item.type)}
                  </div>
                )}
              </div>
            )
          })}
          {user.favorites.length > 5 && (
            <div className="w-8 h-12 rounded bg-default-200 flex items-center justify-center text-xs text-default-400">
              +{user.favorites.length - 5}
            </div>
          )}
        </div>

        {/* 展开图标 */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-pink-500">
            <Heart className="w-4 h-4 fill-current" />
            <span className="font-semibold">{user.favorite_count}</span>
          </div>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-default-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-default-400" />
          )}
        </div>
      </div>

      {/* 展开的收藏列表 */}
      {expanded && (
        <div className="px-3 pb-3 pt-0">
          <div className="bg-default-100 rounded-lg p-3">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
              {user.favorites.map((item) => (
                <UserFavoriteItemCard
                  key={item.item_id}
                  item={item}
                  getTypeIcon={getTypeIcon}
                  getTypeLabel={getTypeLabel}
                  serverId={serverId}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// 用户收藏的单个项目卡片
interface UserFavoriteItemCardProps {
  item: UserFavoriteItem
  getTypeIcon: (type: string) => React.ReactNode
  getTypeLabel: (type: string) => string
  serverId?: string
}

function UserFavoriteItemCard({ item, getTypeIcon, getTypeLabel, serverId }: UserFavoriteItemCardProps) {
  const posterId = item.series_id || item.item_id
  // 构建带 server_id 的海报 URL
  const getPosterUrl = () => {
    const params = new URLSearchParams({ maxHeight: '720', maxWidth: '480' })
    if (serverId) params.set('server_id', serverId)
    return `/api/poster/${posterId}?${params.toString()}`
  }

  return (
    <div className="bg-default-50 rounded-lg overflow-hidden">
      {/* 海报 */}
      <div className="aspect-[2/3] bg-default-200 relative">
        {item.has_poster ? (
          <img
            src={getPosterUrl()}
            alt={item.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {getTypeIcon(item.type)}
          </div>
        )}
        {/* 类型标签 */}
        <div className="absolute top-1 right-1 px-1.5 py-0.5 bg-black/60 rounded text-[10px] text-white">
          {getTypeLabel(item.type)}
        </div>
      </div>
      {/* 信息 */}
      <div className="p-2">
        <p className="text-xs font-medium truncate" title={item.name}>
          {item.name}
        </p>
        {item.year && (
          <p className="text-[10px] text-default-400">{item.year}</p>
        )}
        {item.series_name && (
          <p className="text-[10px] text-default-400 truncate" title={item.series_name}>
            {item.series_name}
          </p>
        )}
      </div>
    </div>
  )
}

// 热门榜单项目卡片（保留原有设计）
interface FavoriteItemCardProps {
  item: FavoriteItem
  rank: number
  expanded: boolean
  onToggle: () => void
  getTypeIcon: (type: string) => React.ReactNode
  getTypeLabel: (type: string) => string
  serverId?: string
}

function FavoriteItemCard({ item, rank, expanded, onToggle, getTypeIcon, getTypeLabel, serverId }: FavoriteItemCardProps) {
  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'text-yellow-500'
      case 2:
        return 'text-gray-400'
      case 3:
        return 'text-amber-600'
      default:
        return 'text-default-400'
    }
  }

  const posterId = item.series_id || item.item_id
  // 构建带 server_id 的海报 URL
  const getPosterUrl = () => {
    const params = new URLSearchParams({ maxHeight: '256', maxWidth: '192' })
    if (serverId) params.set('server_id', serverId)
    return `/api/poster/${posterId}?${params.toString()}`
  }

  return (
    <div className="bg-default-50 rounded-lg overflow-hidden">
      <div
        className="flex items-center gap-3 p-3 cursor-pointer hover:bg-default-100 transition-colors"
        onClick={onToggle}
      >
        {/* 排名 */}
        <div className={`w-8 text-center font-bold ${getRankColor(rank)}`}>
          #{rank}
        </div>

        {/* 海报 */}
        <div className="w-12 h-16 flex-shrink-0 rounded overflow-hidden bg-default-200">
          {item.has_poster ? (
            <img
              src={getPosterUrl()}
              alt={item.name}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              {getTypeIcon(item.type)}
            </div>
          )}
        </div>

        {/* 信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium text-sm truncate">{item.name}</h4>
            {item.year && (
              <span className="text-xs text-default-400">({item.year})</span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="inline-flex items-center gap-1 text-xs text-default-400">
              {getTypeIcon(item.type)}
              {getTypeLabel(item.type)}
            </span>
            {item.series_name && (
              <span className="text-xs text-default-400 truncate">
                {item.series_name}
              </span>
            )}
          </div>
        </div>

        {/* 收藏人数 */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 text-pink-500">
            <Heart className="w-4 h-4 fill-current" />
            <span className="font-semibold">{item.favorite_count}</span>
          </div>
          {expanded ? (
            <ChevronUp className="w-4 h-4 text-default-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-default-400" />
          )}
        </div>
      </div>

      {/* 展开的用户列表 */}
      {expanded && (
        <div className="px-3 pb-3 pt-0">
          <div className="bg-default-100 rounded-lg p-3">
            <p className="text-xs text-default-400 mb-2">收藏用户：</p>
            <div className="flex flex-wrap gap-2">
              {item.users.map(user => (
                <span
                  key={user.user_id}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-default-200 rounded-full text-xs"
                >
                  <Users className="w-3 h-3" />
                  {user.username}
                </span>
              ))}
            </div>
            {item.overview && (
              <p className="text-xs text-default-400 mt-3 line-clamp-3">
                {item.overview}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
