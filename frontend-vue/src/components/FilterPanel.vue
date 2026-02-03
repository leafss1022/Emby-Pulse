<template>
  <v-navigation-drawer
    v-model="internalShow"
    location="right"
    width="400"
    temporary
  >
    <v-toolbar color="primary" density="compact">
      <v-toolbar-title>筛选</v-toolbar-title>
      <v-spacer />
      <v-btn icon="mdi-close" @click="handleClose" />
    </v-toolbar>

    <v-card flat>
      <v-card-text>
        <!-- 快速时间范围 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">时间范围</div>
          <v-btn-toggle
            v-model="filterStore.days"
            color="primary"
            variant="outlined"
            divided
            mandatory
            @update:model-value="handleDaysChange"
          >
            <v-btn :value="7" size="small">7天</v-btn>
            <v-btn :value="30" size="small">30天</v-btn>
            <v-btn :value="90" size="small">90天</v-btn>
            <v-btn :value="365" size="small">1年</v-btn>
          </v-btn-toggle>
        </div>

        <!-- 自定义日期范围 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">自定义日期</div>
          <v-text-field
            v-model="filterStore.startDate"
            type="date"
            label="开始日期"
            density="compact"
            variant="outlined"
            clearable
            hide-details="auto"
            class="mb-2"
            @update:model-value="handleDateChange"
          />
          <v-text-field
            v-model="filterStore.endDate"
            type="date"
            label="结束日期"
            density="compact"
            variant="outlined"
            clearable
            hide-details="auto"
            @update:model-value="handleDateChange"
          />
        </div>

        <v-divider class="my-4" />

        <!-- 用户筛选 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">用户</div>
          <v-select
            v-model="filterStore.users"
            :items="userOptions"
            item-title="name"
            item-value="id"
            label="选择用户"
            density="compact"
            variant="outlined"
            multiple
            chips
            closable-chips
            hide-details="auto"
          >
            <template #chip="{ item, props: chipProps }">
              <v-chip v-bind="chipProps" size="small">
                {{ item.title }}
              </v-chip>
            </template>
          </v-select>
        </div>

        <!-- 客户端筛选 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">客户端</div>
          <v-select
            v-model="filterStore.clients"
            :items="clientOptions"
            label="选择客户端"
            density="compact"
            variant="outlined"
            multiple
            chips
            closable-chips
            hide-details="auto"
          >
            <template #chip="{ item, props: chipProps }">
              <v-chip v-bind="chipProps" size="small">
                {{ item.title }}
              </v-chip>
            </template>
          </v-select>
        </div>

        <!-- 设备筛选 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">设备</div>
          <v-select
            v-model="filterStore.devices"
            :items="deviceOptions"
            label="选择设备"
            density="compact"
            variant="outlined"
            multiple
            chips
            closable-chips
            hide-details="auto"
          >
            <template #chip="{ item, props: chipProps }">
              <v-chip v-bind="chipProps" size="small">
                {{ item.title }}
              </v-chip>
            </template>
          </v-select>
        </div>

        <!-- 媒体类型筛选 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">媒体类型</div>
          <v-select
            v-model="filterStore.itemTypes"
            :items="itemTypeOptions"
            label="选择媒体类型"
            density="compact"
            variant="outlined"
            multiple
            chips
            closable-chips
            hide-details="auto"
          >
            <template #chip="{ item, props: chipProps }">
              <v-chip v-bind="chipProps" size="small">
                {{ item.title }}
              </v-chip>
            </template>
          </v-select>
        </div>

        <!-- 播放方式筛选 -->
        <div class="mb-4">
          <div class="text-subtitle-2 mb-2">播放方式</div>
          <v-select
            v-model="filterStore.playbackMethods"
            :items="playbackMethodOptions"
            label="选择播放方式"
            density="compact"
            variant="outlined"
            multiple
            chips
            closable-chips
            hide-details="auto"
          >
            <template #chip="{ item, props: chipProps }">
              <v-chip v-bind="chipProps" size="small">
                {{ item.title }}
              </v-chip>
            </template>
          </v-select>
        </div>
      </v-card-text>

      <v-divider />

      <!-- 底部操作按钮 -->
      <v-card-actions>
        <v-btn
          variant="text"
          color="error"
          prepend-icon="mdi-filter-off"
          @click="handleClearFilters"
        >
          清空筛选
        </v-btn>
        <v-spacer />
        <v-btn
          color="primary"
          variant="elevated"
          prepend-icon="mdi-check"
          @click="handleApply"
        >
          应用
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed, watch, onMounted } from 'vue'
import { useFilterStore, useServerStore } from '@/stores'

interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  apply: []
}>()

const filterStore = useFilterStore()
const serverStore = useServerStore()

const internalShow = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

// 筛选选项
const userOptions = computed(() => {
  return filterStore.options?.users || []
})

const clientOptions = computed(() => {
  return (
    filterStore.options?.clients.map((c) => ({
      title: c.display,
      value: c.original,
    })) || []
  )
})

const deviceOptions = computed(() => {
  return (
    filterStore.options?.devices.map((d) => ({
      title: d.display,
      value: d.original,
    })) || []
  )
})

const itemTypeOptions = computed(() => {
  return filterStore.options?.item_types || []
})

const playbackMethodOptions = computed(() => {
  return filterStore.options?.playback_methods || []
})

function handleDaysChange(value: number) {
  // 当选择快速时间范围时，清空自定义日期
  filterStore.setDateRange(null, null)
}

function handleDateChange() {
  // 当设置自定义日期时，清空快速时间范围
  if (filterStore.startDate || filterStore.endDate) {
    filterStore.setDays(0)
  }
}

function handleClearFilters() {
  filterStore.clearFilters()
  emit('apply')
}

function handleApply() {
  emit('apply')
  handleClose()
}

function handleClose() {
  emit('update:modelValue', false)
}

// 当服务器切换时，重新加载筛选选项
watch(
  () => serverStore.currentServer?.id,
  (serverId) => {
    if (serverId) {
      filterStore.fetchFilterOptions(serverId)
    }
  }
)

onMounted(() => {
  if (serverStore.currentServer) {
    filterStore.fetchFilterOptions(serverStore.currentServer.id)
  }
})
</script>
