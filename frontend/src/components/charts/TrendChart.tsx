import ReactECharts from 'echarts-for-react'
import type { TrendItem } from '@/types'
import { useTheme } from '@/contexts/ThemeContext'

interface TrendChartProps {
  data: TrendItem[]
}

export function TrendChart({ data }: TrendChartProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  const colors = {
    tooltip: {
      bg: isDark ? '#18181b' : '#ffffff',
      border: isDark ? '#27272a' : '#e4e4e7',
      text: isDark ? '#ECEDEE' : '#18181b',
    },
    axis: {
      line: isDark ? '#27272a' : '#e4e4e7',
      label: isDark ? '#71717a' : '#71717a',
      split: isDark ? '#27272a' : '#f4f4f5',
    },
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: colors.tooltip.bg,
      borderColor: colors.tooltip.border,
      textStyle: { color: colors.tooltip.text, fontSize: 12 },
    },
    legend: {
      data: ['播放次数', '时长(小时)'],
      textStyle: { color: colors.axis.label, fontSize: 12 },
      top: 0,
    },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.map((d) => d.date.slice(5)),
      axisLine: { lineStyle: { color: colors.axis.line } },
      axisLabel: { color: colors.axis.label, fontSize: 11 },
      axisTick: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: '次数',
        nameTextStyle: { color: colors.axis.label, fontSize: 11 },
        axisLine: { show: false },
        axisLabel: { color: colors.axis.label, fontSize: 11 },
        splitLine: { lineStyle: { color: colors.axis.split } },
      },
      {
        type: 'value',
        name: '小时',
        nameTextStyle: { color: colors.axis.label, fontSize: 11 },
        axisLine: { show: false },
        axisLabel: { color: colors.axis.label, fontSize: 11 },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '播放次数',
        type: 'bar',
        data: data.map((d) => d.plays),
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#006FEE' },
              { offset: 1, color: '#004493' },
            ],
          },
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: '50%',
      },
      {
        name: '时长(小时)',
        type: 'line',
        yAxisIndex: 1,
        data: data.map((d) => d.duration_hours),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#17c964', width: 2 },
        itemStyle: { color: '#17c964' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(23, 201, 100, 0.3)' },
              { offset: 1, color: 'rgba(23, 201, 100, 0)' },
            ],
          },
        },
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
