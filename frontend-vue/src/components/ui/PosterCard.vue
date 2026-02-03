<template>
  <div
    class="poster-card"
    @click="handleClick"
  >
    <LazyImage
      :src="finalPosterUrl"
      :aspect-ratio="aspectRatio"
      :cover="true"
      class="poster-image"
      root-margin="100px"
    >
      <!-- 加载骨架屏 -->
      <template #placeholder>
        <div class="d-flex align-center justify-center fill-height bg-grey-darken-3">
          <v-icon icon="mdi-filmstrip" size="48" color="grey-darken-1" />
        </div>
      </template>

      <!-- 加载失败占位 -->
      <template #error>
        <div class="d-flex align-center justify-center fill-height bg-grey-darken-3">
          <v-icon icon="mdi-image-off" size="48" color="grey-darken-1" />
        </div>
      </template>
    </LazyImage>

    <!-- 排名角标 -->
    <div v-if="showRank && rank" class="rank-badge">
      <v-chip
        :color="getRankColor(rank)"
        size="small"
        label
      >
        {{ rank }}
      </v-chip>
    </div>

    <!-- 播放次数角标 -->
    <div v-if="showPlayCount && playCount" class="play-count-badge">
      {{ playCount }}次
    </div>

    <!-- 底部信息栏（在海报内部） -->
    <div class="info-overlay">
      <div class="title-text">
        {{ title }}
      </div>
      <div v-if="subtitle" class="subtitle-text">
        {{ subtitle }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useServerStore } from '@/stores'
import { appendServerId } from '@/utils'
import LazyImage from './LazyImage.vue'

interface Props {
  posterUrl?: string
  title?: string
  subtitle?: string
  showRank?: boolean
  rank?: number
  showPlayCount?: boolean
  playCount?: number
  aspectRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  aspectRatio: 2 / 3,
})

const emit = defineEmits<{
  click: []
}>()

const serverStore = useServerStore()

// 给 URL 追加 server_id
const finalPosterUrl = computed(() => {
  return appendServerId(props.posterUrl, serverStore.currentServer?.id)
})

function handleClick() {
  emit('click')
}

function getRankColor(rank: number): string {
  if (rank === 1) return 'amber'
  if (rank === 2) return 'blue-grey'
  if (rank === 3) return 'orange-darken-2'
  return 'grey'
}
</script>

<style scoped>
.poster-card {
  position: relative;
  cursor: pointer;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px;
  overflow: hidden;
  background-color: rgb(39, 39, 42);
}

.poster-card:hover {
  transform: scale(1.03);
}

.poster-image {
  border-radius: 12px;
  position: relative;
}

.rank-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 2;
}

.play-count-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
  background-color: rgb(59, 130, 246);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  padding-top: 32px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9), transparent);
  z-index: 1;
}

.title-text {
  color: white;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.2;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subtitle-text {
  color: rgb(212, 212, 216);
  font-size: 10px;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
