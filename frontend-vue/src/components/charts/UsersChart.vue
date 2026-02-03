<template>
  <div class="users-chart">
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
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'
import type { UserItem } from '@/types'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
])

interface Props {
  data?: UserItem[]
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  height: '400px',
})

const chartOption = computed<EChartsOption>(() => {
  // 按播放时长排序
  const sortedData = [...props.data].sort((a, b) => b.duration_hours - a.duration_hours)

  const usernames = sortedData.map((item) => item.username)
  const durations = sortedData.map((item) => item.duration_hours)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const data = params[0]
        return `${data.name}<br/>播放时长: ${data.value.toFixed(1)} 小时`
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
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
        lineStyle: {
          color: '#333',
        },
      },
    },
    yAxis: {
      type: 'category',
      data: usernames,
      axisLabel: {
        color: '#ccc',
      },
      axisLine: {
        lineStyle: {
          color: '#444',
        },
      },
    },
    series: [
      {
        name: '播放时长',
        type: 'bar',
        data: durations,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: '#1976d2' },
              { offset: 1, color: '#42a5f5' },
            ],
          },
          borderRadius: [0, 4, 4, 0],
        },
        emphasis: {
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                { offset: 0, color: '#1565c0' },
                { offset: 1, color: '#1976d2' },
              ],
            },
          },
        },
      },
    ],
  }
})
</script>

<style scoped>
.users-chart {
  width: 100%;
}
</style>
