<template>
  <v-card v-if="sessions.length > 0" class="mb-4">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-play-circle" class="mr-2" color="success" />
      <span>正在播放 ({{ sessions.length }})</span>
      <v-spacer />
      <v-chip size="small" color="success" variant="flat">
        <v-icon icon="mdi-circle" size="x-small" class="mr-1 animate-pulse" />
        实时
      </v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text class="pa-2">
      <v-list density="compact">
        <v-list-item
          v-for="(session, index) in sessionsWithServerUrls"
          :key="index"
          class="mb-2"
        >
          <template #prepend>
            <v-avatar size="48" rounded>
              <v-img
                v-if="session.poster_url"
                :src="session.poster_url"
                cover
              />
              <v-icon v-else icon="mdi-television" />
            </v-avatar>
          </template>

          <v-list-item-title class="text-body-2 font-weight-medium">
            {{ session.item_name }}
          </v-list-item-title>

          <v-list-item-subtitle class="text-caption">
            <v-icon icon="mdi-account" size="x-small" class="mr-1" />
            {{ session.user_name }}
            <v-icon icon="mdi-monitor" size="x-small" class="ml-2 mr-1" />
            {{ session.device_name }}
          </v-list-item-subtitle>

          <template #append>
            <div class="text-center" style="min-width: 60px">
              <v-icon
                :icon="session.is_paused ? 'mdi-pause' : 'mdi-play'"
                :color="session.is_paused ? 'warning' : 'success'"
                size="small"
              />
              <div class="text-caption">
                {{ Math.round(session.progress) }}%
              </div>
            </div>
          </template>

          <!-- 进度条 -->
          <v-progress-linear
            :model-value="session.progress"
            color="primary"
            height="4"
            class="mt-2"
          />

          <!-- 时间显示 -->
          <div class="text-caption text-grey mt-1" style="font-size: 11px">
            {{ formatTime(session.position_seconds) }} / {{ formatTime(session.runtime_seconds) }}
          </div>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import { statsApi } from '@/services'
import { useServerStore } from '@/stores'
import { getPosterUrl } from '@/utils'
import { REFRESH_INTERVALS, IMAGE_SIZES } from '@/constants'
import type { NowPlayingItem } from '@/types'

const serverStore = useServerStore()
const sessions = ref<NowPlayingItem[]>([])
const loading = ref(false)

/**
 * 格式化时间（秒 -> HH:MM:SS 或 MM:SS）
 */
function formatTime(seconds: number): string {
  if (!seconds || seconds < 0) return '0:00'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 给正在播放项的海报URL添加server_id和尺寸参数（小尺寸）
const sessionsWithServerUrls = computed(() => {
  return sessions.value.map(session => ({
    ...session,
    poster_url: getPosterUrl(
      session.poster_url,
      serverStore.currentServer?.id,
      IMAGE_SIZES.POSTER_SMALL.maxHeight,
      IMAGE_SIZES.POSTER_SMALL.maxWidth
    )
  }))
})

async function fetchNowPlaying() {
  if (loading.value || !serverStore.currentServer) return

  loading.value = true
  try {
    const response = await statsApi.getNowPlaying({
      server_id: serverStore.currentServer.id,
    })
    sessions.value = response.data.now_playing || []
  } catch (error) {
    console.error('Failed to fetch now playing:', error)
  } finally {
    loading.value = false
  }
}

// 自动刷新（每 5 秒）
const { pause, resume } = useIntervalFn(fetchNowPlaying, REFRESH_INTERVALS.NOW_PLAYING, {
  immediate: false,
})

onMounted(() => {
  fetchNowPlaying()
  resume()
})

onUnmounted(() => {
  pause()
})
</script>

<style scoped>
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
