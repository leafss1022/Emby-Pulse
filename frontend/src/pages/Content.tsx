import { Card, PosterCard, PosterGridSkeleton } from '@/components/ui'
import { useTopShows, useTopContent } from '@/hooks/useStats'
import type { FilterParams } from '@/services/api'

interface ContentProps {
  filterParams: FilterParams
}

export function Content({ filterParams }: ContentProps) {
  const { data: showsData, loading: showsLoading } = useTopShows(filterParams, 16)
  const { data: contentData, loading: contentLoading } = useTopContent(filterParams, 18)

  const shows = showsData?.top_shows ?? []
  const contents = contentData?.top_content ?? []

  return (
    <div className="space-y-4">
      {/* 热门剧集 */}
      <Card className="p-5">
        <h3 className="font-semibold mb-4">热门剧集</h3>
        {showsLoading ? (
          <PosterGridSkeleton count={16} />
        ) : shows.length === 0 ? (
          <p className="text-center text-default-400 py-8">暂无数据</p>
        ) : (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {shows.map((item, index) => (
              <PosterCard
                key={`show-${item.show_name}-${index}`}
                title={item.show_name}
                posterUrl={item.poster_url}
                backdropUrl={item.backdrop_url}
                rank={index + 1}
                playCount={item.play_count}
                durationHours={item.duration_hours}
                overview={item.overview}
              />
            ))}
          </div>
        )}
      </Card>

      {/* 播放排行 */}
      <Card className="p-5">
        <h3 className="font-semibold mb-4">播放排行</h3>
        {contentLoading ? (
          <PosterGridSkeleton count={18} />
        ) : contents.length === 0 ? (
          <p className="text-center text-default-400 py-8">暂无数据</p>
        ) : (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {contents.map((item, index) => (
              <PosterCard
                key={`content-${item.show_name || item.name}-${index}`}
                title={item.show_name || item.name || item.item_name}
                posterUrl={item.poster_url}
                backdropUrl={item.backdrop_url}
                itemName={item.item_name}
                rank={index + 1}
                playCount={item.play_count}
                durationHours={item.duration_hours}
                overview={item.overview}
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
