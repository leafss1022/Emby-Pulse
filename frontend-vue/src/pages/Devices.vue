<template>
  <div class="page">
    <PageHeader title="设备统计" subtitle="了解客户端和设备的使用情况" />

    <v-fade-transition mode="out-in">
      <!-- 骨架屏加载 -->
      <LoadingState v-if="loading" preset="dual-chart-dual-table" />

      <!-- 数据展示 -->
      <div v-else-if="devicesData">
        <!-- 客户端和设备分布图表 -->
        <v-row class="mb-6">
          <v-col cols="12" md="6">
            <v-card v-reveal data-delay="100" hover>
              <v-card-title class="card-header">
                <span>客户端分布</span>
                <v-icon>mdi-application</v-icon>
              </v-card-title>
              <v-card-text>
                <PieChart :data="clientsChartData" />
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="6">
            <v-card v-reveal data-delay="200" hover>
              <v-card-title class="card-header">
                <span>设备分布</span>
                <v-icon>mdi-monitor</v-icon>
              </v-card-title>
              <v-card-text>
                <PieChart :data="devicesChartData" />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 客户端详细表格 -->
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card v-reveal data-delay="300" hover>
              <v-card-title class="card-header">
                <span>客户端详情</span>
                <v-icon>mdi-view-list</v-icon>
              </v-card-title>
              <v-card-text>
                <DataTable
                  :columns="clientColumns"
                  :data="devicesData.clients"
                  item-key="client"
                  mobile-icon="mdi-application"
                >
                  <!-- 自定义客户端列 -->
                  <template #cell-client="{ item }">
                    <div class="d-flex align-center">
                      <v-icon icon="mdi-application" class="mr-2" />
                      {{ item.client }}
                    </div>
                  </template>

                  <!-- 移动端标题 -->
                  <template #mobile-title="{ item }">
                    {{ item.client }}
                  </template>

                  <!-- 移动端副标题 -->
                  <template #mobile-subtitle="{ item }">
                    观看次数: {{ formatNumber((item as Record<string, unknown>).play_count as number) }}
                  </template>
                </DataTable>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 设备详细表格 -->
        <v-row>
          <v-col cols="12">
            <v-card v-reveal data-delay="400" hover>
              <v-card-title class="card-header">
                <span>设备详情</span>
                <v-icon>mdi-view-list</v-icon>
              </v-card-title>
              <v-card-text>
                <DataTable
                  :columns="deviceColumns"
                  :data="devicesData.devices"
                  item-key="device"
                  mobile-icon="mdi-monitor"
                >
                  <!-- 自定义设备列 -->
                  <template #cell-device="{ item }">
                    <div class="d-flex align-center">
                      <v-icon icon="mdi-monitor" class="mr-2" />
                      {{ item.device }}
                    </div>
                  </template>

                  <!-- 移动端标题 -->
                  <template #mobile-title="{ item }">
                    {{ item.device }}
                  </template>

                  <!-- 移动端副标题 -->
                  <template #mobile-subtitle="{ item }">
                    观看次数: {{ formatNumber((item as Record<string, unknown>).play_count as number) }}
                  </template>
                </DataTable>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- 空状态 -->
      <EmptyState v-else message="暂无设备统计数据" />
    </v-fade-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, DataTable, PageHeader, LoadingState, EmptyState, type Column } from '@/components/ui'
import { PieChart } from '@/components/charts'
import { useServerStore, useFilterStore } from '@/stores'
import { useDataFetch } from '@/composables/useDataFetch'
import { statsApi } from '@/services'
import { formatDuration, formatNumber, formatPercentage } from '@/utils'

// 自定义类型
interface ClientData {
  client: string
  play_count: number
  total_duration?: number
  percentage?: number
}

interface DeviceData {
  device: string
  play_count: number
  total_duration?: number
  percentage?: number
}

interface DevicesData {
  clients: ClientData[]
  devices: DeviceData[]
}

const serverStore = useServerStore()
const filterStore = useFilterStore()

const devicesData = ref<DevicesData | null>(null)

// 表格列定义
const clientColumns: Column[] = [
  { key: 'client', label: '客户端' },
  { key: 'play_count', label: '观看次数', align: 'right', format: (v) => formatNumber(v as number) },
]

const deviceColumns: Column[] = [
  { key: 'device', label: '设备' },
  { key: 'play_count', label: '观看次数', align: 'right', format: (v) => formatNumber(v as number) },
]

// 客户端图表数据
const clientsChartData = computed(() => {
  if (!devicesData.value?.clients) return []

  return devicesData.value.clients.map((client: ClientData) => ({
    name: client.client,
    value: client.play_count,
  }))
})

// 设备图表数据
const devicesChartData = computed(() => {
  if (!devicesData.value?.devices) return []

  return devicesData.value.devices.map((device: DeviceData) => ({
    name: device.device,
    value: device.play_count,
  }))
})

// 使用 useDataFetch 处理数据获取
const { loading } = useDataFetch(
  async () => {
    const params = {
      server_id: serverStore.currentServer!.id,
      ...filterStore.buildQueryParams,
    }

    // 并行加载客户端和设备数据
    const [clientsResponse, devicesResponse] = await Promise.all([
      statsApi.getClients(params),
      statsApi.getDevices(params),
    ])

    devicesData.value = {
      clients: clientsResponse.data.clients || [],
      devices: devicesResponse.data.devices || [],
    }
  },
  {
    immediate: true,
    watchFilter: true,
  }
)
</script>

<style scoped>
.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  padding: 16px !important;
}

/* 确保卡片内容不与标题重叠 */
:deep(.v-card-text) {
  padding-top: 16px !important;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
}
</style>
