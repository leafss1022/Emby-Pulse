import { cn } from '@/lib/utils'
import type { ReactNode } from 'react'

interface ChipProps {
  children: ReactNode
  active?: boolean
  onClick?: () => void
  className?: string
}

export function Chip({ children, active, onClick, className }: ChipProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'rounded-full px-3.5 py-1.5 text-sm font-medium transition-all duration-200 border border-transparent',
        active ? 'bg-primary text-white' : 'bg-content2 hover:bg-content3',
        className
      )}
    >
      {children}
    </button>
  )
}
