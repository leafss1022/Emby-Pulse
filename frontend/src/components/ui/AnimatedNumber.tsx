import { useEffect, useState } from 'react'
import { motion, useSpring, useTransform } from 'framer-motion'

interface AnimatedNumberProps {
  value: number
  duration?: number
  formatFn?: (n: number) => string
  decimals?: number  // 保留小数位数
}

export function AnimatedNumber({
  value,
  duration = 1,
  formatFn,
  decimals = 0,
}: AnimatedNumberProps) {
  const spring = useSpring(0, { duration: duration * 1000 })

  // 根据 decimals 决定如何格式化
  const defaultFormatFn = (n: number) => {
    if (decimals > 0) {
      return n.toFixed(decimals)
    }
    return Math.round(n).toLocaleString()
  }

  const actualFormatFn = formatFn || defaultFormatFn

  const display = useTransform(spring, (current) => actualFormatFn(current))
  const [displayValue, setDisplayValue] = useState(actualFormatFn(0))

  useEffect(() => {
    spring.set(value)
  }, [spring, value])

  useEffect(() => {
    return display.on('change', (v) => setDisplayValue(v))
  }, [display])

  return <motion.span>{displayValue}</motion.span>
}
