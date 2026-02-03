<template>
  <div class="pie-chart">
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
import { PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import type { EChartsOption } from 'echarts'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
])

interface DataItem {
  name: string
  value: number
}

interface Props {
  data?: DataItem[]
  title?: string
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  height: '400px',
})

const chartOption = computed<EChartsOption>(() => {
  return {
    title: {
      text: props.title,
      left: 'center',
      top: '5',
      textStyle: {
        color: '#ccc',
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: {
      orient: 'horizontal',
      bottom: '5',
      left: 'center',
      textStyle: {
        color: '#ccc',
        fontSize: 11,
      },
      type: 'scroll',
      pageIconColor: '#1976d2',
      pageIconInactiveColor: '#666',
      pageTextStyle: {
        color: '#ccc',
      },
      formatter: (name: string) => {
        const item = props.data.find(d => d.name === name)
        if (item) {
          const total = props.data.reduce((sum, d) => sum + d.value, 0)
          const percentage = ((item.value / total) * 100).toFixed(1)
          // 截断过长的名字
          const shortName = name.length > 10 ? name.substring(0, 10) + '...' : name
          return `${shortName} ${percentage}%`
        }
        return name
      },
    },
    series: [
      {
        name: props.title,
        type: 'pie',
        radius: ['35%', '55%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#1e1e1e',
          borderWidth: 2,
        },
        label: {
          show: false,
          position: 'center',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#ccc',
            formatter: (params: any) => {
              return `{b|${params.name}}\n{c|${params.value}}\n{d|${params.percent}%}`
            },
            rich: {
              b: {
                fontSize: 12,
                lineHeight: 18,
              },
              c: {
                fontSize: 16,
                fontWeight: 'bold',
                lineHeight: 22,
              },
              d: {
                fontSize: 11,
                lineHeight: 16,
              },
            },
          },
        },
        labelLine: {
          show: false,
        },
        data: props.data,
      },
    ],
  }
})
</script>

<style scoped>
.pie-chart {
  width: 100%;
}
</style>
