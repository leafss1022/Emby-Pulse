<template>
  <v-navigation-drawer
    v-model="isOpenModel"
    location="right"
    temporary
    width="500"
  >
    <!-- 头部 -->
    <template #prepend>
      <div class="pa-4 d-flex align-center justify-space-between border-b">
        <div class="text-h6">名称映射设置</div>
        <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          @click="close"
        />
      </div>
    </template>

    <!-- Tab 切换 -->
    <v-tabs v-model="activeTab" bg-color="transparent" grow>
      <v-tab value="clients">
        <v-icon start>mdi-monitor</v-icon>
        客户端 ({{ clientMappings.length }})
      </v-tab>
      <v-tab value="devices">
        <v-icon start>mdi-cellphone</v-icon>
        设备 ({{ deviceMappings.length }})
      </v-tab>
    </v-tabs>

    <!-- 内容 -->
    <v-window v-model="activeTab" class="flex-grow-1">
      <!-- 客户端映射 -->
      <v-window-item value="clients">
        <div class="pa-4">
          <v-alert
            v-if="loading"
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <v-progress-circular indeterminate size="20" class="mr-2" />
            加载中...
          </v-alert>

          <p class="text-caption text-grey mb-4">
            将长客户端名称映射为简短的显示名称。左侧填写原始名称，右侧填写显示名称。
          </p>

          <!-- 映射列表 -->
          <div class="mb-4">
            <div
              v-for="(mapping, index) in clientMappings"
              :key="index"
              class="d-flex align-center gap-2 mb-2"
            >
              <v-text-field
                v-model="mapping.original"
                placeholder="原始名称"
                variant="outlined"
                density="compact"
                hide-details
              />
              <v-icon>mdi-arrow-right</v-icon>
              <v-text-field
                v-model="mapping.display"
                placeholder="显示名称"
                variant="outlined"
                density="compact"
                hide-details
              />
              <v-btn
                icon="mdi-delete"
                color="error"
                variant="text"
                size="small"
                @click="removeClientMapping(index)"
              />
            </div>
          </div>

          <!-- 添加按钮 -->
          <v-btn
            prepend-icon="mdi-plus"
            variant="text"
            color="primary"
            @click="addClientMapping()"
          >
            添加映射
          </v-btn>
        </div>
      </v-window-item>

      <!-- 设备映射 -->
      <v-window-item value="devices">
        <div class="pa-4">
          <v-alert
            v-if="loading"
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <v-progress-circular indeterminate size="20" class="mr-2" />
            加载中...
          </v-alert>

          <p class="text-caption text-grey mb-4">
            将长设备名称映射为简短的显示名称。左侧填写原始名称，右侧填写显示名称。
          </p>

          <!-- 映射列表 -->
          <div class="mb-4">
            <div
              v-for="(mapping, index) in deviceMappings"
              :key="index"
              class="d-flex align-center gap-2 mb-2"
            >
              <v-text-field
                v-model="mapping.original"
                placeholder="原始名称"
                variant="outlined"
                density="compact"
                hide-details
              />
              <v-icon>mdi-arrow-right</v-icon>
              <v-text-field
                v-model="mapping.display"
                placeholder="显示名称"
                variant="outlined"
                density="compact"
                hide-details
              />
              <v-btn
                icon="mdi-delete"
                color="error"
                variant="text"
                size="small"
                @click="removeDeviceMapping(index)"
              />
            </div>
          </div>

          <!-- 添加按钮 -->
          <v-btn
            prepend-icon="mdi-plus"
            variant="text"
            color="primary"
            @click="addDeviceMapping()"
          >
            添加映射
          </v-btn>
        </div>
      </v-window-item>
    </v-window>

    <!-- 底部操作 -->
    <template #append>
      <div class="pa-4 border-t">
        <v-alert
          v-if="message"
          :type="message.type"
          variant="tonal"
          density="compact"
          closable
          class="mb-3"
          @click:close="message = null"
        >
          {{ message.text }}
        </v-alert>

        <v-btn
          block
          color="primary"
          :loading="saving"
          @click="handleSave"
        >
          <v-icon start>mdi-content-save</v-icon>
          保存配置
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { nameMappingApi } from '@/services'

interface MappingEntry {
  original: string
  display: string
}

interface Props {
  isOpen: boolean
}

interface Emits {
  (e: 'update:isOpen', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isOpenModel = computed({
  get: () => props.isOpen,
  set: (value) => emit('update:isOpen', value)
})

const activeTab = ref<'clients' | 'devices'>('clients')
const clientMappings = ref<MappingEntry[]>([])
const deviceMappings = ref<MappingEntry[]>([])
const loading = ref(false)
const saving = ref(false)
const message = ref<{ type: 'success' | 'error' | 'info'; text: string } | null>(null)

// 加载映射配置
async function loadMappings() {
  loading.value = true
  try {
    const response = await nameMappingApi.getNameMappings()
    const data = response.data

    // 转换为数组格式
    clientMappings.value = Object.entries(data.clients || {}).map(([original, display]) => ({
      original,
      display: display as string
    }))

    deviceMappings.value = Object.entries(data.devices || {}).map(([original, display]) => ({
      original,
      display: display as string
    }))
  } catch (error) {
    console.error('加载映射配置失败:', error)
    message.value = { type: 'error', text: '加载配置失败' }
  } finally {
    loading.value = false
  }
}

// 保存配置
async function handleSave() {
  saving.value = true
  message.value = null
  try {
    // 转换回对象格式，过滤掉空映射
    const mappings = {
      clients: Object.fromEntries(
        clientMappings.value
          .filter(m => m.original && m.display)
          .map(m => [m.original, m.display])
      ),
      devices: Object.fromEntries(
        deviceMappings.value
          .filter(m => m.original && m.display)
          .map(m => [m.original, m.display])
      )
    }

    const response = await nameMappingApi.saveNameMappings(mappings)
    if (response.data.status === 'ok') {
      message.value = { type: 'success', text: '保存成功，刷新页面后生效' }
    } else {
      message.value = { type: 'error', text: '保存失败' }
    }
  } catch (error) {
    console.error('保存映射配置失败:', error)
    message.value = { type: 'error', text: '保存失败' }
  } finally {
    saving.value = false
  }
}

// 客户端映射操作
function addClientMapping() {
  clientMappings.value.push({ original: '', display: '' })
}

function removeClientMapping(index: number) {
  clientMappings.value.splice(index, 1)
}

// 设备映射操作
function addDeviceMapping() {
  deviceMappings.value.push({ original: '', display: '' })
}

function removeDeviceMapping(index: number) {
  deviceMappings.value.splice(index, 1)
}

function close() {
  isOpenModel.value = false
}

// 监听面板打开状态
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadMappings()
  }
})
</script>

<style scoped>
.border-b {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.border-t {
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>
