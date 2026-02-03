<template>
  <div class="page">
    <PageHeader title="内容统计" subtitle="发现最受欢迎的内容和剧集" />

    <!-- 热门内容 -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card style="overflow: visible !important; touch-action: pan-y;">
          <v-card-title class="card-header">
            <span>热门内容</span>
            <v-icon>mdi-fire</v-icon>
          </v-card-title>
          <v-card-text>
            <v-fade-transition mode="out-in">
              <!-- 加载状态 -->
              <LoadingState v-if="topContentLoading" preset="spinner" />

              <!-- 瀑布流海报展示 -->
              <v-row v-else-if="topContents.length > 0">
                <v-col
                  v-for="(item, index) in topContentsWithUrls"
                  :key="`top-content-${item.item_id}-${index}`"
                  cols="6"
                  sm="4"
                  md="3"
                  lg="2"
                >
                  <PosterCard
                    v-reveal
                    :title="item.show_name || item.name"
                    :poster-url="item.poster_url"
                    :play-count="item.play_count"
                    :duration="item.duration_hours * 3600"
                    @click="goToContentDetail(item, true)"
                  />
                </v-col>
              </v-row>

              <!-- 空状态 -->
              <div v-else class="text-center text-grey pa-8">
                暂无数据
              </div>
            </v-fade-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 播放排行 -->
    <v-row>
      <v-col cols="12">
        <v-card style="overflow: visible !important; touch-action: pan-y;">
          <v-card-title class="card-header">
            <span>播放排行</span>
            <v-icon>mdi-trophy</v-icon>
          </v-card-title>
          <v-card-text>
            <v-fade-transition mode="out-in">
              <!-- 加载状态 -->
              <LoadingState v-if="contentLoading" preset="spinner" />

              <!-- 播放排行列表 -->
              <div v-else-if="contents.length > 0" class="ranking-list">
                <div
                  v-for="(item, index) in contentsWithUrls"
                  :key="`content-${item.item_id}-${index}`"
                  v-reveal
                  class="ranking-item"
                  @click="goToContentDetail(item, false)"
                >
                  <!-- 排名 -->
                  <div class="ranking-number" :class="`rank-${index + 1}`">
                    {{ index + 1 }}
                  </div>

                  <!-- 海报 -->
                  <div class="ranking-poster">
                    <LazyImage
                      v-if="item.poster_url"
                      :src="item.poster_url"
                      :alt="item.show_name || item.name"
                      width="60px"
                      height="90px"
                      :cover="true"
                      class="poster-img"
                    >
                      <template #placeholder>
                        <div class="poster-placeholder">
                          <v-icon icon="mdi-filmstrip" size="32" />
                        </div>
                      </template>
                      <template #error>
                        <div class="poster-placeholder">
                          <v-icon icon="mdi-image-off" size="32" />
                        </div>
                      </template>
                    </LazyImage>
                    <div v-else class="poster-placeholder">
                      <v-icon icon="mdi-image-off" size="32" />
                    </div>
                  </div>

                  <!-- 内容信息 -->
                  <div class="ranking-info">
                    <div class="ranking-title">
                      {{ item.show_name || item.name }}
                    </div>
                    <div class="ranking-meta">
                      <v-chip size="x-small" color="primary" class="mr-2">
                        <v-icon icon="mdi-play-circle" size="12" class="mr-1" />
                        {{ item.play_count }} 次
                      </v-chip>
                      <v-chip size="x-small" color="secondary">
                        <v-icon icon="mdi-clock-outline" size="12" class="mr-1" />
                        {{ formatDuration(item.duration_hours * 3600) }}
                      </v-chip>
                    </div>
                  </div>

                  <!-- 箭头 -->
                  <div class="ranking-arrow">
                    <v-icon icon="mdi-chevron-right" />
                  </div>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-else class="text-center text-grey pa-8">
                暂无数据
              </div>
            </v-fade-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PosterCard, LazyImage, PageHeader, LoadingState } from '@/components/ui'
import { useServerStore, useFilterStore } from '@/stores'
import { usePosterUrl } from '@/composables'
import { statsApi } from '@/services'
import { formatDuration } from '@/utils'
import { LIST_LIMITS } from '@/constants'
import type { ContentItem } from '@/types'

const router = useRouter()
const serverStore = useServerStore()
const filterStore = useFilterStore()
const { useItemsWithPosterUrls } = usePosterUrl()

const topContentLoading = ref(false)
const contentLoading = ref(false)
const topContents = ref<ContentItem[]>([])
const contents = ref<ContentItem[]>([])

// 给热门内容的海报URL添加server_id和尺寸参数
const topContentsWithUrls = useItemsWithPosterUrls(topContents, 'large')

// 给播放排行的海报URL添加server_id和尺寸参数
const contentsWithUrls = useItemsWithPosterUrls(contents, 'large')

// 获取热门内容（包括剧集和电影）
async function fetchTopContent() {
  if (!serverStore.currentServer) return

  const params = {
    server_id: serverStore.currentServer.id,
    ...filterStore.buildQueryParams,
    limit: LIST_LIMITS.TOP_CONTENT,
  }

  const response = await statsApi.getTopContent(params)
  topContents.value = response.data.top_content || []
}

// 获取播放排行
async function fetchPlayRankings() {
  if (!serverStore.currentServer) return

  const params = {
    server_id: serverStore.currentServer.id,
    ...filterStore.buildQueryParams,
    limit: LIST_LIMITS.PLAY_RANKING,
  }

  const response = await statsApi.getTopContent(params)
  contents.value = response.data.top_content || []
}

// 并行加载所有数据
async function fetchAllData() {
  if (!serverStore.currentServer) return

  // 统一 loading 状态
  topContentLoading.value = true
  contentLoading.value = true

  try {
    // 并行加载两个数据源
    await Promise.all([
      fetchTopContent(),
      fetchPlayRankings()
    ])
  } catch (error) {
    console.error('Failed to fetch content data:', error)
  } finally {
    topContentLoading.value = false
    contentLoading.value = false
  }
}

// 跳转到内容详情
function goToContentDetail(item: ContentItem, _isShowsCard: boolean) {
  // 热门剧集和播放排行都直接跳转，后端已经返回正确的 ID
  router.push({
    path: `/content/${item.item_id}`,
    query: { name: item.show_name }
  })
}

// 监听服务器和筛选器变化
watch(
  () => [serverStore.currentServer?.id, filterStore.buildQueryParams],
  () => {
    fetchAllData()
  },
  { deep: true }
)

onMounted(() => {
  fetchAllData()
})
</script>

<style scoped>
/* 排行榜样式 */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.ranking-item:hover {
  background: rgba(var(--v-theme-surface-variant), 0.5);
  transform: translateX(4px);
}

.ranking-poster {
  flex-shrink: 0;
  width: 60px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
}

.poster-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ranking-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-title {
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ranking-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.ranking-arrow {
  flex-shrink: 0;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.ranking-item:hover .ranking-arrow {
  opacity: 1;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }

  .ranking-number {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .ranking-poster {
    width: 50px;
    height: 75px;
  }

  .ranking-title {
    font-size: 14px;
  }
}
</style>
