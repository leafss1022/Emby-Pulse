import type { CSSProperties } from 'react'
import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
  style?: CSSProperties
}

export function Skeleton({ className, style }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-lg bg-content2',
        className
      )}
      style={style}
    />
  )
}

export function StatCardSkeleton() {
  return (
    <div className="relative overflow-hidden rounded-[14px] border border-[var(--color-border-light)] bg-gradient-to-br from-content1 to-[var(--color-card-gradient-end)] p-5 flex flex-col">
      <div className="flex items-center gap-3 mb-3">
        <Skeleton className="w-9 h-9 rounded-[10px]" />
        <Skeleton className="h-4 w-16" />
      </div>
      <div className="mt-auto">
        <Skeleton className="h-9 w-24 mb-1" />
        <Skeleton className="h-3 w-12" />
      </div>
    </div>
  )
}

export function PosterCardSkeleton() {
  return (
    <div className="rounded-xl overflow-hidden bg-content1 aspect-[2/3]">
      <Skeleton className="w-full h-full rounded-none" />
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="w-full h-full min-h-[280px] flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="flex items-end gap-2 h-32">
          {[40, 65, 45, 80, 55, 70, 50].map((h, i) => (
            <Skeleton
              key={i}
              className="w-6 rounded-t"
              style={{ height: `${h}%` }}
            />
          ))}
        </div>
        <Skeleton className="h-3 w-32" />
      </div>
    </div>
  )
}

export function UserListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex items-center justify-between p-3 bg-content1 rounded-[10px]">
          <div className="flex items-center gap-3">
            <Skeleton className="w-10 h-10 rounded-xl" />
            <div>
              <Skeleton className="h-4 w-20 mb-1" />
              <Skeleton className="h-3 w-14" />
            </div>
          </div>
          <div className="text-right">
            <Skeleton className="h-4 w-10 mb-1" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function PosterGridSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <PosterCardSkeleton key={i} />
      ))}
    </div>
  )
}
