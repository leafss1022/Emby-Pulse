<template>
  <div class="page">
    <v-fade-transition mode="out-in">
      <!-- 骨架屏加载 -->
      <LoadingState v-if="loading" key="loading">
        <v-row class="mb-6">
          <v-col cols="12" md="4">
            <v-card><v-skeleton-loader type="image" /></v-card>
          </v-col>
          <v-col cols="12" md="8">
            <v-card><v-skeleton-loader type="article" /></v-card>
          </v-col>
        </v-row>
        <v-card><v-skeleton-loader type="table" /></v-card>
      </LoadingState>

      <!-- 数据展示 -->
      <div v-else-if="contentDetail" key="content">
        <!-- 页面标题和返回按钮 -->
        <div class="page-header">
          <div>
            <div class="d-flex align-center mb-2">
              <v-btn
                icon="mdi-arrow-left"
                variant="text"
                size="small"
                @click="goBack"
              />
              <h2 class="page-title ml-2">{{ contentDetail.show_name || contentDetail.item_name }}</h2>
            </div>
            <p class="page-subtitle">
              查看内容详细信息和播放记录
            </p>
          </div>
        </div>

      <!-- 内容信息 -->
      <v-row class="mb-6">
        <v-col cols="12" md="4">
          <!-- 海报 -->
          <v-card hover>
            <LazyImage
              v-if="posterUrl"
              :src="posterUrl"
              aspect-ratio="0.67"
              :cover="true"
            >
              <template #placeholder>
                <div class="d-flex align-center justify-center fill-height">
                  <v-progress-circular indeterminate color="primary" size="48" />
                </div>
              </template>
              <template #error>
                <div class="d-flex align-center justify-center fill-height">
                  <v-icon icon="mdi-image-off" size="48" opacity="0.3" />
                </div>
              </template>
            </LazyImage>
            <LazyImage
              v-else
              src="/placeholder.png"
              aspect-ratio="0.67"
              :cover="true"
            />
          </v-card>
        </v-col>

        <v-col cols="12" md="8">
          <v-card hover>
            <v-card-title class="card-header">
              <span>基本信息</span>
              <v-icon>mdi-information</v-icon>
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template #prepend>
                    <v-icon icon="mdi-filmstrip" />
                  </template>
                  <v-list-item-title>类型</v-list-item-title>
                  <v-list-item-subtitle>{{ contentDetail.item_type }}</v-list-item-subtitle>
                </v-list-item>

                <v-list-item>
                  <template #prepend>
                    <v-icon icon="mdi-play-circle" />
                  </template>
                  <v-list-item-title>观看次数</v-list-item-title>
                  <v-list-item-subtitle>{{ hasPlayRecords ? formatNumber(contentDetail.stats.total_plays) : '暂无播放记录' }}</v-list-item-subtitle>
                </v-list-item>

                <v-list-item v-if="hasPlayRecords">
                  <template #prepend>
                    <v-icon icon="mdi-clock" />
                  </template>
                  <v-list-item-title>总时长</v-list-item-title>
                  <v-list-item-subtitle>{{ contentDetail.stats.total_duration_hours.toFixed(1) }} 小时</v-list-item-subtitle>
                </v-list-item>

                <v-list-item v-if="hasPlayRecords">
                  <template #prepend>
                    <v-icon icon="mdi-account-group" />
                  </template>
                  <v-list-item-title>观看用户数</v-list-item-title>
                  <v-list-item-subtitle>{{ contentDetail.stats.unique_users }}</v-list-item-subtitle>
                </v-list-item>

                <v-list-item v-if="hasPlayRecords">
                  <template #prepend>
                    <v-icon icon="mdi-calendar" />
                  </template>
                  <v-list-item-title>最后观看</v-list-item-title>
                  <v-list-item-subtitle>{{ contentDetail.stats.last_play ? formatDateTime(contentDetail.stats.last_play) : '-' }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>

              <!-- 简介 -->
              <v-divider v-if="contentDetail.overview" class="my-4" />
              <div v-if="contentDetail.overview">
                <div class="text-subtitle-2 mb-2 d-flex align-center">
                  <v-icon icon="mdi-text" size="small" class="mr-2" />
                  简介
                </div>
                <p class="text-body-2 text-medium-emphasis" style="line-height: 1.6;">
                  {{ contentDetail.overview }}
                </p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- 播放历史 -->
      <v-row v-if="hasPlayRecords">
        <v-col cols="12">
          <v-card hover>
            <v-card-title class="card-header">
              <span>播放历史</span>
              <v-icon>mdi-history</v-icon>
            </v-card-title>
            <v-card-text>
              <!-- 桌面端表格 -->
              <v-table v-if="!mobile" density="comfortable">
                <thead>
                  <tr>
                    <th>内容</th>
                    <th>用户</th>
                    <th>设备</th>
                    <th>客户端</th>
                    <th class="text-right">观看时长</th>
                    <th class="text-right">播放时间</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(record, index) in contentDetail.play_records" :key="index">
                    <td>
                      <div class="d-flex align-center">
                        <div class="poster-thumbnail mr-3">
                          <LazyImage
                            v-if="posterUrl"
                            :src="posterUrl"
                            width="48px"
                            height="64px"
                            :cover="true"
                            class="rounded"
                          >
                            <template #placeholder>
                              <div class="poster-placeholder">
                                <v-icon icon="mdi-filmstrip" size="24" />
                              </div>
                            </template>
                            <template #error>
                              <div class="poster-placeholder">
                                <v-icon icon="mdi-filmstrip" size="24" />
                              </div>
                            </template>
                          </LazyImage>
                          <div v-else class="poster-placeholder">
                            <v-icon icon="mdi-filmstrip" size="24" />
                          </div>
                        </div>
                        <div>{{ record.item_name }}</div>
                      </div>
                    </td>
                    <td>
                      <div class="d-flex align-center">
                        <Avatar :name="record.username" size="32" class="mr-2" />
                        {{ record.username }}
                      </div>
                    </td>
                    <td>{{ record.device || '-' }}</td>
                    <td>{{ record.client || '-' }}</td>
                    <td class="text-right">{{ record.duration_minutes ? formatDuration(record.duration_minutes * 60) : '-' }}</td>
                    <td class="text-right">{{ formatDateTime(record.time) }}</td>
                  </tr>
                </tbody>
              </v-table>

              <!-- 移动端列表 -->
              <v-list v-else>
                <v-list-item
                  v-for="(record, index) in contentDetail.play_records"
                  :key="index"
                  class="mb-2"
                >
                  <template #prepend>
                    <div class="poster-thumbnail mr-3">
                      <LazyImage
                        v-if="posterUrl"
                        :src="posterUrl"
                        width="48px"
                        height="64px"
                        :cover="true"
                        class="rounded"
                      >
                        <template #placeholder>
                          <div class="poster-placeholder">
                            <v-icon icon="mdi-filmstrip" size="24" />
                          </div>
                        </template>
                        <template #error>
                          <div class="poster-placeholder">
                            <v-icon icon="mdi-filmstrip" size="24" />
                          </div>
                        </template>
                      </LazyImage>
                      <div v-else class="poster-placeholder">
                        <v-icon icon="mdi-filmstrip" size="24" />
                      </div>
                    </div>
                  </template>
                  <v-list-item-title class="font-weight-medium mb-1">
                    {{ record.item_name }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    <div class="d-flex flex-column">
                      <span>用户: {{ record.username }}</span>
                      <span>设备: {{ record.device || '-' }} / {{ record.client || '-' }}</span>
                      <span>时长: {{ record.duration_minutes ? formatDuration(record.duration_minutes * 60) : '-' }}</span>
                      <span class="text-caption">{{ formatDateTime(record.time) }}</span>
                    </div>
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- 空状态 -->
    <EmptyState v-else key="empty" message="未找到内容详情" />
  </v-fade-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { Avatar, LazyImage, LoadingState, EmptyState } from '@/components/ui'
import { useServerStore } from '@/stores'
import { usePosterUrl } from '@/composables'
import { statsApi } from '@/services'
import { formatDuration, formatDateTime, formatNumber } from '@/utils'
import type { ContentDetailData, StatsQueryParams } from '@/types'

const route = useRoute()
const router = useRouter()
const serverStore = useServerStore()
const { usePosterUrlComputed } = usePosterUrl()
const { mobile } = useDisplay()

const loading = ref(false)
const contentDetail = ref<ContentDetailData | null>(null)

// 判断是否有播放记录
const hasPlayRecords = computed(() => {
  return contentDetail.value &&
         contentDetail.value.play_records &&
         contentDetail.value.play_records.length > 0
})

// 给海报URL添加server_id和尺寸参数
const posterUrlSource = computed(() => contentDetail.value?.poster_url)
const posterUrl = usePosterUrlComputed(posterUrlSource, 'custom', { maxHeight: 900, maxWidth: 600 })

// 获取内容详情
async function fetchContentDetail() {
  const itemId = route.params.id as string

  if (!serverStore.currentServer || !itemId) return

  loading.value = true
  try {
    const params: StatsQueryParams & { item_id: string } = {
      server_id: serverStore.currentServer.id,
      item_id: itemId
    }

    const response = await statsApi.getContentDetail(params)
    contentDetail.value = response.data
  } catch (error) {
    console.error('Failed to fetch content detail:', error)
  } finally {
    loading.value = false
  }
}

// 返回上一页
function goBack() {
  router.back()
}

// 监听路由变化
watch(
  () => route.params.id,
  () => {
    fetchContentDetail()
  }
)

onMounted(() => {
  fetchContentDetail()
})
</script>

<style scoped>
/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
