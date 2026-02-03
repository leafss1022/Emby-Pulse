<template>
  <div class="page">
    <PageHeader title="用户统计" subtitle="分析用户观看行为和偏好" />

    <v-fade-transition mode="out-in">
      <!-- 骨架屏加载 -->
      <LoadingState v-if="loading" preset="chart-table" />

      <!-- 数据展示 -->
      <div v-else-if="usersData">
        <!-- 用户统计图表 -->
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card v-reveal data-delay="100" hover>
              <v-card-title class="card-header">
                <span>用户观看统计</span>
                <v-icon>mdi-chart-bar</v-icon>
              </v-card-title>
              <v-card-text>
                <UsersChart
                  :data="usersData.users"
                  :sort-by="sortBy"
                />
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- 用户详细表格 -->
        <v-row>
          <v-col cols="12">
            <v-card v-reveal data-delay="200" hover>
              <v-card-title class="card-header">
                <span>用户详情</span>
                <v-select
                  v-model="sortBy"
                  :items="sortOptions"
                  item-title="label"
                  item-value="value"
                  label="排序方式"
                  density="compact"
                  variant="outlined"
                  hide-details
                  style="max-width: 200px"
                />
              </v-card-title>
              <v-card-text>
                <DataTable
                  :columns="userColumns"
                  :data="sortedUsers"
                  item-key="username"
                  mobile-icon="mdi-account"
                >
                  <!-- 自定义用户名列 -->
                  <template #cell-username="{ item }">
                    <div class="d-flex align-center">
                      <Avatar :name="item.username" size="32" class="mr-2" />
                      {{ item.username }}
                    </div>
                  </template>

                  <!-- 移动端头像 -->
                  <template #mobile-prepend="{ item }">
                    <Avatar :name="item.username" size="48" class="mr-3" />
                  </template>

                  <!-- 移动端标题 -->
                  <template #mobile-title="{ item }">
                    {{ item.username }}
                  </template>

                  <!-- 移动端副标题 -->
                  <template #mobile-subtitle="{ item }">
                    <div class="d-flex flex-column">
                      <span>观看次数: {{ formatNumber((item as Record<string, unknown>).play_count as number) }}</span>
                      <span>观看时长: {{ ((item as Record<string, unknown>).duration_hours as number).toFixed(1) }} 小时</span>
                      <span>最后观看: {{ (item as Record<string, unknown>).last_play ? formatDate((item as Record<string, unknown>).last_play as string) : '-' }}</span>
                    </div>
                  </template>
                </DataTable>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- 空状态 -->
      <EmptyState v-else message="暂无用户统计数据" />
    </v-fade-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Card, Avatar, DataTable, PageHeader, LoadingState, EmptyState, type Column } from '@/components/ui'
import { UsersChart } from '@/components/charts'
import { useServerStore, useFilterStore } from '@/stores'
import { useDataFetch } from '@/composables/useDataFetch'
import { statsApi } from '@/services'
import { formatDuration, formatDate, formatNumber } from '@/utils'
import type { UsersData } from '@/types'

const serverStore = useServerStore()
const filterStore = useFilterStore()

const usersData = ref<UsersData | null>(null)
const sortBy = ref<'play_count' | 'duration_hours'>('play_count')

const sortOptions = [
  { label: '观看次数', value: 'play_count' },
  { label: '观看时长', value: 'duration_hours' },
]

// 表格列定义
const userColumns: Column[] = [
  { key: 'username', label: '用户名' },
  { key: 'play_count', label: '观看次数', align: 'right', format: (v) => formatNumber(v as number) },
  { key: 'duration_hours', label: '观看时长（小时）', align: 'right', format: (v) => (v as number).toFixed(1) },
  { key: 'last_play', label: '最后观看', align: 'right', format: (v) => v ? formatDate(v as string) : '-' },
]

// 排序后的用户列表
const sortedUsers = computed(() => {
  if (!usersData.value?.users) return []

  return [...usersData.value.users].sort((a, b) => {
    return b[sortBy.value] - a[sortBy.value]
  })
})

// 使用 useDataFetch 处理数据获取
const { loading } = useDataFetch(
  async () => {
    const response = await statsApi.getUsers({
      server_id: serverStore.currentServer!.id,
      ...filterStore.buildQueryParams,
    })
    usersData.value = response.data
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
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
}
</style>
