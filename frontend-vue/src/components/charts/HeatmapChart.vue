<template>
  <div class="heatmap-chart">
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
import { HeatmapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'
import type { HourlyItem } from '@/types'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
])

interface Props {
  data?: HourlyItem[]
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  height: '400px',
})

const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)

const chartOption = computed<EChartsOption>(() => {
  // 将数据转换为 ECharts 需要的格式 [hour, day, value]
  const heatmapData = props.data.map((item) => [item.hour, item.day, item.count])

  // 计算最大值用于视觉映射
  const maxValue = Math.max(...props.data.map((item) => item.count), 1)

  return {
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const hour = hours[params.data[0]]
        const day = days[params.data[1]]
        const count = params.data[2]
        return `${day} ${hour}<br/>播放次数: ${count}`
      },
    },
    grid: {
      left: '10%',
      right: '5%',
      top: '5%',
      bottom: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: {
        show: true,
      },
      axisLabel: {
        color: '#ccc',
        interval: 2, // 每隔2小时显示一个标签
      },
      axisLine: {
        lineStyle: {
          color: '#444',
        },
      },
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: {
        show: true,
      },
      axisLabel: {
        color: '#ccc',
      },
      axisLine: {
        lineStyle: {
          color: '#444',
        },
      },
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0',
      textStyle: {
        color: '#ccc',
      },
      inRange: {
        color: ['#1a237e', '#1976d2', '#42a5f5', '#81d4fa'],
      },
    },
    series: [
      {
        name: '播放次数',
        type: 'heatmap',
        data: heatmapData,
        label: {
          show: false,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }
})
</script>

<style scoped>
.heatmap-chart {
  width: 100%;
}
</style>
