import { cn } from '@/lib/utils'
import type { ReactNode, CSSProperties } from 'react'
import { AnimatedNumber } from './AnimatedNumber'

interface CardProps {
  children: ReactNode
  className?: string
  hover?: boolean
  style?: CSSProperties
}

export function Card({ children, className, hover = true, style }: CardProps) {
  return (
    <div
      className={cn(
        'bg-content1 rounded-2xl border border-[var(--color-border)]',
        'shadow-[0_2px_8px_rgba(0,0,0,0.08)]',
        'dark:shadow-[0_2px_12px_rgba(0,0,0,0.3)]',
        'transition-all duration-150 ease-out',
        hover && 'cursor-pointer hover:shadow-[0_4px_16px_rgba(0,0,0,0.12)] hover:-translate-y-0.5 active:scale-[0.97]',
        'dark:hover:shadow-[0_4px_20px_rgba(0,0,0,0.4)]',
        className
      )}
      style={style}
    >
      {children}
    </div>
  )
}

interface StatCardProps {
  icon: ReactNode
  iconClassName: string
  label: string
  value: string | number
  suffix?: string
  animate?: boolean
  decimals?: number
}

export function StatCard({ icon, iconClassName, label, value, suffix, animate = true, decimals = 0 }: StatCardProps) {
  const numericValue = typeof value === 'number' ? value : parseFloat(value.toString().replace(/,/g, ''))
  const isNumeric = !isNaN(numericValue)

  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-2xl bg-content1 border border-[var(--color-border)] p-5 flex flex-col',
        'shadow-[0_2px_8px_rgba(0,0,0,0.08)]',
        'dark:shadow-[0_2px_12px_rgba(0,0,0,0.3)] dark:bg-gradient-to-br dark:from-content1 dark:to-[var(--color-card-gradient-end)]',
        'transition-all duration-150 ease-out cursor-pointer',
        'hover:shadow-[0_4px_16px_rgba(0,0,0,0.12)] hover:-translate-y-0.5',
        'dark:hover:shadow-[0_4px_20px_rgba(0,0,0,0.4)]',
        'active:scale-[0.97]'
      )}
    >
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[var(--color-border)] to-transparent" />
      <div className="flex items-center gap-3 mb-3">
        <div className={cn('w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0', iconClassName)}>
          {icon}
        </div>
        <span className="text-sm text-[var(--color-text-muted)]">{label}</span>
      </div>
      <div className="mt-auto">
        <p className="text-3xl font-bold">
          {animate && isNumeric ? (
            <AnimatedNumber value={numericValue} decimals={decimals} />
          ) : (
            value
          )}
        </p>
        {suffix ? (
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">{suffix}</p>
        ) : (
          <p className="text-xs text-[var(--color-text-secondary)] mt-1 invisible">placeholder</p>
        )}
      </div>
    </div>
  )
}
