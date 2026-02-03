<template>
  <div class="page">
    <PageHeader title="播放历史" subtitle="查看所有播放记录和搜索内容" />

    <v-row>
      <v-col cols="12">
        <v-card style="overflow: visible !important; touch-action: pan-y;">
          <v-card-title class="card-header">
            <span>最近播放</span>
            <v-icon>mdi-history</v-icon>
          </v-card-title>
          <v-card-text>
            <!-- 搜索栏 -->
            <div class="d-flex flex-column flex-sm-row align-sm-center justify-space-between ga-3 mb-4">
              <!-- 搜索框 -->
              <div class="d-flex ga-3 flex-grow-1" style="max-width: 450px;">
                <v-text-field
                  v-model="searchInput"
                  placeholder="搜索内容名称..."
                  prepend-inner-icon="mdi-magnify"
                  :append-inner-icon="searchInput ? 'mdi-close' : ''"
                  @click:append-inner="clearSearch"
                  @keydown.enter="handleSearch"
                  density="comfortable"
                  variant="outlined"
                  hide-details
                  rounded
                  style="flex: 1;"
                />
                <v-btn
                  color="primary"
                  @click="handleSearch"
                  rounded
                >
                  搜索
                </v-btn>
              </div>
            </div>

            <!-- 搜索结果提示 -->
            <div v-if="searchQuery" class="mb-4 text-caption text-medium-emphasis">
              搜索结果："{{ searchQuery }}"
              <span v-if="!loading && searchStats">
                ({{ searchStats.count }} 条记录，共 {{ formatDuration(searchStats.duration) }})
              </span>
            </div>

            <!-- 列表内容 -->
            <div class="history-content">
              <v-fade-transition mode="out-in">
                <!-- 初始加载状态 -->
                <div v-if="isInitialLoading" key="loading" class="d-flex justify-center py-12">
                  <v-progress-circular indeterminate color="primary" />
                </div>

                <!-- 无限滚动容器 -->
                <v-infinite-scroll
                  v-else
                  key="content"
                  :items="historyItems"
                  @load="loadMore"
                  :disabled="!hasMore"
                  side="end"
                >
                <!-- 搜索结果：标准卡片列表 -->
                <template v-if="isSearching">
                  <div class="search-results-list">
                    <div
                      v-for="(item, index) in searchItems"
                      :key="item._searchKey"
                      v-reveal
                      class="d-flex align-center pa-3 mb-3 rounded-lg border bg-card-hover cursor-pointer transition-all"
                      @click="goToContentDetail(String(item.item_id))"
                    >
                      <!-- 左侧海报 -->
                      <div class="flex-shrink-0 mr-4">
                        <LazyImage
                          v-if="item.poster_url"
                          :src="item.poster_url"
                          width="56px"
                          height="80px"
                          :cover="true"
                          class="rounded shadow-sm"
                        />
                        <div v-else class="d-flex align-center justify-center rounded bg-grey-lighten-3" style="width: 56px; height: 80px;">
                          <v-icon icon="mdi-filmstrip" color="grey" />
                        </div>
                      </div>

                      <!-- 右侧信息：严格 3 行布局 -->
                      <div class="flex-grow-1 min-w-0 d-flex flex-column justify-center">
                        <!-- 第一行：标题 -->
                        <div class="text-subtitle-1 font-weight-bold text-primary text-truncate mb-1">
                          {{ formatEpisodeName(item.item_name) }}
                        </div>
                        
                        <!-- 第二行：用户 | 客户端 -->
                        <div class="d-flex align-center text-caption text-medium-emphasis mb-1">
                          <div style="width: 160px; flex-shrink: 0;" class="d-flex align-center">
                            <v-icon size="14" class="mr-2" color="blue">mdi-account</v-icon>
                            <span class="text-truncate">{{ item.username }}</span>
                          </div>
                          <div class="ml-8 d-flex align-center text-truncate">
                            <v-icon size="14" class="mr-2" color="purple">mdi-cellphone-link</v-icon>
                            <span class="text-truncate">{{ item.client }} <span class="opacity-60 d-none d-sm-inline">({{ item.device }})</span></span>
                          </div>
                        </div>

                        <!-- 第三行：时间 | 时长 -->
                        <div class="d-flex align-center text-caption text-medium-emphasis">
                          <div style="width: 160px; flex-shrink: 0; white-space: nowrap;" class="d-flex align-center">
                            <v-icon size="14" class="mr-2" color="cyan">mdi-clock-outline</v-icon>
                            <span>{{ formatDateTime(item.time) }}</span>
                          </div>
                          <div v-if="item.duration_minutes" class="ml-8 d-flex align-center text-truncate">
                            <v-icon size="14" class="mr-2" color="success">mdi-timer-outline</v-icon>
                            <span class="text-truncate">{{ formatDuration(item.duration_minutes * 60) }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- 默认：海报网格展示 -->
                <template v-else>
                  <v-row dense>
                    <v-col
                      v-for="(item, index) in itemsWithServerUrls"
                      :key="`poster-${item.item_id}-${item.time}-${index}`"
                      cols="4"
                      sm="3"
                      md="2"
                      lg="2"
                    >
                      <PosterCard
                        v-reveal
                        :title="formatEpisodeName(item.item_name)"
                        :poster-url="item.poster_url"
                        :subtitle="`${item.username} · ${formatDateTime(item.time)}`"
                        @click="goToContentDetail(String(item.item_id))"
                      />
                    </v-col>
                  </v-row>
                </template>

                <!-- 加载更多状态 -->
                <template #loading>
                  <div class="d-flex justify-center py-4">
                    <v-progress-circular indeterminate color="primary" size="24" />
                  </div>
                </template>

                <!-- 没有更多数据 -->
                <template #empty>
                  <div class="text-center py-8 text-caption text-medium-emphasis">
                    <v-divider class="mb-4" />
                    已加载全部记录 (共 {{ historyItems.length }} 条)
                  </div>
                </template>

                <!-- 错误状态 -->
                <template #error="{ props }">
                  <div class="text-center py-4">
                    <p class="text-error mb-2">加载失败</p>
                    <v-btn v-bind="props" variant="text" color="primary">重试</v-btn>
                  </div>
                </template>
              </v-infinite-scroll>
            </v-fade-transition>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { PosterCard, LazyImage, PageHeader, LoadingState } from '@/components/ui'
import { useServerStore, useFilterStore } from '@/stores'
import { useDataFetch } from '@/composables/useDataFetch'
import { usePosterUrl } from '@/composables'
import { statsApi } from '@/services'
import { formatDateTime, formatDuration } from '@/utils'
import type { RecentItem } from '@/types'

const router = useRouter()
const serverStore = useServerStore()
const filterStore = useFilterStore()
const { useItemsWithPosterUrls } = usePosterUrl()

const historyItems = ref<RecentItem[]>([])
const searchInput = ref('')
const searchQuery = ref('')
const searchStats = ref<{ count: number; duration: number } | null>(null)
const searchListKey = ref(0)

const pageSize = 42
const hasMore = ref(true)
const isInitialLoading = ref(true)

// 是否在搜索状态
const isSearching = computed(() => !!searchQuery.value.trim())

// 给历史记录项的海报URL添加server_id和尺寸参数
const itemsWithServerUrls = useItemsWithPosterUrls(historyItems, 'large')
const searchItems = computed(() =>
  itemsWithServerUrls.value.map((item, index) => ({
    ...item,
    _searchKey: `${item.item_id ?? 'unknown'}-${item.time}-${index}`,
  }))
)

// 格式化剧集名称（提取S01E02等信息）
function formatEpisodeName(name: string): string {
  if (!name) return ''

  // 如果包含 " - " 分隔符，提取剧集信息
  if (name.includes(' - ')) {
    const parts = name.split(' - ')
    const episodePart = parts[1]
    if (episodePart) {
      const match = episodePart.match(/s(\d+)e(\d+)/i)
      if (match && match[1] && match[2]) {
        const season = match[1]
        const episode = match[2]
        return `${parts[0]} S${season}E${episode}`
      }
    }
  }

  return name
}

// 记录正在加载的 offset，防止重复请求
const loadingOffsets = new Set<number>()

// 加载更多数据
async function loadMore({ done }: { done: (status: 'loading' | 'error' | 'empty' | 'ok') => void }) {
  // 如果正在初始加载或已经没有更多，直接返回
  if (isInitialLoading.value || !hasMore.value || !serverStore.currentServer) {
    if (!hasMore.value) done('empty')
    else done('ok')
    return
  }

  const offset = historyItems.value.length
  
  // 防止重复加载同一个 offset
  if (loadingOffsets.has(offset)) {
    done('loading')
    return
  }

  loadingOffsets.add(offset)

  try {
    // 构建查询参数
    const params: any = {
      server_id: serverStore.currentServer.id,
      limit: pageSize,
      offset: offset,
    }

    if (isSearching.value) {
      params.search = searchQuery.value.trim()
    } else {
      Object.assign(params, filterStore.buildQueryParams)
    }

    const response = await statsApi.getRecent(params)
    const newItems = response.data.recent || []
    const total = response.data.total_count || 0

    if (newItems.length > 0) {
      // 避免重复添加
      const existingKeys = new Set(historyItems.value.map(item => `${item.time}-${item.item_id}`))
      const filteredNewItems = newItems.filter(item => !existingKeys.has(`${item.time}-${item.item_id}`))
      
      if (filteredNewItems.length > 0) {
        historyItems.value.push(...filteredNewItems)
      }

      // 判断是否还有更多
      hasMore.value = historyItems.value.length < total
      done(hasMore.value ? 'ok' : 'empty')
    } else {
      hasMore.value = false
      done('empty')
    }
  } catch (error) {
    console.error('Failed to load more history:', error)
    done('error')
  } finally {
    loadingOffsets.delete(offset)
  }
}

// 使用 useDataFetch 处理初始加载和刷新
const { loading, refresh } = useDataFetch(
  async () => {
    isInitialLoading.value = true
    historyItems.value = []
    hasMore.value = true
    loadingOffsets.clear()

    try {
      // 显式加载第 1 页
      const params: any = {
        server_id: serverStore.currentServer!.id,
        limit: pageSize,
        offset: 0,
      }

      if (isSearching.value) {
        params.search = searchQuery.value.trim()
      } else {
        Object.assign(params, filterStore.buildQueryParams)
      }

      const response = await statsApi.getRecent(params)
      const items = response.data.recent || []
      const total = response.data.total_count || 0
      
      historyItems.value = items

      // 搜索模式下保存统计信息
      searchStats.value = isSearching.value
        ? { count: total, duration: response.data.total_duration_seconds || 0 }
        : null

      // 判断是否还有更多
      hasMore.value = historyItems.value.length < total
    } finally {
      isInitialLoading.value = false
    }
  },
  {
    immediate: true,
    watchFilter: false,
  }
)

// 刷新函数
function handleRefresh() {
  refresh()
}

// 自定义监听：只在非搜索状态下监听筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    if (!isSearching.value) {
      handleRefresh()
    }
  },
  { deep: true }
)

// 监听搜索状态变化
watch(searchQuery, () => {
  handleRefresh()
})

// 执行搜索
function handleSearch() {
  searchQuery.value = searchInput.value
}

// 清除搜索
function clearSearch() {
  searchInput.value = ''
  searchQuery.value = ''
}

// 跳转到内容详情
function goToContentDetail(itemId: string) {
  router.push(`/content/${itemId}`)
}
</script>

<style scoped>
.search-results-list {
  display: flex;
  flex-direction: column;
}

.history-scroll-container {
  /* 让容器高度自适应，v-infinite-scroll 会自动寻找父级滚动容器 */
  min-height: 200px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
}
</style>
