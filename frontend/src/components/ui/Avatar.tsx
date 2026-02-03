import { cn } from '@/lib/utils'

const COLORS = [
  'bg-primary',
  'bg-success',
  'bg-warning',
  'bg-danger',
  'bg-zinc-600',
]

interface AvatarProps {
  name: string
  index?: number
  className?: string
}

export function Avatar({ name, index = 0, className }: AvatarProps) {
  const colorClass = COLORS[index % COLORS.length]
  const initial = name.charAt(0).toUpperCase()

  return (
    <div
      className={cn(
        'w-10 h-10 rounded-xl flex items-center justify-center font-semibold text-base',
        colorClass,
        className
      )}
    >
      {initial}
    </div>
  )
}
