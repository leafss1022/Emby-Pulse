import { Card, StatCard, StatCardSkeleton, ChartSkeleton } from '@/components/ui'
import { TrendChart, HeatmapChart } from '@/components/charts'
import { useOverview, useTrend, useHourly } from '@/hooks/useStats'
import { formatNumber } from '@/lib/utils'
import { PlayCircle, Clock, Users, Film } from 'lucide-react'
import type { FilterParams } from '@/services/api'

interface OverviewProps {
  filterParams: FilterParams
}

export function Overview({ filterParams }: OverviewProps) {
  const { data: overview, loading: overviewLoading } = useOverview(filterParams)
  const { data: trend, loading: trendLoading } = useTrend(filterParams)
  const { data: hourly, loading: hourlyLoading } = useHourly(filterParams)

  return (
    <div>
      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {overviewLoading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            <StatCard
              icon={<PlayCircle className="w-5 h-5" />}
              iconClassName="bg-primary/20 text-primary"
              label="播放次数"
              value={overview ? formatNumber(overview.total_plays) : '--'}
            />
            <StatCard
              icon={<Clock className="w-5 h-5" />}
              iconClassName="bg-warning/20 text-warning"
              label="播放时长"
              value={overview ? overview.total_duration_hours : '--'}
              suffix="小时"
              decimals={2}
            />
            <StatCard
              icon={<Users className="w-5 h-5" />}
              iconClassName="bg-success/20 text-success"
              label="活跃用户"
              value={overview ? overview.unique_users : '--'}
            />
            <StatCard
              icon={<Film className="w-5 h-5" />}
              iconClassName="bg-danger/20 text-danger"
              label="观看内容"
              value={overview ? overview.unique_items : '--'}
            />
          </>
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 items-stretch">
        <Card className="lg:col-span-2 p-5 flex flex-col" style={{ minHeight: 360 }}>
          <h3 className="font-semibold mb-4">播放趋势</h3>
          <div className="flex-1" style={{ minHeight: 280 }}>
            {trendLoading ? <ChartSkeleton /> : trend && <TrendChart data={trend.trend} />}
          </div>
        </Card>
        <Card className="p-5 flex flex-col" style={{ minHeight: 360 }}>
          <h3 className="font-semibold mb-4">活跃时段</h3>
          <div className="flex-1" style={{ minHeight: 280 }}>
            {hourlyLoading ? <ChartSkeleton /> : hourly && <HeatmapChart data={hourly.hourly} />}
          </div>
        </Card>
      </div>
    </div>
  )
}
