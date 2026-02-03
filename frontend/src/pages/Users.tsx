import { Card, Avatar, ChartSkeleton, UserListSkeleton } from '@/components/ui'
import { UsersChart } from '@/components/charts'
import { useUsers } from '@/hooks/useStats'
import { formatDate } from '@/lib/utils'
import type { FilterParams } from '@/services/api'

interface UsersProps {
  filterParams: FilterParams
}

export function Users({ filterParams }: UsersProps) {
  const { data: usersData, loading } = useUsers(filterParams)

  return (
    <div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 items-stretch">
        <Card className="p-5 flex flex-col" style={{ minHeight: 360 }}>
          <h3 className="font-semibold mb-4">用户观看时长</h3>
          <div className="flex-1" style={{ minHeight: 280 }}>
            {loading ? <ChartSkeleton /> : usersData && <UsersChart data={usersData.users} />}
          </div>
        </Card>

        <Card className="p-5 flex flex-col" style={{ minHeight: 360 }}>
          <h3 className="font-semibold mb-4">用户详情</h3>
          <div className="space-y-3 flex-1 overflow-y-auto pr-1">
            {loading ? (
              <UserListSkeleton />
            ) : (
              usersData?.users.map((user, index) => (
                <div
                  key={user.username}
                  className="flex items-center justify-between p-3 bg-content1 rounded-[10px] transition-colors hover:bg-content2"
                >
                  <div className="flex items-center gap-3">
                    <Avatar name={user.username} index={index} />
                    <div>
                      <p className="font-medium text-sm">{user.username}</p>
                      <p className="text-xs text-[var(--color-text-secondary)]">{user.play_count} 次播放</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-primary text-sm">{user.duration_hours}h</p>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      {user.last_play ? formatDate(user.last_play) : '-'}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}
