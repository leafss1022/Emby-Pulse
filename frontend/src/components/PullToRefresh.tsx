import { useState, useRef, type ReactNode } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'
import { RefreshCw } from 'lucide-react'

interface PullToRefreshProps {
  onRefresh: () => Promise<void>
  children: ReactNode
}

export function PullToRefresh({ onRefresh, children }: PullToRefreshProps) {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const startY = useRef(0)
  const y = useMotionValue(0)

  const pullProgress = useTransform(y, [0, 100], [0, 1])
  const rotate = useTransform(y, [0, 100], [0, 360])
  const opacity = useTransform(y, [0, 50, 100], [0, 0.5, 1])
  const scale = useTransform(y, [0, 100], [0.5, 1])

  const handleTouchStart = (e: React.TouchEvent) => {
    if (containerRef.current?.scrollTop === 0) {
      startY.current = e.touches[0].clientY
    }
  }

  const handleTouchMove = (e: React.TouchEvent) => {
    if (isRefreshing) return
    if (containerRef.current?.scrollTop !== 0) return

    const currentY = e.touches[0].clientY
    const diff = currentY - startY.current

    if (diff > 0 && diff < 150) {
      y.set(diff)
    }
  }

  const handleTouchEnd = async () => {
    if (isRefreshing) return

    if (y.get() > 80) {
      setIsRefreshing(true)
      animate(y, 60, { duration: 0.2 })
      await onRefresh()
      setIsRefreshing(false)
    }

    animate(y, 0, { type: 'spring', stiffness: 400, damping: 30 })
  }

  return (
    <div
      ref={containerRef}
      className="h-full overflow-auto"
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Pull indicator */}
      <motion.div
        style={{ height: y, opacity }}
        className="flex items-center justify-center overflow-hidden"
      >
        <motion.div style={{ scale, rotate }}>
          <RefreshCw
            className={`w-6 h-6 text-primary ${isRefreshing ? 'animate-spin' : ''}`}
          />
        </motion.div>
      </motion.div>

      {/* Content */}
      <motion.div style={{ y: useTransform(pullProgress, [0, 1], [0, 0]) }}>
        {children}
      </motion.div>
    </div>
  )
}
