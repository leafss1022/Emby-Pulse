import { useState, useEffect, useRef, type ReactNode } from 'react'

interface LazyItemProps {
  children: ReactNode
  placeholder?: ReactNode
  rootMargin?: string
  className?: string
}

/**
 * 懒加载包装组件
 * 使用 Intersection Observer 延迟渲染屏幕外的内容
 */
export function LazyItem({
  children,
  placeholder,
  rootMargin = '50px',
  className,
}: LazyItemProps) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    // 如果浏览器不支持 IntersectionObserver，直接显示
    if (!('IntersectionObserver' in window)) {
      setIsVisible(true)
      return
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      {
        rootMargin,
        threshold: 0,
      }
    )

    observer.observe(element)

    return () => observer.disconnect()
  }, [rootMargin])

  return (
    <div ref={ref} className={className}>
      {isVisible ? children : placeholder}
    </div>
  )
}
