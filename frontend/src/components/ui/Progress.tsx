import { cn } from '@/lib/utils'

interface ProgressProps {
  value: number
  className?: string
}

export function Progress({ value, className }: ProgressProps) {
  return (
    <div className={cn('h-1 bg-content2 rounded overflow-hidden', className)}>
      <div
        className="h-full bg-gradient-to-r from-primary to-primary-500 rounded transition-all duration-500"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}
