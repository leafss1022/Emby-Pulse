<template>
  <div class="page">
    <PageHeader title="播放统计总览" subtitle="实时监控媒体服务器播放数据" />

    <!-- 正在播放 -->
    <NowPlaying v-reveal />

    <v-fade-transition mode="out-in">
      <!-- 骨架屏加载 -->
      <LoadingState v-if="loading" preset="overview" />

      <!-- 数据展示 -->
      <div v-else-if="overviewData && trendData && hourlyData">
        <!-- 统计卡片 -->
        <v-row class="mb-6">
          <v-col cols="12" sm="6" md="3">
            <StatCard
              v-reveal
              data-delay="100"
              icon="mdi-play-circle"
              icon-color="primary"
              icon-bg-color="rgba(29, 78, 216, 0.1)"
              label="总播放次数"
              :value="overviewData.total_plays"
              value-color="primary"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <StatCard
              v-reveal
              data-delay="200"
              icon="mdi-clock-outline"
              icon-color="success"
              icon-bg-color="rgba(34, 197, 94, 0.1)"
              label="总播放时长"
              :value="`${overviewData.total_duration_hours.toFixed(1)}h`"
              value-color="success"
              :animated="false"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <StatCard
              v-reveal
              data-delay="300"
              icon="mdi-account-group"
              icon-color="warning"
              icon-bg-color="rgba(249, 115, 22, 0.1)"
              label="活跃用户"
              :value="overviewData.unique_users"
              value-color="warning"
            />
          </v-col>

          <v-col cols="12" sm="6" md="3">
            <StatCard
              v-reveal
              data-delay="400"
              icon="mdi-filmstrip"
              icon-color="error"
              icon-bg-color="rgba(239, 68, 68, 0.1)"
              label="观看内容数"
              :value="overviewData.unique_items"
              value-color="error"
            />
          </v-col>
        </v-row>

        <!-- 趋势图表 -->
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card v-reveal data-delay="500" hover class="hover-lift">
              <v-card-title class="card-header">
                <span>播放趋势</span>
                <v-icon>mdi-chart-line</v-icon>
              </v-card-title>
              <v-card-text>
                <TrendChart
                  :data="trendData.trend"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 时段热力图 -->
        <v-row>
          <v-col cols="12">
            <v-card v-reveal data-delay="600" hover class="hover-lift">
              <v-card-title class="card-header">
                <span>活跃时段分布</span>
                <v-icon>mdi-clock-time-four-outline</v-icon>
              </v-card-title>
              <v-card-text>
                <HeatmapChart
                  :data="hourlyData.hourly"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- 空状态 -->
      <EmptyState v-else message="暂无统计数据" />
    </v-fade-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { StatCard, PageHeader, LoadingState, EmptyState } from '@/components/ui'
import { TrendChart, HeatmapChart } from '@/components/charts'
import NowPlaying from '@/components/NowPlaying.vue'
import { useServerStore, useFilterStore } from '@/stores'
import { statsApi } from '@/services'
import type { OverviewData, TrendData, HourlyData } from '@/types'

const serverStore = useServerStore()
const filterStore = useFilterStore()

const loading = ref(false)
const overviewData = ref<OverviewData | null>(null)
const trendData = ref<TrendData | null>(null)
const hourlyData = ref<HourlyData | null>(null)

// 获取所有概览数据
async function fetchOverviewData() {
  if (!serverStore.currentServer) return

  loading.value = true
  try {
    const params = {
      server_id: serverStore.currentServer.id,
      ...filterStore.buildQueryParams,
    }

    const [overviewRes, trendRes, hourlyRes] = await Promise.all([
      statsApi.getOverview(params),
      statsApi.getTrend(params),
      statsApi.getHourly(params),
    ])

    overviewData.value = overviewRes.data
    trendData.value = trendRes.data
    hourlyData.value = hourlyRes.data
  } catch (error) {
    console.error('Failed to fetch overview data:', error)
  } finally {
    loading.value = false
  }
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchOverviewData()
  },
  { deep: true }
)

onMounted(() => {
  fetchOverviewData()
})
</script>

<style scoped>
.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* 卡片标题 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
}
</style>
