<template>
  <div class="trend-chart">
    <v-chart
      :option="chartOption"
      :autoresize="true"
      :style="{ height: height, width: '100%' }"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'
import type { TrendItem } from '@/types'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
])

interface Props {
  data?: TrendItem[]
  height?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  height: '400px',
  loading: false,
})

const chartOption = computed<EChartsOption>(() => {
  const dates = props.data.map((item) => item.date)
  const plays = props.data.map((item) => item.plays)
  const durations = props.data.map((item) => item.duration_hours)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
    },
    legend: {
      data: ['播放次数', '播放时长'],
      textStyle: {
        color: '#ccc',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        color: '#ccc',
      },
      axisLine: {
        lineStyle: {
          color: '#444',
        },
      },
    },
    yAxis: [
      {
        type: 'value',
        name: '播放次数',
        nameTextStyle: {
          color: '#ccc',
        },
        axisLabel: {
          color: '#ccc',
        },
        axisLine: {
          lineStyle: {
            color: '#444',
          },
        },
        splitLine: {
          lineStyle: {
            color: '#333',
          },
        },
      },
      {
        type: 'value',
        name: '播放时长 (小时)',
        nameTextStyle: {
          color: '#ccc',
        },
        axisLabel: {
          color: '#ccc',
        },
        axisLine: {
          lineStyle: {
            color: '#444',
          },
        },
        splitLine: {
          show: false,
        },
      },
    ],
    series: [
      {
        name: '播放次数',
        type: 'line',
        data: plays,
        smooth: true,
        itemStyle: {
          color: '#1976d2',
        },
        areaStyle: {
          opacity: 0.3,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(25, 118, 210, 0.5)' },
              { offset: 1, color: 'rgba(25, 118, 210, 0.1)' },
            ],
          },
        },
      },
      {
        name: '播放时长',
        type: 'line',
        yAxisIndex: 1,
        data: durations,
        smooth: true,
        itemStyle: {
          color: '#4CAF50',
        },
        areaStyle: {
          opacity: 0.3,
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(76, 175, 80, 0.5)' },
              { offset: 1, color: 'rgba(76, 175, 80, 0.1)' },
            ],
          },
        },
      },
    ],
  }
})
</script>

<style scoped>
.trend-chart {
  width: 100%;
}
</style>
