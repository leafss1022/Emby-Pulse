import ReactECharts from 'echarts-for-react'
import type { UserItem } from '@/types'
import { useTheme } from '@/contexts/ThemeContext'

interface UsersChartProps {
  data: UserItem[]
}

export function UsersChart({ data }: UsersChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const colors = {
    tooltip: {
      bg: isDark ? '#18181b' : '#ffffff',
      border: isDark ? '#27272a' : '#e4e4e7',
      text: isDark ? '#ECEDEE' : '#18181b',
    },
    axis: {
      label: isDark ? '#71717a' : '#71717a',
      yLabel: isDark ? '#a1a1aa' : '#52525b',
      split: isDark ? '#27272a' : '#f4f4f5',
    },
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: colors.tooltip.bg,
      borderColor: colors.tooltip.border,
      textStyle: { color: colors.tooltip.text, fontSize: 12 },
    },
    grid: { left: '3%', right: '10%', top: '3%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'value',
      name: '小时',
      nameTextStyle: { color: colors.axis.label },
      axisLine: { show: false },
      axisLabel: { color: colors.axis.label, fontSize: 11 },
      splitLine: { lineStyle: { color: colors.axis.split } },
    },
    yAxis: {
      type: 'category',
      data: data.map((d) => d.username).reverse(),
      axisLine: { show: false },
      axisLabel: { color: colors.axis.yLabel, fontSize: 11 },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        data: data.map((d) => d.duration_hours).reverse(),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#006FEE' },
              { offset: 1, color: '#338ef7' },
            ],
          },
          borderRadius: [0, 4, 4, 0],
        },
        barWidth: '60%',
      },
    ],
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: '100%', minHeight: 280 }}
      opts={{ renderer: 'canvas' }}
    />
  )
}
