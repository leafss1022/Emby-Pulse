import ReactECharts from 'echarts-for-react'
import { useTheme } from '@/contexts/ThemeContext'

interface PieChartProps {
  data: Array<{ name: string; value: number }>
  colors?: string[]
}

const DEFAULT_COLORS = ['#006FEE', '#17c964', '#f5a524', '#f31260', '#71717a']

export function PieChart({ data, colors = DEFAULT_COLORS }: PieChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const chartColors = {
    tooltip: {
      bg: isDark ? '#18181b' : '#ffffff',
      border: isDark ? '#27272a' : '#e4e4e7',
      text: isDark ? '#ECEDEE' : '#18181b',
    },
    label: isDark ? '#a1a1aa' : '#52525b',
    labelLine: isDark ? '#3f3f46' : '#d4d4d8',
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: chartColors.tooltip.bg,
      borderColor: chartColors.tooltip.border,
      textStyle: { color: chartColors.tooltip.text, fontSize: 12 },
    },
    series: [
      {
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['50%', '50%'],
        label: { show: true, color: chartColors.label, fontSize: 11, formatter: '{b}' },
        labelLine: { lineStyle: { color: chartColors.labelLine } },
        data: data.map((item, i) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: colors[i % colors.length] },
        })),
      },
    ],
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: '100%', minHeight: 240 }}
      opts={{ renderer: 'canvas' }}
    />
  )
}
